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
from profdumbledorebot.model import PortalType, Professions
from profdumbledorebot.sql.support import are_banned
from profdumbledorebot.sql.user import get_user, get_real_user, get_user_by_name
from profdumbledorebot.sql.usergroup import exists_user_group, set_user_group, join_group, message_counter
from profdumbledorebot.sql.group import get_poi_list, set_plant, get_plant_list, get_poi, delete_plant, get_group, get_plant
from profdumbledorebot.admin import last_run

@run_async
def fort_list_cmd(bot, update, args=None):
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
                coords = str(lat) + ", " + str(lon)
                if re.match(r"(([0-1]?[0-9])|([0-9])|([2][0-3])):([0-5][0-9])", args[0]):
                    regDay = None
                    reg = re.match(r"(([0-1]?[0-9])|([0-9])|([2][0-3])):([0-5][0-9])", args[0]).group()
                elif re.match(r"(([0-2][0-9])|([1-9])|([3][0-1]))\/(([0-1]?[0-9])|([0-9])|([2][0-3])):([0-5][0-9])", args[0]):
                    reg = None
                    regDay = re.match(r"(([0-2][0-9])|([1-9])|([3][0-1]))\/(([0-1]?[0-9])|([0-9])|([2][0-3])):([0-5][0-9])", args[0]).group()
                if reg:
                    poi_list = get_poi_list(chat_id, PortalType.FORTRESS.value)
                    poi_sorted = sort_list(poi_list, coords)

                    button_list = []
                    if len(poi_sorted) >= 1:
                        button_list.append([InlineKeyboardButton(poi_sorted[0].name, callback_data='fort_addubi_{0}_{1}_{2}'.format(poi_sorted[0].id, user_id, reg))])
                    if len(poi_sorted) >= 2:
                        button_list.append([InlineKeyboardButton(poi_sorted[1].name, callback_data='fort_addubi_{0}_{1}_{2}'.format(poi_sorted[1].id, user_id, reg))])
                    if len(poi_sorted) >= 3:
                        button_list.append([InlineKeyboardButton(poi_sorted[2].name, callback_data='fort_addubi_{0}_{1}_{2}'.format(poi_sorted[2].id, user_id, reg))])
                    if len(poi_sorted) >= 4:
                        button_list.append([InlineKeyboardButton(poi_sorted[3].name, callback_data='fort_addubi_{0}_{1}_{2}'.format(poi_sorted[3].id, user_id, reg))])
                    if len(poi_sorted) >= 5:
                        button_list.append([InlineKeyboardButton(poi_sorted[4].name, callback_data='fort_addubi_{0}_{1}_{2}'.format(poi_sorted[4].id, user_id, reg))])
                    button_list.append([InlineKeyboardButton("❌ Cancelar", callback_data='fort_cancel_{}'.format(user_id))])

                    bot.send_venue(
                        chat_id=chat_id,
                        title=reg,
                        address="¿En qué fortaleza vais a quedar?",
                        latitude=lat,
                        longitude=lon,
                        reply_markup=InlineKeyboardMarkup(button_list)
                    )
                    return
                elif regDay:
                    poi_list = get_poi_list(chat_id, PortalType.FORTRESS.value)
                    poi_sorted = sort_list(poi_list, coords)

                    button_list = []
                    if len(poi_sorted) >= 1:
                        button_list.append([InlineKeyboardButton(poi_sorted[0].name, callback_data='fort_addubi_{0}_{1}_{2}'.format(poi_sorted[0].id, user_id, regDay))])
                    if len(poi_sorted) >= 2:
                        button_list.append([InlineKeyboardButton(poi_sorted[1].name, callback_data='fort_addubi_{0}_{1}_{2}'.format(poi_sorted[1].id, user_id, regDay))])
                    if len(poi_sorted) >= 3:
                        button_list.append([InlineKeyboardButton(poi_sorted[2].name, callback_data='fort_addubi_{0}_{1}_{2}'.format(poi_sorted[2].id, user_id, regDay))])
                    if len(poi_sorted) >= 4:
                        button_list.append([InlineKeyboardButton(poi_sorted[3].name, callback_data='fort_addubi_{0}_{1}_{2}'.format(poi_sorted[3].id, user_id, regDay))])
                    if len(poi_sorted) >= 5:
                        button_list.append([InlineKeyboardButton(poi_sorted[4].name, callback_data='fort_addubi_{0}_{1}_{2}'.format(poi_sorted[4].id, user_id, regDay))])
                    button_list.append([InlineKeyboardButton("❌ Cancelar", callback_data='fort_cancel_{}'.format(user_id))])

                    bot.send_venue(
                        chat_id=chat_id,
                        title=regDay,
                        address="¿En qué fortaleza vais a quedar?",
                        latitude=lat,
                        longitude=lon,
                        reply_markup=InlineKeyboardMarkup(button_list)
                    )
                    return
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Debes responder a una ubicación para crear la fortaleza.",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
    else:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Debes indicar una hora para crear la fortaleza.",
            parse_mode=telegram.ParseMode.MARKDOWN
        )

