#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from setuptools import setup
from setuptools import find_packages


def get_version(package):
    with open(os.path.join(package, "__init__.py")) as f:
        return re.search("__version__ = ['\"]([^'\"]+)['\"]", f.read()).group(1)


def get_long_description():
    with open("README.md", encoding="utf8") as f:
        return f.read()


setup(
    name="jupyter_kernel_hook",
    python_requires=">=3.6",
    version=get_version("jupyter_kernel_hook"),
    license="MIT",
    description="Compose simple and intuitive Jupyter server extension hooks.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="ryxcommar",
    author_email="ryxcommar@gmail.com",
    url="https://github.com/ryxcommar/jupyter_kernel_hook",
    packages=find_packages(exclude=["tests*", "examples*"]),
    include_package_data=True,
    install_requires=[
        'dataclasses>=0.6;python_version<"3.7"',
        "IPython",
        "notebook",
        "jinja2",
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Plugins",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    zip_safe=False
)
