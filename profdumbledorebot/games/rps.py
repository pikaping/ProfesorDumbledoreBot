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

    listaPalabras = game_data.split("_")
    
    user_choice = listaPalabras[2]
    user_id = listaPalabras[3]
    other_user = get_user(user_id)
    vs_choice = listaPalabras[1]

    ent = message.parse_entities(["mention"])
    if listaPalabras[0] == "ai":
        if texto.find(username) != -1:
            return
        if len(ent) > 1:
            bot.answer_callback_query(query.id, "Alguien ha respondido ya.", show_alert=True)
            return
    elif listaPalabras[0] == "us":
        if texto.find(username) == -1:
            return
        if len(ent) > 2:
            bot.answer_callback_query(query.id, "Alguien ha respondido ya.", show_alert=True)
            return
        if list(ent.values())[0].lower() == "@" + username.lower():
            bot.answer_callback_query(query.id, "Espera a que tu contrincante elija.", show_alert=True)
            return

    if vs_choice == "r": #rock
        if user_choice == "p":
            update_user_points(user_id, 1)
            update_user_points(vs_id, -1)
            bot.edit_message_text(
                text=texto + "\n\n¡El papel de @" + other_user.alias + " ha ganado a la piedra de @" + username + "!",
                chat_id=chat_id,
                message_id=message_id) #PEKO PEKO PEKO PEKO
            bot.answer_callback_query(query.id, "¡Has perdido!", show_alert=True) #MIKO MIKO MIKO MIKO
        elif user_choice == "s":
            update_user_points(vs_id, 1)
            update_user_points(user_id, -1)
            bot.edit_message_text(
                text=texto + "\n\n¡La piedra de @" + username + " ha ganado a las tijeras de @" + other_user.alias + "!",
                chat_id=chat_id,
                message_id=message_id) #PEKO PEKO PEKO PEKO
            bot.answer_callback_query(query.id, "¡Has ganado!", show_alert=True) #MIKO MIKO MIKO MIKO
        elif user_choice == "r":
            bot.edit_message_text(
                text=texto + "\n\n¡@" + username + " y @" + other_user.alias + " han elegido piedra! ¡Empate!",
                chat_id=chat_id,
                message_id=message_id) #PEKO PEKO PEKO PEKO
            bot.answer_callback_query(query.id, "¡Has empatado!", show_alert=True) #MIKO MIKO MIKO MIKO

    elif vs_choice == "p": #paper
        if user_choice == "p":
            bot.edit_message_text(
                text=texto + "\n\n¡@" + username + " y @" + other_user.alias + " han elegido papel! ¡Empate!",
                chat_id=chat_id,
                message_id=message_id) #PEKO PEKO PEKO PEKO
            bot.answer_callback_query(query.id, "¡Has empatado!", show_alert=True) #MIKO MIKO MIKO MIKO
        elif user_choice == "s":
            update_user_points(user_id, 1)
            update_user_points(vs_id, -1)
            bot.edit_message_text(
                text=texto + "\n\n¡Las tijeras de @" + other_user.alias + " han ganado al papel de @" + username + "!",
                chat_id=chat_id,
                message_id=message_id) #PEKO PEKO PEKO PEKO
            bot.answer_callback_query(query.id, "¡Has perdido!", show_alert=True) #MIKO MIKO MIKO MIKO
        elif user_choice == "r":
            update_user_points(vs_id, 1)
            update_user_points(user_id, -1)
            bot.edit_message_text(
                text=texto + "\n\n¡El papel de @" + username + " ha ganado a la piedra de @" + other_user.alias + "!",
                chat_id=chat_id,
                message_id=message_id) #PEKO PEKO PEKO PEKO
            bot.answer_callback_query(query.id, "¡Has ganado!", show_alert=True) #MIKO MIKO MIKO MIKO

    elif vs_choice == "s": #scissors
        if user_choice == "p":
            update_user_points(vs_id, 1)
            update_user_points(user_id, -1)
            bot.edit_message_text(
                text=texto + "\n\n¡Las tijeras de @" + username + " han ganado al papel de @" + other_user.alias + "!",
                chat_id=chat_id,
                message_id=message_id) #PEKO PEKO PEKO PEKO
            bot.answer_callback_query(query.id, "¡Has ganado!", show_alert=True) #MIKO MIKO MIKO MIKO
        elif user_choice == "s":
            bot.edit_message_text(
                text=texto + "\n\n¡@" + username + " y @" + other_user.alias + " han elegido piedra! ¡Empate!",
                chat_id=chat_id,
                message_id=message_id) #PEKO PEKO PEKO PEKO
            bot.answer_callback_query(query.id, "¡Has empatado!", show_alert=True) #MIKO MIKO MIKO MIKO
        elif user_choice == "r":
            update_user_points(user_id, 1)
            update_user_points(vs_id, -1)
            bot.edit_message_text(
                text=texto + "\n\n¡La piedra de @" + other_user.alias + " ha ganado a las tijeras de @" + username + "!",
                chat_id=chat_id,
                message_id=message_id) #PEKO PEKO PEKO PEKO
            bot.answer_callback_query(query.id, "¡Has perdido!", show_alert=True) #MIKO MIKO MIKO MIKO
    return

@run_async
def rps_ai_cmd(bot, update):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    choices = ["r", "p", "s"]

    b1 = "g*rps_ai_r_" + choices[randint(0,2)] + "_" + str(bot.id)
    b2 = "g*rps_ai_p_" + choices[randint(0,2)] + "_" + str(bot.id)
    b3 = "g*rps_ai_s_" + choices[randint(0,2)] + "_" + str(bot.id)

    markup = [
	[InlineKeyboardButton(text="Piedra", callback_data=b1)],
    [InlineKeyboardButton(text="Papel", callback_data=b2)],
    [InlineKeyboardButton(text="Tijera", callback_data=b3)]]

    bot.sendMessage(
	    chat_id=chat_id, 
	    text='@ProfesorDumbledoreBot te desafía a Piedra, Papel o Tijera! \n ¿Qué eliges?', 
	    disable_notification=True, 
	    reply_markup=InlineKeyboardMarkup(markup))

@run_async
def rps_user_cmd(bot, update, job_queue, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    username = update.effective_user.username
    support.delete_message(chat_id, message.message_id, bot)

    if update.effective_user.username is None:
        return
    
    if not is_staff(user_id):
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
            if vs_user.id == user_id:
                bot.sendMessage(
                    chat_id=chat_id, 
                    text='Necesitas a alguien más para jugar.', 
                    disable_notification=True)
                return
            if vs_user.is_bot == True:
                bot.sendMessage(
                    chat_id=chat_id, 
                    text='No puedes jugar contra un bot.', 
                    disable_notification=True)
                return
            if args[0].lower() == "piedra":
                b1 = "g*rps_us_r_r_" + str(user_id)
                b2 = "g*rps_us_p_r_" + str(user_id)
                b3 = "g*rps_us_s_r_" + str(user_id)
            elif args[0].lower() == "papel":
                b1 = "g*rps_us_r_p_" + str(user_id)
                b2 = "g*rps_us_p_p_" + str(user_id)
                b3 = "g*rps_us_s_p_" + str(user_id)
            elif args[0].lower() == "tijera":
                b1 = "g*rps_us_r_s_" + str(user_id)
                b2 = "g*rps_us_p_s_" + str(user_id)
                b3 = "g*rps_us_s_s_" + str(user_id)
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
                text='@' + username + ' ha retado a @' + vs_user.username + ' a Piedra, Papel o Tijera! \n ¿Qué eliges?', 
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