def fort_btn(bot, update, job_queue):
    query = update.callback_query
    data = query.data
    user = update.effective_user
    username = query.from_user.username
    user_id = query.from_user.id
    text = query.message.text
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    message = query.message
    markdown_text = query.message.text_markdown_urled

    if are_banned(user_id, chat_id):
        return

    user = get_user(user_id)
    if user is None:
        bot.answer_callback_query(query.id, "❌ Debes registrarte para usar esta función.", show_alert=True)
        return

    queryData = data.split("_")

    if len(queryData) == 5:
        if queryData[3] == str(user_id) or support.is_admin(chat_id, user_id, bot):
            if queryData[1] == "addubi":
                group = get_group(chat_id)
                group_tz = group.timezone
                tz = pytz.timezone(group_tz)

                try:
                    userTime = datetime.strptime(queryData[4], '%d/%H:%M')
                    userDatetime = datetime.now().replace(day=userTime.day, hour=userTime.hour, minute=userTime.minute, second=0)
                    dateText = f"el *{userDatetime.day}/{userDatetime.month}* a las *{userDatetime.hour:02}:{userDatetime.minute:02}*"
                except:
                    userTime = datetime.strptime(queryData[4], '%H:%M')
                    userDatetime = datetime.now().replace(hour=userTime.hour, minute=userTime.minute, second=0)
                    dateText = f"a las *{userDatetime.hour:02}:{userDatetime.minute:02}*"

                userAsLocal = tz.localize(userDatetime)
                userAsLocal = userAsLocal.astimezone(pytz.utc)

                if datetime.now(pytz.utc) > userAsLocal:
                    userAsLocal = userAsLocal + timedelta(days=1)
                    userDatetime = userDatetime + timedelta(days=1)
                    dateText = f"el *{userDatetime.day}/{userDatetime.month}* a las *{userDatetime.hour:02}:{userDatetime.minute:02}*"

                userAsLocal30 = userAsLocal - timedelta(minutes=30)
                #userAsLocal30 = userAsLocal30.time()
                #userAsLocalTime = userAsLocal.time()

                userAsLocal = userAsLocal.replace(tzinfo=None)

                poi = get_poi(queryData[2])
                lat = poi.latitude
                lon = poi.longitude

                button_list = [
                    [(InlineKeyboardButton("🙋‍♀️ Voy", callback_data=f'fort_yes_{poi.id}')),
                    (InlineKeyboardButton("🕒 Tardo", callback_data=f'fort_late_{poi.id}')),
                    (InlineKeyboardButton("❌ No voy", callback_data=f'fort_no_{poi.id}'))],
                    [(InlineKeyboardButton("✅ Estoy", callback_data=f'fort_here_{poi.id}')),
                    (InlineKeyboardButton("📍 Ubicación", callback_data=f'fort_ubi_{poi.id}')),
                    (InlineKeyboardButton("⚠️ Aviso", callback_data=f'fort_alert_{poi.id}'))]
                ]

                text = "Fortaleza en [{0}](https://maps.google.com/maps?q={1},{2}) {3}\n\nLista:".format(poi.name, lat, lon, dateText)

                fort_msg = bot.sendMessage(
                    chat_id=chat_id,
                    text=text,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(button_list)
                )

                chat_url = support.message_url(message, fort_msg.message_id, "desafío")

                f_object = support.AlertFortressContext(chat_id, f"¡Mago de *{message.chat.title}*, en 30 minutos tendrá lugar un {chat_url} que pondrá a prueba tus habilidades como mago en [{poi.name}](https://maps.google.com/maps?q={lat},{lon})!", fort_msg.message_id, poi.id)
                job_queue.run_once(
                    support.callback_AlertFortress, 
                    userAsLocal,
                    context=f_object
                )

                bot.delete_message(
                    chat_id=chat_id,
                    message_id=message_id)
                return

        else:
            bot.answer_callback_query(
                callback_query_id=query.id,
                text="Sólo un administrador o el usuario que ha creado el aviso puede pulsar ese botón.",
                show_alert=True)
            return
    if queryData[1] == "cancel":
        if queryData[2] == str(user_id) or support.is_admin(chat_id, user_id, bot):
                    bot.delete_message(
                        chat_id=chat_id,
                        message_id=message_id)
                    return
        else:
            bot.answer_callback_query(
                    callback_query_id=query.id,
                    text="Sólo un administrador o el usuario que ha creado el aviso puede pulsar ese botón.",
                    show_alert=True)
            return

    poi_id = queryData[2]
    poi = get_poi(poi_id)
    lat = poi.latitude
    lon = poi.longitude

    button_list = [
        [(InlineKeyboardButton("🙋‍♀️ Voy", callback_data=f'fort_yes_{poi.id}')),
        (InlineKeyboardButton("🕒 Tardo", callback_data=f'fort_late_{poi.id}')),
        (InlineKeyboardButton("❌ No voy", callback_data=f'fort_no_{poi.id}'))],
        [(InlineKeyboardButton("✅ Estoy", callback_data=f'fort_here_{poi.id}')),
        (InlineKeyboardButton("📍 Ubicación", callback_data=f'fort_ubi_{poi.id}')),
        (InlineKeyboardButton("⚠️ Aviso", callback_data=f'fort_alert_{poi.id}'))]
    ]

    string = r'\n(🙋‍♀️|✅|🕒|❌) (🍮|⚔|🐾|📚) (\d|\d\d) @{}'.format(username)


    if queryData[1] == "ubi":
        bot.send_venue(
            chat_id=user_id,
            title=poi.name,
            address=" ",
            latitude=lat,
            longitude=lon,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="📍 Google Maps", url='https://maps.google.com/maps?q={0},{1}'.format(lat, lon))]])
        )
        return
    elif queryData[1] == "alert":
        if last_run(str(user_id) + str(chat_id) + str(message_id), 'fort_alert'):
            bot.answer_callback_query(
                callback_query_id=query.id,
                text="Ya has enviado un ⚠️ Aviso, espera un rato para enviar otro.",
                show_alert=True)
            return
        if re.search(string, markdown_text):
            search = re.search(string, markdown_text)
            if search.group(0) == "❌":
                pass
            ent = message.parse_entities(["mention"])
            chat_url = support.message_url(message, message_id, "fortaleza")
            for mention in ent:
                usermention = message.parse_entity(mention)
                user = get_user_by_name(usermention[1:])
                bot.sendMessage(
                    chat_id=user.id,
                    text=f"Alerta para la {chat_url} en [{poi.name}](https://maps.google.com/maps?q={lat},{lon}) enviada por @{username}",
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
        else:
            bot.answer_callback_query(query.id, "❌ Debes apuntarte para poder enviar una alerta.", show_alert=True)
        return


    markdown_text = re.sub(string, "", markdown_text)

    if user is None or user.profession is Professions.NONE.value:
        text_prof = "🍮"
    elif user.profession is Professions.AUROR.value:
        text_prof = "⚔"
    elif user.profession is Professions.MAGIZOOLOGIST.value:
        text_prof = "🐾"
    elif user.profession is Professions.PROFESSOR.value:
        text_prof = "📚"

    if queryData[1] == "yes":
        text = markdown_text + f"\n🙋‍♀️ {text_prof} {user.level} @{username}"
    elif queryData[1] == "here":
        text = markdown_text + f"\n✅ {text_prof} {user.level} @{username}"
    elif queryData[1] == "late":
        text = markdown_text + f"\n🕒 {text_prof} {user.level} @{username}"
    elif queryData[1] == "no":
        text = markdown_text + f"\n❌ {text_prof} {user.level} @{username}"
    
    bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=message_id,
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(button_list),
        disable_web_page_preview=True)

def dist_calc(point, point2):
    dist = great_circle(point, str(point2.latitude) + ", " + str(point2.longitude)).meters
    return dist

def sort_list(list1, point):
    sorted_list = sorted(list1, key=lambda x: dist_calc(point, x))
    return sorted_list