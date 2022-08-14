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
import time

import telegram
from telegram.ext.dispatcher import run_async

import profdumbledorebot.sql.news as news_sql
import profdumbledorebot.supportmethods as support
from profdumbledorebot.sql.support import are_banned


@run_async
def init_news(bot, update, args=None):
    chat_id, chat_type, user_id, text, message, message_type = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if chat_type != "channel":
        return

    if hasattr(message.chat, 'username') and message.chat.username is not None:
        alias = message.chat.username
    elif args is not None and len(args)!=0:
        alias = args[0]
    else:
        output = "❌ He reconocido este canal como un canal privado y no me has especificado un nombre para el canal."
        bot.sendMessage(chat_id=chat_id, text=output)
        return

    if not news_sql.is_news_provider(chat_id):
        news_sql.set_news_provider(chat_id, alias)

    output = (
        "📰 Bienvenido al sistema de noticias de @ProfesorDumbledoreBot.\nYa tan solo "
        "queda el último paso. Ejecuta `/add_news {}` en los grupos que quie"
        "ras recibir las noticias de este canal.".format(chat_id)
    )
    bot.sendMessage(chat_id=chat_id, text=output, parse_mode=telegram.ParseMode.MARKDOWN)


@run_async
def stop_news(bot, update):
    chat_id, chat_type, user_id, text, message, message_type = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if chat_type != "channel":
        return

    if news_sql.is_news_provider(chat_id):
        news_sql.rm_news_provider(chat_id)
        output = "✅ ¡Canal eliminado correctamente!"
    else:
        output = "❌ No he reconocido este canal como proveedor de noticias."

    bot.sendMessage(chat_id=chat_id, text=output)


@run_async
def add_news(bot, update, args=None):
    chat_id, chat_type, user_id, text, message, message_type = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    if args is None or len(args)!=1:
        return

    output = "❌ No he reconocido este canal como proveedor de noticias."

    if news_sql.is_news_provider(args[0]) and not news_sql.is_news_subscribed(chat_id, args[0]):
        news_sql.set_news_subscription(chat_id, args[0])
        output = "✅ ¡Suscripción realizada correctamente!"

    bot.sendMessage(chat_id=chat_id, text=output)


@run_async
def rm_news(bot, update, args=None):
    chat_id, chat_type, user_id, text, message, message_type = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    if args is None or len(args)!=1:
        return

    output = "❌ No he reconocido este canal como proveedor de noticias."

    if news_sql.is_news_provider(args[0]) and news_sql.is_news_subscribed(chat_id, args[0]):
        news_sql.rm_news_subscription(chat_id, args[0])
        output = "✅ ¡Suscripción eliminada correctamente!"

    bot.sendMessage(chat_id=chat_id, text=output)


@run_async
def list_news(bot, update):
    chat_id, chat_type, user_id, text, message, message_type = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    active_news = news_sql.get_news_subscribed(chat_id)
    verified_out = ""
    def_out = ""

    if active_news is None:
        output = "❌ No hay suscrpiciones activas en este grupo."

    else:
        for k in active_news:
            provider = news_sql.get_news_provider(k.news_id)
            if provider.active:
                verified_out = "🔰 @{}\n".format(provider.alias) + verified_out
            else:
                def_out = "📰 {} - `{}`\n".format(provider.alias, provider.id) + def_out

        output = "Listado de canales activos:\n" + verified_out + def_out

    bot.sendMessage(chat_id=chat_id, text=output, parse_mode=telegram.ParseMode.MARKDOWN)


@run_async
def send_news(bot, update):
    chat_id, chat_type, user_id, text, message, message_type = support.extract_update_info(update)

    if chat_type != "channel":
        return

    if not news_sql.is_news_provider(chat_id):
        return

    time.sleep(60)

    groups = news_sql.get_news_consumers(chat_id)
    if groups is None:
        return

    exceptions_users = []
    for k in groups:
        time.sleep(0.2)
        try:
            bot.forwardMessage(
                chat_id=k.user_id,
                from_chat_id=chat_id, 
                message_id=message.message_id
            )
        except Exception:
            exceptions_users.append(k.user_id)
            logging.info('sendingMessageTo:FAILURE->: %s', k.user_id)

    for k in exceptions_users:
        news_sql.rm_all_news_subscription(k)

