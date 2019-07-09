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
import threading
import profdumbledorebot.model as model


from profdumbledorebot.mwt import MWT
from profdumbledorebot.db import get_session
from sqlalchemy.sql.expression import and_, or_
from profdumbledorebot.sql.support import get_unique_from_query

LOCK = threading.RLock()


@MWT(timeout=60)
def get_group(group_id):
    try:
        session = get_session()
        group = get_unique_from_query(session.query(model.Group).filter(model.Group.id == group_id))
        return group
    finally:
        session.close()

def get_real_group(group_id):
    try:
        session = get_session()
        group = get_unique_from_query(session.query(model.Group).filter(model.Group.id == group_id))
        return group
    finally:
        session.close()


def set_group(group_id, group_title):
    with LOCK:
        session = get_session()
        group = model.Group(id=group_id, title=group_title)
        session.add(group)
        session.commit()
        set_j = model.SettingsJoin(id=group_id)
        set_w = model.Welcome(chat_id=group_id)
        set_adm = model.SettingsAdmin(id=group_id)
        set_group = model.SettingsGroup(id=group_id)
        session.add(set_j)
        session.add(set_w)
        session.add(set_adm)
        session.add(set_group)
        session.commit()
        session.close()


def commit_group(user_id, title=None, language=None, timezone=None):
    with LOCK:
        session = get_session()
        group = get_unique_from_query(session.query(model.Group).filter(model.Group.id == chat_id))
        if title:
            group.title = title
        if language:
            group.language = language
        if timezone:
            group.timezone = timezone
        session.commit()
        session.close()

