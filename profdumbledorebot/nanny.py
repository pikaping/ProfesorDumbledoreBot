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

from telegram.ext.dispatcher import run_async
from profdumbledorebot.news import init_news, stop_news
from profdumbledorebot.sql.usergroup import warn_user
from profdumbledorebot.sql.settings import get_nanny_settings, get_group_settings, set_nanny_reply


def nanny_text(bot, user_id, chat_id, message, job_queue):
    nanny = get_nanny_settings(chat_id)

    if nanny and nanny.text:
        if support.is_admin(chat_id, user_id, bot) and not nanny.admin_too:
            return False

        support.delete_message(chat_id, message.message_id, bot)
        if nanny and nanny.warn:
            send_warn(bot, chat_id, user_id, job_queue, nanny.reply)
        else:
            send_alert(bot, chat_id, job_queue, nanny.reply)

        return True

    return False
    

def process_gif(bot, update, job_queue):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    nanny = get_nanny_settings(chat_id)

    if nanny and nanny.animation:
        if support.is_admin(chat_id, user_id, bot) and not nanny.admin_too:
            return

        support.delete_message(chat_id, message.message_id, bot)
        if nanny.warn:
            send_warn(bot, chat_id, user_id, job_queue, nanny.reply)
        else:
            send_alert(bot, chat_id, job_queue, nanny.reply)


def process_cmd(bot, update, job_queue):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)

    try:
        args = re.sub(r"^/[a-zA-Z0-9_]+", "", text).strip().split(" ")
        if len(args) == 1 and args[0] == "":
            args = []

    except Exception:
        args = None

    m = re.match("/([a-zA-Z0-9_]+)", text)

    if m is not None:
        command = m.group(1).lower()

        if command == "init_news":
            init_news(bot, update, args)
            return

        elif command == "stop_news":
            stop_news(bot, update, job_queue)
            return

    nanny = get_nanny_settings(chat_id)

    if nanny and nanny.command:
        if support.is_admin(chat_id, user_id, bot) and not nanny.admin_too:
            return

        support.delete_message(chat_id, message.message_id, bot)

        if nanny and nanny.warn:
            send_warn(bot, chat_id, user_id, job_queue, nanny.reply)

        else:
            send_alert(bot, chat_id, job_queue, nanny.reply)


def process_contact(bot, update, job_queue):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update) 
    nanny = get_nanny_settings(chat_id)

    if nanny and nanny.contact:
        if support.is_admin(chat_id, user_id, bot) and not nanny.admin_too:
            return

        support.delete_message(chat_id, message.message_id, bot)

        if nanny and nanny.warn:
            send_warn(bot, chat_id, user_id, job_queue, nanny.reply)

        else:
            send_alert(bot, chat_id, job_queue, nanny.reply)


def process_file(bot, update, job_queue):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update) 
    nanny = get_nanny_settings(chat_id)

    if nanny and nanny.document:
        if support.is_admin(chat_id, user_id, bot) and not nanny.admin_too:
            return

        support.delete_message(chat_id, message.message_id, bot)

        if nanny and nanny.warn:
            send_warn(bot, chat_id, user_id, job_queue, nanny.reply)

        else:
            send_alert(bot, chat_id, job_queue, nanny.reply)


def process_game(bot, update, job_queue):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)

    nanny = get_nanny_settings(chat_id)

    if nanny and nanny.games:
        if support.is_admin(chat_id, user_id, bot) and not nanny.admin_too:
            return

        support.delete_message(chat_id, message.message_id, bot)

        if nanny and nanny.warn:
            send_warn(bot, chat_id, user_id, job_queue, nanny.reply)

        else:
            send_alert(bot, chat_id, job_queue, nanny.reply)


def process_ubi(bot, update, job_queue):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update) 

    nanny = get_nanny_settings(chat_id)
    if nanny and nanny.location:
        if support.is_admin(chat_id, user_id, bot) and not nanny.admin_too:
            return

        support.delete_message(chat_id, message.message_id, bot)

        if nanny and nanny.warn:
            send_warn(bot, chat_id, user_id, job_queue, nanny.reply)

        else:
            send_alert(bot, chat_id, job_queue, nanny.reply)


