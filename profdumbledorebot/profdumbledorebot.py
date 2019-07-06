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

import os
import re
import sys
import logging
import telegram

from threading import Thread
from datetime import datetime
from nursejoybot.rules import send_rules
from nursejoybot.config import get_config
from telegram.ext.dispatcher import run_async
from nursejoybot.model import Team, ValidationType


@run_async
def start_cmd(bot, update, args=None):
    config = get_config()
    chat_id, chat_type, user_id, text, message = extract_update_info(update)
    delete_message(chat_id, message.message_id, bot)

    if are_banned(user_id, chat_id):
        return

    if chat_type == "private" and args is not None and len(args)!=0:
        send_rules(bot, update, args[0])
        return

    if chat_type != "private":
        group = get_group_settings(chat_id)
        if group.reply_on_group:
            dest_id = chat_id
        else:
            dest_id = user_id
    else:
        dest_id = user_id

    sent_message = bot.sendMessage(
        chat_id=dest_id,
        text=(
            "📖 ¡Bienvenido al centro Pokémon de la Enfermera Joy! Tómate"
            " tu tiempo en leer <a href='%s'>la guía de entrenadores</a>.\n\n"
            "<b>Lee con detenimiento la </b><a href='%s'>politica de privacidad</a>"
            "<b> antes de registrarte.</b>\n\n"
            "💙💛❤️<b>Registrar nivel/equipo</b>\nEscríbeme por privado en @%s el "
            "comando <code>/register</code>. En vez de eso, puedes preguntar "
            "<code>/profile</code> a @detectivepikachubot y reenviarme su "
            "respuesta.\n\n🔔 <b>Subida de nivel</b>\nPara subir de nivel,"
            " unicamente debes enviarme una captura de pantalla de tu perfil"
            " de Pokémon GO por privado y yo haré el resto.\n\n" % (
                config["telegram"]["bothelp"],
                config["telegram"]["botrgpd"],
                config["telegram"]["botalias"])
        ),
        parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True)

    if chat_type != "private" and group.reply_on_group:
        Thread(target=delete_message_timed, args=(chat_id, sent_message.message_id, 40, bot)).start()


@run_async
def register_cmd(bot, update, args=None):
    chat_id, chat_type, user_id, text, message = extract_update_info(update)

    if are_banned(user_id, chat_id):
        return

    user = get_user(user_id)
    if user is None:
        set_user(user_id)
    elif user.validation is not ValidationType.NONE:
        #warning
        return

    text = 

    bot.sendMessage


@run_async
def ping_cmd(bot, update):
    logging.debug("nursejoybot:joyping: %s %s", bot, update)
    chat_id, chat_type, user_id, text, message = extract_update_info(update)

    sent_dt = message.date
    now_dt = datetime.now()
    timediff = now_dt - sent_dt

    if chat_type != "private":
        try:
            bot.deleteMessage(chat_id=chat_id, message_id=message.message_id)

        except Exception:
            pass

    if chat_type != "private":
        group = get_group_settings(chat_id)
        if group and group.reply_on_group:
            dest_id = chat_id
        else:
            dest_id = user_id
    else:
        dest_id = user_id

    sent_message = bot.sendMessage(
        chat_id=dest_id,
        text=(
            "¿Ves como no era para tanto el pinchazo? Fueron solo %d seg"
            "undos 🤗" % (timediff.seconds)
        ),
        parse_mode=telegram.ParseMode.HTML,
        disable_web_page_preview=True
    )

    if chat_type != "private" and group and group.reply_on_group:
        Thread(target=delete_message_timed,
               args=(chat_id, sent_message.message_id, 10, bot)).start()


