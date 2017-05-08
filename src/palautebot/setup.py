# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='palautebot',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    setup_requires=[],
    install_requires=[
        'tweepy'
    ],
)

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
