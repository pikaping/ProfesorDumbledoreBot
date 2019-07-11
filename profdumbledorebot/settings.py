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
import telegram

import profdumbledorebot.supportmethods as support

from pytz import timezone
from datetime import datetime
from nursejoybot.db import get_session
from telegram.ext.dispatcher import run_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from profdumbledorebot.sql.group import get_group
from profdumbledorebot.sql.support import are_banned
from profdumbledorebot.sql.usergroup import remove_warn
from profdumbledorebot.sql.admin import set_admin_settings, set_ladmin_settings
from profdumbledorebot.sql.news import is_news_subscribed, rm_news_subscription, set_news_subscription
from profdumbledorebot.sql.welcome import set_welc_preference, set_custom_welcome, set_welcome_settings
from profdumbledorebot.sql.settings import set_max_members, set_general_settings, set_join_settings, set_nanny_settings


@run_async
def settings(bot, update, args=None):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    group = get_group(chat_id)
    if group is None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ No puedo reconocer este grupo. Si estaba funcionando hasta ahora, pregunta en @profesordumbledoreayuda.",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return

    message = bot.sendMessage(chat_id=chat_id, text="Oído cocina!...")
    support.update_settings_message(chat_id, bot, message.message_id, keyboard="main")


@run_async
def set_welcome(bot, update):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    text, data_type, content, buttons = support.get_welcome_type(message)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    group = get_group(chat_id)
    if group is None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ No puedo reconocer este grupo. Si estaba funcionando hasta ahora, pregunta en @profesordumbledoreayuda.",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return

    if data_type is None:
        set_welc_preference(chat_id, False)
        bot.sendMessage(chat_id=chat_id, text="👌 Mensaje de bienvenida desactivado correctamente")
        return

    set_welc_preference(chat_id, True)
    set_custom_welcome(chat_id, content or text, data_type, buttons)
    bot.sendMessage(chat_id=chat_id, text="👌 Mensaje de bienvenida guardado correctamente")


@run_async
def set_zone(bot, update, args=None):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    group = get_group(chat_id)
    if group is None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ No puedo reconocer este grupo. Si estaba funcionando hasta ahora, pregunta en @profesordumbledoreayuda.",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return

    if args is None or len(args) != 1 or len(args[0]) < 3 or len(args[0]) > 60:
        bot.sendMessage(
            chat_id=chat_id,
            text=("❌ Me siento un poco perdida ahora mismo. Debes pasarme un nombre de zona horaria en inglés, por ejemplo, `America/Montevideo` o `Europe/Madrid`."))
        return

    tz = support.get_unified_timezone(args[0])

    if len(tz) == 1:
        commit_group(chat_id, timezone=tz[0])
        bot.sendMessage(
            chat_id=chat_id,
            text="👌 Perfecto! Ya se que hora es. *{}*.".format(group.timezone))
        now = datetime.now(timezone(group.timezone)).strftime("%H:%M")
        bot.sendMessage(
            chat_id=chat_id,
            text="🕒 Por favor, comprueba que la hora sea correcta: {}".format(now))

    elif len(tz) == 0:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Uy, no he encontrado ninguna zona horaria con ese nombre")

    else:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Has sido demasiado genérico con el nombre de la zona horaria. Intenta concretar más.")


@run_async
def set_maxmembers(bot, update, args=None):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    group = get_group(chat_id)
    if group is None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ No puedo reconocer este grupo. Si estaba funcionando hasta ahora, pregunta en @profesordumbledoreayuda.",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return

    if args is None or len(args) != 1 or not args[0].isdigit() or int(args[0])<0:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ No he reconocido el parámetro introducido. Por favor, revisa el comando e intenta de nuevo.")
        return

    if int(args[0]) is 0:
        set_max_members(chat_id, None)
        output = "👌 Número máximo de miembros en el grupo desactivado correctamente."
    else:
        set_max_members(chat_id, int(args[0]))
        output = "👌 Número máximo de miembros en el grupo establecido a {}".format(args[0])
    bot.sendMessage(
        chat_id=chat_id,
        text=output,
        parse_mode=telegram.ParseMode.MARKDOWN)
    return


@run_async
def set_cooldown(bot, update, args=None):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    group = get_group(chat_id)
    if group is None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ No puedo reconocer este grupo. Si estaba funcionando hasta ahora, pregunta en @profesordumbledoreayuda.",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return

    if args is None or len(args) != 1 or not args[0].isdigit() or int(args[0])<0:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ No he reconocido el parámetro introducido. Por favor, revisa el comando e intenta de nuevo.")
        return

    if int(args[0]) is 0:
        set_welcome_cooldown(chat_id, None)
        output = "👌 El mensaje de bienvenida no se eliminará automáticamente."
    else:
        set_welcome_cooldown(chat_id, int(args[0]))
        output = "👌 El mensaje de bienvenida se eliminará automáticamente en {} segundos".format(args[0])
    bot.sendMessage(
        chat_id=chat_id,
        text=output,
        parse_mode=telegram.ParseMode.MARKDOWN)
    return


