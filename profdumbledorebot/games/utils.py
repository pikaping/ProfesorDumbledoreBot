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

from profdumbledorebot.games import grageas, whosaid, rps

@run_async
def btn_parser(bot, update):
    query = update.callback_query
    data = query.data
    user = update.effective_user
    username = query.from_user.username
    user_id = query.from_user.id
    texto = query.message.text
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    message = query.message

    if are_banned(user_id, chat_id):
        return

    user = get_user(user_id)
    if user is None:
        return

    game = data[2:].split("_")[0]
    game_data = data[2:].split("_")[1:]
    game_data = "_".join(game_data)
    if game == "gra":
        grageas.grag_btn(bot, update, game_data)
    if game == "whosaid":
        whosaid.whosaid_btn(bot, update, game_data)
    if game == "rps":
        rps.rps_btn(bot, update, game_data)

@run_async
def game_spawn_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)
    
    if not is_staff(user_id):
        return
    
    games = {"grageas":grageas.grag_cmd, "quién dijo":whosaid.whosaid_cmd, "rps":rps.rps_ai_cmd}
    
    if args == None or len(args) == 0:
        game_list = games.keys()
        game_list = '\n'.join(game_list)
        bot.sendMessage(
            chat_id=chat_id, 
            text='Estos son los juegos disponibles:\n' + game_list, 
            disable_notification=True)
        return
    args = " ".join(args)
    
    if games[args] != None:
        games[args](bot, update)

@run_async
def game_selection(bot, update):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)

    if are_banned(user_id, chat_id):
        return

    group_message_counter(chat_id)

    cfg = config.get_config()
    if chat_id != int(cfg["telegram"]["spain_id"]) and chat_id != int(cfg["telegram"]["comedor_id"]) and chat_id != int(cfg["telegram"]["raven_id"]) and chat_id != int(cfg["telegram"]["huff_id"]) and chat_id != int(cfg["telegram"]["gryff_id"]) and chat_id != int(cfg["telegram"]["sly_id"]):
        return
    user = get_user(user_id)
    if user is None:
        return

    if last_run(chat_id, 'games'):
        return

    if (group_message_counter(chat_id, read_only=True) is randrange(40, 70)) or (group_message_counter(chat_id, read_only=True) >= 70):
        group_message_counter(chat_id, reset=True)
        game_list = [grageas.grag_cmd, whosaid.whosaid_cmd]
        choice(game_list)(bot, update)

# got 5€ from doing this, god i love my work
@run_async
def potato_process(bot, update):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    
    if (chat_type == "private"):
        bot.sendMessage(
                chat_id=chat_id, 
                text='🥔')



''' broken af, better rewrite than fix

@run_async
def duel_cmd(bot, update):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)
    user_username = message.from_user.username

    if are_banned(user_id, chat_id):
        return
    user = get_user(user_id)
    if user is None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Debes registrarte para usar este comando.",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return
    try:
        if user_username is None:
            bot.sendMessage(
                chat_id=chat_id,
                text="❌ Es necesario que configures un alias en Telegram antes de continuar usando el bot.",
                parse_mode=telegram.ParseMode.MARKDOWN
            )
            return
    except:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Es necesario que configures un alias en Telegram antes de continuar usando el bot.",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return

    text = f"@{message.from_user.username} Vs ???\n\n¿Quién aceptará el duelo?"
    markup = [[InlineKeyboardButton(text="Aceptar el duelo", callback_data=f"g*duel_accept_{user_id}")]]

    bot.sendMessage(
	    chat_id=chat_id, 
	    text=text, 
	    disable_notification=True, 
	    reply_markup=InlineKeyboardMarkup(markup))

@run_async
def btn(bot, update):
    query = update.callback_query
    data = query.data
    user = update.effective_user
    username = query.from_user.username
    user_id = query.from_user.id
    texto = query.message.text
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    message = query.message

    if are_banned(user_id, chat_id):
        return

    user = get_user(user_id)
    if user is None:
        return

    if re.match(r"g\*duel_", data):
        
        if texto.find(username) != -1:
            return
        

        listaPalabras = data.split("_")

        if listaPalabras[1] == "accept":
            if listaPalabras[2] == user_id:
                bot.answer_callback_query(query.id, "Busca a alguien con quien pelear.", show_alert=True)
                return

            ent = message.parse_entities(["mention"])
            for mention in ent:
                userCreated = message.parse_entity(mention)

                replace = f"Hechizos {userCreated}: 0\nHechizos @{username}: 0\n\n ¡Empieza el duelo!"

                re1 = re.sub(r"(¿Quién aceptará el duelo\?)", replace, texto)
                re2 = re.sub(r"(\?\?\?)", f"@{username}", re1)

                buttons = [
                    [InlineKeyboardButton(text="Atacar", callback_data=f"g*duel_attack_0_0_{listaPalabras[2]}_{user_id}")],
                    [InlineKeyboardButton(text="Defender", callback_data=f"g*duel_defend_0_0_{listaPalabras[2]}_{user_id}")],
                    [InlineKeyboardButton(text="Pensar", callback_data=f"g*duel_think_0_0_{listaPalabras[2]}_{user_id}")]]

                bot.edit_message_text(
                    text=re2,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=InlineKeyboardMarkup(buttons))
                return
        elif listaPalabras[1] == "attack":
            createdUser = listaPalabras[4]
            otherUser = listaPalabras[5]
            user1magic = listaPalabras[2]
            user2magic = listaPalabras[3]
            
            ent = message.parse_entities(["mention"])
            duelUsers = {}
            count = 0
            for mention in ent:
                user = message.parse_entity(mention)
                if count == 0:
                    duelUsers[createdUser] = user
                    count += 1
                elif count == 1:
                    duelUsers[otherUser] = user
                    count += 1
            
            if user_id == int(createdUser) and int(user1magic) == 0:
                bot.answer_callback_query(query.id, "Antes de atacar debes pensar.", show_alert=True)
                return
            elif user_id == int(otherUser) and int(user2magic) == 0:
                bot.answer_callback_query(query.id, "Antes de atacar debes pensar.", show_alert=True)
                return

            replace = f"Hechizos {userCreated}: 0\nHechizos @{username}: 0\n\n ¡Empieza el duelo!"

            re1 = re.sub(r"(¿Quién aceptará el duelo\?)", replace, texto)
            re2 = re.sub(r"(\?\?\?)", f"@{username}", re1)

            buttons = [
                [InlineKeyboardButton(text="Atacar", callback_data=f"g*duel_attack_0_0_{listaPalabras[2]}_{user_id}")],
                [InlineKeyboardButton(text="Defender", callback_data=f"g*duel_defend_0_0_{listaPalabras[2]}_{user_id}")],
                [InlineKeyboardButton(text="Pensar", callback_data=f"g*duel_think_0_0_{listaPalabras[2]}_{user_id}")]]

            bot.edit_message_text(
                text=re2,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=InlineKeyboardMarkup(buttons))
            return

        update_user_points(user_id, -1)
        update_group_points(chat_id, -1)
        bot.answer_callback_query(query.id, "Has fallado.", show_alert=True)
'''
