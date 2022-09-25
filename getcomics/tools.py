# -*- coding: utf-8 -*-
from getcomics import default_values

# import default_values
import click
import inquirer
import re
from datetime import datetime
from collections import defaultdict
import requests
import asyncio
import os


def check_version(current_version):
    latest_version_url = "https://raw.githubusercontent.com/PhunkyBob/getcomics/master/VERSION"
    res = requests.get(latest_version_url)
    if res.status_code != 200:
        print(f"Version {current_version} (can't check official version)")
    else:
        latest_version = res.text.strip()
        if latest_version == current_version:
            print(f"Version {current_version} (official version)")
        else:
            print(f"Version {current_version} (official version is different: {latest_version})")
            print("Please check https://github.com/PhunkyBob/getcomics/releases/latest")
    print()


def inquir(query):
    questions = [query]
    answers = inquirer.prompt(questions)
    _, val = answers.popitem()
    return val


def date_validator(ctx, param, value):
    if is_valid_date(value):
        return value
    else:
        raise click.BadParameter("Format must be 'YYYY-MM-DD'")


def is_valid_date(value: str):
    format = "%Y-%m-%d"
    if not re.match("(\d{4})-(\d{2})-(\d{2})", value):
        return False
    res = True
    try:
        res = bool(datetime.strptime(value, format))
    except ValueError:
        res = False
    return res


def file_not_exists_validator(answers, current):
    if current and os.path.exists(current):
        raise inquirer.errors.ValidationError("", reason="File already exists...")
    return True


def override_parameters(search, host, limit_date, pages, output):
    search = inquir(inquirer.Text("search", message="Search for"))

    # Print default parameters
    print("Default parameters: ")
    title = "Limit date:"
    print(f"{title:20} {limit_date}")
    title = "Limit pages:"
    print(f"{title:20} {pages}")
    hosts_txt = ", ".join(host)
    title = "Filter on host(s):"
    print(f"{title:20} {hosts_txt}")

    # Override default parameters.
    keep_default = inquir(inquirer.List("keep_default", message="Keep default parameters?", choices=["Yes", "No"]))
    if keep_default.lower() == "no":
        limit_date = inquir(
            inquirer.Text(
                "date",
                message=f"Limit date (default: {default_values.DEFAULT_LIMIT_DATE})",
                validate=lambda _, x: is_valid_date(x) or not x,
            )
        )
        if not limit_date:
            limit_date = default_values.DEFAULT_LIMIT_DATE
        pages = inquir(
            inquirer.Text(
                "pages",
                message=f"How many pages to search (default: {default_values.DEFAULT_PAGES})",
                validate=lambda _, x: x.isdigit() or not x,
            )
        )
        if not pages:
            pages = default_values.DEFAULT_PAGES
        pages = int(pages)
        output = inquir(
            inquirer.Text(
                "output",
                message="Save result to file (default: print in console)",
            )
        )
        host = "?"

    return search, host, limit_date, pages, output


def confirm_output(output: str) -> str:
    overwrite = inquir(inquirer.List("overwrite", message="File already exists. Overwrite?", choices=["Yes", "No"]))
    if overwrite.lower() == "no":
        output = inquir(
            inquirer.Text(
                "output",
                message=f"Save result to file (default: print in console)",
                validate=file_not_exists_validator,
            )
        )
    return output


def get_hosts(all_links: list) -> dict:
    hosts = defaultdict(int)
    for elem in all_links:
        for k in elem["links"].keys():
            hosts[k] += 1
    return hosts


def get_link_location(url):
    try:
        res = requests.get(url, allow_redirects=False)
        if res.status_code in [300, 301, 302, 307, 308] and "Location" in res.headers:
            url = res.headers["Location"]
    except:
        pass  # This link is maybe invalid, it's okay
    return url


async def get_link_location_async(url):
    new_url = url
    try:
        res = await http_get(url, allow_redirects=False)
        if res.status_code in [300, 301, 302, 307, 308] and "Location" in res.headers:
            new_url = res.headers["Location"]
    except:
        pass  # This link is maybe invalid, it's okay
    return url, new_url


def http_get_sync(url: str, allow_redirects: bool = True):
    response = requests.get(url, allow_redirects=allow_redirects)
    return response


async def http_get(url: str, allow_redirects: bool = True):
    return await asyncio.to_thread(http_get_sync, url, allow_redirects)
