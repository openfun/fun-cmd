#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name='fun-cmd',
    version='0.1',
    description="Command runner for OpenFUN",
    long_description="Commands for running OpenFUN LMS or CMS systems",
    classifiers=[],
    keywords='',
    author=u"France Université Numérique",
    author_email='regis@openfun.fr',
    url='https://github.com/openfun/fun-cmd.git',
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'fun = funcmd.cmd:fun',
        ]
    },
)

