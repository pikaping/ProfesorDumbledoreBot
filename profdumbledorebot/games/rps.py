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
def rps_btn(bot, update, game_data):
    query = update.callback_query
    data = query.data
    user = update.effective_user
    username = query.from_user.username
    vs_id = query.from_user.id
    texto = query.message.text
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    message = query.message

    vs_user = get_user(vs_id)
    if vs_user is None:
        return

    if username is None:
        bot.answer_callback_query(query.id, "Necesitas una @ para poder usar este bot.", show_alert=True)
        return

    if texto.find(username) != -1:
        return

    ent = message.parse_entities(["mention"])
    if len(ent) > 1:
        bot.answer_callback_query(query.id, "Alguien ha respondido ya.", show_alert=True)
        return

    listaPalabras = game_data.split("_")

    if listaPalabras[0] == "ai":
        bot_choice = randint(0,2)
        if bot_choice == 0:
            #success
            update_user_points(vs_id, 1)
            bot.edit_message_text(
                text=texto + "\n\n¡@" + username + " ha ganado!",
                chat_id=chat_id,
                message_id=message_id)
            bot.answer_callback_query(query.id, "¡Has ganado!", show_alert=True)
        else:
            #hahayousuck
            update_user_points(vs_id, -1)
            bot.edit_message_text(
                text=texto + "\n\n¡@" + username + " ha perdido!",
                chat_id=chat_id,
                message_id=message_id)
            bot.answer_callback_query(query.id, "Has perdido.", show_alert=True)
        return
    elif listaPalabras[0] == "us":
        user_choice = listaPalabras[2]
        user_id = listaPalabras[3]
        other_user = get_user(user_id)
        vs_choice = listaPalabras[1]
        if vs_choice == "r": #rock
            if user_choice == "p":
                update_user_points(user_id, 1)
                update_user_points(vs_id, -1)
                bot.edit_message_text(
                    text=texto + "\n\n¡El papel de @" + other_user.username + " ha ganado a la piedra de @" + username + "!",
                    chat_id=chat_id,
                    message_id=message_id) #PEKO PEKO PEKO PEKO
                bot.answer_callback_query(query.id, "¡Has perdido!", show_alert=True) #MIKO MIKO MIKO MIKO
            elif user_choice == "s":
                update_user_points(vs_id, 1)
                update_user_points(user_id, -1)
                bot.edit_message_text(
                    text=texto + "\n\n¡La piedra de @" + username + " ha ganado a las tijeras de @" + other_user.username + "!",
                    chat_id=chat_id,
                    message_id=message_id) #PEKO PEKO PEKO PEKO
                bot.answer_callback_query(query.id, "¡Has ganado!", show_alert=True) #MIKO MIKO MIKO MIKO
            elif user_choice == "r":
                bot.edit_message_text(
                    text=texto + "\n\n¡@" + username + " y @" + other_user.username + " han elegido piedra! ¡Empate!",
                    chat_id=chat_id,
                    message_id=message_id) #PEKO PEKO PEKO PEKO
                bot.answer_callback_query(query.id, "¡Has empatado!", show_alert=True) #MIKO MIKO MIKO MIKO

        elif vs_choice == "p": #paper
            if user_choice == "p":
                bot.edit_message_text(
                    text=texto + "\n\n¡@" + username + " y @" + other_user.username + " han elegido papel! ¡Empate!",
                    chat_id=chat_id,
                    message_id=message_id) #PEKO PEKO PEKO PEKO
                bot.answer_callback_query(query.id, "¡Has empatado!", show_alert=True) #MIKO MIKO MIKO MIKO
            elif user_choice == "s":
                update_user_points(user_id, 1)
                update_user_points(vs_id, -1)
                bot.edit_message_text(
                    text=texto + "\n\n¡Las tijeras de @" + other_user.username + " ha ganado al papel de @" + username + "!",
                    chat_id=chat_id,
                    message_id=message_id) #PEKO PEKO PEKO PEKO
                bot.answer_callback_query(query.id, "¡Has perdido!", show_alert=True) #MIKO MIKO MIKO MIKO
            elif user_choice == "r":
                update_user_points(vs_id, 1)
                update_user_points(user_id, -1)
                bot.edit_message_text(
                    text=texto + "\n\n¡El papel de @" + username + " ha ganado a la piedra de @" + other_user.username + "!",
                    chat_id=chat_id,
                    message_id=message_id) #PEKO PEKO PEKO PEKO
                bot.answer_callback_query(query.id, "¡Has ganado!", show_alert=True) #MIKO MIKO MIKO MIKO

        elif vs_choice == "s": #scissors
            if user_choice == "p":
                update_user_points(vs_id, 1)
                update_user_points(user_id, -1)
                bot.edit_message_text(
                    text=texto + "\n\n¡Las tijeras de @" + username + " han ganado al papel de @" + other_user.username + "!",
                    chat_id=chat_id,
                    message_id=message_id) #PEKO PEKO PEKO PEKO
                bot.answer_callback_query(query.id, "¡Has ganado!", show_alert=True) #MIKO MIKO MIKO MIKO
            elif user_choice == "s":
                bot.edit_message_text(
                    text=texto + "\n\n¡@" + username + " y @" + other_user.username + " han elegido piedra! ¡Empate!",
                    chat_id=chat_id,
                    message_id=message_id) #PEKO PEKO PEKO PEKO
                bot.answer_callback_query(query.id, "¡Has empatado!", show_alert=True) #MIKO MIKO MIKO MIKO
            elif user_choice == "r":
                update_user_points(user_id, 1)
                update_user_points(vs_id, -1)
                bot.edit_message_text(
                    text=texto + "\n\n¡La piedra de @" + other_user.username + " ha ganado a las tijeras de @" + username + "!",
                    chat_id=chat_id,
                    message_id=message_id) #PEKO PEKO PEKO PEKO
                bot.answer_callback_query(query.id, "¡Has perdido!", show_alert=True) #MIKO MIKO MIKO MIKO
        return

