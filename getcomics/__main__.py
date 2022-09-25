# -*- coding: utf-8 -*-
"""
Get direct links for GetComics releases.
You can search with the following criteria: 
- Search string.
- Limit date.
- Number of page results. 
Result can be saved in a file. 
"""

__version__ = "0.1.0"

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from getcomics.gc import GetComics
import getcomics.tools as tools
import getcomics.default_values as default_values
import click
import inquirer
import os


@click.command()
@click.argument("search", required=False)
@click.option("--host", help="Filter links on specific host.", multiple=True)
@click.option(
    "--limit-date",
    help="Don't return releases older than this date (format: YYYY-MM-DD).",
    default=default_values.DEFAULT_LIMIT_DATE,
    callback=tools.date_validator,
)
@click.option("--pages", help="Search on the first N pages.", type=int, default=default_values.DEFAULT_PAGES)
@click.option("-o", "--output", help="Save result to file.")
@click.option("-v", "--version", is_flag=True, help="Display version.")
def main(search, host, limit_date, pages, output, version) -> None:
    tools.check_version(__version__)
    if version:
        sys.exit(0)

    is_command_line = True
    if not search:
        search, host, limit_date, pages, output = tools.override_parameters(search, host, limit_date, pages, output)
        is_command_line = False

    gc = GetComics(search, pages=pages, limit_date=limit_date)
    res = gc.search()

    if host == "?":
        available_hosts = tools.get_hosts(res)
        choices = [(f"{k} ({v}/{len(res)})", k) for k, v in available_hosts.items()]
        host = tools.inquir(inquirer.Checkbox("host", message="Filter on host(s)", choices=choices, carousel=True))

    parsed = GetComics.parse_results(res, host, gc.async_mode)
    if output and os.path.exists(output) and not is_command_line:
        output = tools.confirm_output(output)

    GetComics.write_results(parsed, output)


if __name__ == "__main__":
    main()
