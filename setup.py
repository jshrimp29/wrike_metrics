#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open("wrike_metrics/version.py") as f:
    exec(f.read())

long_description = open('README.md').read()

with open('requirements.txt') as requirements:
    required = requirements.read().splitlines()

kwargs = {
    "name": "wrike_metrics",
    "version": str(__version__),
    "packages": ['wrike_metrics'],
    "package_data": {'': ['*.credentials','wrike_files/*']},
    "include_package_data": True,
    "description": "Python module to transform tasks on the Wrike platform and run performance metrics",
    "long_description": long_description,
    "author": "Tim Campbell",
    "maintainer": "Tim Campbell",
    "author_email": "campbell.timothym@gmail.com",
    "maintainer_email": "campbell.timothym@gmail.com",
    "license": "MIT",
    "install_requires": required,
    "url": "https://github.com/jshrimp29/wrike_metrics",
    "download_url": "https://github.com/jshrimp29/wrike_metrics/archive/master.tar.gz",
    "keywords": "wrike project-management api python",
    "classifiers": [
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
}

setup(**kwargs)