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

import telegram
from telegram.error import BadRequest
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import escape_markdown

import profdumbledorebot.sql.rules as rul_sql
import profdumbledorebot.supportmethods as support
from profdumbledorebot.sql.settings import get_group_settings
from profdumbledorebot.sql.support import are_banned


def send_rules(bot, update, group_id=None):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if group_id is None:
        try:
            chat = bot.get_chat(chat_id)
        except BadRequest as excp:
            return
        rules = rul_sql.get_rules(chat_id)
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
            rules = rul_sql.get_rules(group_id)
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
        bot.sendMessage(
            dest_id,
            text,
            parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        bot.sendMessage(
            dest_id,
            "❌ No hay normas establecidas en este grupo.",
            parse_mode=telegram.ParseMode.MARKDOWN)

@run_async
def rules(bot, update):
    send_rules(bot, update)


@run_async
def set_rules(bot, update):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    args = text.split(None, 1)
    if len(args) == 2:
        txt = args[1]
        offset = len(txt) - len(text)
        markdown_rules = support.markdown_parser(txt, entities=message.parse_entities(), offset=offset)

        rul_sql.add_rules(chat_id, markdown_rules)
        update.effective_message.reply_text("✅ Normas del grupo establecidas correctamente.".format(chat_id))

@run_async
def clear_rules(bot, update):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return
    
    rul_sql.add_rules(chat_id, "")
    update.effective_message.reply_text("❌ Normas del grupo eliminadas correctamente.")
