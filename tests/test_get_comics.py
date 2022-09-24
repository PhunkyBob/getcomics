# -*- coding: utf-8 -*-
from context import getcomics
from datetime import date
import asyncio
import copy

url = "https://getcomics.info/marvel/star-wars-episode-iv-a-new-hope-remastered-2015/"
search_result = [
    {
        "title": "Star Wars – The Mandalorian #3",
        "language": "English",
        "image": "JPG",
        "date": "2022-09-21",
        "year": "2022",
        "size": "40 MB",
        "links": {
            "GETCOMICS": "https://getcomics.info/links.php/ozit5+c/AmgxkldjEfKYZCnytR8eoLLkF6NEUOFADqcPdJ/qBpxvJ/iZSZqoe+5U2B6bwFhsBuUzzqx+uIkfdap9JPTZ+DW3vCrV7apPPHj/oCNT/jWGaW6jDVgexm+3t0b/H/5TQ22tOk8vhIkMgmx5ot0xzk75qI3pRqguaiLywJ8nwL+Zu8hk6KdgxFuT:Bous8IqytiTg6vfcwt9bRw==",
            "MEGA": "https://getcomics.info/links.php/EvzpaNRgj3D6jveIZRL5MVkdsgLQnwZHrsIfzSfD7ZsZ9nbUkZhhRhYIvQReOom1A+Dr5hoB079DSP4EWKtyTWmLtv21N2Kc49EiuF7cSuA=:cXypjkXotET2IfDwMurjWA==",
        },
        "source": "https://getcomics.in...an-3-2022/",
    },
    {
        "title": "Star Wars – Darth Vader #27",
        "language": "English",
        "image": "JPG",
        "date": "2022-09-21",
        "year": "2022",
        "size": "32 MB",
        "links": {
            "GETCOMICS": "https://getcomics.info/links.php/aCPah2SZ5hjFNyfbU9twwv/ghod5GnOiyB6ARS1ScvjBkP+IAyTOj7BhrFKeA1dEhxDk55c12N9LDvshuoWm3bT4Yd29L2YXgEwknR46IW25a9fm2pbQCYZUHuODlJ0d7SDAXOcCrLxhIfrCDM8JLIECIBCJfeBk3fZ3GkUfBvmlOE6fZnyAGcLXK3QIjOk+:O30IadYpG9u/NGd+Vicwng==",
            "MEGA": "https://getcomics.info/links.php/E4wPAPwIEcWW8+U7ht0Ybv5a9a6lxUEF7HAZSAGLYz32JOA3JJRVmr5XHzCo6K1EXtzBIc1R+Lnqw2MQxIB0FXuJAwa7QcDhXo3q4DaNTs8=:JJ/iGaSYUI7lGXlWu5PzSg==",
        },
        "source": "https://getcomics.in...r-27-2022/",
    },
]


parsed_result = [
    {
        "date": "2022-09-21",
        "title": "Star Wars – The Mandalorian #3",
        "year": "2022",
        "size": "40 MB",
        "language": "English",
        "image": "JPG",
        "host": "GETCOMICS",
        "url": "https://getcomics.info/links.php/ozit5+c/AmgxkldjEfKYZCnytR8eoLLkF6NEUOFADqcPdJ/qBpxvJ/iZSZqoe+5U2B6bwFhsBuUzzqx+uIkfdap9JPTZ+DW3vCrV7apPPHj/oCNT/jWGaW6jDVgexm+3t0b/H/5TQ22tOk8vhIkMgmx5ot0xzk75qI3pRqguaiLywJ8nwL+Zu8hk6KdgxFuT:Bous8IqytiTg6vfcwt9bRw==",
    }
]


def test_search_limit_date():
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")
    gc = getcomics.gc.GetComics("star wars", limit_date=today_str, pages=100)
    assert gc.search_pattern == "star+wars"
    res = gc.search()
    assert len(res) < 20


def test_search_page_async():
    gc = getcomics.gc.GetComics()
    gc.set_search("star wars")
    res = asyncio.run(gc.search_page_async(1))
    assert res
    assert "title" in res[0]
    assert res[0]["title"]


def test_search_page_sync():
    gc = getcomics.gc.GetComics()
    gc.set_search("star wars")
    res = gc.search_page_sync()
    assert res
    assert "title" in res[0]
    assert res[0]["title"]


def test_get_infos_from_page():
    res = getcomics.gc.GetComics().get_infos_from_page(url)
    assert res
    assert res["title"] == "Star Wars – Episode IV – A New Hope – Remastered (2015)"
    assert res["date"] == "2018-11-27"
    assert len(res["links"]) > 0


def test_parse_result_async():
    result = copy.deepcopy(search_result)
    res = getcomics.gc.GetComics().parse_results(result, ["MEGA"], True)
    assert len(res) == 2
    for i in range(len(res)):
        assert res[i]["url"].startswith("https://mega.nz")
        assert res[i]["host"] == "MEGA"


def test_parse_result_sync():
    result = copy.deepcopy(search_result)
    res = getcomics.gc.GetComics().parse_results_sync(result, ["MEGA"])
    assert len(res) == 2
    for i in range(len(res)):
        assert res[i]["url"].startswith("https://mega.nz")
        assert res[i]["host"] == "MEGA"


def test_write_result(capsys):
    result = copy.deepcopy(parsed_result)
    getcomics.gc.GetComics.write_results(result)
    captured = capsys.readouterr()
    lines = [l.strip() for l in captured.out.split("\n") if l]
    assert len(lines) == 2
    assert lines[0].startswith("date")
    assert lines[1].startswith("2022")
