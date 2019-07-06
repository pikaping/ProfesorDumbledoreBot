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

import logging

import profdumbledorebot.model as model

from profdumbledorebot.mwt import MWT
from profdumbledorebot.db import get_session


def get_unique_from_query(query):
    '''
    Handly method to retrieve an element from a query when it should be unique.

    If no element matches the query or there are several ones, return None
    '''

    return query[0] if query.count() == 1 else None


@MWT(timeout=60*60*24)
def are_banned(user_id, chat_id):
    try:
        session = get_session()
        if user_id != chat_id:
            group = get_unique_from_query(session.query(model.Group).filter(model.Group.id == chat_id))
        else:
            group = None
        user = get_unique_from_query(session.query(model.User).filter(model.User.id == user_id))
        
        if (user is not None and user.banned) or (group is not None and group.banned):
            return True
        else:
            return False
    finally:
        session.close()