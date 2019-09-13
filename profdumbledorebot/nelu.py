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
import time
import random
import json
from geopy.distance import great_circle
from datetime import datetime, timedelta, time, timezone
import pytz

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext.dispatcher import run_async

import profdumbledorebot.supportmethods as support
from profdumbledorebot.model import PortalType, Professions
from profdumbledorebot.sql.support import are_banned
from profdumbledorebot.sql.user import get_user, get_real_user, get_user_by_name
from profdumbledorebot.sql.usergroup import exists_user_group, set_user_group, join_group, message_counter
from profdumbledorebot.sql.group import get_poi_list, set_plant, get_plant_list, get_poi, delete_plant, get_group, get_plant
from profdumbledorebot.admin import last_run
from profdumbledorebot.games import grag_cmd, whosaid_cmd

with open('/var/local/profdumbledore/json/nelu.json') as file:
    nelu_json = json.load(file)

@run_async
def nelu_cmd(bot, update, job_queue):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)
    realchat = chat_id

    chat_id = 0
    nelu_id = 0
    a1_object = support.SendContext(chat_id, "60")
    a1time = datetime.now().replace(hour=21, minute=00, second=1)
    job_queue.run_once(
        support.callback_send, 
        a1time,
        context=a1_object
    )
    a1_object = support.SendContext(chat_id, "30")
    a1time = datetime.now().replace(hour=21, minute=30, second=1)
    
    job_queue.run_once(
        support.callback_send, 
        a1time,
        context=a1_object
    )
    a1_object = support.SendContext(chat_id, "15")
    a1time = datetime.now().replace(hour=21, minute=45, second=1)
    
    job_queue.run_once(
        support.callback_send, 
        a1time,
        context=a1_object
    )
    a1_object = support.SendContext(chat_id, "14")
    a1time = datetime.now().replace(hour=21, minute=46, second=1)
    
    job_queue.run_once(
        support.callback_send, 
        a1time,
        context=a1_object
    )
    a1_object = support.SendContext(chat_id, "13")
    a1time = datetime.now().replace(hour=21, minute=47, second=1)
    
    job_queue.run_once(
        support.callback_send, 
        a1time,
        context=a1_object
    )
    a1_object = support.SendContext(chat_id, "12")
    a1time = datetime.now().replace(hour=21, minute=48, second=1)
    
    job_queue.run_once(
        support.callback_send, 
        a1time,
        context=a1_object
    )
    a1_object = support.SendContext(chat_id, "11")
    a1time = datetime.now().replace(hour=21, minute=49, second=1)
    
    job_queue.run_once(
        support.callback_send, 
        a1time,
        context=a1_object
    )
    a1_object = support.SendContext(chat_id, "10")
    a1time = datetime.now().replace(hour=21, minute=50, second=1)
    
    job_queue.run_once(
        support.callback_send, 
        a1time,
        context=a1_object
    )
    a1_object = support.SendContext(chat_id, "9")
    a1time = datetime.now().replace(hour=21, minute=51, second=1)
    
    job_queue.run_once(
        support.callback_send, 
        a1time,
        context=a1_object
    )
    a1_object = support.SendContext(chat_id, "8")
    a1time = datetime.now().replace(hour=21, minute=52, second=1)
    
    job_queue.run_once(
        support.callback_send, 
        a1time,
        context=a1_object
    )
    a1_object = support.SendContext(chat_id, "7")
    a1time = datetime.now().replace(hour=21, minute=53, second=1)
    
    job_queue.run_once(
        support.callback_send, 
        a1time,
        context=a1_object
    )
    a1_object = support.SendContext(chat_id, "6")
    a1time = datetime.now().replace(hour=21, minute=54, second=1)
    
    job_queue.run_once(
        support.callback_send, 
        a1time,
        context=a1_object
    )
    a1_object = support.SendContext(chat_id, "5")
    a1time = datetime.now().replace(hour=21, minute=55, second=1)
    
    job_queue.run_once(
        support.callback_send, 
        a1time,
        context=a1_object
    )
    a1_object = support.SendContext(chat_id, "4")
    a1time = datetime.now().replace(hour=21, minute=56, second=1)
    
    job_queue.run_once(
        support.callback_send, 
        a1time,
        context=a1_object
    )
    a1_object = support.SendContext(chat_id, "3")
    a1time = datetime.now().replace(hour=21, minute=57, second=1)
    
    job_queue.run_once(
        support.callback_send, 
        a1time,
        context=a1_object
    )
    a1_object = support.SendContext(chat_id, "2")
    a1time = datetime.now().replace(hour=21, minute=58, second=1)
    
    job_queue.run_once(
        support.callback_send, 
        a1time,
        context=a1_object
    )
    a1_object = support.SendContext(chat_id, "1")
    a1time = datetime.now().replace(hour=21, minute=59, second=1)
    
    job_queue.run_once(
        support.callback_send, 
        a1time,
        context=a1_object
    )
    a1_object = support.SendContext(chat_id, "¡Muchas felicidades @nelulita! 🦉✉️ He mandado una lechuza con una carta para tí , ¿Por qué no le echas un vistazo cuando llegue?")
    a1time = datetime.now().replace(hour=22, minute=00, second=0, microsecond=250000)
    job_queue.run_once(
        support.callback_send, 
        a1time,
        context=a1_object
    )

    a1_object = support.SendContext(nelu_id, "🦉✉️ Bienvenida de nuevo a Hogwarts @nelulita, me gustaría que nos conociésemos en mi despacho al final del primer día de clases. \nNo olvide que Hagrid la está esperando en la estación. https://t.me/joinchat/H1N0wBeA28423yBKPKBGSA \n\n- Albus Dumbledore")
    a1time = datetime.now().replace(day=12, hour=5, minute=00, second=1)
    job_queue.run_once(
        support.callback_send, 
        a1time,
        context=a1_object
    )
    count = 0
    bot.send_message(
        chat_id=realchat,
        text=nelu_json[count]["frase"],
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=nelu_json[count]["button"], callback_data=f'nelu_{count}')]])
    )


