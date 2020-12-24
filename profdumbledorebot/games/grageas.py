import re
import json
from random import randrange, randint, shuffle, choice

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext.dispatcher import run_async

import profdumbledorebot.supportmethods as support
from profdumbledorebot.admin import last_run
from profdumbledorebot.sql.support import are_banned
from profdumbledorebot.sql.user import get_user, update_user_points, is_staff
from profdumbledorebot.sql.group import group_message_counter, update_group_points
import profdumbledorebot.config as config

@run_async
def grag_btn(bot, update, game_data):
    query = update.callback_query
    data = query.data
    user = update.effective_user
    username = query.from_user.username
    user_id = query.from_user.id
    texto = query.message.text
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    message = query.message

    user = get_user(user_id)
    if user is None:
        return

    if username is None:
        bot.answer_callback_query(query.id, "Necesitas una @ para poder usar el bot.", show_alert=True)
        return

    if texto.find(username) != -1:
        bot.answer_callback_query(query.id, "Ya has cogido una, deja algo al resto del grupo.", show_alert=True)
        return

    listaPalabras = game_data.split("_")
    
    escogido = listaPalabras[0]
    sel1 = listaPalabras[1]
    sel2 = listaPalabras[2]
    sel3 = listaPalabras[3]
    sel4 = listaPalabras[4]
    sel5 = listaPalabras[5]
    
    #user_lang = get_lang(chat_id)
    user_lang = "es_ES"
    flavors = grageas_json[user_lang]["sabores"]
    flavor = randint(0, len(flavors)-1)
    
    texto = texto + "\n @" + username + " ha escogido la gragea " + escogido + " y sabía a... ¡" + flavors[flavor] + "!"
    
    b1 = "g*gra_" + sel1 + "_" + sel1 + "_" + sel2 + "_" + sel3 + "_" + sel4 + "_" + sel5 
    b2 = "g*gra_" + sel2 + "_" + sel1 + "_" + sel2 + "_" + sel3 + "_" + sel4 + "_" + sel5 
    b3 = "g*gra_" + sel3 + "_" + sel1 + "_" + sel2 + "_" + sel3 + "_" + sel4 + "_" + sel5 
    b4 = "g*gra_" + sel4 + "_" + sel1 + "_" + sel2 + "_" + sel3 + "_" + sel4 + "_" + sel5 
    b5 = "g*gra_" + sel5 + "_" + sel1 + "_" + sel2 + "_" + sel3 + "_" + sel4 + "_" + sel5 

    markup = []
    
    if texto.find(sel1)== -1:
        markup.append([InlineKeyboardButton(text=sel1, callback_data=b1)])
    if texto.find(sel2)== -1:
        markup.append([InlineKeyboardButton(text=sel2, callback_data=b2)])
    if texto.find(sel3)== -1:
        markup.append([InlineKeyboardButton(text=sel3, callback_data=b3)])
    if texto.find(sel4)== -1:
        markup.append([InlineKeyboardButton(text=sel4, callback_data=b4)])
    if texto.find(sel5)== -1:
        markup.append([InlineKeyboardButton(text=sel5, callback_data=b5)])

    update_user_points(user_id, 1)

    bot.edit_message_text(
    text=texto,
    chat_id=chat_id,
    message_id=message_id,
    reply_markup=InlineKeyboardMarkup(markup))

with open('/var/local/profdumbledore/json/grageas.json') as f:
    grageas_json = json.load(f)

@run_async
def grag_cmd(bot, update):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)

    colours = []
    for k in range(5):
        colour = get_gragea_colour(colours)
        colours.append(colour)

    sel1 = colours[0]
    sel2 = colours[1]
    sel3 = colours[2]
    sel4 = colours[3]
    sel5 = colours[4]

    b1 = "g*gra_" + sel1 + "_" + sel1 + "_" + sel2 + "_" + sel3 + "_" + sel4 + "_" + sel5
    b2 = "g*gra_" + sel2 + "_" + sel1 + "_" + sel2 + "_" + sel3 + "_" + sel4 + "_" + sel5
    b3 = "g*gra_" + sel3 + "_" + sel1 + "_" + sel2 + "_" + sel3 + "_" + sel4 + "_" + sel5
    b4 = "g*gra_" + sel4 + "_" + sel1 + "_" + sel2 + "_" + sel3 + "_" + sel4 + "_" + sel5
    b5 = "g*gra_" + sel5 + "_" + sel1 + "_" + sel2 + "_" + sel3 + "_" + sel4 + "_" + sel5

    texto = "Alguien ha abierto una bolsa de grageas de todos los sabores. ¿Quieres una?"

    markup = [
	[InlineKeyboardButton(text=sel1, callback_data=b1)],
    [InlineKeyboardButton(text=sel2, callback_data=b2)],
    [InlineKeyboardButton(text=sel3, callback_data=b3)],
    [InlineKeyboardButton(text=sel4, callback_data=b4)],
    [InlineKeyboardButton(text=sel5, callback_data=b5)]]

    bot.sendMessage(
	    chat_id=chat_id, 
	    text=texto, 
	    disable_notification=True, 
	    reply_markup=InlineKeyboardMarkup(markup))

def get_gragea_colour(items_list):
       #user_lang = get_lang(chat_id)
       user_lang = "es_ES"
       
       colours = grageas_json[user_lang]["colores"]
       colour = randint(0, len(colours)-1)
       if colours[colour] not in items_list:
              return colours[colour]
       else:
              return get_gragea_colour(items_list)