@run_async
def rps_ai_cmd(bot, update):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    b1 = "g*rps_ai_r"
    b2 = "g*rps_ai_p"
    b3 = "g*rps_ai_s"

    markup = [
	[InlineKeyboardButton(text="Piedra", callback_data=b1)],
    [InlineKeyboardButton(text="Papel", callback_data=b2)],
    [InlineKeyboardButton(text="Tijera", callback_data=b3)]]

    bot.sendMessage(
	    chat_id=chat_id, 
	    text='¡@ProfesorDumbledoreBot te desafia a Piedra, Papel o Tijera! \n ¿Qué eliges?', 
	    disable_notification=True, 
	    reply_markup=InlineKeyboardMarkup(markup))

@run_async
def rps_user_cmd(bot, update, job_queue, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    username = update.effective_user.username
    support.delete_message(chat_id, message.message_id, bot)

    if update.effective_user.username is None:
        return

    if args is not None and len(args) > 0:
        if message.reply_to_message is not None:
            vs_user = message.reply_to_message.from_user
            if vs_user.username is None:
                sent = bot.sendMessage(
                    chat_id=chat_id, 
                    text='Ese usuario no tiene una @.', 
                    disable_notification=True)
                delete_object = support.DeleteContext(chat_id, sent.message_id)
                job_queue.run_once(
                    support.callback_delete, 
                    10,
                    context=delete_object)
                return
            if args[0].lower() == "piedra":
                b1 = "g*rps_us_r_r_" + user_id
                b2 = "g*rps_us_p_r_" + user_id
                b3 = "g*rps_us_s_r_" + user_id
            elif args[0].lower() == "papel":
                b1 = "g*rps_us_r_p_" + user_id
                b2 = "g*rps_us_p_p_" + user_id
                b3 = "g*rps_us_s_p_" + user_id
            elif args[0].lower() == "tijera":
                b1 = "g*rps_us_r_s_" + user_id
                b2 = "g*rps_us_p_s_" + user_id
                b3 = "g*rps_us_s_s_" + user_id
            else:
                sent = bot.sendMessage(
                    chat_id=chat_id, 
                    text='No has escrito una de las opciones posibles (piedra, papel, tijera).', 
                    disable_notification=True)
                delete_object = support.DeleteContext(chat_id, sent.message_id)
                job_queue.run_once(
                    support.callback_delete, 
                    10,
                    context=delete_object)
                return

            markup = [
            [InlineKeyboardButton(text="Piedra", callback_data=b1)],
            [InlineKeyboardButton(text="Papel", callback_data=b2)],
            [InlineKeyboardButton(text="Tijera", callback_data=b3)]]

            bot.sendMessage(
                chat_id=chat_id, 
                text='¡@' + username + ' ha retado a @' + vs_user.username + ' a Piedra, Papel o Tijera! \n ¿Qué eliges?', 
                disable_notification=True, 
                reply_markup=InlineKeyboardMarkup(markup))
        else:
            bot.sendMessage(
                chat_id=chat_id, 
                text='Tienes que responder al mensaje de otro usuario para poder retarlo.', 
                disable_notification=True)
    else:
        bot.sendMessage(
            chat_id=chat_id, 
            text='No has escrito una de las opciones posibles (piedra, papel, tijera).', 
            disable_notification=True)