@run_async
def settingsbutton(bot, update):
    logging.debug("%s %s", bot, update)
    query = update.callback_query
    data = query.data
    user = update.effective_user
    user_id = query.from_user.id
    user_username = query.from_user.username
    chat_id = query.message.chat.id
    message_id = query.message.message_id

    are_banned(user_id, chat_id)

    settings_goto = {
        "settings_goto_general": "general",
        "settings_goto_join": "join",
        "settings_goto_news": "news",
        "settings_goto_welcome": "welcome",
        "settings_goto_nanny": "nanny",
        "settings_goto_ladmin": "ladmin",
        "settings_goto_main": "main"
    }
    settings_general = {
        "settings_general_jokes": "jokes",
        "settings_general_games": "games",
        "settings_general_hard": "hard",
        "settings_general_reply": "reply",
        "settings_general_warn": "warn"
    }
    settings_join = {
        "settings_join_mute": "mute",
        "settings_join_silence": "silence",
        "settings_join_val": "val"
    }
    settings_welcome = {
        "settings_welcome_welcome": "should_welcome"
    }
    settings_nanny = {
        "settings_nanny_command": "cmd",
        "settings_nanny_animation": "animation",
        "settings_nanny_contact": "contact",
        "settings_nanny_photo": "photo",
        "settings_nanny_games": "games",
        "settings_nanny_text": "text",
        "settings_nanny_sticker": "sticker",
        "settings_nanny_location": "location",
        "settings_nanny_url": "url",
        "settings_nanny_video": "video",
        "settings_nanny_warn": "warn",
        "settings_nanny_admin_too": "admin_too"
    }
    settings_ladmin = {
        "settings_ladmin_welcome": "welcome",
        "settings_ladmin_admin": "admin",
        "settings_ladmin_ejections": "ejections"
    }
    settings_admin = {
        "settings_admin_welcome": "welcome",
        "settings_admin_goodbye": "goodbye",
        "settings_admin_admin": "admin",
        "settings_admin_ejections": "ejections"
    }

    if re.match("^settings_.+$", data) is not None:
        match = re.match(r"settings_news_([-0-9]*)", query.data)
        if not support.is_admin(chat_id, user_id, bot):
            bot.answerCallbackQuery(
                text="Solo los administradores del grupo pueden configurar el bot.",
                callback_query_id=update.callback_query.id,
                show_alert="true"
            )
            return

        if data in settings_goto:
            support.update_settings_message(chat_id, bot, message_id, keyboard=settings_goto[data])
        elif data == "settings_done":
            support.delete_message(chat_id, message_id, bot)
        elif data in settings_general:
            set_general_settings(chat_id, settings_general[data])
            support.update_settings_message(chat_id, bot, message_id, keyboard="general")          
        elif data in settings_join:
            set_join_settings(chat_id, settings_join[data])
            support.update_settings_message(chat_id, bot, message_id, keyboard="join")
        elif data in settings_welcome:
            set_welcome_settings(chat_id, settings_welcome[data])
            support.update_settings_message(chat_id, bot, message_id, keyboard="welcome")
        elif data in settings_nanny:
            set_nanny_settings(chat_id, settings_nanny[data])
            support.update_settings_message(chat_id, bot, message_id, keyboard="nanny")
        elif data in settings_admin:
            set_admin_settings(chat_id, settings_admin[data])
            support.update_settings_message(chat_id, bot, message_id, keyboard="admin")
        elif data in settings_ladmin:
            set_ladmin_settings(chat_id, settings_ladmin[data])
            support.update_settings_message(chat_id, bot, message_id, keyboard="ladmin")
        elif data == "settings_admin_spy":
            set_ladmin_settings(chat_id, "admin_bot")
            support.delete_message(chat_id, message_id, bot)
            output = "Antes de nada administradores quiero daros las gracias. Debeis haber demostrado verdadera lealtad hacia mi en el grupo, y solo eso ha podido lograr que acuda Fawkes a vuestro grupo.\nÉl no puede leer nada de lo que suceda en el grupo, simplemente enviará las alertas que hayais configurado. Si necesitais configurar de nuevo las alertas o quereis usar los comandos, invitadme de nuevo al grupo y cuando acabeis volved a activar a Fawkes."
            bot.sendMessage(chat_id=chat_id, text=output, parse_mode=telegram.ParseMode.MARKDOWN)
            bot.leaveChat(chat_id=chat_id)

        elif match:
            news_id = match.group(1)
            if is_news_subscribed(chat_id, news_id):
                rm_news_subscription(chat_id, news_id)
            else:
                set_news_subscription(chat_id, news_id)
            support.update_settings_message(chat_id, bot, message_id, keyboard="news")

        return

    match = re.match(r"rm_warn\((.+?)\)", query.data)
    if match:
        if not support.is_admin(chat_id, user_id, bot):
            bot.answerCallbackQuery(
                text="Solo los administradores del grupo pueden retirar warns.",
                callback_query_id=update.callback_query.id,
                show_alert="true"
            )
            return

        user_id = match.group(1)
        res = remove_warn(user_id, chat_id)
        if res:
            text = "Aviso eliminado por @{}.".format(user_username)
            bot.answerCallbackQuery(
                text="Has eliminado un warn.", callback_query_id=update.callback_query.id, show_alert="true")

        else:
            bot.answerCallbackQuery(
                text="En estos momentos no puedo eliminar el warn, prueba mas tarde.",
                callback_query_id=update.callback_query.id,
                show_alert="true"
            )
            return
        bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=message_id,
            parse_mode=telegram.ParseMode.HTML,
            disable_web_page_preview=True
        )
        return

    match = re.match(r"rm_ban\((.+?)\)", query.data)
    if match:
        if not support.is_admin(chat_id, user_id, bot):
            bot.answerCallbackQuery(
                text="Solo los administradores del grupo pueden retirar bans.",
                callback_query_id=update.callback_query.id,
                show_alert="true"
            )
            return
        us_id = match.group(1)
        bot.unbanChatMember(chat_id, us_id)
        bot.answerCallbackQuery(
            text="Has eliminado un ban.", callback_query_id=update.callback_query.id, show_alert="true")
        text="Ban retirado por @{}.".format(user_username)
        bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=message_id,
            parse_mode=telegram.ParseMode.HTML,
            disable_web_page_preview=True
        )
        return

    else:
        logging.error('settingsbutton:%s is not a expected settings command', data)

