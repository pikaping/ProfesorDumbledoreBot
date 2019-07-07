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


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

from profdumbledorebot.config import get_config


__ENGINE = None
__BASE = None
__SESSION = None


def get_db_engine():
    global __ENGINE

    if __ENGINE is None:
        config = get_config()

        try:
            db_url = config['database']['db-url']

        except KeyError:
            db_url = 'mysql://{user}:{password}@{host}:{port}/{schema}?charset=utf8mb4'.format(
                **config['database']
            )

        debug = config['database'].get('debug', "false")

        if debug.lower() == "false":
            debug = False

        else:
            try:
                debug = bool(int(debug))  # numeric values

            except ValueError:
                debug = bool(debug)

        if debug:
            print('DB URL: ', db_url)

        __ENGINE = create_engine(db_url, pool_size=35, max_overflow=50, echo=False, pool_pre_ping=True)

    return __ENGINE


def get_declarative_base():
    global __BASE

    if __BASE is None:
        __BASE = declarative_base()

    return __BASE


def get_session():
    global __SESSION

    if __SESSION is None:
        session_factory = sessionmaker(bind=get_db_engine(), autoflush=False,)
        __SESSION = scoped_session(session_factory)

    return __SESSION
