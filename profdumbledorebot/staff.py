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
import profdumbledorebot.model as model
from profdumbledorebot.sql.user import get_user, is_staff, set_staff, get_real_user, set_user, commit_user, set_ghost, add_flag, rm_flag

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
        add_flag(args[0], "🧙‍♂️")
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
        rm_flag(args[0], "🧙‍♂️")
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

@run_async
def staff_register_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not is_staff(user_id):
        return

    if len(args) == 0:
        return

    if message.reply_to_message is not None:
        replied_userid = message.reply_to_message.from_user.id
        if message.reply_to_message.from_user.username is None:
            replied_username = "None"
        else:
            replied_username = support.ensure_escaped(message.reply_to_message.from_user.username)
        user_username = message.from_user.username
    else: 
        return

    if args == None or len(args)>5:
        logging.debug("%s", len(args))
        bot.sendMessage(
            chat_id=chat_id, 
            text="Has puesto demasiadas opciones, o ninguna.", 
            parse_mode=telegram.ParseMode.MARKDOWN)
        return

    output="🧙 [{0}](tg://user?id={1}) made changes to [{2}](tg://user?id={3}):".format(
            message.from_user.first_name,
            message.from_user.id,
            replied_username,        
            replied_userid
    )

    user = get_real_user(replied_userid)
    if user is None:
        set_user(replied_userid)
    
    alias = None
    level = None
    profession = None
    house = None
    team = None
    validation = None

    for arg in args:
        if arg=="v":
            validation = True
            change="\n- Validation set to *validated*"
        elif arg.lower() in ["p","m","a","bot"]:
            if arg=="p":
                profession = model.Professions.PROFESSOR.value
                change="\n- Profession set to *Professor*"
            elif arg=="m":
                profession = model.Professions.MAGIZOOLOGIST.value
                change="\n- Profession set to *Magizoologist*"
            elif arg=="a":
                profession = model.Professions.AUROR.value
                change="\n- Profession set to *Auror*"
            elif arg=="bot":
                profession = model.Professions.BOT.value
                change="\n- Profession set to *Bot*"
        elif arg.lower() in ["n","g","h","r","s","bothouse"]:
            if arg=="n":
                house = model.Houses.NONE.value
                change="\n- House set to *None*"
            elif arg=="g":
                house = model.Houses.GRYFFINDOR.value
                change="\n- House set to *Gryffindor*"
            elif arg=="h":
                house = model.Houses.HUFFLEPUFF.value
                change="\n- House set to *Hufflepuff*"
            elif arg=="r":
                house = model.Houses.RAVENCLAW.value
                change="\n- House set to *Ravenclaw*"
            elif arg=="s":
                house = model.Houses.SLYTHERIN.value
                change="\n- House set to *Slytherin*"
            elif arg=="bothouse":
                house = model.Houses.BOTS.value
                change="\n- House set to *Bots*"
        elif arg.isdigit() and int(arg) >= 1 and int(arg) <= 60:
            level = int(arg)
            change="\n- Level set to *{}*".format(level)
        elif re.match(r'[a-zA-Z0-9]{3,30}$', arg) is not None:
            alias = arg
            change="\n- Alias set to *{}*".format(alias)
        else:
            change="\n- *{}* was not a valid argument and was skipped.".format(arg)
        output="{}{}".format(output,change)

    try:
        commit_user(user_id=replied_userid, alias=alias, level=level, profession=profession, house=house, team=team, validation=validation)
    except:
        output="Huh... Se ha roto algo en el proceso @Sarayalth"
    bot.sendMessage(chat_id=chat_id, text=output, parse_mode=telegram.ParseMode.MARKDOWN)

@run_async
def add_ghost_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not is_staff(user_id):
        return

    if len(args) == 0:
        return

    user = get_user(user_id)

    if user is not None:
        set_ghost(args[0], True)
        add_flag(args[0], "👻")

    else:
        bot.sendMessage(
        chat_id=chat_id,
        text="❌ Ese usuario no existe.",
        parse_mode=telegram.ParseMode.MARKDOWN)
        return

    bot.sendMessage(
        chat_id=chat_id,
        text="👌 El usuario ahora es un fantasma 👻",
        parse_mode=telegram.ParseMode.MARKDOWN)

@run_async
def rm_ghost_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not is_staff(user_id):
        return

    if len(args) == 0:
        return

    if get_user(user_id) is not None:
        set_ghost(args[0], False)
        rm_flag(args[0], "👻")
    else:
        bot.sendMessage(
        chat_id=chat_id,
        text="❌ Ese usuario no existe.",
        parse_mode=telegram.ParseMode.MARKDOWN)
        return

    bot.sendMessage(
        chat_id=chat_id,
        text="👌 El usuario ya no es un fantasma 👻",
        parse_mode=telegram.ParseMode.MARKDOWN)