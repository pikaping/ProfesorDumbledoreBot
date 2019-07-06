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


def is_news_provider(news_id):
    try:
        session = get_session()
        provider = get_unique_from_query(session.query(model.News).filter(model.News.id == news_id))
        if provider is None:
            return False
        return True
    finally:
        session.close()


def get_verified_providers():
    try:
        session = get_session()
        providers = session.query(model.News).filter(model.News.active == True)
        return providers
    finally:
        session.close()


def get_news_provider(news_id):
    try:
        session = get_session()
        provider = get_unique_from_query(session.query(model.News).filter(model.News.id == news_id))
        return provider
    finally:
        session.close()


def set_news_provider(news_id, alias):
    with LOCK:
        session = get_session()
        news = model.News(id=news_id, alias=alias, active=False)
        session.add(news)
        session.commit()
        session.close()
        return
  

def rm_news_provider(news_id):
    with LOCK:
        session = get_session()
        session.query(model.NewsSubs).filter(model.NewsSubs.news_id == news_id).delete()
        session.query(model.News).filter(model.News.id == news_id).delete()
        session.commit()
        session.close()
        return


def is_news_subscribed(chat_id, news_id):
    try:
        session = get_session()
        group = get_unique_from_query(session.query(model.NewsSubs).filter(and_(model.NewsSubs.news_id == news_id,model.NewsSubs.user_id == chat_id)))
        if group is None:
            return False
        return True
    finally:
        session.close()


def get_news_consumers(news_id):
    try:
        session = get_session()
        group = session.query(model.NewsSubs).filter(model.NewsSubs.news_id == news_id)
        return group
    finally:
        session.close()


def get_news_subscribed(chat_id):
    try:
        session = get_session()
        group = session.query(model.NewsSubs).filter(model.NewsSubs.user_id == chat_id)
        return group
    finally:
        session.close()


def set_news_subscription(chat_id, news_id):
    with LOCK:
        session = get_session()
        news = model.NewsSubs(user_id=chat_id,news_id=news_id)
        session.add(news)
        session.commit()
        session.close()
        return
    

def rm_news_subscription(chat_id, news_id):
    with LOCK:
        session = get_session()
        session.query(model.NewsSubs).filter(and_(model.NewsSubs.user_id == chat_id,model.NewsSubs.news_id == news_id)).delete()
        session.commit()
        session.close()
        return


def rm_all_news_subscription(chat_id):
    with LOCK:
        session = get_session()
        session.query(model.NewsSubs).filter(model.NewsSubs.user_id == chat_id).delete()
        session.commit()
        session.close()
        return


      