@run_async
def whois_cmd(bot, update, args=None):
    logging.debug("%s %s %s", bot, update, args)
    chat_id, chat_type, user_id, text, message = extract_update_info(update)

    delete_message(chat_id, message.message_id, bot)

    if are_banned(user_id, chat_id):
        return

    match = REGWHOIS.match(text)

    logging.debug("Pass banned")
    if message.reply_to_message is not None:
        if message.reply_to_message.forward_from is not None:
            user = get_user(message.reply_to_message.forward_from.id)
            if user is not None:
                replied_id = user.id
        elif message.reply_to_message.from_user is not None:
            user = get_user(message.reply_to_message.from_user.id)
            if user is not None:
                replied_id = user.id
    elif args is not None and len(args)== 1:
        logging.debug("Getting user")
        user = get_user_by_name(args[0])
        if user is not None:
            replied_id = user.id
        logging.debug("User: %s", user)
    elif match:
        logging.debug("Getting user")
        user = get_user_by_name(match.group(2))
        if user is not None:
            replied_id = user.id
        logging.debug("User: %s", user)  
    else:
        return

    logging.debug("Pass get user")

    if user is None or user.level is 0:
        output = "❌ No tengo información sobre este entrenador."
        bot.sendMessage(
            chat_id=user_id,
            text=output,
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return

    if user.team is Team.NONE:
        text_team = "_Desconocido_"
    elif user.team is Team.BLUE:
        text_team = "del equipo *Sabiduría*"
    elif user.team is Team.RED:
        text_team = "del equipo *Valor*"
    elif user.team is Team.YELLOW:
        text_team = "del equipo *Instinto*"

    text_trainername = ("{}".format(user.trainer_name)
                        if user.trainer_name is not None
                        else "Desconocido")
    
    text_level = ("*{}*".format(user.level)
                  if user.level is not None
                  else "_Desconocido_")

    text_friend_id = ("Su ID de Entrenador: `{}`".format(user.friend_id)
                      if has_fc(user_id) and user.friend_id is not None
                      else "")

    text_ds_id = ("\nSu ID de N3DS: `{}`".format(user.ds_id)
                      if has_ds_fc(user_id) and user.ds_id is not None
                      else "")

    text_switch_id = ("\nSu ID de Nintendo Switch: `{}`".format(user.switch_id)
                      if has_switch_fc(user_id) and user.switch_id is not None
                      else "")

    if user.banned == 1:
        text_validationstatus = "⛔️"

    elif user.validation_type in [
            ValidationType.INTERNAL, ValidationType.PIKACHU, ValidationType.GOROCHU]:
        text_validationstatus = "✅"

    else:
        text_validationstatus = "⚠️"

    if user.admin == 1:
        text_admin = "👩‍⚕️"

    else:
        text_admin = ""

    flag_text = ("{}".format(user.flag)
                  if user.flag is not None
                  else " ")

    output = "[{0}](tg://user?id={1}), es {2} nivel {3} {4} {5} {7}\n{6}{8}{9}".format(
        text_trainername, 
        replied_id,
        text_team,
        text_level,
        text_validationstatus,
        text_admin,
        text_friend_id,
        flag_text,
        text_ds_id,
        text_switch_id
    )

    if chat_type != "private":
        group = get_group_settings(chat_id)
        if group.reply_on_group:
            dest_id = chat_id
        else:
            dest_id = user_id
    else:
        dest_id = user_id

    bot.sendMessage(
        chat_id=dest_id,
        text=output,
        parse_mode=telegram.ParseMode.MARKDOWN
    )


@run_async
def fclist_cmd(bot, update):
    chat_id, chat_type, user_id, text, message = extract_update_info(update)
    delete_message(chat_id, message.message_id, bot)

    if are_banned(user_id, chat_id) or chat_type == "private":
        return

    main = get_user(user_id)
    count = 0
    text = "**Listado de Friend Codes:**"

    if main is None or not main.fclists or main.friend_id is None:
        text = "❌ No cumples los requisitos para solicitar el listado."
        bot.sendMessage(
            chat_id=user_id,
            text=text,
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return

    users = get_users_from_group(chat_id)
    for user_data in users:
        try:
            data = bot.get_chat_member(chat_id, user_data.user_id)
        except:
            data = None
            pass
        if data is None or (data and data.status not in ['kicked','left'] and not data.user.is_bot):
            user = get_user(user_data.user_id)
            if user and not user.banned and user.friend_id and user.fclists:
                if user.team is Team.BLUE:
                    text_team = "💙"
                elif user.team is Team.RED:
                    text_team = "❤️"
                elif user.team is Team.YELLOW:
                    text_team = "💛"

                text = text + "\n{0}[{1}](tg://user?id={2}) `{3}`".format(
                    text_team,
                    user.trainer_name,
                    user.id,
                    user.friend_id
                )
                count += 1
                if count == 100:
                    bot.sendMessage(
                        chat_id=user_id,
                        text=text,
                        parse_mode=telegram.ParseMode.MARKDOWN
                    )
                    count = 0

    bot.sendMessage(
        chat_id=user_id,
        text=text,
        parse_mode=telegram.ParseMode.MARKDOWN
    )


@run_async
def set_friendid_cmd(bot, update, args=None):
    logging.debug("%s", update)
    chat_id, chat_type, user_id, text, message = extract_update_info(update)

    if are_banned(chat_id, user_id):
        return

    fc = None

    if len(args) == 3:
        fc = ''.join(args)

    elif len(args) == 1:
        fc = args[0]

    logging.debug("FC:%s",fc)
    user = get_user(user_id)

    if user is None:
        bot.sendMessage(
            chat_id=chat_id,
            text=(
                "❌ Esto… no encuentro tu Ficha de Entrenador.¿Qu"
                "ién eres? ¿Te has registrado conmigo? En caso "
                "afirmativo, pide ayuda en @enfermerajoyayuda. "
                "De no ser así, registrate antes de usar este comando"
            ),
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return

    if fc is None and user.friend_id is None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Vaya, no he reconocido ese ID de entrenador... "
        )
        return

    elif fc is None and user.friend_id is not None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ ID de entrenador eliminado correctamente"
        )
        set_fc(None, user_id)
        return

    friendcode = re.match(r'^[0-9]{12}$', fc)

    if friendcode is None and user.friend_id is None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Vaya, no he reconocido ese ID de entrenador... {}".format(fc)
        )
        return

    else:
        set_fc(fc, user_id)
        bot.sendMessage(
            chat_id=chat_id,
            text=(
                "👌 Ya he registrado tu ID de entrenador como ‘{}’. "
                "\n Disfruta ahora interactuando con tus compañeros "
                "de grupo, mandándo regalos e intercambiando Pokémon"
                " por todo el mundo. \n\n *Y recuerda, la suplantac"
                "ión de entrenadores es motivo de baneo*".format(fc)
            ),
            parse_mode=telegram.ParseMode.MARKDOWN
        )


