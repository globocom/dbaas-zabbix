#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='dbaas-zabbix',
    version='0.0.2',
    description='A Zabbix Integration for DBaaS.',
    long_description=readme + '\n\n' + history,
    author='Felippe Raposo',
    author_email='raposo.felippe@gmail.com',
    url='https://github.com/felippemr'
        '/dbaas-zabbix',
    packages=[
        'dbaas-zabbix',
    ],
    package_dir={'dbaas-zabbix':
                 'dbaas-zabbix'},
    include_package_data=True,
    install_requires=[
    ],
    license="BSD",
    zip_safe=False,
    keywords='dbaas-zabbix',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
)