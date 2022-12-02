# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""The script for setting up airphin."""
import logging
import os
import sys
from distutils.dir_util import remove_tree
from typing import List

if sys.version_info.major < 3 or (
    sys.version_info.major == 3 and sys.version_info.minor < 7
):
    raise Exception("airphin support Python 3.7 and above.")

from os.path import dirname, join

from setuptools import Command, find_packages, setup

version = "0.0.2"

logger = logging.getLogger(__name__)

# Start package required
prod = [
    "libcst",
    "PyYaml",
]

style = [
    "flake8>=4.0",
    "flake8-docstrings>=1.6",
    "flake8-black>=0.2",
    "isort>=5.10",
    "autoflake>=1.4",
]

test = [
    "pytest>=6.2",
]

dev = style + test + prod


def read(*names, **kwargs):
    """Read a file and return the contents as a string."""
    return open(
        join(dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")
    ).read()


class CleanCommand(Command):
    """Command to clean up python api before setup by running `python setup.py pre_clean`."""

    description = "Clean up project root"
    user_options: List[str] = []
    clean_list = [
        "build",
        "htmlcov",
        "dist",
        ".pytest_cache",
        ".coverage",
    ]

    def initialize_options(self) -> None:
        """Set default values for options."""

    def finalize_options(self) -> None:
        """Set final values for options."""

    def run(self) -> None:
        """Run and remove temporary files."""
        for cl in self.clean_list:
            if not os.path.exists(cl):
                logger.info("Path %s do not exists.", cl)
            elif os.path.isdir(cl):
                remove_tree(cl)
            else:
                os.remove(cl)
        logger.info("Finish pre_clean process.")


setup(
    name="airphin",
    version=version,
    license="Apache License 2.0",
    description="Airflow to DolphinScheduler migration tool",
    long_description=read("README.md"),
    # Make sure pypi is expecting markdown!
    long_description_content_type="text/markdown",
    author="Jay Chung",
    author_email="zhongjiajie955@gmail.com",
    url="https://github.com/WhaleOps/airphin",
    python_requires=">=3.6",
    keywords=[
        "transfer",
        "tool",
        "parser",
        "airflow",
        "dolphinscheduler",
    ],
    project_urls={
        "Source": "https://github.com/WhaleOps/airphin",
        "Issue Tracker": "https://github.com/WhaleOps/airphin/issues",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "airphin": ["rules/**/*.yaml"],
    },
    platforms=["any"],
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Utilities",
        "Topic :: Software Development :: Quality Assurance",
    ],
    install_requires=prod,
    extras_require={
        "dev": dev,
    },
    cmdclass={
        "clean": CleanCommand,
    },
    entry_points={
        "console_scripts": [
            "airphin = airphin.cli.command:main",
        ],
    },
)
