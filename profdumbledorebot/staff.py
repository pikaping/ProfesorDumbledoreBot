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
import re

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import escape_markdown

import profdumbledorebot.supportmethods as support
from profdumbledorebot.sql.user import get_user, is_staff, set_staff

@run_async
def add_staff_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not is_staff(user_id):
        return

    if len(args) == 0:
        return

    if get_user(user_id) is not None:
        set_staff(args[0], True)
    else:
        bot.sendMessage(
        chat_id=chat_id,
        text="❌ Ese usuario no existe.",
        parse_mode=telegram.ParseMode.MARKDOWN)
        return

    bot.sendMessage(
        chat_id=chat_id,
        text="👌 El usuario ahora forma parte del Staff",
        parse_mode=telegram.ParseMode.MARKDOWN)

@run_async
def rm_staff_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not is_staff(user_id):
        return

    if len(args) == 0:
        return

    if get_user(user_id) is not None:
        set_staff(args[0], False)
    else:
        bot.sendMessage(
        chat_id=chat_id,
        text="❌ Ese usuario no existe.",
        parse_mode=telegram.ParseMode.MARKDOWN)
        return

    bot.sendMessage(
        chat_id=chat_id,
        text="👌 El usuario ya no forma parte del Staff",
        parse_mode=telegram.ParseMode.MARKDOWN)

