#!/usr/bin/env python

import sys

from setuptools import setup, find_packages

if not sys.version_info[0] == 3:
    print('only python3 supported!')
    sys.exit(1)

setup(
    name='coastSHARK',
    version='2.0.6',
    description='Collect AST Information for smartSHARK.',
    install_requires=['javalang>=0.13.1', 'pycoshark>=1.2.6'],
    dependency_links=['git+https://github.com/atrautsch/javalang.git#egg=javalang-0.13.1'],
    author='atrautsch',
    author_email='alexander.trautsch@stud.uni-goettingen.de',
    url='https://github.com/smartshark/coastSHARK',
    download_url='https://github.com/smartshark/coastSHARK/zipball/master',
    test_suite='coastSHARK.tests',
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache2.0 License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
