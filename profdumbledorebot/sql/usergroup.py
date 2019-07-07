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

from datetime import datetime
from profdumbledorebot.mwt import MWT
from profdumbledorebot.db import get_session
from profdumbledorebot.model import UserGroup
from sqlalchemy.sql.expression import and_, or_
from profdumbledorebot.sql.support import get_unique_from_query

LOCK = threading.RLock()


@MWT(timeout=60*60)
def get_users_from_group(group_id):
    try:
        session = get_session()
        gusers = session.query(UserGroup).filter(
                UserGroup.group_id == group_id)
        return gusers
    finally:
        session.close()
        

def exists_user_group(user_id, chat_id):
    try:
        session = get_session()
        guser = get_unique_from_query(
            session.query(UserGroup).filter(and_(
                UserGroup.group_id == chat_id,
                UserGroup.user_id == user_id))
        )
        if guser is None:
            return False
        else:
            return True
    finally:
        session.close()


def get_user_group(user_id, chat_id):
    try:
        session = get_session()
        guser = get_unique_from_query(
            session.query(UserGroup).filter(and_(
                UserGroup.group_id == chat_id,
                UserGroup.user_id == user_id))
        )
        return guser
    finally:
        session.close()


def warn_user(chat_id, user_id, warning):
    with LOCK:
        session = get_session()
        guser = get_unique_from_query(session.query(UserGroup).filter(and_(
            UserGroup.group_id == chat_id, UserGroup.user_id == user_id)))

        if warning == 0:
            guser.warn = 0
            
        elif warning > 0 or (warning < 0 and guser.warn != 0):
            guser.warn = guser.warn + warning
            warning = guser.warn
        else:
            warning = 999
        session.commit()
        session.close()
        return warning


def remove_warn(user_id, chat_id):
    with LOCK:
        session = get_session()
        removed = False
        warned_user = get_unique_from_query(session.query(UserGroup).filter(and_(
            UserGroup.group_id == chat_id,UserGroup.user_id == user_id)))

        if warned_user and warned_user.warn > 0:
            warned_user.warn -= 1
            session.commit()
            removed = True

        session.close()
        return removed


def set_user_group(user_id, chat_id):
    with LOCK:
        session = get_session()
        guser = UserGroup(user_id = user_id, group_id = chat_id)
        session.add(guser)
        session.commit()
        session.close()
        return


def join_group(user_id, chat_id):
    with LOCK:
        session = get_session()
        guser = get_unique_from_query(session.query(UserGroup).filter(and_(UserGroup.group_id == chat_id, UserGroup.user_id == user_id)))
        guser.join_date = datetime.utcnow()
        session.commit()
        session.close()
        return


def message_counter(user_id, chat_id):
    with LOCK:
        session = get_session()
        guser = get_unique_from_query(session.query(UserGroup).filter(and_(UserGroup.group_id == chat_id, UserGroup.user_id == user_id)))
        guser.total_messages += 1
        guser.last_message = datetime.utcnow()
        session.commit()
        session.close()
        return

