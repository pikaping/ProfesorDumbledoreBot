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

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import escape_markdown

import pytz
from datetime import datetime

import profdumbledorebot.supportmethods as support
from profdumbledorebot.sql.support import are_banned
from profdumbledorebot.sql.user import get_user
from profdumbledorebot.sql.group import get_group

@run_async
def sighting_cmd(bot, update):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    username = message.from_user.username
    support.delete_message(chat_id, message.message_id, bot)

    if are_banned(user_id, chat_id):
        return

    if message.reply_to_message is not None:
        if message.reply_to_message.location is not None:
            support.delete_message(chat_id, message.reply_to_message.message_id, bot)
            lat = message.reply_to_message.location.latitude
            lon = message.reply_to_message.location.longitude

            group = get_group(chat_id)
            group_tz = group.timezone
            tz = pytz.timezone(group_tz)

            localTime = datetime.now().replace(tzinfo=pytz.utc)
            groupDateTime = localTime.astimezone(tz)
            groupTime = groupDateTime.time()

            button_list = [
                [InlineKeyboardButton(text="📍 Ubicación", callback_data='sighting_ubi_{0}_{1}'.format(lat, lon))],
                [InlineKeyboardButton(text="🙋‍♀️ ¡Está!", callback_data='sighting_yes_{0}_{1}'.format(lat, lon)),
                InlineKeyboardButton(text="🙅‍♀️ No está...", callback_data='sighting_no_{0}_{1}'.format(lat, lon))
            ]]

            output = text.split(None, 1)
            out = "🐾 " + escape_markdown(output[1]) + f"\n\n👤 Avistado por @{username} a las {groupTime.hour:02}:{groupTime.minute:02}\nℹ️ Información:"

            bot.sendMessage(
                chat_id=chat_id,
                text=out,
                reply_markup=InlineKeyboardMarkup(button_list))


def sighting_btn(bot, update):
    query = update.callback_query
    data = query.data
    user = update.effective_user
    username = query.from_user.username
    user_id = query.from_user.id
    text = query.message.text
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    dataThings = data.split("_")
    lat = dataThings[2]
    lon = dataThings[3]

    if are_banned(user_id, chat_id):
        return   

    user = get_user(user_id)

    if user is None:
        return

    if re.match(r"^sighting_ubi_", data):
        bot.send_location(
            chat_id=user_id,
            latitude=lat,
            longitude=lon,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="📍 Google Maps", url='https://maps.google.com/maps?q={0},{1}'.format(lat, lon))]])
        )
        return

    string = r'\n🕚 (\d\d:\d\d) - @{} \| (🙋‍♀️ ¡Está!|🙅‍♀️ No está...)'.format(username)
    text = re.sub(string, "", text)

    group = get_group(chat_id)
    group_tz = group.timezone
    tz = pytz.timezone(group_tz)

    localTime = datetime.now().replace(tzinfo=pytz.utc)
    groupDateTime = localTime.astimezone(tz)
    groupTime = groupDateTime.time()

    if re.match(r"^sighting_yes_", data):
        text = text + f"\n🕚 {groupTime.hour:02}:{groupTime.minute:02} - @{username} | 🙋‍♀️ ¡Está!"

    if re.match(r"^sighting_no_", data):
        text = text + f"\n🕚 {groupTime.hour:02}:{groupTime.minute:02} - @{username} | 🙅‍♀️ No está..."

    button_list = [
                [InlineKeyboardButton(text="📍 Ubicación", callback_data='sighting_ubi_{0}_{1}'.format(lat, lon))],
                [InlineKeyboardButton(text="🙋‍♀️ ¡Está!", callback_data='sighting_yes_{0}_{1}'.format(lat, lon)),
                InlineKeyboardButton(text="🙅‍♀️ No está...", callback_data='sighting_no_{0}_{1}'.format(lat, lon))
            ]]

    bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=InlineKeyboardMarkup(button_list),
        disable_web_page_preview=True)
