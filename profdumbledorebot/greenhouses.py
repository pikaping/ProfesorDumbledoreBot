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

import re
import logging
import time
import random
from geopy.distance import great_circle
from datetime import datetime, timedelta, time, timezone
import pytz

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext.dispatcher import run_async

import profdumbledorebot.supportmethods as support
from profdumbledorebot.model import PortalType
from profdumbledorebot.sql.support import are_banned
from profdumbledorebot.sql.user import get_user, get_real_user
from profdumbledorebot.sql.usergroup import exists_user_group, set_user_group, join_group, message_counter
from profdumbledorebot.sql.group import get_poi_list, set_plant, get_plant_list, get_poi, delete_plant, get_group, get_plant

@run_async
def add_ingredients_cmd(bot, update, args=None):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if are_banned(chat_id, user_id):
        return

    user = get_real_user(user_id)
    if user is None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Debes registrarte para usar este comando.",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return

    if args is not None and len(args) > 0:
        if message.reply_to_message is not None:
            if message.reply_to_message.location is not None:
                support.delete_message(chat_id, message.reply_to_message.message_id, bot)
                lat = message.reply_to_message.location.latitude
                lon = message.reply_to_message.location.longitude
                reg = re.match(r"(([0-1]?[0-9])|([0-9])|([2][0-3])):([0-5][0-9])", args[0]).group()
                if reg:
                    button_list = [
                    [InlineKeyboardButton("Ajenjo", callback_data='gh_addplant_1_{0}_{1}'.format(user_id, reg))],
                    [InlineKeyboardButton("Campanilla de invierno", callback_data='gh_addplant_2_{0}_{1}'.format(user_id, reg))],
                    [InlineKeyboardButton("Grano de sopóforo", callback_data='gh_addplant_3_{0}_{1}'.format(user_id, reg))],
                    [InlineKeyboardButton("Raíz de jengibre", callback_data='gh_addplant_4_{0}_{1}'.format(user_id, reg))],
                    [InlineKeyboardButton("Coclearia", callback_data='gh_addplant_5_{0}_{1}'.format(user_id, reg))],
                    [InlineKeyboardButton("Raíz de valeriana", callback_data='gh_addplant_6_{0}_{1}'.format(user_id, reg))],
                    [InlineKeyboardButton("Raíz amarga", callback_data='gh_addplant_7_{0}_{1}'.format(user_id, reg))],
                    [InlineKeyboardButton("Ligústico", callback_data='gh_addplant_8_{0}_{1}'.format(user_id, reg))],
                    [InlineKeyboardButton("Tármica", callback_data='gh_addplant_9_{0}_{1}'.format(user_id, reg))],
                    [InlineKeyboardButton("Hongo saltarín", callback_data='gh_addplant_10_{0}_{1}'.format(user_id, reg))],
                    [InlineKeyboardButton("Cristoforiana", callback_data='gh_addplant_11_{0}_{1}'.format(user_id, reg))],
                    [InlineKeyboardButton("Trompeta de ángel", callback_data='gh_addplant_12_{0}_{1}'.format(user_id, reg))],
                    [InlineKeyboardButton("❌ Cancelar", callback_data='gh_cancel_{}'.format(user_id))]]

                    bot.send_venue(
                        chat_id=chat_id,
                        title=reg,
                        address="¿Qué planta hay en el invernadero?",
                        latitude=lat,
                        longitude=lon,
                        reply_markup=InlineKeyboardMarkup(button_list)
                    )

