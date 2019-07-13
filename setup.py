#!/usr/bin/python
# -*- coding: utf-8 -*-

############################################################################
#                                                                          #
# Profesor Dumbledore Bot                                                  # 
# Copyright (C) 2019 - Pikaping                                            #
#                                                                          #
# This program is free software: you can redistribute it and/or modify     #
# it under the terms of the GNU Affero General Public License as           #
# published by the Free Software Foundation, either version 3 of the       #
# License, or (at your option) any later version.                          #
#                                                                          #
# This program is distributed in the hope that it will be useful,          #
# but WITHOUT ANY WARRANTY; without even the implied warranty of           #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
# GNU Affero General Public License for more details.                      #
#                                                                          #
# You should have received a copy of the GNU Affero General Public License #
# along with this program.  If not, see <https://www.gnu.org/licenses/>.   #
#                                                                          #
############################################################################

from setuptools import setup, find_packages

DIST_NAME = 'profdumbledorebot'
VERSION = '1.0'


setup(
    name=DIST_NAME,
    packages=find_packages(),
    version=VERSION,
    description='Telegram bot for helping Wizards Unite groups management',
    install_requires=[
        'emoji==0.5.1',
        'python-Levenshtein==0.12.0',
        'python-telegram-bot==12.0.0b1',
        'pytz>=2018.9',
        'SQLAlchemy==1.2.17',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts': [
            'profdumbledore = profdumbledorebot.cli:start_bot'
        ],
    },
    include_package_data=True,
)
