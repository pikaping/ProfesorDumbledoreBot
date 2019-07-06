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

import os
import re
import logging
import telegram
import profdumbledorebot.supportmethods as support

from telegram.ext.dispatcher import run_async
from profdumbledorebot.sql.user import get_user
from telegram.utils.helpers import escape_markdown
from profdumbledorebot.sql.support import are_banned
from profdumbledorebot.model import Houses, ValidationType
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

REGLIST = re.compile(
    r'Apuntados:'
)

@run_async
def list_cmd(bot, update):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if are_banned(user_id, chat_id):
        return

    button_list = [[
        InlineKeyboardButton(text="Me apunto!", callback_data='list_join'),
        InlineKeyboardButton(text="Paso...", callback_data='list_left')
    ]]

    output = text.split(None, 1)
    out = escape_markdown(output[1]) + "\n\nApuntados:"

    bot.send_message(
        chat_id=chat_id,
        text=out,
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(button_list))


def list_btn(bot, update):
    query = update.callback_query
    data = query.data
    user = update.effective_user
    username = query.from_user.username
    user_id = query.from_user.id
    text = query.message.text
    chat_id = query.message.chat.id
    message_id = query.message.message_id

    if are_banned(user_id, chat_id):
        return   

    user = get_user(user_id)

    if user is None or user.validation_type == ValidationType.NONE:
        return

    if user.house is Houses.GRYFFINDOR:
        text_team = "❤️🦁"
    elif user.house is Houses.HUFFLEPUFF:
        text_team = "💛🦡"
    elif user.house is Houses.RAVENCLAW:
        text_team = "💙🦅"
    elif user.house is Houses.SLYTHERIN:
        text_team = "💚🐍"

    string = r'\n(.|❤️🦁|💙🦅|💛🦡|💚🐍)(\d\d|\d) - @{}'.format(username)
    text = re.sub(string, "", text)

    if data == "list_join":
        text = escape_markdown(text) + "\n{0}**{1}** - @{2}".format(
            text_team,
            user.level,
            escape_markdown("{}".format(username))
        )

    button_list = [[
        InlineKeyboardButton(text="Me apunto!", callback_data='list_join'),
        InlineKeyboardButton(text="Paso...", callback_data='list_left')
    ]]
    bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=message_id,
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(button_list),
        disable_web_page_preview=True)


@run_async
def listclose_cmd(bot, update):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if message.reply_to_message is None or message.reply_to_message.chat.id != chat_id:
        return

    if message.reply_to_message.from_user.id != bot.id:
        return

    if are_banned(user_id, chat_id) or not support.is_admin(chat_id, user_id, bot):
        return

    text = message.reply_to_message.text
    if REGLIST.search(text) is None:
        return

    bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message.reply_to_message.message_id,
        reply_markup=None)


@run_async
def listopen_cmd(bot, update):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)
    
    if message.reply_to_message is None or message.reply_to_message.chat.id != chat_id:
        return

    if message.reply_to_message.from_user.id != bot.id:
        return

    if are_banned(user_id, chat_id) or not support.is_admin(chat_id, user_id, bot):
        return

    text = message.reply_to_message.text
    if REGLIST.search(text) is None:
        return

    button_list = [[
        InlineKeyboardButton(text="Me apunto!", callback_data='list_join'),
        InlineKeyboardButton(text="Paso...", callback_data='list_left')
    ]]

    bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message.reply_to_message.message_id,
        reply_markup=InlineKeyboardMarkup(button_list)
    )
  

@run_async
def listrefloat_cmd(bot, update):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)
    
    if message.reply_to_message is None or message.reply_to_message.chat.id != chat_id:
        return

    if message.reply_to_message.from_user.id != bot.id:
        return

    if are_banned(user_id, chat_id) or not support.is_admin(chat_id, user_id, bot):
        return

    text = message.reply_to_message.text
    if REGLIST.search(text) is None:
        return

    text = message.reply_to_message.text
    button_list = [[
        InlineKeyboardButton(text="Me apunto!", callback_data='list_join'),
        InlineKeyboardButton(text="Paso...", callback_data='list_left')
    ]]

    bot.send_message(
        chat_id=chat_id,
        text=escape_markdown(text),
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(button_list)
    )
    support.delete_message(chat_id, message.reply_to_message.message_id, bot)

