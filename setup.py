#!/usr/bin/env python

"""Yoda"""
import os.path
from setuptools import setup, find_packages

__author__      = 'David Chenaux'
__license__     = 'Modified BSD license'
__version__     = '0.2'
__maintainer__  = __author__
__email__       = 'd.chenaux@gmail.com'
__url__         = 'https://github.com/dchenaux/yoda'
__summary__     = __doc__


setup(
    name='yoda',
    version=__version__,
    author=__author__,
    author_email=__email__,
    maintainer=__maintainer__,
    maintainer_email=__email__,
    url=__url__,
    download_url=__url__,

    description=__summary__,
    long_description=open('README').read(),

    license=__license__,
    packages=find_packages(),

    install_requires=['mongoengine>=0.10.6', 'Flask>=0.10.1', 'Flask-Bootstrap>=3.3.5.7', 'flask-mongoengine>=0.7.5'],
    dependency_links=[],
    scripts=['yoda/generate_trace.py',
             'yoda/main.py'],

    classifiers=[
        'Development Status :: 0.1 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: Modified BSD license',
        'Programming Language :: Python',
        'Topic :: Database',
        ],
    zip_safe=True
    )
