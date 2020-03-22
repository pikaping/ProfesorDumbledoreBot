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
def game_spawn_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)
    '''
    if not is_staff(user_id):
        return
    '''
    if args == None or len(args) == 0:
        return
    args = " ".join(args)

    games = {"grageas":grag_cmd, "quién dijo":whosaid_cmd}
    if games[args] != None:
        games[args](bot, update)

@run_async
def games_cmd(bot, update):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)

    if are_banned(user_id, chat_id):
        return

    group_message_counter(chat_id)

    cfg = config.get_config()
    if chat_id != int(cfg["telegram"]["spain_id"]):
        return
    user = get_user(user_id)
    if user is None:
        return

    if last_run(chat_id, 'games'):
        return

    if (group_message_counter(chat_id, read_only=True) is randrange(40, 70)) or (group_message_counter(chat_id, read_only=True) >= 70):
        group_message_counter(chat_id, reset=True)
        game_list = [grag_cmd, whosaid_cmd]
        choice(game_list)(bot, update)

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

    if re.match(r"^g\*gra_", data):
        if texto.find(username) != -1:
            bot.answer_callback_query(query.id, "Ya has cogido una, deja algo al resto del grupo.", show_alert=True)
            return

        listaPalabras = data.split("_")
        
        escogido = listaPalabras[1]
        sel1 = listaPalabras[2]
        sel2 = listaPalabras[3]
        sel3 = listaPalabras[4]
        sel4 = listaPalabras[5]
        sel5 = listaPalabras[6]
        
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
    elif re.match(r"g\*whosaid_", data):
        if texto.find(username) != -1:
            return

        ent = message.parse_entities(["mention"])
        if len(ent) > 0:
            bot.answer_callback_query(query.id, "Alguien ha respondido ya.", show_alert=True)
            return

        listaPalabras = data.split("_")

        if listaPalabras[1] == "success":
            update_user_points(user_id, 3)
            update_group_points(chat_id, 3)
            bot.edit_message_text(
                text=texto + "\n\n@" + username + " ha acertado!",
                chat_id=chat_id,
                message_id=message_id)
            return

        update_user_points(user_id, -1)
        bot.answer_callback_query(query.id, "Has fallado.", show_alert=True)
    elif re.match(r"g\*duel_", data):
        '''
        if texto.find(username) != -1:
            return
        '''

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

with open('/var/local/profdumbledore/json/grageas.json') as f:
    grageas_json = json.load(f)

with open('/var/local/profdumbledore/json/whosaid.json') as file:
    who_json = json.load(file)

@run_async
def grag_cmd(bot, update):
    try:
        chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    except:
        query = update.callback_query
        data = query.data
        user = update.effective_user
        username = query.from_user.username
        user_id = query.from_user.id
        texto = query.message.text
        chat_id = query.message.chat.id
        message_id = query.message.message_id
        message = query.message

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

@run_async
def whosaid_cmd(bot, update):
    try:
        chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    except:
        query = update.callback_query
        data = query.data
        user = update.effective_user
        username = query.from_user.username
        user_id = query.from_user.id
        text = query.message.text
        chat_id = query.message.chat.id
        message_id = query.message.message_id
        message = query.message

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