def gh_btn(bot, update, job_queue):
    query = update.callback_query
    data = query.data
    user = update.effective_user
    user_id = query.from_user.id
    text = query.message.text
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    name = query.message.venue.title
    lat = query.message.location.latitude
    lon = query.message.location.longitude
    coords = str(lat) + ", " + str(lon)

    if are_banned(user_id, chat_id):
        return

    queryData = data.split("_")
    userBtn = queryData[2]

    if userBtn == str(user_id) or support.is_admin(chat_id, user_id, bot):
        if queryData[1] == "addplant":
            bot.delete_message(
                chat_id=chat_id,
                message_id=message_id)
            
            poi_list = get_poi_list(chat_id, PortalType.GREENHOUSE.value)
            poi_sorted = sort_list(poi_list, coords)

            button_list = []
            if len(poi_sorted) >= 1:
                button_list.append([InlineKeyboardButton(poi_sorted[0].name, callback_data='gh_addubi_{0}_{1}_{2}_{3}'.format(poi_sorted[0].id, queryData[2], user_id, queryData[4]))])
            if len(poi_sorted) >= 2:
                button_list.append([InlineKeyboardButton(poi_sorted[1].name, callback_data='gh_addubi_{0}_{1}_{2}_{3}'.format(poi_sorted[1].id, queryData[2], user_id, queryData[4]))])
            if len(poi_sorted) >= 3:
                button_list.append([InlineKeyboardButton(poi_sorted[2].name, callback_data='gh_addubi_{0}_{1}_{2}_{3}'.format(poi_sorted[2].id, queryData[2], user_id, queryData[4]))])
            if len(poi_sorted) >= 4:
                button_list.append([InlineKeyboardButton(poi_sorted[3].name, callback_data='gh_addubi_{0}_{1}_{2}_{3}'.format(poi_sorted[3].id, queryData[2], user_id, queryData[4]))])
            if len(poi_sorted) >= 5:
                button_list.append([InlineKeyboardButton(poi_sorted[4].name, callback_data='gh_addubi_{0}_{1}_{2}_{3}'.format(poi_sorted[4].id, queryData[2], user_id, queryData[4]))])
            button_list.append([InlineKeyboardButton("❌ Cancelar", callback_data='gh_cancel_{}'.format(user_id))])

            plant = support.replace_plants(int(queryData[2]))

            bot.send_venue(
                    chat_id=chat_id,
                    title=plant + " " + queryData[4],
                    address="¿En qué invernadero está plantado?",
                    latitude=lat,
                    longitude=lon,
                    reply_markup=InlineKeyboardMarkup(button_list)
                )
            return
        elif queryData[1] == "addubi":
            userTime = datetime.strptime(queryData[5], '%H:%M')

            group = get_group(chat_id)
            group_tz = group.timezone
            tz = pytz.timezone(group_tz)

            userDatetime = datetime.now().replace(hour=userTime.hour, minute=userTime.minute, second=0)
            userAsLocal = tz.localize(userDatetime)
            userAsLocal = userAsLocal.astimezone(pytz.utc)

            '''
            if datetime.now(pytz.utc) > userAsLocal:
                userAsLocal = userAsLocal + timedelta(days=1)
            '''
            
            userAsLocal15 = userAsLocal - timedelta(minutes=15)
            userAsLocalDeletePlant = userAsLocal + timedelta(minutes=30)
            userAsLocal15 = userAsLocal15.time()
            userAsLocalTime = userAsLocal.time()
            userAsLocalDPTime = userAsLocalDeletePlant.time()

            plant = support.replace_plants(int(queryData[3]))

            setPlant = set_plant(queryData[2], queryData[3], chat_id, userDatetime, userAsLocalDeletePlant)
            thePlant = get_plant(setPlant)

            poi = get_poi(queryData[2])
            ap_object = support.AlertPlantContext(chat_id, "¡Magos de *{0}*, en 15 minutos se podrá recoger *{1}* en [{2}](https://maps.google.com/maps?q={3},{4})!".format(query.message.chat.title, plant, poi.name, poi.latitude, poi.longitude), False, thePlant.id)
            job_queue.run_once(
                support.callback_AlertPlant, 
                userAsLocal15,
                context=ap_object,
                name="{}_plantJob15".format(thePlant.id)
            )

            ap_object = support.AlertPlantContext(chat_id, "¡Magos de *{0}*, ya se puede recoger *{1}* en [{2}](https://maps.google.com/maps?q={3},{4})!".format(query.message.chat.title, plant, poi.name, poi.latitude, poi.longitude), True, thePlant.id)
            job_queue.run_once(
                support.callback_AlertPlant, 
                userAsLocalTime,
                context=ap_object,
                name="{}_plantJob".format(thePlant.id)
            )
            dp_object = support.DeletePlantContext(thePlant.id)
            job_queue.run_once(
                support.callback_DeletePlant,
                userAsLocalDPTime,
                context=dp_object,
                name="{}_plantJobDelete".format(thePlant.id)
            )

            bot.delete_message(
                chat_id=chat_id,
                message_id=message_id)
            return
        elif queryData[1] == "cancel":
            bot.delete_message(
                chat_id=chat_id,
                message_id=message_id)
            return
    else:
        bot.answer_callback_query(
                callback_query_id=query.id,
                text="Sólo un administrador o el usuario que ha creado el aviso puede pulsar ese botón.",
                show_alert=True)

