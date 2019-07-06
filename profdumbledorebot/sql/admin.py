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
from sqlalchemy.sql.expression import and_, or_
from profdumbledorebot.sql.support import get_unique_from_query

LOCK = threading.RLock()


def get_admin(chat_id):
    try:
        session = get_session()
        return get_unique_from_query(session.query(model.AdminGroups).filter(model.AdminGroups.id == chat_id))
    finally:
        session.close()


def get_particular_admin(chat_id):
    try:
        session = get_session()
        return get_unique_from_query(session.query(model.SettingsAdmin).filter(model.SettingsAdmin.id == chat_id))
    finally:
        session.close()


def get_admin_from_linked(chat_id):
    try:
        session = get_session()
        linked = get_unique_from_query(session.query(model.LinkedGroups).filter(model.LinkedGroups.linked_id == chat_id))
        if linked is None:
            session.close()
            return None

        return get_unique_from_query(session.query(model.AdminGroups).filter(model.AdminGroups.id == linked.admin_id))
    finally:
        session.close()



def set_admin_settings(chat_id, settings_str):
    with LOCK:
        session = get_session() 
        admin = get_unique_from_query(session.query(model.AdminGroups).filter(model.AdminGroups.id == chat_id))
        admin.set_admset_from_str(settings_str)
        session.commit()
        session.close()
        return

def set_ladmin_settings(chat_id, settings_str):
    with LOCK:
        session = get_session() 
        admin = get_unique_from_query(session.query(model.SettingsAdmin).filter(model.SettingsAdmin.id == chat_id))
        admin.set_setadm_from_str(settings_str)
        session.commit()
        session.close()
        return

def set_admin(chat_id):
    with LOCK:
        session = get_session()
        admin = model.AdminGroups(id=chat_id)
        session.add(admin)
        session.commit()
        session.close()
        return  

def rm_admin(chat_id):
    with LOCK:
        session = get_session()
        try:
            session.query(model.LinkedGroups).filter(model.LinkedGroups.admin_id==chat_id).delete()
            session.query(model.AdminGroups).filter(model.AdminGroups.id==chat_id).delete()
            session.commit()
            out = True
        except:
            session.rollback()
            out = False
        finally:
            session.close()
            return out



def get_linked_admin(chat_id, args):
    try:
        session = get_session()
        linked = get_unique_from_query(session.query(model.LinkedGroups).filter(
            and_(model.LinkedGroups.admin_id == chat_id, model.LinkedGroups.linked_id == args)))

        if linked is None:
            return False

        return True
    finally:
        session.close()

def get_all_groups(chat_id):
    try:
        session = get_session()
        linked = get_unique_from_query(session.query(model.LinkedGroups).filter(model.LinkedGroups.linked_id == chat_id))
        if linked is None:
            linked = get_unique_from_query(session.query(model.AdminGroups).filter(model.AdminGroups.id == chat_id))
            if linked is None:
                session.close()
                return None
            else:
                admin_id = linked.id
        else:
            admin_id = linked.admin_id

        return session.query(model.LinkedGroups).filter(model.LinkedGroups.admin_id == admin_id)
    finally:
        session.close()

def get_groups(chat_id):
    try:
        session = get_session()
        linked = get_unique_from_query(session.query(model.LinkedGroups).filter(model.LinkedGroups.linked_id == chat_id))
        return linked
    finally:
        session.close()


def new_link(admin, chat, title):
    with LOCK:
        session = get_session()
        linked = model.LinkedGroups(admin_id=admin, linked_id=chat, title=title)
        session.add(linked)
        session.commit()
        session.close()
        return  


def rm_link(group_id):
    with LOCK:
        session = get_session()
        session.query(model.LinkedGroups).filter(model.LinkedGroups.linked_id == group_id).delete()
        session.commit()
        session.close()
        return 

def add_tlink(chat_id, arg):
    with LOCK:
        session = get_session()
        linked = get_unique_from_query(session.query(model.LinkedGroups).filter(model.LinkedGroups.linked_id == chat_id))
        if linked is None:
            session.close()
            return None

        linked.link = arg
        session.commit()
        session.close()
        return

def add_type(chat_id, arg):
    with LOCK:
        session = get_session()
        linked = get_unique_from_query(session.query(model.LinkedGroups).filter(model.LinkedGroups.linked_id == chat_id))
        if linked is None:
            session.close()
            return

        linked.group_type = arg
        session.commit()
        session.close()
        return

def set_tag(chat_id, arg):
    with LOCK:
        session = get_session()
        linked = get_unique_from_query(session.query(model.LinkedGroups).filter(model.LinkedGroups.linked_id == chat_id))
        if linked is None:
            session.close()
            return

        linked.label = arg
        session.commit()
        session.close()
        return
