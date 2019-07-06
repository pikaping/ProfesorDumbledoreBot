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
BTN_LOCK = threading.RLock()


def get_welc_pref(chat_id):
    try:
        session = get_session()
        welc = session.query(model.Welcome).get(str(chat_id))
        if welc:
            return welc.should_welcome, welc.custom_welcome, welc.welcome_type
        else:
            return False, None, model.Types.TEXT
    finally:
        session.close()


def get_welc_buttons(chat_id):
    session = get_session()
    try:
        return session.query(model.WelcomeButtons).filter(
            model.WelcomeButtons.chat_id == str(chat_id)).order_by(model.WelcomeButtons.id).all()
    finally:
        session.close()


def get_welcome_settings(chat_id):
    try:    
        session = get_session()
        group = get_unique_from_query(
            session.query(model.Welcome).filter(model.Welcome.chat_id == chat_id)
        )
        return group
    finally:
        session.close()


def set_welc_preference(chat_id, should_welcome):
    with LOCK:
        session = get_session()
        curr = session.query(model.Welcome).get(str(chat_id))
        if not curr:
            curr = model.Welcome(str(chat_id), should_welcome=should_welcome)
        else:
            curr.should_welcome = should_welcome

        session.add(curr)
        session.commit()


def set_custom_welcome(chat_id, custom_welcome, welcome_type, buttons=None):
    if buttons is None:
        buttons = []

    with LOCK:
        session = get_session()
        welcome_settings = session.query(model.Welcome).get(str(chat_id))
        if not welcome_settings:
            welcome_settings = model.Welcome(str(chat_id), True)

        if custom_welcome:
            welcome_settings.custom_welcome = custom_welcome
            welcome_settings.welcome_type = welcome_type.value

        session.add(welcome_settings)

        with BTN_LOCK:
            prev_buttons = session.query(model.WelcomeButtons).filter(model.WelcomeButtons.chat_id == str(chat_id)).all()
            for btn in prev_buttons:
                session.delete(btn)

            for b_name, url, same_line in buttons:
                button = model.WelcomeButtons(chat_id, b_name, url, same_line)
                session.add(button)

        session.commit()


def set_welcome_settings(chat_id, settings_str):
    with LOCK:
        session = get_session()
        group = get_unique_from_query(session.query(model.Welcome).filter(model.Welcome.chat_id == chat_id))
        group.set_welcomeset_from_str()
        session.commit()
        session.close()
        return

