#!/usr/bin/env python

import os
from setuptools import setup, find_packages
from jerrybuild import __METADATA__


def find_requirements():
    with open("requirements.txt", "r") as fh:
        return [line.strip() for line in fh.readlines()]

def find_data_files():
    """
    Walk through data/ and return a list of all its contents suitable for
    passing to setup()'s `data_files`.
    """
    data_files = []

    for walk_dir, walk_subdirs, walk_files in os.walk('data/'):
        dst_dir = os.path.join("lib", __METADATA__["name"], walk_dir.lstrip("data/"))
        src_files = [os.path.join(walk_dir, walk_file) for walk_file in walk_files]
        data_files.append([dst_dir, src_files])

    return data_files

setup(
    name=__METADATA__["name"],
    version=__METADATA__["version"],
    author=__METADATA__["author"],
    author_email=__METADATA__["author_email"],
    description=__METADATA__["desc"],
    keywords="security report reporting alert alerting scan intrusion detection",
    url=__METADATA__["homepage"],
    classifiers=[
        "License :: OSI Approved :: GNU Affero General Public License v3"
    ],

    install_requires=find_requirements(),
    python_requires='>=3',
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "{name} = {name}.main:main".format(name=__METADATA__["name"])
        ]
    },
    data_files=find_data_files(),
)