def nelu_btn(bot, update):
    query = update.callback_query
    data = query.data
    user = update.effective_user
    username = query.from_user.username
    user_id = query.from_user.id
    text = query.message.text
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    message = query.message
    markdown_text = query.message.text_markdown_urled
    queryData = data.split("_")
    count = int(queryData[1])

    timejson = nelu_json[count]["time"]
    tz = pytz.timezone("Europe/Madrid")

    userTime = datetime.strptime(timejson, '%H:%M')
    userDatetime = datetime.now().replace(hour=userTime.hour, minute=userTime.minute, second=0)
    dateText = f"Podrás continuar la historia a las {userDatetime.hour}:{userDatetime.minute}."

    userAsLocal = tz.localize(userDatetime)
    userAsLocal = userAsLocal.astimezone(pytz.utc)
    
    if datetime.now(pytz.utc) < userAsLocal:
        bot.answer_callback_query(query.id, dateText, show_alert=True)
        return

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=text
    )
    if queryData[0] == "nelu":
        if count == 1 and chat_id == -1001413955692:
            count += 1
            bot.send_message(
            chat_id=chat_id,
            text=nelu_json[count]["frase"],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=nelu_json[count]["button"], url="")]])
            )
            count += 1
            bot.send_message(
            chat_id=-1001411652944,
            text="🏆 Copa de las Casas 🏆\n\n🥇 Gryffindor  - ❤️🦁 - 893247324 puntos\n\n🥈 Ravenclaw  - 💙🦅 - 194 puntos\n\n🥉 Hufflepuff- 💛🦡 - 166 puntos\n\n💩 Slytherin - 💚🐍 - 3 puntos"
            )
            bot.send_message(
            chat_id=-1001411652944,
            text=nelu_json[count]["frase"],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=nelu_json[count]["button"], callback_data=f'nelu_{count}')]])
            )
            return
        elif count == 3 and chat_id == -1001411652944:
            count += 1
            bot.send_message(
            chat_id=chat_id,
            text=nelu_json[count]["frase"],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=nelu_json[count]["button"], url="")]])
            )
            count += 1
            bot.send_message(
            chat_id=-1001262639687,
            text=nelu_json[count]["frase"],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=nelu_json[count]["button"], callback_data=f'nelu_{count}')]])
            )
            return
        elif count == 10 and chat_id == -1001262639687:
            count += 1
            bot.send_message(
            chat_id=chat_id,
            text=nelu_json[count]["frase"],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=nelu_json[count]["button"], url="")]])
            )
            count += 1
            bot.send_message(
            chat_id=-1001213109153,
            text=nelu_json[count]["frase"],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=nelu_json[count]["button"], callback_data=f'nelu_{count}')]])
            )
            return
        elif count == 18 and chat_id == -1001213109153:
            count += 1
            grag_cmd(bot, update)
            bot.send_message(
            chat_id=chat_id,
            text=nelu_json[count]["frase"],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=nelu_json[count]["button"], callback_data=f'nelu_{count}')]])
            )
            return
        elif count == 22 and chat_id == -1001213109153:
            count += 1
            bot.send_message(
            chat_id=chat_id,
            text=nelu_json[count]["frase"],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=nelu_json[count]["button"], url="")]])
            )
            bot.send_message(
            chat_id=chat_id,
            text=f"👌 Mago @{username} advertido correctamente! 1/3\nMotivo: Andar por los pasillos en horario de clases."
            )
            count += 1
            bot.send_message(
            chat_id=-1001452977399,
            text=nelu_json[count]["frase"],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=nelu_json[count]["button"], callback_data=f'nelu_{count}')]])
            )
            return
        elif count == 25 and chat_id == -1001452977399:
            count += 1
            bot.send_message(
            chat_id=chat_id,
            text=nelu_json[count]["frase"],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=nelu_json[count]["button"], url="")]])
            )
            count += 1
            bot.send_message(
            chat_id=-1001493284207,
            text=nelu_json[count]["frase"],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=nelu_json[count]["button"], callback_data=f'nelu_{count}')]])
            )
            return
        elif count == 29 and chat_id == -1001493284207:
            count += 1
            bot.send_message(
            chat_id=chat_id,
            text=nelu_json[count]["frase"],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=nelu_json[count]["button"], url="")]])
            )
            count += 1
            bot.send_message(
            chat_id=-1001270494406,
            text=nelu_json[count]["frase"],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=nelu_json[count]["button"], callback_data=f'nelu_{count}')]])
            )
            return
        elif count == 36 and chat_id == -1001270494406:
            count += 1
            bot.send_message(
            chat_id=chat_id,
            text=nelu_json[count]["frase"],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=nelu_json[count]["button"], url="")]])
            )
            count += 1
            bot.send_message(
            chat_id=-1001170330486,
            text=nelu_json[count]["frase"],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=nelu_json[count]["button"], callback_data=f'nelu_{count}')]])
            )
            return
        elif count == 44 and chat_id == -1001170330486:
            count += 1
            bot.send_message(
            chat_id=chat_id,
            text=nelu_json[count]["frase"],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=nelu_json[count]["button"], url="")]])
            )
            return
        elif count == 45:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text
            )
            return
        else:
            count += 1
            bot.send_message(
            chat_id=chat_id,
            text=nelu_json[count]["frase"],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=nelu_json[count]["button"], callback_data=f'nelu_{count}')]])
            )
            return