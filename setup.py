"""The script for setting up airtolphin."""

import sys

if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 9):
    raise Exception("airtolphin support Python 3.9 and above.")

from os.path import dirname
from os.path import join

from setuptools import find_packages, setup

version = "0.0.1dev"


def read(*names, **kwargs):
    """Read a file and return the contents as a string."""
    return open(
        join(dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")
    ).read()


setup(
    name="airtolphin",
    version=version,
    license="MIT License",
    description="Airflow to DolphinScheduler migration tool",
    long_description=read("README.md"),
    # Make sure pypi is expecting markdown!
    long_description_content_type="text/markdown",
    author="Jay Chung",
    author_email="zhongjiajie955@gmail.com",
    url="https://github.com/WhaleOps/airtolphin",
    python_requires=">=3.9",
    keywords=[
        "transfer",
        "tool",
        "parser",
        "airflow",
        "dolphinscheduler",
    ],
    project_urls={
        "Source": "https://github.com/WhaleOps/airtolphin",
        "Issue Tracker": "https://github.com/WhaleOps/airtolphin/issues",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
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
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Utilities",
        "Topic :: Software Development :: Quality Assurance",
    ],
    install_requires=[
        # Core
        'libcst',
    ],
)
