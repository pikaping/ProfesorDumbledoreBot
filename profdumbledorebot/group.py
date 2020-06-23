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

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import escape_markdown

import profdumbledorebot.nanny as nanny
import profdumbledorebot.sql.group as group_sql
import profdumbledorebot.supportmethods as support
from profdumbledorebot.config import get_config
from profdumbledorebot.model import ValidationRequiered, Houses, Professions
from profdumbledorebot.sql.admin import get_particular_admin, get_admin_from_linked, get_admin, set_admin_settings
from profdumbledorebot.sql.rules import has_rules
from profdumbledorebot.sql.settings import get_join_settings, get_group_settings
from profdumbledorebot.sql.support import are_banned
from profdumbledorebot.sql.user import get_user, is_staff
from profdumbledorebot.sql.usergroup import exists_user_group, set_user_group, join_group, message_counter
from profdumbledorebot.sql.welcome import get_welc_pref
from profdumbledorebot.welcome import send_welcome
from profdumbledorebot.games import games_cmd


@run_async
def joined_chat(bot, update, job_queue):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    new_chat_member = message.new_chat_members[0] if message.new_chat_members else None

    config = get_config()
    bot_alias = config['telegram']['bot_alias']

    if new_chat_member.username == bot_alias:
        if are_banned(user_id, chat_id):
            bot.leaveChat(chat_id=chat_id)
            return

        chat_title = message.chat.title
        chat_id = message.chat.id
        group = group_sql.get_real_group(chat_id)
        if group is None:
            group_sql.set_group(chat_id, message.chat.title)

        message_text = (
            "Si necesitais ayuda podéis lanzar chispas rojas c"
            "on vuestra varita o utilizando el comando `/help`"
            " para conocer todas las funciones. Aseguraos de v"
            "er la ayuda para prefectos de los grupos, donde s"
            "e explica en detalle todos los pasos que se deben"
            " seguir.".format(escape_markdown(chat_title)))

        admin = get_admin(chat_id)
        if admin is not None and admin.admin_bot is True:
            set_admin_settings(chat_id, "admin_bot")
            message_text = message_text + "\n\n*Fawkes emprendió el vuelo.*"


        bot.sendMessage(
            chat_id=chat_id, 
            text=message_text, 
            parse_mode=telegram.ParseMode.MARKDOWN)

    elif new_chat_member.username != bot_alias:
        chat_id = message.chat.id
        user_id = update.effective_message.new_chat_members[0].id

        group = get_join_settings(chat_id)
        if group is not None:
            if group.delete_header:
                support.delete_message(chat_id, message.message_id, bot)

            if are_banned(user_id, user_id):
                bot.kickChatMember(chat_id, user_id)
                return

            user = get_user(user_id)       
            staff = is_staff(user_id)
            if user is None and group.requirment is not ValidationRequiered.NO_VALIDATION.value and staff is False:
                bot.kickChatMember(chat_id=chat_id, user_id=user_id, until_date=time.time()+31)
                if group.val_alert is False:
                    output = "👌 Mago sin registrarse expulsado!"
                    bot.sendMessage(
                        chat_id=chat_id, 
                        text=output, 
                        parse_mode=telegram.ParseMode.MARKDOWN)
                good_luck(bot, chat_id, message, "El usuario no está registrado")
                return

            elif group.requirment is ValidationRequiered.VALIDATION.value and user.level is None and staff is False:
                bot.kickChatMember(chat_id=chat_id, user_id=user_id, until_date=time.time()+31)
                if group.val_alert is False:
                    output = "👌 Mago infiltrado expulsado!"
                    bot.sendMessage(
                        chat_id=chat_id, 
                        text=output, 
                        parse_mode=telegram.ParseMode.MARKDOWN)           
                good_luck(bot, chat_id, message, "El usuario no está registrado")
                try:
                    bot.sendMessage(
                        chat_id=user_id, 
                        text="❌ Debes validarte para entrar en este grupo", 
                        parse_mode=telegram.ParseMode.MARKDOWN)
                except Exception:
                    pass
                return

            elif group.requirment is ValidationRequiered.PROFESSOR.value and user.profession is not Professions.PROFESSOR.value and staff is False:
                bot.kickChatMember(chat_id=chat_id, user_id=user_id, until_date=time.time()+31)
                if group.val_alert is False:
                    output = "👌 Mago infiltrado expulsado!"
                    bot.sendMessage(
                        chat_id=chat_id, 
                        text=output, 
                        parse_mode=telegram.ParseMode.MARKDOWN)           
                good_luck(bot, chat_id, message, "El usuario no está registrado")
                try:
                    bot.sendMessage(
                        chat_id=user_id, 
                        text="❌ Debes validarte para entrar en este grupo", 
                        parse_mode=telegram.ParseMode.MARKDOWN)
                except Exception:
                    pass
                return

            elif group.requirment is ValidationRequiered.MAGIZOOLOGIST.value and user.profession is not Professions.MAGIZOOLOGIST.value and staff is False:
                bot.kickChatMember(chat_id=chat_id, user_id=user_id, until_date=time.time()+31)
                if group.val_alert is False:
                    output = "👌 Mago infiltrado expulsado!"
                    bot.sendMessage(
                        chat_id=chat_id, 
                        text=output, 
                        parse_mode=telegram.ParseMode.MARKDOWN)           
                good_luck(bot, chat_id, message, "El usuario no está registrado")
                try:
                    bot.sendMessage(
                        chat_id=user_id, 
                        text="❌ Debes validarte para entrar en este grupo", 
                        parse_mode=telegram.ParseMode.MARKDOWN)
                except Exception:
                    pass
                return

            elif group.requirment is ValidationRequiered.AUROR.value and user.profession is not Professions.AUROR.value and staff is False:
                bot.kickChatMember(chat_id=chat_id, user_id=user_id, until_date=time.time()+31)
                if group.val_alert is False:
                    output = "👌 Mago infiltrado expulsado!"
                    bot.sendMessage(
                        chat_id=chat_id, 
                        text=output, 
                        parse_mode=telegram.ParseMode.MARKDOWN)           
                good_luck(bot, chat_id, message, "El usuario no está registrado")
                try:
                    bot.sendMessage(
                        chat_id=user_id, 
                        text="❌ Debes validarte para entrar en este grupo", 
                        parse_mode=telegram.ParseMode.MARKDOWN)
                except Exception:
                    pass
                return

            elif group.requirment is ValidationRequiered.GRYFFINDOR.value and user.house is not Houses.GRYFFINDOR.value and staff is False:
                bot.kickChatMember(chat_id=chat_id, user_id=user_id, until_date=time.time()+31)
                if group.val_alert is False:
                    output = "👌 Mago infiltrado expulsado!"
                    bot.sendMessage(
                        chat_id=chat_id, 
                        text=output, 
                        parse_mode=telegram.ParseMode.MARKDOWN)           
                good_luck(bot, chat_id, message, "El usuario no está registrado")
                try:
                    bot.sendMessage(
                        chat_id=user_id, 
                        text="❌ Debes validarte para entrar en este grupo", 
                        parse_mode=telegram.ParseMode.MARKDOWN)
                except Exception:
                    pass
                return

            elif group.requirment is ValidationRequiered.HUFFLEPUFF.value and user.house is not Houses.HUFFLEPUFF.value and staff is False:
                bot.kickChatMember(chat_id=chat_id, user_id=user_id, until_date=time.time()+31)
                if group.val_alert is False:
                    output = "👌 Mago infiltrado expulsado!"
                    bot.sendMessage(
                        chat_id=chat_id, 
                        text=output, 
                        parse_mode=telegram.ParseMode.MARKDOWN)           
                good_luck(bot, chat_id, message, "El usuario no está registrado")
                try:
                    bot.sendMessage(
                        chat_id=user_id, 
                        text="❌ Debes validarte para entrar en este grupo", 
                        parse_mode=telegram.ParseMode.MARKDOWN)
                except Exception:
                    pass
                return

            elif group.requirment is ValidationRequiered.RAVENCLAW.value and user.house is not Houses.RAVENCLAW.value and staff is False:
                bot.kickChatMember(chat_id=chat_id, user_id=user_id, until_date=time.time()+31)
                if group.val_alert is False:
                    output = "👌 Mago infiltrado expulsado!"
                    bot.sendMessage(
                        chat_id=chat_id, 
                        text=output, 
                        parse_mode=telegram.ParseMode.MARKDOWN)           
                good_luck(bot, chat_id, message, "El usuario no está registrado")
                try:
                    bot.sendMessage(
                        chat_id=user_id, 
                        text="❌ Debes validarte para entrar en este grupo", 
                        parse_mode=telegram.ParseMode.MARKDOWN)
                except Exception:
                    pass
                return

            elif group.requirment is ValidationRequiered.SLYTHERIN.value and user.house is not Houses.SLYTHERIN.value and staff is False:
                bot.kickChatMember(chat_id=chat_id, user_id=user_id, until_date=time.time()+31)
                if group.val_alert is False:
                    output = "👌 Mago infiltrado expulsado!"
                    bot.sendMessage(
                        chat_id=chat_id, 
                        text=output, 
                        parse_mode=telegram.ParseMode.MARKDOWN)           
                good_luck(bot, chat_id, message, "El usuario no está registrado")
                try:
                    bot.sendMessage(
                        chat_id=user_id, 
                        text="❌ Debes validarte para entrar en este grupo", 
                        parse_mode=telegram.ParseMode.MARKDOWN)
                except Exception:
                    pass
                return
        
            if group.max_members is not None and group.max_members > 0 and bot.get_chat_members_count(chat_id) >= group.max_members and staff is False:
                if group.val_alert is False:
                    output = "❌ El número máximo de integrantes en el grupo ha sido alcanzado"
                    sent = bot.sendMessage(
                        chat_id=chat_id, 
                        text=output, 
                        parse_mode=telegram.ParseMode.MARKDOWN)
                    delete_object = support.DeleteContext(chat_id, sent.message_id)
                    job_queue.run_once(
                        support.callback_delete, 
                        10,
                        context=delete_object
                    )
                time.sleep(2)
                bot.kickChatMember(chat_id=chat_id, user_id=user_id, until_date=time.time()+31)
                return

            if (not exists_user_group(user_id, chat_id)):
                set_user_group(user_id, chat_id)
            else:
                join_group(user_id, chat_id)

            if has_rules(chat_id) and staff is False:
                bot.restrict_chat_member(
                    chat_id,
                    user_id,
                    until_date=0,
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False)

            if get_welc_pref(chat_id):
                sent = send_welcome(bot, update)
                if sent is not None and group.delete_cooldown is not None and group.delete_cooldown > 0:
                    delete_object = support.DeleteContext(chat_id, sent.message_id)
                    job_queue.run_once(
                        support.callback_delete, 
                        group.delete_cooldown,
                        context=delete_object
                    )
            '''
            if group.val_alert and (user is None or user.level is None):
                sent = bot.sendMessage(
                    chat_id=chat_id,
                    text="",
                    parse_mode=telegram.ParseMode.MARKDOWN
                )
                if sent is not None:
                    delete_object = support.DeleteContext(chat_id, sent.message_id)
                    job_queue.run_once(
                        support.callback_delete, 
                        group.delete_cooldown or 60,
                        context=delete_object
                    )
            '''
            ladmin = get_particular_admin(chat_id)
            if ladmin is not None and ladmin.welcome:
                admin = get_admin_from_linked(chat_id)
                if admin is not None and admin.welcome and admin.admin_bot:
                    config = get_config()
                    adm_bot = Bot(token=config["telegram"]["admin_token"])
                    replace_pogo = support.replace(user_id, message.from_user.first_name, admin=True)
                    message_text = ("ℹ️ {}\n👤 {} ha entrado en el grupo").format(message.chat.title, replace_pogo)
                    adm_bot.sendMessage(chat_id=admin.id, text=message_text,
                                    parse_mode=telegram.ParseMode.MARKDOWN)
                elif admin is not None and admin.welcome :
                    replace_pogo = support.replace(user_id, message.from_user.first_name, admin=True)
                    message_text = ("ℹ️ {}\n👤 {} ha entrado en el grupo").format(message.chat.title, replace_pogo)
                    bot.sendMessage(chat_id=admin.id, text=message_text,
                                    parse_mode=telegram.ParseMode.MARKDOWN)


