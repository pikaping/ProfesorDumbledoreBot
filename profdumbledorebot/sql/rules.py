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

from profdumbledorebot.model import Rules
from profdumbledorebot.db import get_session
from sqlalchemy.sql.expression import and_, or_
from profdumbledorebot.sql.support import get_unique_from_query

LOCK = threading.RLock()


def get_rules(chat_id):
    try:
        session = get_session()
        rules = session.query(Rules).get(str(chat_id))
        ret = ""
        if rules:
            ret = rules.rules
        return ret
    finally:
        session.close()


def has_rules(chat_id):
    try:
        session = get_session()
        rules = session.query(Rules).get(str(chat_id))
        if rules is not None and rules.rules != "":
            return True
        return False
    finally:
        session.close()


def add_rules(chat_id, rules_text):
    with LOCK:
        session = get_session()
        rules = session.query(Rules).get(str(chat_id))
        if not rules:
            rules = Rules(str(chat_id))
        rules.rules = rules_text
        session.add(rules)
        session.commit()
        session.close()
        return