@run_async
def plants_list_cmd(bot, update, args=None):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if are_banned(chat_id, user_id):
        return

    user = get_real_user(user_id)
    if user is None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Debes registrarte para usar este comando.",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return

    text = "Lista de plantaciones en *{}*:\n".format(message.chat.title)
    plants_list = get_plant_list(chat_id)
    if not list(plants_list):
        bot.sendMessage(
            chat_id=user_id,
            text="❌ No hay plantaciones registradas.",
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return
    count = 0
    for plant in plants_list:
        plantName = support.replace_plants(plant.plant_type)
        poi = get_poi(plant.portal)
        if plant.alerted:
            text = text + "\n- #{0} *{1}* - ⚠️ {2} ⚠️ - [{3}](https://maps.google.com/maps?q={4},{5})".format(
                plant.id,
                plantName,
                f"{plant.grow_end.hour:02}:{plant.grow_end.minute:02}",
                poi.name,
                poi.latitude,
                poi.longitude
            )
        else:
            text = text + "\n- #{0} *{1}* - {2} - [{3}](https://maps.google.com/maps?q={4},{5})".format(
                plant.id,
                plantName,
                f"{plant.grow_end.hour:02}:{plant.grow_end.minute:02}",
                poi.name,
                poi.latitude,
                poi.longitude
            )
        count += 1
        if count == 100:
            pass

    bot.sendMessage(
            chat_id=user_id,
            text=text,
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )

@run_async
def rem_plant_cmd(bot, update, job_queue, args=None):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if are_banned(chat_id, user_id) or not support.is_admin(chat_id, user_id, bot):
        return

    user = get_real_user(user_id)
    if user is None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Debes registrarte para usar este comando.",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return

    if args is not None and len(args)!=0:
        if re.match(r"^[0-9]{0,10}$", args[0]):
            try:
                alert15PlantJob = job_queue.get_jobs_by_name("{}_plantJob15".format(args[0]))
                alert15PlantJob[0].schedule_removal()
            except:
                pass
            try:
                alertPlantJob = job_queue.get_jobs_by_name("{}_plantJob".format(args[0]))
                alertPlantJob[0].schedule_removal()
            except:
                pass
            try:
                deletePlantJob = job_queue.get_jobs_by_name("{}_plantJobDelete".format(args[0]))
                deletePlantJob[0].schedule_removal()
            except:
                pass

            delete_plant(plant_id=args[0])
            bot.sendMessage(
            chat_id=chat_id,
            text="Plantación eliminada correctamente.",
            parse_mode=telegram.ParseMode.MARKDOWN
            )
        elif args[0] == "all":
            plants = delete_plant(group_id=chat_id)
            for plant in plants:
                logging.debug("%s", plant.plant_type)
                try:
                    alert15PlantJob = job_queue.get_jobs_by_name("{}_plantJob15".format(plant.id))
                    alert15PlantJob[0].schedule_removal()
                except:
                    continue
                try:
                    alertPlantJob = job_queue.get_jobs_by_name("{}_plantJob".format(plant.id))
                    alertPlantJob[0].schedule_removal()
                except:
                    continue
                try:
                    deletePlantJob = job_queue.get_jobs_by_name("{}_plantJobDelete".format(plant.id))
                    deletePlantJob[0].schedule_removal()
                except:
                    continue
            bot.sendMessage(
            chat_id=chat_id,
            text="Todas las plantaciones eliminadas correctamente.",
            parse_mode=telegram.ParseMode.MARKDOWN
            )

def dist_calc(point, point2):
    dist = great_circle(point, str(point2.latitude) + ", " + str(point2.longitude)).meters
    return dist

def sort_list(list1, point):
    sorted_list = sorted(list1, key=lambda x: dist_calc(point, x))
    return sorted_list