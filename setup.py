# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="getcomics",
    version="0.1.0",
    description="Get direct links for GetComics.info releases.",
    long_description=readme,
    author="PhunkyBob",
    author_email="PhunkyBob@noreply.github.com",
    url="https://github.com/PhunkyBob/getcomics",
    license=license,
    packages=find_packages(exclude=("tests", "docs")),
)
