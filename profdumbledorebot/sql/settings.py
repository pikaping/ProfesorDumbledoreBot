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

from profdumbledorebot.db import get_session
from profdumbledorebot.sql.support import get_unique_from_query

LOCK = threading.RLock()


def get_nanny_settings(chat_id):
    try:
        session = get_session()
        nanny = get_unique_from_query(session.query(model.SettingsNurse).filter(model.SettingsNurse.id==chat_id))
        return nanny
    finally:
        session.close()


def get_group_settings(group_id):
    try:
        session = get_session()
        group = get_unique_from_query(session.query(model.SettingsGroup).filter(model.SettingsGroup.id == group_id))
        return group
    finally:
        session.close()
        

def get_warn_limit(group_id):
    try:    
        session = get_session()
        group = get_unique_from_query(session.query(model.SettingsGroup).filter(model.SettingsGroup.id == group_id))
        return group.warn.value 
    finally:
        session.close()


def get_join_settings(chat_id):
    try:
        session = get_session()
        group = get_unique_from_query(session.query(model.SettingsJoin).filter(model.SettingsJoin.id == chat_id))
        return group
    finally:
        session.close()


def set_general_settings(chat_id, settings_str):
    with LOCK:
        session = get_session()
        group = get_unique_from_query(session.query(model.SettingsGroup).filter(model.SettingsGroup.id == chat_id))
        group.set_settings_from_str(settings_str)
        session.commit()
        session.close()
        return


def set_join_settings(chat_id, settings_str):
    with LOCK:
        session = get_session()
        group = get_unique_from_query(session.query(model.SettingsJoin).filter(model.SettingsJoin.id == chat_id))
        group.set_joinset_from_str(settings_str)
        session.commit()
        session.close()
        return


def set_max_members(chat_id, max_members):
    with LOCK:
        session = get_session()
        group = get_unique_from_query(session.query(model.SettingsJoin).filter(model.SettingsJoin.id == chat_id))
        group.max_members = max_members
        session.commit()
        session.close()
        return


def set_welcome_cooldown(chat_id, delete_cooldown):
    with LOCK:
        session = get_session()
        group = get_unique_from_query(session.query(model.SettingsJoin).filter(model.SettingsJoin.id == chat_id))
        group.delete_cooldown = delete_cooldown
        session.commit()
        session.close()
        return


def set_nanny_reply(chat_id, text):
    with LOCK:
        session = get_session()
        nanny = get_unique_from_query(session.query(model.SettingsNurse).filter(model.SettingsNurse.id==chat_id))
        nanny.reply = text
        session.commit()
        session.close()
        return


def set_nanny_settings(chat_id, settings_str):
    with LOCK:
        session = get_session()
        nanny = get_unique_from_query(session.query(model.SettingsNurse).filter(model.SettingsNurse.id==chat_id))
        nanny.set_nurseset_from_str(settings_str)
        session.commit()
        session.close()
        return

