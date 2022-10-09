# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import urllib.parse
import datetime
import re
import asyncio

from getcomics import tools
from tqdm.asyncio import tqdm

# import tools
import csv
from io import StringIO


class GetComics:
    root_path: str = "https://getcomics.info/page"
    search_pattern: str
    pages: int = 1
    from_page: int = 1
    limit_date: datetime
    async_mode: bool = True

    def __init__(self, search: str = "", pages: int = 1, from_page: int = 1, limit_date: str = "") -> None:
        self.search_pattern = urllib.parse.quote_plus(search)
        self.pages = pages
        self.from_page = from_page
        self.limit_date = datetime.datetime.strptime("1901-01-01", "%Y-%m-%d")
        if limit_date:
            self.limit_date = datetime.datetime.strptime(limit_date, "%Y-%m-%d")

    def set_search(self, search: str = "") -> None:
        self.search_pattern = urllib.parse.quote_plus(search)

    def set_pages(self, pages: int = 1):
        self.pages = pages

    def set_from_page(self, from_page: int = 1):
        self.from_page = from_page

    def set_limit_date(self, limit_date) -> None:
        self.limit_date = datetime.datetime.strptime("1901-01-01", "%Y-%m-%d")
        if limit_date:
            self.limit_date = datetime.datetime.strptime(limit_date, "%Y-%m-%d")

    def search(self) -> list:
        """Search and retreive the desired number of result pages."""
        results = []
        current_page = self.from_page
        for current_page in range(self.from_page, self.from_page + self.pages):
            new_results = self.search_page(current_page)
            if len(new_results) == 0:
                break
            results += new_results
        return results

    def search_page(self, page: int = 1) -> list:
        if self.async_mode:
            return asyncio.run(self.search_page_async(page))
        return self.search_page_sync(page)

    async def search_page_async(self, page: int = 1) -> list:
        """
        Search infos on all releases of the result page N.
        Infos will be retrieved in a asynchronous way.
        """
        results = []
        url = f"{self.root_path}/{page}/?s={self.search_pattern}"
        res = requests.get(url)
        if res.status_code not in [200]:
            return results
        soup = BeautifulSoup(res.text, features="html.parser")

        all_urls = []
        for div in soup.find_all("div", class_="post-info"):
            title = div.find("h1")
            if title:
                main_url = title.find("a").get("href")
                all_urls.append(main_url)

        results = await tqdm.gather(
            *[GetComics.get_infos_from_page_async(url) for url in all_urls], desc=f"Page {page}", leave=False
        )
        results = [elem for elem in results if datetime.datetime.strptime(elem["date"], "%Y-%m-%d") >= self.limit_date]

        return results

    def search_page_sync(self, page: int = 1) -> list:
        """
        DEPRECATED
        Search infos on all releases of the result page N.
        Infos will be retrieved 1 by 1 (synchronous).
        """
        results = []
        url = f"{self.root_path}/{page}/?s={self.search_pattern}"
        res = requests.get(url)
        if res.status_code not in [200]:
            return results
        soup = BeautifulSoup(res.text, features="html.parser")
        for div in soup.find_all("div", class_="post-info"):
            title = div.find("h1")
            if title:
                main_url = title.find("a").get("href")
                infos = GetComics.get_infos_from_page(main_url)
                if self.limit_date >= datetime.datetime.strptime(infos["date"], "%Y-%m-%d"):
                    break
                results.append(infos)
        return results

    @staticmethod
    def get_infos_from_page(url) -> dict:
        return asyncio.run(GetComics.get_infos_from_page_async(url))

    @staticmethod
    async def get_infos_from_page_async(url) -> dict:
        infos = {
            "date": "?",
            "title": "?",
            "year": "?",
            "size": "?",
            "language": "?",
            "image": "?",
            "source": url,
            "links": {},
        }

        # res = requests.get(url)
        res = await tools.http_get(url)
        if res.status_code not in [200]:
            return infos
        soup = BeautifulSoup(res.text, features="html.parser")
        post_date = soup.find("li", class_="post-date")
        if post_date:
            infos["date"] = post_date.find("time").get("datetime")
        content = soup.find("section", class_="post-contents")
        if content:
            for p in content.find_all("p"):
                r = re.match(
                    "(?P<title>.+)Language :\s(?P<language>.+) \| Image Format :\s(?P<image>.+) \| Year :\s(?P<year>.+) \| Size :\s(?P<size>.+)",
                    p.text,
                )
                if r:
                    infos["title"] = r.group("title")
                    infos["language"] = r.group("language")
                    infos["image"] = r.group("image")
                    infos["year"] = r.group("year")
                    infos["size"] = r.group("size")
                    break

        for div in soup.find_all("div", class_="aio-pulse"):
            link = div.find("a")
            title = link.get("title")
            if title.upper() == "DOWNLOAD NOW":
                title = "GETCOMICS"
            title = title.split(" ")[0]
            href = link.get("href")
            infos["links"][title.upper()] = href

        return infos

    @staticmethod
    def parse_results(search_result: list[dict], hosts_filter: list | None = None, async_mode: bool = True):
        if async_mode:
            return asyncio.run(GetComics.parse_results_async(search_result, hosts_filter))
        return GetComics.parse_results_sync(search_result, hosts_filter)

    @staticmethod
    async def parse_results_async(search_result: list[dict], hosts_filter: list | None = None):
        # First we get a list of all links.
        all_urls = []
        for elem in search_result:
            links = elem["links"]
            for h, l in links.items():
                if not hosts_filter or h in hosts_filter:
                    all_urls.append(l)
        results = await tqdm.gather(*[tools.get_link_location_async(url) for url in all_urls], desc="Links")
        url_real_location = {old: new for old, new in results}

        output = []
        for elem in search_result:
            links = elem["links"]
            del elem["links"]
            del elem["source"]
            for h, l in links.items():
                if not hosts_filter or h in hosts_filter:
                    url = url_real_location[l]
                    elem["host"] = h
                    elem["url"] = url
                    output.append(elem.copy())
        return output

    @staticmethod
    def parse_results_sync(search_result: list[dict], hosts_filter: list | None = None):
        output = []
        for elem in search_result:
            links = elem["links"]
            del elem["links"]
            del elem["source"]
            for h, l in links.items():
                if not hosts_filter or h in hosts_filter:
                    url = tools.get_link_location(l)
                    elem["host"] = h
                    elem["url"] = url
                    output.append(elem.copy())
        return output

    @staticmethod
    def write_results(result: list[dict], output: str = ""):
        delimiter = ";"
        if not output:
            delimiter = "\t"

        f = StringIO()
        writer = csv.DictWriter(f, fieldnames=result[0].keys(), delimiter=delimiter, lineterminator="\n")
        writer.writeheader()
        for elem in result:
            writer.writerow(elem)

        if not output:
            print(f.getvalue())
        else:
            with open(output, "w", encoding="utf-8") as file:
                file.write(f.getvalue())
            print(f'Result saved in "{output}".')
