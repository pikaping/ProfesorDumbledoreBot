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
from datetime import datetime
import random

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext.dispatcher import run_async

import profdumbledorebot.sql.user as user_sql
import profdumbledorebot.supportmethods as support
from profdumbledorebot.config import get_config
from profdumbledorebot.model import Houses, Professions, PortalType
from profdumbledorebot.rules import send_rules
from profdumbledorebot.admin import last_run
from profdumbledorebot.sql.settings import get_group_settings
from profdumbledorebot.sql.support import are_banned
from profdumbledorebot.sql.usergroup import get_users_from_group
from profdumbledorebot.sql.group import create_poi, get_poi_list, delete_poi


@run_async
def start_cmd(bot, update, args=None):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if are_banned(user_id, chat_id):
        return

    if chat_type == "private" and args is not None and len(args)!=0:
        send_rules(bot, update, args[0])
        return

    config = get_config()

    if chat_type != "private":
        group = get_group_settings(chat_id)
        if group.reply_on_group:
            dest_id = chat_id
        else:
            dest_id = user_id
    else:
        dest_id = user_id

    output = "📖 Bienvenido al mundo mágico del profesor Dumbledore. Tómate tu tiempo en leer la guía para magos.\n\n💙💛❤️💚 Registrar pasaporte del Ministerio\nEscríbeme por privado la contraseña /cucuruchodecucarachas y responde a mis preguntas.\n\n🔔 Editar pasaporte del Ministerio."

    sent_message = bot.sendMessage(
        chat_id=dest_id,
        text=output,
        parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True)

    if chat_type != "private" and group.reply_on_group:
        delete_object = support.DeleteContext(chat_id, sent_message.message_id)
        job_queue.run_once(
            support.callback_delete, 
            40,
            context=delete_object
        )

@run_async
def register_cmd(bot, update, args=None):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    user_username = message.from_user.username

    if are_banned(user_id, chat_id):
        return

    try:
        if user_username is None:
            bot.sendMessage(
                chat_id=chat_id,
                text=(
                    "❌ Es necesario que configures un alias en Telegram antes de registrarte."
                ),
                parse_mode=telegram.ParseMode.MARKDOWN
            )
            return
    except:
        bot.sendMessage(
            chat_id=chat_id,
            text=(
                "❌ Es necesario que configures un alias en Telegram antes de registrarte."
            ),
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return

    user = user_sql.get_real_user(user_id)
    if user is None:
        user_sql.set_user(user_id)

    user_sql.commit_user(user_id, alias=user_username)

    text = "Son nuestras elecciones las que muestran lo que somos, mucho más que nuestras habilidades, así pues elige bien y dime, ¿Cuál es tu casa de Hogwarts?"
    button_list = [
            [InlineKeyboardButton("🦁 Gryffindor", callback_data='reg_hse_1')],
            [InlineKeyboardButton("🦡 Hufflepuff", callback_data='reg_hse_2')],
            [InlineKeyboardButton("🦅 Ravenclaw", callback_data='reg_hse_3')],
            [InlineKeyboardButton("🐍 Slytherin", callback_data='reg_hse_4')],
            [InlineKeyboardButton("🙈 Sin casa", callback_data='reg_hse_0')]]

    reply_markup = InlineKeyboardMarkup(button_list)
    bot.sendMessage(
        chat_id=chat_id,
        text=text,
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=reply_markup)


@run_async
def ping_cmd(bot, update):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)

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
        text=("Después de %d segundos... ¡Siempre!" % (timediff.seconds)),
        parse_mode=telegram.ParseMode.HTML,
        disable_web_page_preview=True
    )

    if chat_type != "private" and group.reply_on_group:
        delete_object = support.DeleteContext(chat_id, sent_message.message_id)
        job_queue.run_once(
            support.callback_delete, 
            10,
            context=delete_object
        )


