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


def commit_group(chat_id, title=None, language=None, timezone=None):
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


def group_message_counter(group_id, read_only=False, reset=False):
    with LOCK:
        try:
            if read_only:
                session = get_session()
                group = get_unique_from_query(session.query(model.Group).filter(model.Group.id == group_id))
                return group.message_num
            if reset:
                session = get_session()
                group = get_unique_from_query(session.query(model.Group).filter(model.Group.id == group_id))
                group.message_num = 0
                return group.message_num
            else:
                session = get_session()
                group = get_unique_from_query(session.query(model.Group).filter(model.Group.id == group_id))
                if group.message_num is None:
                    group.message_num = 0
                group.message_num += 1
                return group.message_num
        finally:
            session.commit()
            session.close()

def update_group_points(group_id, points=0, read_only=False):
    with LOCK:
        try:
            if read_only:
                session = get_session()
                group = get_unique_from_query(session.query(model.Group).filter(model.Group.id == group_id))
                if group.games_points == None:
                    group.games_points = 0
                return group.games_points
            else:
                session = get_session()
                group = get_unique_from_query(session.query(model.Group).filter(model.Group.id == group_id))
                if group.games_points == None:
                    group.games_points = 0
                if group.games_points == 0:
                    return
                group.games_points += points
        finally:
            session.commit()
            session.close()

def create_poi(name, lat, lon, poi_type, group_id, user_id):
    with LOCK:
        session = get_session()
        poi = model.Portals(name=name, latitude=lat, longitude=lon, portal_type=poi_type, group_id=group_id, user_id=user_id)
        session.add(poi)
        session.commit()
        session.close()
        return

def get_poi_list(group_id, poi_type=None):
    try:
        session = get_session()
        if poi_type is None:
            pois = session.query(model.Portals).filter(model.Portals.group_id == group_id)
        elif poi_type is model.PortalType.GREENHOUSE.value:
            pois = session.query(model.Portals).filter(and_(model.Portals.group_id == group_id, model.Portals.portal_type == model.PortalType.GREENHOUSE.value))
        elif poi_type is model.PortalType.FORTRESS.value:
            pois = session.query(model.Portals).filter(and_(model.Portals.group_id == group_id, model.Portals.portal_type == model.PortalType.FORTRESS.value))
        return pois
    finally:
        session.close()

def delete_poi(poi_id):
    with LOCK:
        session = get_session()
        session.query(model.Portals).filter(model.Portals.id == poi_id).delete()
        session.commit()
        session.close()
        return

def set_plant(poi_id, plant_type, group_id, grow_end, harvest_end):
    with LOCK:
        session = get_session()
        plant = model.Plants(group_id=group_id, portal=poi_id, plant_type=plant_type, grow_end=grow_end, harvest_end=harvest_end)
        session.add(plant)
        session.flush()
        plant_id = plant.id
        session.commit()
        session.close()
        return plant_id

def get_plant(plant_id):
    try:
        session = get_session()
        plant = get_unique_from_query(session.query(model.Plants).filter(model.Plants.id == plant_id))
        return plant
    finally:
        session.close()

def set_plant_alerted(plant_id):
    with LOCK:
        session = get_session()
        plant = get_unique_from_query(session.query(model.Plants).filter(model.Plants.id == plant_id))
        plant.alerted = True
        session.commit()
        session.close()
        return

def delete_plant(plant_id=None, group_id=None):
    with LOCK:
        session = get_session()
        if group_id:
            session.query(model.Plants).filter(model.Plants.group_id == group_id).delete()
        elif plant_id:
            session.query(model.Plants).filter(model.Plants.id == plant_id).delete()
        session.commit()
        session.close()
        return

def get_plant_list(group_id):
    try:
        session = get_session()
        plants = session.query(model.Plants).filter(model.Plants.group_id == group_id)
        return plants
    finally:
        session.close()

def get_poi(poi_id):
    try:
        session = get_session()
        poi = get_unique_from_query(session.query(model.Portals).filter(model.Portals.id == poi_id))
        return poi
    finally:
        session.close()