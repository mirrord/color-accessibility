#!/usr/bin/env python

import os

from distutils.core import setup
from setuptools import find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

# User-friendly description from README.md
current_directory = os.path.dirname(os.path.abspath(__file__))
try:
    with open(os.path.join(current_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except Exception:
    long_description = ''

setup(
    # Name of the package
    name="color-accessibility",

    # Packages to include into the distribution
    packages=find_packages('.'), 

    # Start with a small number and increase it with every change you make
    # https://semver.org
    version='0.0.1',

    # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    # For example: MIT
    license='BSD2',

    # Short description of your library
    description='',

    # Long description of your library
    long_description = long_description,
    long_description_context_type = 'text/markdown',

    # Your name
    author='Dane Howard', 

    # Your email
    author_email='mirrord@gmail.com',     

    # Either the link to your github or to your website
    url='',

    # Link from which the project can be downloaded
    download_url='',

    # List of keyword arguments
    keywords=["color", "accessiblity", "WCAG20"],

    # List of packages to install with this one
    install_requires=required,

    # https://pypi.org/classifiers/
    classifiers=[]  
)