@run_async
def whois_cmd(bot, update, args=None):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if are_banned(user_id, chat_id):
        return

    if message.reply_to_message is not None:
        if message.reply_to_message.forward_from is not None:
            user = user_sql.get_user(message.reply_to_message.forward_from.id)
            if user is not None:
                replied_id = user.id
        elif message.reply_to_message.from_user is not None:
            user = user_sql.get_user(message.reply_to_message.from_user.id)
            if user is not None:
                replied_id = user.id

    elif args is not None and len(args)== 1:
        args[0] = re.sub("@", "", args[0])
        user = user_sql.get_user_by_name(args[0])
        if user is not None:
            replied_id = user.id
        elif args[0].isdigit():
            user = user_sql.get_user(args[0])
            replied_id = user.id

    else:
        return

    if user is None:
        output = "❌ No tengo ningún registro sobre este mago."
        bot.sendMessage(
            chat_id=user_id,
            text=output,
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return

    text_friend_id = ("\nSu Clave de Amigo: `{}`".format(user.friend_id)
                      if user_sql.has_fc(user_id) and user.fclists is not False and user.friend_id is not None
                      else "")

    output = support.replace(replied_id) + text_friend_id

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
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if are_banned(user_id, chat_id):
        return

    main = user_sql.get_real_user(user_id)
    text = "**Listado de Friend Codes:**"
    friends = []

    if main is None:
        text = "❌ Debes registrarte para usar este comando."
        bot.sendMessage(
            chat_id=user_id,
            text=text,
            parse_mode=telegram.ParseMode.MARKDOWN)
        return

    if not main.fclists:
        text = "❌ Debes hacer público tu código de amigo desde el /pasaporte para poder pedir la lista."
        bot.sendMessage(
            chat_id=user_id,
            text=text,
            parse_mode=telegram.ParseMode.MARKDOWN)
        return

    if main.friend_id is None:
        text = "❌ Debes añadir tu código de amigo al bot para poder pedir la lista."
        bot.sendMessage(
            chat_id=user_id,
            text=text,
            parse_mode=telegram.ParseMode.MARKDOWN)
        return

    users = get_users_from_group(chat_id)
    if(users.count() == 0):
        text = "¡Vaya! Parece que nadie ha hablado en este grupo 🧐"
        bot.sendMessage(
            chat_id=user_id,
            text=text,
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return
    for user_data in users:
        try:
            data = support.get_usergroup_tlg(chat_id, user_data.user_id, bot)
        except:
            data = None
            pass
        if data is None or (data and data.status not in ['kicked','left'] and not data.user.is_bot):
            user = user_sql.get_user(user_data.user_id)
            if user and not user.banned and user.friend_id and user.fclists:
                if user.house is Houses.GRYFFINDOR.value:
                    text_team = "🦁"
                elif user.house is Houses.HUFFLEPUFF.value:
                    text_team = "🦡"
                elif user.house is Houses.RAVENCLAW.value:
                    text_team = "🦅"
                elif user.house is Houses.SLYTHERIN.value:
                    text_team = "🐍"
                elif user.house is Houses.NONE.value:
                    text_team = "🙈"

                friends.append("\n{0}[{1}](tg://user?id={2}) `{3}`".format(
                    text_team,
                    user.alias,
                    user.id,
                    user.friend_id
                ))

    random.shuffle(friends)
    friends = "".join(friends[:30])
    text = text + friends
    bot.sendMessage(
        chat_id=user_id,
        text=text,
        parse_mode=telegram.ParseMode.MARKDOWN
    )

@run_async
def set_friendid_cmd(bot, update, args=None):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)

    if are_banned(chat_id, user_id):
        return

    fc = None
    if len(args) == 3:
        fc = ''.join(args)
    elif len(args) == 1:
        fc = args[0]

    user = user_sql.get_user(user_id)
    if user is None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Debes registrarte para usar este comando.")
        return

    if fc is None and user.friend_id is None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Vaya, no he reconocido esta Clave de Amigo... ")
        return

    elif fc is None and user.friend_id is not None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Clave de Amigo eliminada correctamente"
        )
        user_sql.set_fc(None, user_id)
        return

    friendcode = re.match(r'^[0-9]{12}$', fc)

    if friendcode is None and user.friend_id is None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Vaya, no he reconocido ese Clave de Amigo... {}".format(fc))
        return

    else:
        user_sql.set_fc(fc, user_id)
        bot.sendMessage(
            chat_id=chat_id,
            text="👌 He registrado tu Clave de Amigo como `{}`.".format(fc),
            parse_mode=telegram.ParseMode.MARKDOWN)


