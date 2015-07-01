#!/usr/bin/env python
# encoding: utf-8

import os, sys
from setuptools import setup

setup(
    # metadata
    name='hipbot',
    description='A very simple HipChat bot',
    long_description="""
		A simple HipChat bot that exposes two "plugin" methods:

		* reactive - processes any new messages in the subscribed rooms
		* non-reactive - gets called every 10 seconds
    """,
    license='MIT',
    version='0.1',
    author='James Johnson',
    maintainer='James Johnson',
    author_email='d0c.s4vage@gmail.com',
    url='https://github.com/d0c-s4vage/hipbot',
    platforms='Cross Platform',
	install_requires = [
		"hypchat==9.9.9",
		"pytz", 
		"python-dateutil",
		# for ssl-connections
		"pyopenssl",
		"ndg-httpsclient",
		"pyasn1",
	],
	dependency_links = [
		"git+ssh://git@github.com/d0c-s4vage/HypChat.git#egg=hypchat-9.9.9"
	],
    classifiers = [
        'Programming Language :: Python :: 2',
		# untested
        #'Programming Language :: Python :: 3',
	],
    packages=['hipbot'],
)
