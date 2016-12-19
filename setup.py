#!/usr/bin/env python

import sys

from setuptools import setup, find_packages

if not sys.version_info[0] == 3:
    print('only python3 supported!')
    sys.exit(1)

setup(
    name='coastSHARK',
    version='1.0.0',
    description='Collect AST Information for smartSHARK.',
    install_requires=['javalang', 'mongoengine', 'pymongo', 'pycoshark'],
    dependency_links=['https://github.com/smartshark/pycoSHARK/tarball/master'],
    author='atrautsch',
    author_email='alexander.trautsch@stud.uni-goettingen.de',
    url='https://github.com/smartshark/coastSHARK',
    download_url='https://github.com/smartshark/coastSHARK/tarball/master',
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