@run_async
def passport_cmd(bot, update):
    logging.debug("%s", update)
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    user_username = message.from_user.username

    if are_banned(chat_id, user_id):
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

    user = user_sql.get_real_user(user_id)
    if user is None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Debes registrarte para usar este comando.",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return

    user_sql.commit_user(user_id, alias=user_username)

    output = (
        "Bienvenido {}, este es tu pasaporte del ministerio, aquí podrás editar "
        "tu información de perfil y los ajustes con Dumbledore entre otras funciones.".format(support.replace(user_id, frce=True)))

    button_list = [
        [InlineKeyboardButton("👤 Perfil", callback_data='profile_edit')],
        [InlineKeyboardButton("🗣 Menciones", callback_data='profile_ment')],
        #[InlineKeyboardButton("👥 Otros Ajustes", callback_data='profile_other')],
        [InlineKeyboardButton("Salir", callback_data='profile_end')]
    ]

    reply_markup = InlineKeyboardMarkup(button_list)
    bot.sendMessage(
        chat_id=chat_id,
        text=output,
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=reply_markup)


REGPRIV = re.compile(r'^profile_edit_([a-z0-9]{1,3})(_([a-z0-9]{1,3})|)(_([0-9]{1,3})|)')

@run_async
def passport_btn(bot, update):
    query = update.callback_query
    data = query.data
    user = update.effective_user
    user_id = query.from_user.id
    text = query.message.text
    chat_id = query.message.chat.id
    message_id = query.message.message_id

    if are_banned(user_id, chat_id):
        return

    if data == "profile_end":
        support.delete_message(chat_id, message_id, bot)
        return

    elif data == "profile_back":
        button_list = [
        [InlineKeyboardButton("👤 Perfil", callback_data='profile_edit')],
        [InlineKeyboardButton("🗣 Menciones", callback_data='profile_ment')],
        #[InlineKeyboardButton("👥 Otros Ajustes", callback_data='profile_other')],
        [InlineKeyboardButton("Salir", callback_data='profile_end')]
    ]

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(button_list))
        return

    elif data == "profile_edit":
        button_list = [
            [InlineKeyboardButton("🏘 Casa Hogwarts", callback_data='profile_edit_hse')],
            #[InlineKeyboardButton("👨‍👩‍👧‍👦 Equipo", callback_data='profile_edit_tea')],
            #[InlineKeyboardButton("🆙 Nivel", callback_data='profile_edit_lvl_pj')],
            #[InlineKeyboardButton("🛡 Profesion", callback_data='profile_edit_prf')],
            [InlineKeyboardButton("🗑 Eliminar perfil", callback_data='profile_edit_del')],
            [InlineKeyboardButton("« Volver", callback_data='profile_back')]]

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(button_list))
        return

    elif data == "profile_ment":
        user = user_sql.get_real_user(user_id)
        text = "🔕 Menciones desactivadas"
        if user.alerts:
            text = "🔔 Menciones activas"

        button_list = [
            [InlineKeyboardButton(text, callback_data='profile_ment_1')],
            [InlineKeyboardButton("« Volver", callback_data='profile_back')]]

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(button_list))
        return
        
    elif data == "profile_other":
        user = user_sql.get_real_user(user_id)
        friendtext = "▪️ Clave de amigo"
        rankingtext = "▪️ Ranking"
        if user.fclists:
            friendtext = "✅ Clave de amigo"
        if user.ranking:
            rankingtext = "✅ Ranking"

        button_list = [
            [InlineKeyboardButton(friendtext, callback_data='profile_other_1')],
            [InlineKeyboardButton(rankingtext, callback_data='profile_other_2')],
            [InlineKeyboardButton("« Volver", callback_data='profile_back')]]

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(button_list))
        return

    elif data == "profile_edit_lvl_pj":
        button_list = [
            [InlineKeyboardButton("1-10", callback_data='profile_edit_btn_pj_0'),
            InlineKeyboardButton("11-20", callback_data='profile_edit_btn_pj_10'),
            InlineKeyboardButton("21-30", callback_data='profile_edit_btn_pj_20')],
            [InlineKeyboardButton("31-40", callback_data='profile_edit_btn_pj_30'),
            InlineKeyboardButton("41-50", callback_data='profile_edit_btn_pj_40'),
            InlineKeyboardButton("51-60", callback_data='profile_edit_btn_pj_50')],
            [InlineKeyboardButton("« Volver", callback_data='profile_edit')]]

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(button_list))
        return

    elif data == "profile_edit_hse":
        button_list = [
            [InlineKeyboardButton("🦁 Gryffindor", callback_data='profile_edit_hse_1')],
            [InlineKeyboardButton("🦡 Hufflepuff", callback_data='profile_edit_hse_2')],
            [InlineKeyboardButton("🦅 Ravenclaw", callback_data='profile_edit_hse_3')],
            [InlineKeyboardButton("🐍 Slytherin", callback_data='profile_edit_hse_4')],
            [InlineKeyboardButton("« Volver", callback_data='profile_edit')]]

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(button_list))
        return

    elif data == "profile_edit_tea":
        button_list = [
            [InlineKeyboardButton("Team Harry", callback_data='profile_edit_tea_2')],
            [InlineKeyboardButton("Team Ron", callback_data='profile_edit_tea_1')],
            [InlineKeyboardButton("Team Hermione", callback_data='profile_edit_tea_3')],
            [InlineKeyboardButton("« Volver", callback_data='profile_edit')]]

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(button_list))
        return

    elif data == "profile_edit_prf":
        button_list = [
            [InlineKeyboardButton("⚔ Auror", callback_data='profile_edit_prf_3')],
            [InlineKeyboardButton("🐾 Magizoologo", callback_data='profile_edit_prf_2')],
            [InlineKeyboardButton("📚 Profesor", callback_data='profile_edit_prf_1')],
            [InlineKeyboardButton("« Volver", callback_data='profile_edit')]]

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(button_list))
        return

    elif data == "profile_edit_del":
        button_list = [
            [InlineKeyboardButton("🗑 Confirmar", callback_data='profile_edit_del_1')],
            [InlineKeyboardButton("« Volver", callback_data='profile_edit')]]

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(button_list))
        return

    elif data == "profile_other_1":
        user_sql.update_fclist(user_id)
        user = user_sql.get_real_user(user_id)
        friendtext = "▪️ Clave de amigo"
        rankingtext = "▪️ Ranking"
        if user.fclists:
            friendtext = "✅ Clave de amigo"
        if user.ranking:
            rankingtext = "✅ Ranking"

        button_list = [
            [InlineKeyboardButton(friendtext, callback_data='profile_other_1')],
            [InlineKeyboardButton(rankingtext, callback_data='profile_other_2')],
            [InlineKeyboardButton("« Volver", callback_data='profile_back')]]

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(button_list))
        return

    elif data == "profile_other_2":
        user_sql.update_ranking(user_id)
        user = user_sql.get_real_user(user_id)
        friendtext = "▪️ Clave de amigo"
        rankingtext = "▪️ Ranking"
        if user.fclists:
            friendtext = "✅ Clave de amigo"
        if user.ranking:
            rankingtext = "✅ Ranking"

        button_list = [
            [InlineKeyboardButton(friendtext, callback_data='profile_other_1')],
            [InlineKeyboardButton(rankingtext, callback_data='profile_other_2')],
            [InlineKeyboardButton("« Volver", callback_data='profile_back')]]

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(button_list))
        return

    elif data == "profile_ment_1":
        user_sql.update_mentions(user_id)
        user = user_sql.get_real_user(user_id)
        text = "🔕 Menciones desactivadas"
        if user.alerts:
            text = "🔔 Menciones activas"

        button_list = [
            [InlineKeyboardButton(text, callback_data='profile_ment_1')],
            [InlineKeyboardButton("« Volver", callback_data='profile_back')]]

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(button_list))
        return

    elif data == "profile_edit_del_1":
        user_sql.del_user(user_id)
        support.delete_message(chat_id, message_id, bot)
        bot.sendMessage(
            chat_id=chat_id,
            text="Tu perfil ha sido eliminado.",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return
    
    match = REGPRIV.match(query.data)
    if match:
        par = match.group(1)
        typ = match.group(3) 
        val = match.group(5)        
    else:
        return

    if par == "btn":
        if typ == "pj":
            button_list = [
                [InlineKeyboardButton("{}".format(1+int(val)), callback_data='profile_edit_lvl_pj_{}'.format(1+int(val))),
                InlineKeyboardButton("{}".format(2+int(val)), callback_data='profile_edit_lvl_pj_{}'.format(2+int(val))),
                InlineKeyboardButton("{}".format(3+int(val)), callback_data='profile_edit_lvl_pj_{}'.format(3+int(val))),
                InlineKeyboardButton("{}".format(4+int(val)), callback_data='profile_edit_lvl_pj_{}'.format(4+int(val))),
                InlineKeyboardButton("{}".format(5+int(val)), callback_data='profile_edit_lvl_pj_{}'.format(5+int(val)))],
                [InlineKeyboardButton("{}".format(6+int(val)), callback_data='profile_edit_lvl_pj_{}'.format(6+int(val))),
                InlineKeyboardButton("{}".format(7+int(val)), callback_data='profile_edit_lvl_pj_{}'.format(7+int(val))),
                InlineKeyboardButton("{}".format(8+int(val)), callback_data='profile_edit_lvl_pj_{}'.format(8+int(val))),
                InlineKeyboardButton("{}".format(9+int(val)), callback_data='profile_edit_lvl_pj_{}'.format(9+int(val))),
                InlineKeyboardButton("{}".format(10+int(val)), callback_data='profile_edit_lvl_pj_{}'.format(10+int(val)))],
                [InlineKeyboardButton("« Volver", callback_data='profile_edit_lvl_pj')]]

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(button_list))
        return

    elif par == "hse":
        user_sql.commit_user(user_id, house=typ)
        output = (
        "Bienvenido {}, este es tu pasaporte del ministerio, aquí podrás editar "
        "tu información de perfil y los ajustes con Dumbledore entre otras funciones.".format(support.replace(user_id, frce=True)))
        button_list = [
            [InlineKeyboardButton("🏘 Casa Hogwarts", callback_data='profile_edit_hse')],
            #[InlineKeyboardButton("👨‍👩‍👧‍👦 Equipo", callback_data='profile_edit_tea')],
            #[InlineKeyboardButton("🆙 Nivel", callback_data='profile_edit_lvl_pj')],
            #[InlineKeyboardButton("🛡 Profesion", callback_data='profile_edit_prf')],
            [InlineKeyboardButton("🗑 Eliminar perfil", callback_data='profile_edit_del')],
            [InlineKeyboardButton("« Guardar y salir", callback_data='profile_end')]]
       
        bot.edit_message_text(
            text=output,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(button_list),
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=True)
        return

    elif par == "tea":
        user_sql.commit_user(user_id, team=typ)
        output = (
        "Bienvenido {}, este es tu pasaporte del ministerio, aquí podrás editar "
        "tu información de perfil y los ajustes con Dumbledore entre otras funciones.".format(support.replace(user_id, frce=True)))
        button_list = [
            [InlineKeyboardButton("🏘 Casa Hogwarts", callback_data='profile_edit_hse')],
            #[InlineKeyboardButton("👨‍👩‍👧‍👦 Equipo", callback_data='profile_edit_tea')],
            #[InlineKeyboardButton("🆙 Nivel", callback_data='profile_edit_lvl_pj')],
            #[InlineKeyboardButton("🛡 Profesion", callback_data='profile_edit_prf')],
            [InlineKeyboardButton("🗑 Eliminar perfil", callback_data='profile_edit_del')],
            [InlineKeyboardButton("« Guardar y salir", callback_data='profile_end')]]
       
        bot.edit_message_text(
            text=output,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(button_list),
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return

    elif par == "prf":
        user_sql.commit_user(user_id, profession=typ)
        output = (
        "Bienvenido {}, este es tu pasaporte del ministerio, aquí podrás editar "
        "tu información de perfil y los ajustes con Dumbledore entre otras funciones.".format(support.replace(user_id, frce=True)))
        button_list = [
            [InlineKeyboardButton("🏘 Casa Hogwarts", callback_data='profile_edit_hse')],
            #[InlineKeyboardButton("👨‍👩‍👧‍👦 Equipo", callback_data='profile_edit_tea')],
            #[InlineKeyboardButton("🆙 Nivel", callback_data='profile_edit_lvl_pj')],
            #[InlineKeyboardButton("🛡 Profesion", callback_data='profile_edit_prf')],
            [InlineKeyboardButton("🗑 Eliminar perfil", callback_data='profile_edit_del')],
            [InlineKeyboardButton("« Guardar y salir", callback_data='profile_end')]]
       
        bot.edit_message_text(
            text=output,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(button_list),
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return

    elif par == "lvl":
        if typ == "pj":
            user_sql.commit_user(user_id, level=val)
        output = (
        "Bienvenido {}, este es tu pasaporte del ministerio, aquí podrás editar "
        "tu información de perfil y los ajustes con Dumbledore entre otras funciones.".format(support.replace(user_id, frce=True)))
        button_list = [
            [InlineKeyboardButton("🏘 Casa Hogwarts", callback_data='profile_edit_hse')],
            #[InlineKeyboardButton("👨‍👩‍👧‍👦 Equipo", callback_data='profile_edit_tea')],
            #[InlineKeyboardButton("🆙 Nivel", callback_data='profile_edit_lvl_pj')],
            #[InlineKeyboardButton("🛡 Profesion", callback_data='profile_edit_prf')],
            [InlineKeyboardButton("🗑 Eliminar perfil", callback_data='profile_edit_del')],
            [InlineKeyboardButton("« Guardar y salir", callback_data='profile_end')]]
        bot.edit_message_text(
            text=output,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(button_list),
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return


REGREG = re.compile(r'^reg_([a-z0-9]{1,3})(_([0-9]{1,3})|)')

@run_async
def register_btn(bot, update):
    query = update.callback_query
    data = query.data
    user = update.effective_user
    user_id = query.from_user.id
    text = query.message.text
    chat_id = query.message.chat.id
    message_id = query.message.message_id

    if are_banned(user_id, chat_id):
        return

    match = REGREG.match(query.data)
    if match:
        par = match.group(1)
        val = match.group(3)        
    else:
        return

    if par == "hse":
        user_sql.commit_user(user_id, house=val)
        user_sql.commit_user(user_id, validation=True)
        bot.edit_message_text(
            text="Felicidades, has completado el proceso de validación.",
            chat_id=chat_id,
            message_id=message_id,
            parse_mode=telegram.ParseMode.HTML,
            disable_web_page_preview=True
        )
        return
        '''PLANED FREATURE
        button_list = [
            [InlineKeyboardButton("Team Harry", callback_data='reg_tea_2')],
            [InlineKeyboardButton("Team Ron", callback_data='reg_tea_1')],
            [InlineKeyboardButton("Team Hermione", callback_data='reg_tea_3')]]

        text = "Para finalizar, necesito saber con que equipo juegas."

        bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(button_list)s,
            parse_mode=telegram.ParseMode.HTML,
            disable_web_page_preview=True
        )

    elif par == "tea":
        commit_user(user_id, team=val)
        commit_user(user_id, validation=True)
        bot.edit_message_text(
            text="Felicidades, has completado el proceso de validación.",
            chat_id=chat_id,
            message_id=message_id,
            parse_mode=telegram.ParseMode.HTML,
            disable_web_page_preview=True
        )
        return
        '''


@run_async
def ranking_spain_cmd(bot, update):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)
    config = get_config()

    if are_banned(user_id, chat_id):
        return

    main = user_sql.get_user(user_id)
    count = 0
    text = "🏆 *Ranking de {0}* 🏆\n".format(message.chat.title)
    user_list = []

    users = get_users_from_group(chat_id)
    for user_data in users:
        try:
            data = support.get_usergroup_tlg(chat_id, user_data.user_id, bot)
        except:
            data = None
            pass
        if data is None or (data and data.status not in ['kicked','left'] and not data.user.is_bot):
            user = user_sql.get_user(user_data.user_id)
            if user and not user.banned and user.ranking:
                if user.house is Houses.GRYFFINDOR.value:
                    text_team = "🦁"
                elif user.house is Houses.HUFFLEPUFF.value:
                    text_team = "🦡"
                elif user.house is Houses.RAVENCLAW.value:
                    text_team = "🦅"
                elif user.house is Houses.SLYTHERIN.value:
                    text_team = "🐍"
                elif user.house is Houses.NONE.value:
                    text_team = "🙈"
                if user.profession is Professions.PROFESSOR.value:
                    text_prof = "📚"
                elif user.profession is Professions.MAGIZOOLOGIST.value:
                    text_prof = "🐾"
                elif user.profession is Professions.AUROR.value:
                    text_prof = "⚔️"
                elif user.profession is Professions.NONE.value:
                    text_prof = "🍮"

                user_list.append("[@{0}](tg://user?id={1}) - {2} - {3} - {4}".format(
                    user.alias,
                    user.id,
                    text_team,
                    user.level,
                    text_prof
                ))

                count += 1

    sorted_user = sorted(user_list, key=lambda x: int(x.split(' - ')[2]), reverse=True)
    if count >= 1:
        sorted_user[0] = "\n🥇 " + sorted_user[0] + "\n"
    if count >= 2:
        sorted_user[1] = "🥈 " + sorted_user[1] + "\n"
    if count >= 3:
        sorted_user[2] = "🥉 " + sorted_user[2] + "\n"
    bot.sendMessage(
        chat_id=int(config["telegram"]["ranking_id"]),
        text=text + '\n'.join(sorted_user[:100]),
        parse_mode=telegram.ParseMode.MARKDOWN
    )

@run_async
def private_ranking_cmd(bot, update):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)
    config = get_config()

    if are_banned(user_id, chat_id):
        return

    main = user_sql.get_user(user_id)
    if main is None:
        return

    if not main.ranking:
        return

    '''
    if last_run(user_id + chat_id, 'ranking'):
        return
    '''
    count = 0
    text = "🏆 *Ranking de {0}* 🏆\n".format(message.chat.title)
    user_list = []

    users = get_users_from_group(chat_id)
    for user_data in users:
        try:
            data = support.get_usergroup_tlg(chat_id, user_data.user_id, bot)
        except:
            data = None
            pass
        if data is None or (data and data.status not in ['kicked','left'] and not data.user.is_bot):
            user = user_sql.get_user(user_data.user_id)
            if user and not user.banned and user.ranking:
                if user.house is Houses.GRYFFINDOR.value:
                    text_team = "🦁"
                elif user.house is Houses.HUFFLEPUFF.value:
                    text_team = "🦡"
                elif user.house is Houses.RAVENCLAW.value:
                    text_team = "🦅"
                elif user.house is Houses.SLYTHERIN.value:
                    text_team = "🐍"
                elif user.house is Houses.NONE.value:
                    text_team = "🙈"
                if user.profession is Professions.PROFESSOR.value:
                    text_prof = "📚"
                elif user.profession is Professions.MAGIZOOLOGIST.value:
                    text_prof = "🐾"
                elif user.profession is Professions.AUROR.value:
                    text_prof = "⚔️"
                elif user.profession is Professions.NONE.value:
                    text_prof = "🍮"

                if user.id == user_id:
                    user_list.append("*@{0} - {1} - {2} - {3}*".format(
                    user.alias,
                    text_team,
                    user.level,
                    text_prof
                ))
                else:
                    user_list.append("[@{0}](tg://user?id={1}) - {2} - {3} - {4}".format(
                        user.alias,
                        user.id,
                        text_team,
                        user.level,
                        text_prof
                    ))

                count += 1

    sorted_user = sorted(user_list, key=lambda x: int(x.split(' - ')[2]), reverse=True)
    count = 0
    for user in sorted_user:
        if count == 0:
            sorted_user[0] = "\n🥇 " + sorted_user[0] + "\n"
            count += 1
            continue
        if count == 1:
            sorted_user[1] = "🥈 " + sorted_user[1] + "\n"
            count += 1
            continue
        if count == 2:
            sorted_user[2] = "🥉 " + sorted_user[2]
            count += 1
            continue
        
        sorted_user[count] = "\n" + str(count+1) + ". " + sorted_user[count]

        count += 1

    matching = [i for i, s in enumerate(sorted_user) if user_sql.get_user(user_id).alias in s]

    if matching[0] <= 10:
        ranking_text = sorted_user[:10]
    else:
        ranking_text = sorted_user[:10]
        ranking_text.append("\n\n✨✨✨✨✨\n")
        if not matching[0]-2 <= 9:
            ranking_text.append(sorted_user[matching[0]-2])
        if not matching[0]-1 <= 9:
            ranking_text.append(sorted_user[matching[0]-1])
        ranking_text.append(sorted_user[matching[0]])
        try:
            if not matching[0]+1 <= len(sorted_user)-2:
                ranking_text.append(sorted_user[matching[0]+1])
            if not matching[0]+2 <= len(sorted_user)-1:
                ranking_text.append(sorted_user[matching[0]+2])
        except:
            pass

    bot.sendMessage(
        chat_id=user_id,
        text=text + ''.join(ranking_text),
        parse_mode=telegram.ParseMode.MARKDOWN
    )


@run_async
def points_cmd(bot, update):
    logging.debug("%s", update)
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    user_username = message.from_user.username

    if are_banned(chat_id, user_id):
        return

    user = user_sql.get_real_user(user_id)
    if user is None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Debes registrarte para usar este comando.",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return

    text = "Actualmente tienes {} puntos.".format(user_sql.update_user_points(user_id, read_only=True))

    bot.sendMessage(
        chat_id=chat_id,
        text=text,
        parse_mode=telegram.ParseMode.MARKDOWN)

@run_async
def add_poi_cmd(bot, update, args=None):
    logging.debug("%s", update)
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if are_banned(chat_id, user_id) or not support.is_admin(chat_id, user_id, bot):
        return

    user = user_sql.get_real_user(user_id)
    if user is None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Debes registrarte para usar este comando.",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return

    if args is not None and len(args)!=0:
        if message.reply_to_message is not None:
            if message.reply_to_message.location is not None:
                support.delete_message(chat_id, message.reply_to_message.message_id, bot)
                lat = message.reply_to_message.location.latitude
                lon = message.reply_to_message.location.longitude

                button_list = [
                [InlineKeyboardButton("🌱 Invernadero", callback_data='poi_greenhouse_{}'.format(user_id)),
                InlineKeyboardButton("🏰 Fortaleza", callback_data='poi_fortress_{}'.format(user_id))],
                [InlineKeyboardButton("❌ Cancelar", callback_data='poi_cancel_{}'.format(user_id))]]

                bot.send_venue(
                    chat_id=chat_id,
                    title=' '.join(args),
                    address="¿Qué tipo de POI quieres añadir?",
                    latitude=lat,
                    longitude=lon,
                    reply_markup=InlineKeyboardMarkup(button_list)
                )

@run_async
def rem_poi_cmd(bot, update, args=None):
    logging.debug("%s", update)
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if are_banned(chat_id, user_id) or not support.is_admin(chat_id, user_id, bot):
        return

    user = user_sql.get_real_user(user_id)
    if user is None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Debes registrarte para usar este comando.",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return

    try:
        if args is not None and len(args)!=0:
            if re.match(r"^[0-9]{1,10}$", args[0]):
                if delete_poi(poi_id=args[0], group_id=chat_id):
                    text = "POI eliminado correctamente."
                else:
                    text = "❌ No se pudo eliminar el POI."
                bot.sendMessage(
                chat_id=chat_id,
                text=text,
                parse_mode=telegram.ParseMode.MARKDOWN
                )
            elif args[0] == "all":
                delete_poi(group_id=chat_id, group=True)
                bot.sendMessage(
                chat_id=chat_id,
                text="Todos los POIs eliminados correctamente.",
                parse_mode=telegram.ParseMode.MARKDOWN
                )
    except:
        bot.sendMessage(
            chat_id=chat_id,
            text="Para poder eliminar todos los POIs tienes que eliminar antes las plantaciones activas.",
            parse_mode=telegram.ParseMode.MARKDOWN
        )

@run_async
def poi_list_cmd(bot, update, args=None):
    logging.debug("%s", update)
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if are_banned(chat_id, user_id):
        return

    user = user_sql.get_real_user(user_id)
    if user is None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Debes registrarte para usar este comando.",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return

    text = "Lista de POIs:\n"
    count = 0
    poi_list = get_poi_list(chat_id)
    for poi in poi_list:
        if poi.portal_type is PortalType.GREENHOUSE.value:
            poi_type = "🌱"
        elif poi.portal_type is PortalType.FORTRESS.value:
            poi_type = "🏰"
        elif poi.portal_type is PortalType.NONE.value:
            poi_type = "🍮"
        text = text + "\n#{0} {1} - [{2}](https://maps.google.com/maps?q={3},{4})".format(
            poi.id,
            poi_type,
            poi.name,
            poi.latitude,
            poi.longitude
        )

        count += 1
        if count == 100:
            pass

    if not list(poi_list):
        text= "❌ No hay POIs registrados."

    bot.sendMessage(
            chat_id=user_id,
            text=text,
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
    

def poi_btn(bot, update):
    query = update.callback_query
    data = query.data
    user = update.effective_user
    user_id = query.from_user.id
    text = query.message.text
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    name = query.message.venue.title
    lat = query.message.location.latitude
    lon = query.message.location.longitude

    if are_banned(user_id, chat_id):
        return

    queryData = data.split("_")
    userBtn = queryData[2]

    if userBtn == str(user_id) or support.is_admin(chat_id, user_id, bot):
        if queryData[1] == "greenhouse":
            create_poi(name, lat, lon, PortalType.GREENHOUSE.value, chat_id, user_id)
            bot.delete_message(
                chat_id=chat_id,
                message_id=message_id)
            bot.sendMessage(
                chat_id=chat_id,
                text="🌱 Invernadero registrado correctamente.",
                parse_mode=telegram.ParseMode.MARKDOWN
                )
            return
        elif queryData[1] == "fortress":
            create_poi(name, lat, lon, PortalType.FORTRESS.value, chat_id, user_id)
            bot.delete_message(
                chat_id=chat_id,
                message_id=message_id)
            bot.sendMessage(
                chat_id=chat_id,
                text="🏰 Fortaleza registrada correctamente.",
                parse_mode=telegram.ParseMode.MARKDOWN
                )
            return
        elif queryData[1] == "cancel":
            bot.delete_message(
                chat_id=chat_id,
                message_id=message_id)
            return