def good_luck(bot, chat_id, message, text):
    ladmin = get_particular_admin(chat_id)
    user_id = message.from_user.id
    if ladmin is not None and ladmin.welcome:
        admin = get_admin_from_linked(chat_id)
        if admin is not None and admin.welcome and admin.admin_bot:
            config = get_config()
            adm_bot = Bot(token=config["telegram"]["admin_token"])
            replace_pogo = support.replace(user_id, message.from_user.first_name, admin=True)
            message_text = ("ℹ️ {}\n👤 {} {}").format(message.chat.title, replace_pogo, text)
            adm_bot.sendMessage(chat_id=admin.id, text=message_text,
                            parse_mode=telegram.ParseMode.MARKDOWN)
        elif admin is not None and admin.welcome:
            replace_pogo = support.replace(user_id, message.from_user.first_name, admin=True)
            message_text = ("ℹ️ {}\n👤 {} {}").format(message.chat.title, replace_pogo, text)
            bot.sendMessage(chat_id=admin.id, text=message_text,
                            parse_mode=telegram.ParseMode.MARKDOWN)


@run_async
def process_group_message(bot, update, job_queue):
    chat_id, chat_type, user_id, text, message = support.extract_update_info(update)
    msg = update.effective_message
    
    if are_banned(user_id, chat_id):
        return
  
    group = group_sql.get_group(chat_id)
    if group is None:
        group_sql.set_group(chat_id, message.chat.title)
    if not exists_user_group(user_id, chat_id):
        set_user_group(user_id, chat_id)
        
    message_counter(user_id, chat_id)
    if get_group_settings(chat_id).games == True and (chat_type == 'supergroup' or chat_type == 'group'):
        games_cmd(bot, update)

    if text is None or msg.photo is None:
        if msg and msg.document:
            nanny.process_gif(bot, update, job_queue)
            return
        elif msg and msg.contact:
            nanny.process_contact(bot, update, job_queue)
            return
        elif msg and msg.game:
            nanny.process_game(bot, update, job_queue)
            return
        elif msg and msg.location or msg.venue:
            nanny.process_ubi(bot, update, job_queue)
            return
        elif msg and msg.photo:
            nanny.process_pic(bot, update, job_queue)
            return
        elif msg and msg.sticker:
            nanny.process_sticker(bot, update, job_queue)
            return
        elif msg and msg.voice or msg.audio:
            nanny.process_voice(bot, update, job_queue)
            return
        elif msg and msg.video or msg.video_note:
            nanny.process_video(bot, update, job_queue)
            return

    if msg and msg.entities and nanny.process_url(bot, update, job_queue):
        return

    if nanny.nanny_text(bot, user_id, chat_id, message, job_queue):
        return

    if text is not None and re.search("@admin(?!\w)", text) is not None:
        replace_pogo = support.replace(user_id, message.from_user.first_name, admin=True)

        chat_text = support.message_url(message, message.message_id, message.chat.title)

        message_text=("ℹ️ {}\n👤 {} ha enviado una alerta a los administradores\n\nMensaje: {}").format(
            chat_text,
            replace_pogo,
            text
        )
        for admin in bot.get_chat_administrators(chat_id):
            user = get_user(admin.user.id)
            if user is not None and user.alerts:
                bot.sendMessage(
                    chat_id=admin.user.id,
                    text=message_text,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
        ladmin = get_particular_admin(chat_id)
        if ladmin is not None and ladmin.admin:
            admin = get_admin_from_linked(chat_id)
            if admin is not None and admin.admin and admin.admin_bot:
                config = get_config()
                adm_bot = Bot(token=config["telegram"]["admin_token"])
                replace_pogo = support.replace(user_id, message.from_user.first_name, admin=True)
                message_text = ("ℹ️ {}\n👤 {} {}").format(chat_text, replace_pogo, text)
                adm_bot.sendMessage(chat_id=admin.id, text=message_text,
                                parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)
            elif admin is not None and admin.admin:
                replace_pogo = support.replace(user_id, message.from_user.first_name, admin=True)
                message_text = ("ℹ️ {}\n👤 {} {}").format(chat_text, replace_pogo, text)
                bot.sendMessage(chat_id=admin.id, text=message_text,
                                parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)
'''
    if text and len(text) < 31:
        commands = get_commands(chat_id)
        if commands is None:
            return
        for command in commands:
            logging.debug("%s %s", text, command)
            if distance(text.lower(), command.command.lower()) < 1:
                logging.debug("%s %s", text, command.command)
                ENUM_FUNC_MAP = {
                    Types.TEXT.value: bot.sendMessage,
                    Types.BUTTON_TEXT.value: bot.sendMessage,
                    Types.STICKER.value: bot.sendSticker,
                    Types.DOCUMENT.value: bot.sendDocument,
                    Types.PHOTO.value: bot.sendPhoto,
                    Types.AUDIO.value: bot.sendAudio,
                    Types.VOICE.value: bot.sendVoice,
                    Types.VIDEO.value: bot.sendVideo
                }
                if command.command_type != Types.TEXT and command.command_type != Types.BUTTON_TEXT:
                    ENUM_FUNC_MAP[command.command_type](chat_id, command.media)
                    return

                if command.command_type == Types.BUTTON_TEXT:
                    buttons = get_cmd_buttons(chat_id)
                    keyb = build_keyboard(buttons)
                    keyboard = InlineKeyboardMarkup(keyb)
                else:
                    keyboard = None
                try:
                    msg = update.effective_message.reply_text(
                        command.media,
                        reply_markup=keyboard,
                        parse_mode=telegram.ParseMode.MARKDOWN,
                        disable_web_page_preview=True, 
                        disable_notification=False
                        )

                except IndexError:
                    msg = update.effective_message.reply_text(
                            markdown_parser(
                                "\nBip bop bip: El mensaje tiene errores de"
                                "Markdown, revisalo y configuralo de nuevo."),
                        parse_mode=telegram.ParseMode.MARKDOWN)
                except KeyError:
                    msg = update.effective_message.reply_text(
                            markdown_parser(
                                "\nBip bop bip: El mensaje tiene errores con"
                                "las llaves, revisalo y configuralo de nuevo."),
                        parse_mode=telegram.ParseMode.MARKDOWN)
                return
'''


def send_alert(bot, chat_id, user_id):
    button_list = [[
        InlineKeyboardButton(text="Empezar!", url="https://t.me/ProfDumbledoreBot")
    ]]
    reply_markup = InlineKeyboardMarkup(button_list)
    sent_message = bot.sendMessage(
        chat_id=chat_id,
        text=(
            "¡Hola mago/a!\n\nPara permanecer en este grupo, debes registra"
            "rte conmigo: @ProfDumbledoreBot.\nPara hacerlo, pulsa *Empezar*, inicia el"
            " chat privado y sigue los pasos."
        ),
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )
    return sent_message