@run_async
def profile_cmd(bot, update):
    logging.debug("%s", update)
    chat_id, chat_type, user_id, text, message = extract_update_info(update)

    if are_banned(chat_id, user_id):
        return

    user = get_user(user_id)

    if user is None or user.validation_type == ValidationType.NONE:
        bot.sendMessage(
            chat_id=chat_id,
            text=(
                "❌ Esto… no encuentro tu Ficha de Entrenador.¿Qu"
                "ién eres? ¿Te has registrado conmigo? En caso "
                "afirmativo, pide ayuda en @enfermerajoyayuda . "
                "De no ser así, registrate antes de usar este comando"
            ),
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return


    button_list = [
        #[InlineKeyboardButton(text="🤖 Bots", callback_data='privacity_bots_goo')],
        [InlineKeyboardButton(text="🗣 Menciones", callback_data='privacity_men_goo')],
        [InlineKeyboardButton(text="👥 Friend Code", callback_data='privacity_fc_goo')],
        [InlineKeyboardButton("Terminado", callback_data='privacity_')]
    ]
    reply_markup = InlineKeyboardMarkup(button_list)
    bot.send_message(
        chat_id=chat_id,
        text=(
            "¡Bienvenido al apartado de privacidad para tu cuenta en"
            " @NurseJoyBot. Selecciona una de las opciones para conti"
            "nuar.\n\n👥 Friend Code: Pulsa en el botón para activar"
            " o desactivar para cambiar tu configuración.\n"
            #"🤖 Bots: Pulsa en el nombre del bot para aceptar o rech"
            #"azar la transferencia de datos."
            ),
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )


@run_async
def profile_btn(bot, update):
    query = update.callback_query
    data = query.data
    user = update.effective_user
    user_id = query.from_user.id
    text = query.message.text
    chat_id = query.message.chat.id
    message_id = query.message.message_id

    if are_banned(user_id, chat_id):
        return

    if data == "privacity_":
        delete_message(chat_id, message_id, bot)
    
    match = REGPRIV.match(query.data)
    keyboard = []
    if match:
        check = match.group(1)
        option = match.group(2)        
    else:
        return

    if check == "fc":
        if option != "goo":
            update_fclist(user_id)
        user = get_user(user_id)
        if user.fclists:
            text = "✅ Listados de codigos"
        else:
            text = "❌ Listados de codigos"

        button_list = [
            [InlineKeyboardButton(text=text, callback_data='privacity_fc_togle')],
            [InlineKeyboardButton("« Menú principal", callback_data='privacity_back_xxx')]
        ]
        reply_markup = InlineKeyboardMarkup(button_list)

    elif check == "men":
        if option != "goo":
            if option == "ad":
                admin = True
            else:
                admin = False
            update_mentions(user_id, admin)

        user = get_user(user_id)
        if user.adm_alerts:
            text_admin = "✅ Menciones de @admin"
        else:
            text_admin = "◾️ Menciones de @admin"
        if user.usr_alerts:
            text_normal = "✅ Menciones de tu @usuario"
        else:
            text_normal = "◾️ Menciones de tu @usuario"
        button_list = [
            [InlineKeyboardButton(text=text_admin, callback_data='privacity_men_ad')],
            [InlineKeyboardButton(text=text_normal, callback_data='privacity_men_us')],
            [InlineKeyboardButton("« Menú principal", callback_data='privacity_back_xxx')]
        ]
        reply_markup = InlineKeyboardMarkup(button_list)

    elif check == "back":
        button_list = [
            #[InlineKeyboardButton(text="🤖 Bots", callback_data='privacity_bots_go')],
            [InlineKeyboardButton(text="🗣 Menciones", callback_data='privacity_men_goo')],
            [InlineKeyboardButton(text="👥 Friend Code", callback_data='privacity_fc_goo')],
            [InlineKeyboardButton("Terminado", callback_data='privacity_')]
        ]
        reply_markup = InlineKeyboardMarkup(button_list)

    bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=reply_markup
    )

