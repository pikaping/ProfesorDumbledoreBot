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
import logging
import telegram

import profdumbledorebot.sql.welcome as welcome_sql
import profdumbledorebot.supportmethods as support

from telegram.error import BadRequest
from profdumbledorebot.model import Types
from profdumbledorebot.config import get_config
from profdumbledorebot.sql.rules import has_rules
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.utils.helpers import mention_markdown, escape_markdown


VALID_WELCOME_FORMATTERS = ['nombre', 'apellido', 'nombre_completo', 'usuario', 'id', 'count', 'title', 'hpwu', 'mention']


def send_welcome(bot, update):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    chat = update.effective_chat

    ENUM_FUNC_MAP = {
        Types.TEXT.value: bot.sendMessage,
        Types.BUTTON_TEXT.value: bot.sendMessage,
        Types.STICKER.value: bot.sendSticker,
        Types.DOCUMENT.value: bot.sendDocument,
        Types.PHOTO.value: bot.sendPhoto,
        Types.AUDIO.value: bot.sendAudio,
        Types.VOICE.value: bot.sendVoice,
        Types.VIDEO.value: bot.sendVideo
    }

    should_welc, cust_welcome, welc_type = welcome.get_welc_pref(chat.id)
    if should_welc:
        sent = None
        new_members = update.effective_message.new_chat_members
        for new_mem in new_members:

            if welc_type != Types.TEXT and welc_type != Types.BUTTON_TEXT:
                msg = ENUM_FUNC_MAP[welc_type](chat.id, cust_welcome)
                return msg

            first_name = new_mem.first_name or ""

            if cust_welcome:
                if new_mem.last_name:
                    fullname = "{} {}".format(first_name, new_mem.last_name)
                else:
                    fullname = first_name
                count = chat.get_members_count()
                mention = mention_markdown(new_mem.id, first_name)
                if new_mem.username:
                    username = "@" + escape_markdown(new_mem.username)
                else:
                    username = mention

                valid_format = support.escape_invalid_curly_brackets(cust_welcome, VALID_WELCOME_FORMATTERS)
                res = valid_format.format(nombre=escape_markdown(first_name),
                                          apellido=escape_markdown(new_mem.last_name or first_name),
                                          pogo=support.replace(new_mem.id, first_name),
                                          nombre_completo=escape_markdown(fullname), usuario=username, mention=mention,
                                          count=count, title=escape_markdown(chat.title), id=new_mem.id)
                buttons = welcome.get_welc_buttons(chat.id)
                keyb = support.build_keyboard(buttons)
                if has_rules(chat.id):
                    config = get_config()
                    url = "t.me/{}?start={}".format(
                        config["telegram"]["bot_alias"],
                        chat.id)
                    keyb.append([InlineKeyboardButton("Normas", url=url)])
            else:
                return

            keyboard = InlineKeyboardMarkup(keyb)

            sent = send(bot, chat_id, res, keyboard)
            return sent


def send(bot, chat_id, message, keyboard):
    try:
        msg = bot.sendMessage(
            chat_id=chat_id,
            text=message, 
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=True, 
            disable_notification=True,
            reply_markup=keyboard
        )

    except IndexError:
        msg = update.effective_message.reply_text(support.markdown_parser("\nBip bop bip: El mensaje tiene errores de"
                                                                  "Markdown, revisalo y configuralo de nuevo."),
                                                  parse_mode=telegram.ParseMode.MARKDOWN)
    except KeyError:
        msg = update.effective_message.reply_text(support.markdown_parser("\nBip bop bip: El mensaje tiene errores con"
                                                                  "las llaves, revisalo y configuralo de nuevo."),
                                                  parse_mode=telegram.ParseMode.MARKDOWN)
    except BadRequest as excp:
        if excp.message == "Button_url_invalid":
            msg = update.effective_message.reply_text(support.markdown_parser("\nBip bop bip: El mensaje tiene errores en"
                                                                  "los botones, revisalo y configuralo de nuevo."),
                                                      parse_mode=telegram.ParseMode.MARKDOWN)
        elif excp.message == "Unsupported url protocol":
            msg = update.effective_message.reply_text(support.markdown_parser("\nBip bop bip: El mensaje tiene URLs"
                                                                  "invalidas para Telegram, revisalo y configuralo de nuevo."),
                                                      parse_mode=telegram.ParseMode.MARKDOWN)
        elif excp.message == "Wrong url host":
            msg = update.effective_message.reply_text(support.markdown_parser("\nBip bop bip: El mensaje tiene URLs"
                                                                  "erroneas, revisalo y configuralo de nuevo."),
                                                      parse_mode=telegram.ParseMode.MARKDOWN)
        else:
            msg = update.effective_message.reply_text(support.markdown_parser("\nBip bop bip: Hubo un error mandando el mensaje."
                                                                  "Contacta con @Pikapiing"),
                                                      parse_mode=telegram.ParseMode.MARKDOWN)
    return msg

