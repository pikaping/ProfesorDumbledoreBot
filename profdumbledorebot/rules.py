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
import os
import logging
import telegram

from telegram.error import BadRequest
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import escape_markdown

import profdumbledorebot.sql.rules as rules

from nursejoybot.supportmethods import (
    extract_update_info,
    delete_message,
    markdown_parser,
    is_admin
)
from nursejoybot.storagemethods import (
    are_banned,
    get_group_settings,
    get_rules,
    add_rules
)

def send_rules(bot, update, group_id=None):
    chat_id, chat_type, user_id, text, message = extract_update_info(update)

    if group_id is None:
        try:
            chat = bot.get_chat(chat_id)
        except BadRequest as excp:
            return
        rules = get_rules(chat_id)
        if chat_type != "private":
            group = get_group_settings(chat_id)
            if group.reply_on_group:
                dest_id = chat_id
            else:
                dest_id = user_id
        else:
            dest_id = user_id
    else:
        try:
            chat = bot.get_chat(group_id)
            rules = get_rules(group_id)
            dest_id = user_id
            bot.restrict_chat_member(
                group_id,
                user_id,
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        except BadRequest as excp:
            return

    text = "Normas de *{}*:\n\n{}".format(escape_markdown(chat.title), rules)

    if rules:
        bot.send_message(
            dest_id,
            text,
            parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        bot.send_message(
            dest_id,
            "❌ No hay normas establecidas en este grupo.",
            parse_mode=telegram.ParseMode.MARKDOWN)

@run_async
def rules(bot, update):
    send_rules(bot, update)


@run_async
def set_rules(bot, update):
    chat_id, chat_type, user_id, text, message = extract_update_info(update)
    if not is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    args = text.split(None, 1)
    if len(args) == 2:
        txt = args[1]
        offset = len(txt) - len(text)
        markdown_rules = markdown_parser(txt, entities=message.parse_entities(), offset=offset)

        add_rules(chat_id, markdown_rules)
        update.effective_message.reply_text(
            "✅ Normas del grupo establecidas correctamente.".format(chat_id))

@run_async
def clear_rules(bot, update):
    chat_id, chat_type, user_id, text, message = extract_update_info(update)
    if not is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return
    
    add_rules(chat_id, "")
    update.effective_message.reply_text("❌ Normas del grupo eliminadas correctamente.")
