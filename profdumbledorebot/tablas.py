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

import json
import logging
import re
from uuid import uuid4

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedPhoto
from telegram.ext.dispatcher import run_async

from profdumbledorebot.config import get_config
from profdumbledorebot.supportmethods import extract_update_info

try:
    with open('/var/local/profdumbledore/json/tablas.json') as f:
        __TABLAS_JSON = json.load(f)
except:
    __TABLAS_JSON = None


@run_async
def list_pics(bot, update, args):
    logging.debug("%s %s" % (bot, update))
    chat_id, chat_type, user_id, text, message = extract_update_info(update)
    output = "Listado de tablas:"
    count = 0

    if args is None or len(args)!=1:
        for k in __TABLAS_JSON["tablas"]:
            count = count + 1
            output = output + "\n\nTitle: {1}\nKeywords: {2}\nID: `{0}`".format(
                k["id"],
                k["name"],
                k["keywords"]
            )
            if count == 5:  
                bot.sendMessage(
                    chat_id=chat_id,
                    text=output,
                    parse_mode=telegram.ParseMode.MARKDOWN)
                count = 0
                output = ""
    else:
        for k in __TABLAS_JSON["tablas"]:
            if args[0] in k["keywords"]:
                count = count + 1
                output = output + "\n\nTitle: {1}\nKeywords: {2}\nID: `{0}`".format(
                    k["id"],
                    k["name"],
                    k["keywords"]
                )
                if count == 5:  
                    bot.sendMessage(
                        chat_id=chat_id,
                        text=output,
                        parse_mode=telegram.ParseMode.MARKDOWN)
                    count = 0
                    output = ""


    if count != 0:
        bot.sendMessage(
            chat_id=chat_id,
            text=output,
            parse_mode=telegram.ParseMode.MARKDOWN)