def process_pic(bot, update, job_queue):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update) 

    nanny = get_nanny_settings(chat_id)

    if nanny and nanny.photo:
        if support.is_admin(chat_id, user_id, bot) and not nanny.admin_too:
            return

        support.delete_message(chat_id, message.message_id, bot)

        if nanny and nanny.warn:
            send_warn(bot, chat_id, user_id, job_queue, nanny.reply)

        else:
            send_alert(bot, chat_id, job_queue, nanny.reply)


def process_sticker(bot, update, job_queue):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update) 

    nanny = get_nanny_settings(chat_id)

    if nanny and nanny.sticker:
        if support.is_admin(chat_id, user_id, bot) and not nanny.admin_too:
            return

        support.delete_message(chat_id, message.message_id, bot)

        if nanny and nanny.warn:
            send_warn(bot, chat_id, user_id, job_queue, nanny.reply)

        else:
            send_alert(bot, chat_id, job_queue, nanny.reply)


def process_voice(bot, update, job_queue):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)  

    nanny = get_nanny_settings(chat_id)

    if nanny and nanny.voice:
        if support.is_admin(chat_id, user_id, bot) and not nanny.admin_too:
            return

        support.delete_message(chat_id, message.message_id, bot)

        if nanny and nanny.warn:
            send_warn(bot, chat_id, user_id, job_queue, nanny.reply)

        else:
            send_alert(bot, chat_id, job_queue, nanny.reply)


def process_video(bot, update, job_queue):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update) 

    nanny = get_nanny_settings(chat_id)

    if nanny and nanny.video:
        if support.is_admin(chat_id, user_id, bot) and not nanny.admin_too:
            return

        support.delete_message(chat_id, message.message_id, bot)

        if nanny and nanny.warn:
            send_warn(bot, chat_id, user_id, job_queue, nanny.reply)

        else:
            send_alert(bot, chat_id, job_queue, nanny.reply)


def process_url(bot, update, job_queue):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)  

    nanny = get_nanny_settings(chat_id)

    if nanny and nanny.urls:
        if support.is_admin(chat_id, user_id, bot) and not nanny.admin_too:
            return False

        support.delete_message(chat_id, message.message_id, bot)

        if nanny and nanny.warn:
            send_warn(bot, chat_id, user_id, job_queue, nanny.reply)

        else:
            send_alert(bot, chat_id, job_queue, nanny.reply)

        return True

    return False


def send_alert(bot, chat_id, job_queue, nanny_text=None):
    if nanny_text is None:
        text = (
            "Shhhh... Lo siento pero aquí no puedes enviar "
            "este tipo de mensaje por este grupo.\n\n_(Es"
            "te mensaje se borrará en unos segundos)_"
        )
    else:
        text = nanny_text

    sent_message = bot.sendMessage(chat_id=chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)
    delete_object = support.DeleteContext(chat_id, sent_message.message_id)
    job_queue.run_once(support.callback_delete, 10, context=delete_object)


def send_warn(bot, chat_id, user_id, job_queue, nanny_text=None):
    warning = warn_user(chat_id, user_id, 1)
    group = get_group_settings(chat_id)
    if nanny_text is not None:
        text = nanny_text + "\n"
    else:
        text = ""
    
    if warning < group.warn:
        text = text + "Has recibido un aviso por enviar contenido prohibido en este grupo.*{}/{}*".format(warning, group.warn)
    else:
        text = "Un entrenador ha sido expulsado por alcanzar el máximo de avisos."
        warn_user(chat_id, user_id, 0)
        try:
            bot.kickChatMember(chat_id, user_id)
            if group.hard is False:
                bot.unbanChatMember(chat_id, user_id)
        except:
            text = "No tengo permisos suficientes para expulsar usuarios"

    sent_message = bot.sendMessage(chat_id=chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)
    delete_object = support.DeleteContext(chat_id, sent_message.message_id)
    job_queue.run_once(support.callback_delete, 10, context=delete_object)


@run_async
def set_nanny(bot, update, args=None):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    if not support.is_admin(chat_id, user_id, bot):
        return

    args = msg.text.split(None, 1)
    if len(args) >= 2:
        offset = len(args[1]) - len(msg.text)
        text, buttons = support.button_markdown_parser(args[1], entities=msg.parse_entities(), offset=offset)
        set_nanny_reply(chat_id, text)
        msg.reply_text("Mensaje del modo biblioteca guardado correctamente")

    else:
        set_nanny_reply(chat_id, None)
        msg.reply_text("Mensaje del modo biblioteca por defecto activado")

