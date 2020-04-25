#!/usr/bin/env python
# coding: utf8

""" Distribution script. """
from os.path import abspath, dirname, join
from setuptools import setup, find_packages

import pyredis

here = abspath(dirname(__file__))
with open(join(here, 'README.md'), 'r', encoding='utf-8') as stream:
    readme = stream.read()

setup(
    name='pyredis',
    version=pyredis.__version__,
    description=pyredis.__doc__,
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Felix Voituret',
    author_email='felix@voituret.fr',
    url='https://github.com/Faylixe/pyredis',
    download_url='https://pypi.org/project/pyredis/#files',
    license='MIT License',
    keywords=['redis', 'datastructure'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries'
    ],
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=['redis'],
    setup_requires=['setuptools>=41.0.1']
)
