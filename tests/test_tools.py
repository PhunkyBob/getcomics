# -*- coding: utf-8 -*-
from getcomics import tools
import pytest
from pathlib import Path
import asyncio
import getcomics.tools


def test_date_validator():
    res = getcomics.tools.date_validator("", "", "2000-01-31")
    assert res
    with pytest.raises(Exception) as e_info:
        res = getcomics.tools.date_validator("", "", "2000-40-40")


def test_is_valid_date():
    res = tools.is_valid_date("dummy")
    assert res == False
    res = tools.is_valid_date("2000-40-40")
    assert res == False
    res = tools.is_valid_date("2000-01-31")
    assert res == True


def test_file_not_exists_validator():
    res = tools.file_not_exists_validator("", "i_dont_exists.ext")
    assert res
    with pytest.raises(Exception) as e_info:
        script_path = Path(__file__).absolute()
        res = tools.file_not_exists_validator("", script_path)


def test_get_hosts():
    input_list = [
        {
            "links": {
                "HOST1": "link_1_host_1",
                "HOST2": "link_1_host_2",
                "HOST3": "link_1_host_2",
            }
        },
        {
            "links": {
                "HOST1": "link_2_host_1",
                "HOST2": "link_2_host_2",
            }
        },
        {
            "links": {
                "HOST4": "link_3_host_4",
            }
        },
    ]
    output = tools.get_hosts(input_list)
    assert len(output.keys()) == 4
    assert output["HOST1"] == 2


def test_get_link_location():
    url = "https://getcomics.info/links.php/4IIXVMKPJMO43AE+zepg979QY0MCBCaNmlJujhElpkJeza3bpEFuvtJLNzI1+qUpoAKEcerRsgyHpTCzAouV2kJRjMsPw+CCp5HfZ8XQm14=:KdtFqwiCBCxScicqSRF0UA=="
    new_url = tools.get_link_location(url)
    assert new_url.startswith("https://mega.nz")


def test_get_link_location_async():
    url = "https://getcomics.info/links.php/4IIXVMKPJMO43AE+zepg979QY0MCBCaNmlJujhElpkJeza3bpEFuvtJLNzI1+qUpoAKEcerRsgyHpTCzAouV2kJRjMsPw+CCp5HfZ8XQm14=:KdtFqwiCBCxScicqSRF0UA=="
    url, new_url = asyncio.run(tools.get_link_location_async(url))
    assert new_url.startswith("https://mega.nz")
