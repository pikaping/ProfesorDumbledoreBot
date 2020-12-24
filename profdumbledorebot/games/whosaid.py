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
def whosaid_btn(bot, update, game_data):
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
        return

    ent = message.parse_entities(["mention"])
    if len(ent) > 0:
        bot.answer_callback_query(query.id, "Alguien ha respondido ya.", show_alert=True)
        return

    listaPalabras = game_data.split("_")

    if listaPalabras[0] == "success":
        update_user_points(user_id, 3)
        update_group_points(chat_id, 3)
        bot.edit_message_text(
            text=texto + "\n\n@" + username + " ha acertado!",
            chat_id=chat_id,
            message_id=message_id)
        return

    update_user_points(user_id, -1)
    bot.answer_callback_query(query.id, "Has fallado.", show_alert=True)

with open('/var/local/profdumbledore/json/whosaid.json') as file:
    who_json = json.load(file)

@run_async
def whosaid_cmd(bot, update):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)

    question = randint(0, len(who_json)-1)	
    
    b1 = "g*whosaid_success"
    b2 = "g*whosaid_fail"
    b3 = "g*whosaid_fail"
    b4 = "g*whosaid_fail"

    markup = [
	[InlineKeyboardButton(text=who_json[question]["reply"], callback_data=b1)],
    [InlineKeyboardButton(text=who_json[question]["others"][0], callback_data=b2)],
    [InlineKeyboardButton(text=who_json[question]["others"][1], callback_data=b3)],
    [InlineKeyboardButton(text=who_json[question]["others"][2], callback_data=b4)]]

    shuffle(markup)
    bot.sendMessage(
	    chat_id=chat_id, 
	    text='Quién dijo...\n\n"' + who_json[question]["question"] + '"\n\n', 
	    disable_notification=True, 
	    reply_markup=InlineKeyboardMarkup(markup))