@run_async
def new_pic(bot, update, args=None):
    logging.debug("%s %s" % (bot, update))
    chat_id, chat_type, user_id, text, message = extract_update_info(update)

    if args is None or len(args)<3:
        return

    if message.reply_to_message is None or message.reply_to_message.photo is None:
        return

    with open('/var/local/profdumbledore/json/tablas.json') as f:
        data = json.load(f)

    name = ""
    while args[0] != "-":
        name = name + args[0]
        del args[0]
    
    del args[0]

    tabla_id = "{}".format(uuid4())
    data['tablas'].insert(0, {  
        "id":tabla_id,
        "name":name,
        "file_id":update.message.reply_to_message.photo[-1]["file_id"],
        "keywords":args
    })

    with open('/var/local/profdumbledore/json/tablas.json', 'w') as outfile:  
        json.dump(data, outfile)

    reload_tablas()

    output = "Nueva tabla añadida.\nID: `{}`\nNombre: *{}*".format(
        tabla_id,
        name
    )
    txt = name.replace(" ", "_")
    keyboard = [[
        InlineKeyboardButton(text="✅ Si", callback_data='tabla_new_{}'.format(txt)),
        InlineKeyboardButton(text="❌ No", callback_data='tabla_rm')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.sendMessage(
        chat_id=chat_id,
        text=output,
        reply_markup=reply_markup,
        parse_mode=telegram.ParseMode.MARKDOWN
    )


@run_async
def edit_pic(bot, update, args=None):
    logging.debug("%s %s" % (bot, update))
    chat_id, chat_type, user_id, text, message = extract_update_info(update)

    if args is None or len(args)!=1 or len(args[0])!=36:
        return

    if message.reply_to_message is None or message.reply_to_message.photo is None:
        return

    with open('/var/local/profdumbledore/json/tablas.json') as f:
        data = json.load(f)

    for k in data["tablas"]:
        if k["id"] == args[0]:
            k["file_id"] = update.message.reply_to_message.photo[-1]["file_id"]
            break

    with open('/var/local/profdumbledore/json/tablas.json', 'w') as outfile:  
        json.dump(data, outfile)

    reload_tablas()

    output = "Tabla editada.\nID: `{}`\nNombre: *{}*".format(
        k["id"],
        k["name"]
    )
    txt = k["name"].replace(" ", "_")
    keyboard = [[
        InlineKeyboardButton(text="✅ Si", callback_data='tabla_edit_{}'.format(txt)),
        InlineKeyboardButton(text="❌ No", callback_data='tabla_rm')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.sendMessage(
        chat_id=chat_id,
        text=output,
        reply_markup=reply_markup,
        parse_mode=telegram.ParseMode.MARKDOWN
    )


@run_async
def rm_pic(bot, update, args=None):
    logging.debug("%s %s" % (bot, update))
    chat_id, chat_type, user_id, text, message = extract_update_info(update)

    if args is None or len(args)!=1 or len(args[0])!=36:
        return
        
    with open('/var/local/profdumbledore/json/tablas.json') as f:
        data = json.load(f)

    for k in data["tablas"]:
        if k["id"] == args[0]:
            data["tablas"].remove(k)
            break

    with open('/var/local/profdumbledore/json/tablas.json', 'w') as outfile:  
        json.dump(data, outfile)

    reload_tablas()

    output = "Tabla eliminada."
    bot.sendMessage(
        chat_id=chat_id,
        text=output,
        parse_mode=telegram.ParseMode.MARKDOWN
    )


@run_async
def inline_tablas(bot, update):
    logging.debug("%s %s" % (bot, update))
    query = update.inline_query.query
    max_range = 25
    results = []

    if len(__TABLAS_JSON["tablas"]) < 25:
        max_range = len(__TABLAS_JSON["tablas"])

    if len(query)>2:
        count = 0
        for i in __TABLAS_JSON["tablas"]:
            if re.search(query.lower(), i["name"].lower()):
                count = count + 1
                results.append(
                    InlineQueryResultCachedPhoto(
                    id=uuid4(),
                    photo_file_id=i["file_id"],
                    title=i["name"],
                    caption="@ProfesorDumbledoreBot {}".format(i["name"]))
                )

            if count == max_range:
                update.inline_query.answer(results=results, cache_time=0)
                return

        for i in __TABLAS_JSON["tablas"]:
            count = count + 1
            in_keywords = False
            for k in i["keywords"]:
                if re.search(query.lower(), k.lower()):
                    results.append(
                        InlineQueryResultCachedPhoto(
                        id=uuid4(),
                        photo_file_id=i["file_id"],
                        title=i["name"],
                        caption="@ProfesorDumbledoreBot {}".format(i["name"]))
                    )
                    break

        update.inline_query.answer(results=results, cache_time=0)

    else:
        for i in range(max_range):
            results.append(InlineQueryResultCachedPhoto(
                id=uuid4(),
                photo_file_id=__TABLAS_JSON["tablas"][i]["file_id"],
                title=__TABLAS_JSON["tablas"][i]["name"],
                caption="@ProfesorDumbledoreBot {}".format(__TABLAS_JSON["tablas"][i]["name"])))

        update.inline_query.answer(results=results, cache_time=0)


def tablas_btn(bot, update):
    logging.debug("%s %s" % (bot, update))

    query = update.callback_query
    data = query.data
    chat_id = query.message.chat.id
    config = get_config()
    news_id = int(config["telegram"]["news_id"])
    message_id = query.message.message_id
    
    match_new = re.match(r"tabla_new_(.*)", query.data)
    if match_new:
        text = "Ha sido añadida la tabla {0} a nuestros archivos. Solicítala ya mediante `@ProfesorDumbledoreBot {0}`\n\n¡Suerte en tu busqueda mago!".format(match_new.group(1))
        bot.sendMessage(
            chat_id=news_id,
            text=text,
            parse_mode=telegram.ParseMode.MARKDOWN)

    match_edit = re.match(r"tabla_edit_(.*)", query.data)
    if match_new is None and match_edit:
        text = "Ha sido modificada la tabla {0}. Recuerda que puedes solicitarla mediante `@ProfesorDumbledoreBot {0}`\n\n¡Suerte en tu busqueda mago!".format(match_edit.group(1))
        bot.sendMessage(
            chat_id=news_id,
            text=text,
            parse_mode=telegram.ParseMode.MARKDOWN)

    bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=None
    )
    return


def reload_tablas():
    global __TABLAS_JSON

    with open('/var/local/profdumbledore/json/tablas.json') as f:
        __TABLAS_JSON = json.load(f)

