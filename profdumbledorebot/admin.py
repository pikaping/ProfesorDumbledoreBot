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
import time
from datetime import datetime, timedelta

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import escape_markdown

import profdumbledorebot.sql.admin as adm_sql
import profdumbledorebot.supportmethods as support
from profdumbledorebot.config import get_config
from profdumbledorebot.sql.settings import get_group_settings
from profdumbledorebot.sql.support import are_banned
from profdumbledorebot.sql.user import get_user, get_user_by_name, is_staff
from profdumbledorebot.sql.usergroup import exists_user_group, set_user_group, warn_user, get_users_from_group
from profdumbledorebot.sql.group import get_group
from profdumbledorebot.model import Teams, Professions, Houses

# Admin Group

@run_async
def settings_admin_cmd(bot, update):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    group = adm_sql.get_admin(chat_id)
    if group is None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ No he reconocido este grupo como un grupo de administración.",
            parse_mode=telegram.ParseMode.MARKDOWN)
        return

    message = bot.sendMessage(chat_id=chat_id, text="Oído cocina!...")
    support.update_settings_message(chat_id, bot, message.message_id, keyboard='admin')


@run_async
def create_admin_cmd(bot, update):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    if adm_sql.get_admin(chat_id) is None:
        adm_sql.set_admin(chat_id)
        output = "👌 Grupo configurado exitosamente. Continua vinculando grupos con este ID: `{}`\nNo olvides activar las alertas con `/settings_admin`.".format(chat_id)
    else:
        output = "👌 Ya está configurado este grupo como administrativo.\nAquí tienes tu ID: `{}`".format(chat_id)

    bot.sendMessage(
        chat_id=chat_id,
        text=output,
        parse_mode=telegram.ParseMode.MARKDOWN)


@run_async
def rm_admin_cmd(bot, update):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    if adm_sql.get_admin(chat_id) is not None:
        adm_sql.rm_admin(chat_id)
    else:
        return

    bot.sendMessage(
        chat_id=chat_id,
        text="👌 Todos los grupos han sido desvinculados",
        parse_mode=telegram.ParseMode.MARKDOWN)


@run_async
def groups_cmd(bot, update):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if are_banned(user_id, chat_id):
        return

    groups = adm_sql.get_all_groups(chat_id)
    output = "*Listado de grupos vinculados:*"

    if groups is None:
        output = "❌ No he encontrado grupos vinculados a este."

    elif support.is_admin(chat_id, user_id, bot):
        for k in groups:
            chat = bot.get_chat(k.linked_id)
            if k.link is not None and re.match('@?[a-zA-Z]([a-zA-Z0-9_]+)$', k.link) is None:
                output = output + "\n🏫 [{}]({}) - `{}`".format(k.label or chat.title, k.link, k.linked_id)
            elif k.link is not None and re.match('@?[a-zA-Z]([a-zA-Z0-9_]+)$', k.link) is not None:
                output = output + "\n🏫 {} - {} - `{}`".format(k.label or chat.title, k.link, k.linked_id)
            else:
                output = output + "\n🏫 {} - `{}`".format(k.label or chat.title, k.linked_id)

    else:
        for k in groups:
            if k.link is not None and re.match('@?[a-zA-Z]([a-zA-Z0-9_]+)$', k.link) is None:
                output = output + "\n🏫 [{}]({})".format(k.label or chat.title, k.link)
            elif k.link is not None and re.match('@?[a-zA-Z]([a-zA-Z0-9_]+)$', k.link) is not None:
                output = output + "\n🏫 {} - {}".format(k.label or chat.title, k.link)
            else:
                output = output + "\n🏫 {}".format(k.label or chat.title)

    bot.sendMessage(
        chat_id=user_id,
        text=output,
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_web_page_preview=True)


@run_async
def add_url_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    if args is None or len(args) != 1 or args[0] != '-' and (len(args[0]) < 3 or len(args[0]) > 60 or re.match("@?[a-zA-Z]([a-zA-Z0-9_]+)$|https://t\.me/joinchat/[a-zA-Z0-9_-]+$", args[0]) is None):
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Necesito que me pases el alias del grupo o un enlace de `t.me` de un grupo privado. Por ejemplo: `@telegram` o `https://t.me/joinchat/XXXXERK2ZfB3ntXXSiWUx`.",
            parse_mode=telegram.ParseMode.MARKDOWN)
        return

    if args[0] != '-':
        enlace = args[0]
        adm_sql.add_tlink(chat_id, enlace)
        bot.sendMessage(
            chat_id=chat_id,
            text="👌 Establecido el link del grupo a {}.".format(support.ensure_escaped(enlace)),
            parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        adm_sql.add_tlink(chat_id, None)
        bot.sendMessage(
            chat_id=chat_id,
            text="👌 Esto... Creo que acabo de olvidar el enlace del grupo...",
            parse_mode=telegram.ParseMode.MARKDOWN)


@run_async
def create_link_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)
    chat_title = message.chat.title

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    if args is None or len(args) != 1 or adm_sql.get_admin(args[0]) is None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Parece ser que has introducido un ID incorrecto.",
            parse_mode=telegram.ParseMode.MARKDOWN)
        return

    adm_sql.new_link(args[0], chat_id)
    bot.sendMessage(
        chat_id=chat_id,
        text="👌 El grupo ha sido vinculado.",
        parse_mode=telegram.ParseMode.MARKDOWN)

@run_async
def add_tag_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    if adm_sql.get_groups(chat_id) is not None:
        message = ' '.join(args)
    else:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Este grupo no esta vinculado.",
            parse_mode=telegram.ParseMode.MARKDOWN)
        return

    if len(message) < 51:
        output = "👌 Nombre del grupo modificado correctamente."
        if message is '-':
            message = None
            output = "👌 Nombre del grupo reestablecido correctamente."
        adm_sql.set_tag(chat_id, message)
    else:
        output = "❌ Este mensaje es demasiado largo."

    bot.sendMessage(
        chat_id=chat_id,
        text=output,
        parse_mode=telegram.ParseMode.MARKDOWN)


@run_async
def rm_link_cmd(bot, update):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    adm_sql.rm_link(chat_id)
    bot.sendMessage(
        chat_id=chat_id,
        text="👌 El grupo ha sido desvinculado",
        parse_mode=telegram.ParseMode.MARKDOWN)


# Moderating tools

uv_last_check = {}
kickuv_last_check = {}
kicklvl_last_check = {}
kickmsg_last_check = {}
kickold_last_check = {}
games_last_check = {}
ranking_check = {}
fort_alert_check = {}

def last_run(id, cmdtype):
    if cmdtype is 'uv':
        if str(id) in uv_last_check:
            lastpress = uv_last_check[str(id)]
        else:
            lastpress = None
        uv_last_check[str(id)] = datetime.now()
    elif cmdtype is 'kickuv':

        if str(id) in kickuv_last_check:
            lastpress = kickuv_last_check[str(id)]
        else:
            lastpress = None
        kickuv_last_check[str(id)] = datetime.now()
    elif cmdtype is 'kicklvl':

        if str(id) in kicklvl_last_check:
            lastpress = kicklvl_last_check[str(id)]
        else:
            lastpress = None
        kicklvl_last_check[str(id)] = datetime.now()
    elif cmdtype is 'kickmsg':

        if str(id) in kickmsg_last_check:
            lastpress = kickmsg_last_check[str(id)]
        else:
            lastpress = None
        kickmsg_last_check[str(id)] = datetime.now()
    elif cmdtype is 'kickold':

        if str(id) in kickold_last_check:
            lastpress = kickold_last_check[str(id)]
        else:
            lastpress = None
        kickold_last_check[str(id)] = datetime.now()
    elif cmdtype is 'games':
        if str(id) in games_last_check:
            lastpress = games_last_check[str(id)]
        else:
            lastpress = None
            games_last_check[str(id)] = datetime.now()

        if lastpress is not None:
            difftime = datetime.now() - lastpress
            seconds = difftime.total_seconds()
            minutes = divmod(seconds, 60)[0]
            if minutes == 0:
                return True
            else:
                games_last_check[str(id)] = datetime.now()
                return False
    elif cmdtype is 'ranking':
        if str(id) in ranking_check:
            lastpress = ranking_check[str(id)]
        else:
            lastpress = None
            ranking_check[str(id)] = datetime.now()

        if lastpress is not None:
            difftime = datetime.now() - lastpress
            seconds = difftime.total_seconds()
            minutes = divmod(seconds, 3600)[0]
            if minutes == 0:
                return True
            else:
                ranking_check[str(id)] = datetime.now()
                return False
    elif cmdtype is 'fort_alert':
        if str(id) in fort_alert_check:
            lastpress = fort_alert_check[str(id)]
        else:
            lastpress = None
            fort_alert_check[str(id)] = datetime.now()

        if lastpress is not None:
            difftime = datetime.now() - lastpress
            seconds = difftime.total_seconds()
            minutes = divmod(seconds, 300)[0]
            if minutes == 0:
                return True
            else:
                fort_alert_check[str(id)] = datetime.now()
                return False

    if lastpress is not None:
        difftime = datetime.now() - lastpress
        if difftime.days == 0:
            return True

    return False


@run_async
def kickmsg_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    if args is None or len(args) != 1 or not args[0].isdigit():
        return

    if last_run(chat_id, 'kickmsg') and is_staff(user_id) is False:
        bot.sendMessage(
            chat_id=chat_id,
            text="Hace menos de un dia que se usó el comando.",
            parse_mode=telegram.ParseMode.MARKDOWN)
        return

    kick = 0
    msg_number = int(args[0])
    users = get_users_from_group(chat_id)
    for user in users:
        time.sleep(0.05)
        try:
            data = bot.get_chat_member(chat_id, user.user_id)
        except:
            data = None
            pass

        if data and data.status not in ['kicked', 'left'] and not data.user.is_bot and user.total_messages < msg_number:
            try:
                bot.kickChatMember(chat_id, user.user_id)
                bot.unbanChatMember(chat_id, user.user_id)
                kick += 1
            except:
                pass

    bot.sendMessage(
        chat_id=chat_id,
        text="Han sido expulsados {} usuarios.".format(kick),
        parse_mode=telegram.ParseMode.MARKDOWN)


@run_async
def kickold_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)
    
    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    if args is None or len(args) != 1 or not args[0].isdigit():
        return

    if last_run(chat_id, 'kickold') and is_staff(user_id) is False:
        bot.sendMessage(
            chat_id=chat_id,
            text="Hace menos de un dia que se usó el comando.",
            parse_mode=telegram.ParseMode.MARKDOWN)
        return


    kick = 0
    days = int(args[0])
    start = datetime.utcnow()
    users = get_users_from_group(chat_id)
    for user in users:
        time.sleep(0.05)
        try:
            data = bot.get_chat_member(chat_id, user.user_id)
        except:
            data = None
            pass
        if data and data.status not in ['kicked', 'left'] and not data.user.is_bot:
            date = start - user.last_message
            if date.days >= days:
                try:
                    bot.kickChatMember(chat_id, user.user_id)
                    bot.unbanChatMember(chat_id, user.user_id)
                    kick += 1
                except:
                    pass

    bot.sendMessage(
        chat_id=chat_id,
        text="Han sido expulsados {} usuarios.".format(kick),
        parse_mode=telegram.ParseMode.MARKDOWN)


@run_async
def uv_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if (not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id)) and is_staff(user_id) is False:
        return

    if last_run(chat_id, 'uv') and is_staff(user_id) is False:
        bot.sendMessage(
            chat_id=chat_id,
            text="Hace menos de un dia que se usó el comando.",
            parse_mode=telegram.ParseMode.HTML)
        return

    unique = outn = uv = g = h = r = s = a = m = p = n = i = 0
    print_ = print_uv = print_g = print_h = print_r = print_s = print_n = print_a = print_m = print_p = print_i = False

    if args is not None and len(args) > 0:
        for arg in args:
            arg = arg.lower()
            if arg == "u":
                print_uv = print_ = True
            elif arg == "n":
                print_n = print_ = True
            elif arg == "i":
                print_i = print_ = True
            elif arg == "g":
                print_g = print_ = True
            elif arg == "h":
                print_h = print_ = True
            elif arg == "r":
                print_r = print_ = True
            elif arg == "s":
                print_s = print_ = True
            elif arg == "a":
                print_a = print_ = True
            elif arg == "m":
                print_m = print_ = True
            elif arg == "p":
                print_p = print_ = True

    output = ''
    if print_:
        output = 'Listado de usuarios:\n'
    users = get_users_from_group(chat_id)
    tlgrm = bot.get_chat_members_count(chat_id)

    for user in users:
        try:
            data = bot.get_chat_member(chat_id, user.user_id)
        except:
            data = None
            pass

        if data and data.status not in ['kicked', 'left'] and not data.user.is_bot:
            unique += 1
            info = get_user(user.user_id)
            icon = ''
            if info is None:
                uv += 1
                if print_ and print_uv:
                    output = output + ' <a href="tg://user?id={1}">❌{0}</a>'.format(
                        escape_markdown(data.user.first_name), user.user_id)
                    outn += 1
                if outn == 100:
                    bot.sendMessage(
                        chat_id=chat_id,
                        text=output,
                        parse_mode=telegram.ParseMode.HTML)
                    output = ''
                    outn = 0
                continue
            elif info.house is Houses.NONE.value and (info.level is None or info.profession is Professions.NONE.value or info.profession_level is None):
                n += 1
                if print_n:
                    icon = icon + '🖤'
                    outn += 1
            elif info.house is Houses.NONE.value:
                i += 1
                if print_i:
                    icon = icon + '🙈'
                    outn += 1
            elif info.house is Houses.GRYFFINDOR.value:
                g += 1
                if print_g:
                    icon = icon + '🦁'
                    outn += 1
            elif info.house is Houses.HUFFLEPUFF.value:
                h += 1
                if print_h:
                    icon = icon + '🦡'
                    outn += 1
            elif info.house is Houses.RAVENCLAW.value:
                r += 1
                if print_r:
                    icon = icon + '🦅'
                    outn += 1
            elif info.house is Houses.SLYTHERIN.value:
                s += 1
                if print_s:
                    icon = icon + '🐍'
                    outn += 1
            if info.profession is Professions.AUROR.value:
                a += 1
                if print_a:
                    icon = icon + '⚔️'
                    outn += 1
            elif info.profession is Professions.MAGIZOOLOGIST.value:
                m += 1
                if print_m:
                    icon = icon + '🐾'
                    outn += 1
            elif info.profession is Professions.PROFESSOR.value:
                p += 1
                if print_p:
                    icon = icon + '📚'
                    outn += 1
            if print_ and len(icon) > 0:
                output = output + ' <a href="tg://user?id={1}">{2}{0}</a>'.format(
                    escape_markdown(data.user.first_name), user.user_id, icon)
            if outn == 100:
                bot.sendMessage(
                    chat_id=chat_id,
                    text=output,
                    parse_mode=telegram.ParseMode.HTML)
                output = ''
                outn = 0

            time.sleep(0.01)

    total = uv + g + h + r + s + a + m + p + n + i
    tlgrm = tlgrm - unique - 1
    output = "🦁 Gryffindor: {}\n🦡 Hufflepuff: {}\n🦅 Ravenclaw: {}\n🐍 Slytherin: {}\n🙈 Sin Casa: {}\n⚔️ Auror: {}\n🐾 Magizoologo: {}\n📚 Profesor: {}\n🖤 Registro incompleto: {}\n❌ Sin registrar: {}\n❓ Desconocidos: {}\n".format(g, h, r, s, i, a, m, p, n, uv, tlgrm) + output
    bot.sendMessage(
        chat_id=chat_id,
        text=output,
        parse_mode=telegram.ParseMode.HTML)


@run_async
def kickuv_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if (not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id)) and is_staff(user_id) is False:
        return

    if last_run(chat_id, 'kickuv') and is_staff(user_id) is False:
        bot.sendMessage(
            chat_id=chat_id,
            text="Hace menos de un dia que se usó el comando.",
            parse_mode=telegram.ParseMode.HTML)
        return

    uv = g = h = r = s = a = m = p = n = i = False

    if args is not None and len(args) > 0:
        for arg in args:
            arg = arg.lower()
            if arg == "u":
                uv = True
            elif arg == "n":
                n = True
            elif arg == "i":
                i = True
            elif arg == "g":
                g = True
            elif arg == "h":
                h = True
            elif arg == "r":
                r = True
            elif arg == "s":
                s = True
            elif arg == "a":
                a = True
            elif arg == "m":
                m = True
            elif arg == "p":
                p = True
    else:
        uv = True
    kicked_users = 0
    users = get_users_from_group(chat_id)
    for user in users:
        try:
            data = bot.get_chat_member(chat_id, user.user_id)
        except:
            data = None
            pass
        if data and data.status not in ['kicked', 'left'] and not data.user.is_bot:
            info = get_user(user.user_id)
            if info is None:
                if uv:
                    try:
                        bot.kickChatMember(chat_id, user.user_id)
                        bot.unbanChatMember(chat_id, user.user_id)
                        kicked_users += 1
                    except:
                        pass
                    time.sleep(0.01)
            elif is_staff(user.user_id):
                pass
            elif info.house is Houses.NONE.value and (info.level is None or info.profession is Professions.NONE.value or info.profession_level is None):
                if n:
                    try:
                        bot.kickChatMember(chat_id, user.user_id)
                        bot.unbanChatMember(chat_id, user.user_id)
                        kicked_users += 1
                    except:
                        pass
                    time.sleep(0.01)
            elif info.house is Houses.NONE.value:
                if i:
                    try:
                        bot.kickChatMember(chat_id, user.user_id)
                        bot.unbanChatMember(chat_id, user.user_id)
                        kicked_users += 1
                    except:
                        pass
                    time.sleep(0.01)
            elif info.house is Houses.GRYFFINDOR.value:
                if g:
                    try:
                        bot.kickChatMember(chat_id, user.user_id)
                        bot.unbanChatMember(chat_id, user.user_id)
                        kicked_users += 1
                    except:
                        pass
                    time.sleep(0.01)
            elif info.house is Houses.HUFFLEPUFF.value:
                if h:
                    try:
                        bot.kickChatMember(chat_id, user.user_id)
                        bot.unbanChatMember(chat_id, user.user_id)
                        kicked_users += 1
                    except:
                        pass
                    time.sleep(0.01)
            elif info.house is Houses.RAVENCLAW.value:
                if r:
                    try:
                        bot.kickChatMember(chat_id, user.user_id)
                        bot.unbanChatMember(chat_id, user.user_id)
                        kicked_users += 1
                    except:
                        pass
                    time.sleep(0.01)
            elif info.house is Houses.SLYTHERIN.value:
                if s:
                    try:
                        bot.kickChatMember(chat_id, user.user_id)
                        bot.unbanChatMember(chat_id, user.user_id)
                        kicked_users += 1
                    except:
                        pass
                    time.sleep(0.01)
            elif info.profession is Professions.AUROR.value:
                if a:
                    try:
                        bot.kickChatMember(chat_id, user.user_id)
                        bot.unbanChatMember(chat_id, user.user_id)
                        kicked_users += 1
                    except:
                        pass
                    time.sleep(0.01)
            elif info.profession is Professions.MAGIZOOLOGIST.value:
                if mute_cmd:
                    try:
                        bot.kickChatMember(chat_id, user.user_id)
                        bot.unbanChatMember(chat_id, user.user_id)
                        kicked_users += 1
                    except:
                        pass
                    time.sleep(0.01)
            elif info.profession is Professions.PROFESSOR.value:
                if p:
                    try:
                        bot.kickChatMember(chat_id, user.user_id)
                        bot.unbanChatMember(chat_id, user.user_id)
                        kicked_users += 1
                    except:
                        pass
                    time.sleep(0.01)

    bot.sendMessage(
        chat_id=chat_id,
        text="Han sido expulsados {} usuarios.".format(kicked_users),
        parse_mode=telegram.ParseMode.MARKDOWN)


@run_async
def warn_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)
    admin_user = get_user(user_id)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    reason = ""
    name = ""
    if message.reply_to_message is not None:
        if message.reply_to_message.forward_from is not None:
            if args is not None and len(args)!=0 and args[0] is "f":
                replied_user = message.reply_to_message.from_user.id
                name = message.reply_to_message.from_user.first_name
                del args[0]
            else:
                replied_user = message.reply_to_message.forward_from.id
                name = message.reply_to_message.forward_from.first_name
        elif message.reply_to_message.from_user is not None:
            replied_user = message.reply_to_message.from_user.id
            name = message.reply_to_message.from_user.first_name
        if args and len(args) > 0:
            reason = ' '.join(args)
    elif args is not None and len(args) > 0:
        if len(args) > 1 and args[0][0] is '-':
            if adm_sql.get_linked_admin(chat_id, args[0]):
                chat_id = args[0]
                del args[0]
            else:
                bot.sendMessage(
                    chat_id=chat_id,
                    text="❌ Ese grupo no esta vinculado a este",
                    parse_mode=telegram.ParseMode.MARKDOWN)
                return
        if args[0].isdigit():
            user = get_user(args[0])
            if user and user.alias:
                name = user.alias
            else:
                name = args[0]
            replied_user = args[0]
            del args[0]
        else:
            args[0] = re.sub("@", "", args[0])
            user = get_user_by_name(args[0])
            del args[0]
            if user:
                name = user.alias
                replied_user = user.id
            else:
                return
    else:
        return

    if args is not None and len(args) > 0:
        reason = " ".join(args)

    if adm_sql.get_admin(chat_id) is not None:
        groups = adm_sql.get_all_groups(chat_id)
    else:
        groups = None

    if groups is None:
        if not exists_user_group(replied_user, chat_id):
            set_user_group(replied_user, chat_id)

        warning = warn_user(chat_id, replied_user, 1)
        group = get_group_settings(chat_id)
        if warning < group.warn:
            output = "👌 Mago [{0}](tg://user?id={1}) advertido correctamente! {2}/{3}".format(name, replied_user, warning, group.warn)
            if reason is not "":
                output = output + "\nMotivo: {}".format(reason)
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Eliminar warn", callback_data='rm_warn({})'.format(replied_user))]])
            bot.sendMessage(
                chat_id=chat_id, 
                text=output,
                parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup=keyboard)
        else:
            output = "👌 Mago {} baneado correctamente!\nAlcanzado número máximo de advertencias.".format(name)
            if reason is not "":
                output = output + "\nMotivo: {}".format(reason)

            warn_user(chat_id, replied_user, 0)
            try:
                bot.kickChatMember(chat_id, replied_user)
                if group.hard is False:
                    bot.unbanChatMember(chat_id, replied_user)
                bot.sendMessage(
                    chat_id=chat_id,
                    text=output,
                    parse_mode=telegram.ParseMode.MARKDOWN)
            except:
                output = "❌ No tengo los permisos necesarios"
                bot.sendMessage(
                    chat_id=chat_id,
                    text=output,
                    parse_mode=telegram.ParseMode.MARKDOWN)
                return

        ladmin = adm_sql.get_particular_admin(chat_id)
        if ladmin is not None and ladmin.ejections:
            chat = bot.get_chat(chat_id)
            admin = adm_sql.get_admin_from_linked(chat_id)
            if admin is not None and admin.ejections and admin.admin_bot:
                config = get_config()
                adm_bot = Bot(token=config["telegram"]["admin_token"])
                replace_pogo = support.replace(replied_user, name, admin=True)
                message_text="ℹ️ {}\n👤 {} ha sido advertido por @{} {}/{}".format(chat.title, replace_pogo, admin_user.alias, warning, group.warn)
                if reason is not "":
                    message_text = message_text + "\n❔ Motivo: {}".format(reason)
                adm_bot.sendMessage(
                    chat_id=admin.id,
                    text=message_text,
                    parse_mode=telegram.ParseMode.MARKDOWN)
            elif admin is not None and admin.ejections :
                replace_pogo = support.replace(replied_user, name, admin=True)
                message_text="ℹ️ {}\n👤 {} ha sido advertido por @{} {}/{}".format(chat.title, replace_pogo, admin_user.alias, warning, group.warn)
                if reason is not "":
                    message_text = message_text + "\n❔ Motivo: {}".format(reason)
                bot.sendMessage(
                    chat_id=admin.id,
                    text=message_text,
                    parse_mode=telegram.ParseMode.MARKDOWN)

    else:
        admin_chat_id = chat_id
        replace_pogo = support.replace(replied_user, name, admin=True)
        warnText = f"👤 {replace_pogo}"
        if reason is not '':
            warnText = warnText + '\n❔ Motivo: {}'.format(reason)
        warnText = warnText + "\nℹ️ @{} ha advertido al mago de:".format(admin_user.alias)
        successBool = False
        errorBool = False
        for group in groups:
            chat_id = group.linked_id
            group = get_group(chat_id)
            group_title = group.title
            if not exists_user_group(replied_user, chat_id):
                set_user_group(replied_user, chat_id)

            warning = warn_user(chat_id, replied_user, 1)
            group = get_group_settings(chat_id)
            if warning < group.warn:
                warnText = warnText + "\n- {0} | {1}/{2}".format(group_title, warning, group.warn)
            else:
                warnText = warnText + "\n- {0} | {1}/{2}".format(group_title, warning, group.warn)
                success = f"👤 {replace_pogo} \n❔ Motivo: Alcanzado el número máximo de advertencias.\nℹ️ Mago baneado correctamente de:"
                error = f"👤 {replace_pogo}\n❌ No he podido banear al mago de:"

                warn_user(chat_id, replied_user, 0)
                try:
                    bot.kickChatMember(chat_id, replied_user)
                    if group.hard is False:
                        bot.unbanChatMember(chat_id, replied_user)
                    successBool = True
                    success = success + "\n- {}".format(group_title)
                except:
                    errorBool = True
                    error = error + "\n- {}".format(group_title)
                    continue

        ladmin = adm_sql.get_particular_admin(chat_id)
        if ladmin is not None and ladmin.ejections:
            admin = adm_sql.get_admin_from_linked(chat_id)
            chat = bot.get_chat(chat_id)
            if admin is not None and admin.ejections and admin.admin_bot:
                config = get_config()
                adm_bot = Bot(token=config["telegram"]["admin_token"])
                adm_bot.send_message(chat_id=admin_chat_id, text=warnText, parse_mode=telegram.ParseMode.MARKDOWN)
                
                if successBool == True:
                    adm_bot.send_message(chat_id=admin_chat_id, text=success, parse_mode=telegram.ParseMode.MARKDOWN)
                
                if errorBool == True:
                    error = error + "\n\nPuede que sea administrador o que yo no tenga los permisos de administración necesarios. (Borrar y expulsar)"
                    adm_bot.send_message(chat_id=admin_chat_id, text=error, parse_mode=telegram.ParseMode.MARKDOWN)
            elif admin is not None and admin.ejections :
                bot.send_message(chat_id=admin_chat_id, text=warnText, parse_mode=telegram.ParseMode.MARKDOWN)
                
                if successBool == True:
                    bot.send_message(chat_id=admin_chat_id, text=success, parse_mode=telegram.ParseMode.MARKDOWN)
                
                if errorBool == True:
                    error = error + "\n\nPuede que sea administrador o que yo no tenga los permisos de administración necesarios. (Borrar y expulsar)"
                    bot.send_message(chat_id=admin_chat_id, text=error, parse_mode=telegram.ParseMode.MARKDOWN)
                    


@run_async
def kick_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)
    admin_user = get_user(user_id)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    reason = ""
    name = ""
    if message.reply_to_message is not None:
        if message.reply_to_message.forward_from is not None:
            if args is not None and len(args)!=0 and args[0] is "f":
                replied_user = message.reply_to_message.from_user.id
                name = message.reply_to_message.from_user.first_name
                del args[0]
            else:
                replied_user = message.reply_to_message.forward_from.id
                name = message.reply_to_message.forward_from.first_name
        elif message.reply_to_message.from_user is not None:
            replied_user = message.reply_to_message.from_user.id
            name = message.reply_to_message.from_user.first_name
        if args and len(args) > 0:
            reason = ' '.join(args)
    elif args is not None and len(args) > 0:
        if len(args) > 1 and args[0][0] is '-':
            if adm_sql.get_linked_admin(chat_id, args[0]):
                chat_id = args[0]
                del args[0]
            else: 
                bot.sendMessage(
                    chat_id=chat_id,
                    text="❌ Ese grupo no esta vinculado a este",
                    parse_mode=telegram.ParseMode.MARKDOWN)
                return
        if args[0].isdigit():
            user = get_user(args[0])
            if user and user.alias:
                name = user.alias
            else:
                name = args[0]
            replied_user = args[0]
            del args[0]
        else:
            args[0] = re.sub("@", "", args[0])
            user = get_user_by_name(args[0])
            del args[0]
            if user:
                name = user.alias
                replied_user = user.id
            else:
                return
    else:
        return

    if args is not None and len(args) > 0:
        reason = ' '.join(args)

    if adm_sql.get_admin(chat_id) is not None:
        groups = adm_sql.get_all_groups(chat_id)
    else:
        groups = None

    if groups is None:
        try:
            bot.kickChatMember(chat_id, replied_user)
            bot.unbanChatMember(chat_id, replied_user)
            output = "👌 Mago {} expulsado correctamente!".format(name)
            if reason is not "":
                output = output + "\nMotivo: {}".format(reason)
            bot.sendMessage(
                chat_id=chat_id,
                text=output,
                parse_mode=telegram.ParseMode.MARKDOWN)
        except:
            bot.sendMessage(
                chat_id=chat_id,
                text="❌ No he podido expulsar al Mago. Puede que sea administrador o ya no forme parte del grupo.",
                parse_mode=telegram.ParseMode.MARKDOWN)
            return

        ladmin = adm_sql.get_particular_admin(chat_id)
        if ladmin is not None and ladmin.ejections:
            admin = adm_sql.get_admin_from_linked(chat_id)
            chat = bot.get_chat(chat_id)
            if admin is not None and admin.ejections and admin.admin_bot:
                config = get_config()
                adm_bot = Bot(token=config["telegram"]["admin_token"])
                replace_pogo = support.replace(replied_user, name, admin=True)
                message_text="ℹ️ {}\n👤 {} ha sido expulsado por @{}".format(chat.title, replace_pogo, admin_user.alias)
                if reason is not "":
                    message_text = message_text + "\n❔ Motivo: {}".format(reason)
                adm_bot.sendMessage(
                    chat_id=admin.id,
                    text=message_text,
                    parse_mode=telegram.ParseMode.MARKDOWN)
            elif admin is not None and admin.ejections :
                replace_pogo = support.replace(replied_user, name, admin=True)
                message_text="ℹ️ {}\n👤 {} ha sido expulsado por @{}".format(chat.title, replace_pogo, admin_user.alias)
                if reason is not "":
                    message_text = message_text + "\n❔ Motivo: {}".format(reason)
                bot.sendMessage(
                    chat_id=admin.id,
                    text=message_text,
                    parse_mode=telegram.ParseMode.MARKDOWN)

    else:
        admin_chat_id = chat_id
        replace_pogo = support.replace(replied_user, name, admin=True)
        success = f"👤 {replace_pogo}"
        if reason is not '':
            success = success + '\n❔ Motivo: {}'.format(reason)
        success = success + "\nℹ️ @{} ha expulsado al mago de:".format(admin_user.alias)
        successBool = False
        error = f"👤 {replace_pogo}\n❌ No he podido expulsar al mago de:"
        errorBool = False
        for group in groups:
            chat_id = group.linked_id
            group = get_group(chat_id)
            try:
                bot.kickChatMember(chat_id, replied_user)
                bot.unbanChatMember(chat_id, replied_user)
                successBool = True
                success = success + "\n- {}".format(group.title)
            except:
                errorBool = True
                error = error + "\n- {}".format(group.title)
                continue

        ladmin = adm_sql.get_particular_admin(chat_id)
        if ladmin is not None and ladmin.ejections:
            chat = bot.get_chat(chat_id)
            admin = adm_sql.get_admin_from_linked(chat_id)
            if admin is not None and admin.ejections and admin.admin_bot:
                config = get_config()
                adm_bot = Bot(token=config["telegram"]["admin_token"])
                replace_pogo = support.replace(replied_user, name, admin=True)
                if successBool == True:
                    adm_bot.send_message(chat_id=admin_chat_id, text=success,
                                        parse_mode=telegram.ParseMode.MARKDOWN)

                if errorBool == True:
                    error = error + "\n\nPuede que sea administrador o que yo no tenga los permisos de administración necesarios. (Borrar y expulsar)"
                    adm_bot.send_message(chat_id=admin_chat_id, text=error,
                                        parse_mode=telegram.ParseMode.MARKDOWN)
            elif admin is not None and admin.ejections :
                replace_pogo = support.replace(replied_user, name, admin=True)
                if successBool == True:
                    bot.send_message(chat_id=admin_chat_id, text=success,
                                        parse_mode=telegram.ParseMode.MARKDOWN)

                if errorBool == True:
                    error = error + "\n\nPuede que sea administrador o que yo no tenga los permisos de administración necesarios. (Borrar y expulsar)"
                    bot.send_message(chat_id=admin_chat_id, text=error,
                                        parse_mode=telegram.ParseMode.MARKDOWN)

@run_async
def ban_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)
    admin_user = get_user(user_id)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    reason = ""
    name = ""
    if message.reply_to_message is not None:
        if message.reply_to_message.forward_from is not None:
            if args is not None and len(args)!=0 and args[0] is "f":
                replied_user = message.reply_to_message.from_user.id
                name = message.reply_to_message.from_user.first_name
                del args[0]
            else:
                replied_user = message.reply_to_message.forward_from.id
                name = message.reply_to_message.forward_from.first_name
        elif message.reply_to_message.from_user is not None:
            replied_user = message.reply_to_message.from_user.id
            name = message.reply_to_message.from_user.first_name
        logging.debug('%s', args)
        if args and len(args) > 0:
            reason = ' '.join(args)
    elif args is not None and len(args) > 0:
        if len(args) > 1 and args[0][0] is '-':
            if adm_sql.get_linked_admin(chat_id, args[0]):
                chat_id = args[0]
                del args[0]
            else:
                bot.sendMessage(
                    chat_id=chat_id,
                    text="❌ Ese grupo no esta vinculado a este",
                    parse_mode=telegram.ParseMode.MARKDOWN)
                return
        if args[0].isdigit():
            user = get_user(args[0])
            if user and user.alias:
                name = user.alias
            else:
                name = args[0]
            replied_user = args[0]
            del args[0]
        else:
            args[0] = re.sub("@", "", args[0])
            user = get_user_by_name(args[0])
            del args[0]
            if user:
                name = user.alias
                replied_user = user.id
            else:
                return
    else:
        return

    if args is not None and len(args) > 0:
        reason = ' '.join(args)

    if adm_sql.get_admin(chat_id) is not None:
        groups = adm_sql.get_all_groups(chat_id)
    else:
        groups = None

    if groups is None:
        try:
            bot.kickChatMember(chat_id, replied_user)
            output = "👌 Mago {} baneado correctamente!".format(name)
            if reason is not '':
                output = output + "\nMotivo: {}".format(reason)
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Eliminar Ban", callback_data='rm_ban({})'.format(replied_user))]])
            bot.sendMessage(
                chat_id=chat_id,
                text=output,
                parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup=keyboard)
        except:
            bot.sendMessage(
                chat_id=chat_id,
                text="❌ No he podido banear al Mago. Puede que sea administrador.",
                parse_mode=telegram.ParseMode.MARKDOWN)
            return

        ladmin = adm_sql.get_particular_admin(chat_id)
        if ladmin is not None and ladmin.ejections:
            chat = bot.get_chat(chat_id)
            admin = adm_sql.get_admin_from_linked(chat_id)
            if admin is not None and admin.ejections and admin.admin_bot:
                config = get_config()
                adm_bot = Bot(token=config["telegram"]["admin_token"])
                replace_pogo = support.replace(replied_user, name, admin=True)
                message_text="ℹ️ {}\n👤 {} ha sido baneado por @{}".format(chat.title, replace_pogo, admin_user.alias)
                if reason is not "":
                    message_text = message_text + "\n❔ Motivo: {}".format(reason)
                adm_bot.sendMessage(
                    chat_id=admin.id,
                    text=message_text,
                    parse_mode=telegram.ParseMode.MARKDOWN)
            elif admin is not None and admin.ejections :
                replace_pogo = support.replace(replied_user, name, admin=True)
                message_text="ℹ️ {}\n👤 {} ha sido baneado por @{}".format(chat.title, replace_pogo, admin_user.alias)
                if reason is not "":
                    message_text = message_text + "\n❔ Motivo: {}".format(reason)
                bot.sendMessage(
                    chat_id=admin.id,
                    text=message_text,
                    parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        admin_chat_id = chat_id
        replace_pogo = support.replace(replied_user, name, admin=True)
        success = f"👤 {replace_pogo}"
        if reason is not '':
            success = success + '\n❔ Motivo: {}'.format(reason)
        success = success + "\nℹ️ @{} ha baneado al mago de:".format(admin_user.alias)
        successBool = False
        error = f"👤 {replace_pogo}\n❌ No he podido banear al mago de:"
        errorBool = False
        for group in groups:
            chat_id = group.linked_id
            group = get_group(chat_id)
            try:
                bot.kickChatMember(chat_id, replied_user)
                successBool = True
                success = success + "\n- {}".format(group.title)
            except:
                errorBool = True
                error = error + "\n- {}".format(group.title)
                continue

        ladmin = adm_sql.get_particular_admin(chat_id)
        if ladmin is not None and ladmin.ejections:
            chat = bot.get_chat(chat_id)
            admin = adm_sql.get_admin_from_linked(chat_id)
            if admin is not None and admin.ejections and admin.admin_bot:
                config = get_config()
                adm_bot = Bot(token=config["telegram"]["admin_token"])
                replace_pogo = support.replace(replied_user, name, admin=True)
                if successBool == True:
                    adm_bot.send_message(chat_id=admin_chat_id, text=success,
                                        parse_mode=telegram.ParseMode.MARKDOWN)

                if errorBool == True:
                    error = error + "\n\nPuede que sea administrador o que yo no tenga los permisos de administración necesarios. (Borrar y expulsar)"
                    adm_bot.send_message(chat_id=admin_chat_id, text=error,
                                        parse_mode=telegram.ParseMode.MARKDOWN)
            elif admin is not None and admin.ejections :
                replace_pogo = support.replace(replied_user, name, admin=True)
                if successBool == True:
                    bot.send_message(chat_id=admin_chat_id, text=success,
                                        parse_mode=telegram.ParseMode.MARKDOWN)

                if errorBool == True:
                    error = error + "\n\nPuede que sea administrador o que yo no tenga los permisos de administración necesarios. (Borrar y expulsar)"
                    bot.send_message(chat_id=admin_chat_id, text=error,
                                        parse_mode=telegram.ParseMode.MARKDOWN)


@run_async
def unban_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)
    admin_user = get_user(user_id)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    reason = ""
    name = ""
    if message.reply_to_message is not None:
        if message.reply_to_message.forward_from is not None:
            if args is not None and len(args)!=0 and args[0] is "f":
                replied_user = message.reply_to_message.from_user.id
                name = message.reply_to_message.from_user.first_name
                del args[0]
            else:
                replied_user = message.reply_to_message.forward_from.id
                name = message.reply_to_message.forward_from.first_name
        elif message.reply_to_message.from_user is not None:
            replied_user = message.reply_to_message.from_user.id
            name = message.reply_to_message.from_user.first_name
        if args and len(args) > 0:
            reason = ' '.join(args)
    elif args is not None and len(args) > 0:
        if len(args) > 1 and args[0][0] is '-':
            if adm_sql.get_linked_admin(chat_id, args[0]):
                chat_id = args[0]
                del args[0]
            else: 
                bot.sendMessage(
                    chat_id=chat_id,
                    text="❌ Ese grupo no esta vinculado a este",
                    parse_mode=telegram.ParseMode.MARKDOWN)
                return
        if args[0].isdigit():
            user = get_user(args[0])
            if user and user.alias:
                name = user.alias
            else:
                name = args[0]
            replied_user = args[0]
            del args[0]
        else:
            args[0] = re.sub("@", "", args[0])
            user = get_user_by_name(args[0])
            del args[0]
            if user:
                name = user.alias
                replied_user = user.id
            else:
                return
    else:
        return

    if args is not None and len(args) > 0:
        reason = ' '.join(args)

    if adm_sql.get_admin(chat_id) is not None:
        groups = adm_sql.get_all_groups(chat_id)
    else:
        groups = None

    if groups is None:
        try:
            bot.unbanChatMember(chat_id, replied_user)
            output = "👌 Mago {} desbaneado correctamente!".format(name)
            if reason is not "":
                output = output + "\nMotivo: {}".format(reason)
            bot.sendMessage(
                chat_id=chat_id,
                text=output,
                parse_mode=telegram.ParseMode.MARKDOWN)
        except:
            bot.sendMessage(
                chat_id=chat_id,
                text="❌ No he podido desbanear al Mago. Puede que sea administrador o ya no forme parte del grupo.",
                parse_mode=telegram.ParseMode.MARKDOWN)
            return

        ladmin = adm_sql.get_particular_admin(chat_id)
        if ladmin is not None and ladmin.ejections:
            admin = adm_sql.get_admin_from_linked(chat_id)
            chat = bot.get_chat(chat_id)
            if admin is not None and admin.ejections and admin.admin_bot:
                config = get_config()
                adm_bot = Bot(token=config["telegram"]["admin_token"])
                replace_pogo = support.replace(replied_user, name, admin=True)
                message_text="ℹ️ {}\n👤 {} ha sido desbaneado por @{}".format(chat.title, replace_pogo, admin_user.alias)
                if reason is not "":
                    message_text = message_text + "\n❔ Motivo: {}".format(reason)
                adm_bot.sendMessage(
                    chat_id=admin.id,
                    text=message_text,
                    parse_mode=telegram.ParseMode.MARKDOWN)
            elif admin is not None and admin.ejections :
                replace_pogo = support.replace(replied_user, name, admin=True)
                message_text="ℹ️ {}\n👤 {} ha sido desbaneado por @{}".format(chat.title, replace_pogo, admin_user.alias)
                if reason is not "":
                    message_text = message_text + "\n❔ Motivo: {}".format(reason)
                bot.sendMessage(
                    chat_id=admin.id,
                    text=message_text,
                    parse_mode=telegram.ParseMode.MARKDOWN)

    else:
        admin_chat_id = chat_id
        replace_pogo = support.replace(replied_user, name, admin=True)
        success = f"👤 {replace_pogo}"
        if reason is not '':
            success = success + '\n❔ Motivo: {}'.format(reason)
        success = success + "\nℹ️ @{} ha desbaneado al mago de:".format(admin_user.alias)
        successBool = False
        error = f"👤 {replace_pogo}\n❌ No he podido desbanear al mago de:"
        errorBool = False
        for group in groups:
            chat_id = group.linked_id
            group = get_group(chat_id)
            try:
                bot.unbanChatMember(chat_id, replied_user)
                successBool = True
                success = success + "\n- {}".format(group.title)
            except:
                errorBool = True
                error = error + "\n- {}".format(group.title)
                continue

        ladmin = adm_sql.get_particular_admin(chat_id)
        if ladmin is not None and ladmin.ejections:
            chat = bot.get_chat(chat_id)
            admin = adm_sql.get_admin_from_linked(chat_id)
            if admin is not None and admin.ejections and admin.admin_bot:
                config = get_config()
                adm_bot = Bot(token=config["telegram"]["admin_token"])
                replace_pogo = support.replace(replied_user, name, admin=True)
                if successBool == True:
                    adm_bot.send_message(chat_id=admin_chat_id, text=success,
                                        parse_mode=telegram.ParseMode.MARKDOWN)

                if errorBool == True:
                    error = error + "\n\nPuede que sea administrador o que yo no tenga los permisos de administración necesarios. (Borrar y expulsar)"
                    adm_bot.send_message(chat_id=admin_chat_id, text=error,
                                        parse_mode=telegram.ParseMode.MARKDOWN)
            elif admin is not None and admin.ejections :
                replace_pogo = support.replace(replied_user, name, admin=True)
                if successBool == True:
                    bot.send_message(chat_id=admin_chat_id, text=success,
                                        parse_mode=telegram.ParseMode.MARKDOWN)

                if errorBool == True:
                    error = error + "\n\nPuede que sea administrador o que yo no tenga los permisos de administración necesarios. (Borrar y expulsar)"
                    bot.send_message(chat_id=admin_chat_id, text=error,
                                        parse_mode=telegram.ParseMode.MARKDOWN)


@run_async
def mute_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    name = ""
    if message.reply_to_message is not None:
        if message.reply_to_message.forward_from is not None:
            if args is not None and len(args)!=0 and args[0] is "f":
                replied_user = message.reply_to_message.from_user.id
                name = message.reply_to_message.from_user.first_name
                del args[0]
            else:
                replied_user = message.reply_to_message.forward_from.id
                name = message.reply_to_message.forward_from.first_name
        elif message.reply_to_message.from_user is not None:
            replied_user = message.reply_to_message.from_user.id
            name = message.reply_to_message.from_user.first_name
        logging.debug('%s', args)
    elif args is not None and len(args) > 0:
        if len(args) > 1 and args[0][0] is '-':
            if adm_sql.get_linked_admin(chat_id, args[0]):
                chat_id = args[0]
                del args[0]
            else:
                bot.sendMessage(
                    chat_id=chat_id,
                    text="❌ Ese grupo no esta vinculado a este",
                    parse_mode=telegram.ParseMode.MARKDOWN)
                return
        if args[0].isdigit():
            user = get_user(args[0])
            if user and user.alias:
                name = user.alias
            else:
                name = args[0]
            replied_user = args[0]
            del args[0]
        else:
            args[0] = re.sub("@", "", args[0])
            user = get_user_by_name(args[0])
            del args[0]
            if user:
                name = user.alias
                replied_user = user.id
            else:
                return
    else:
        return

    if args is not None and len(args) > 0:
        r = re.search(r'^\d+[smhd]$', args[0])
        print(args)
        if r is not None:
            if args[0][-1].lower() == "s":
                time = datetime.now() + timedelta(seconds=int(args[0][:-1]))
            elif args[0][-1].lower() == "m":
                time = datetime.now() + timedelta(minutes=int(args[0][:-1]))
            elif args[0][-1].lower() == "h":
                time = datetime.now() + timedelta(hours=int(args[0][:-1]))
            elif args[0][-1].lower() == "d":
                time = datetime.now() + timedelta(days=int(args[0][:-1]))
            try:
                if args[1].lower() == "media":
                    text = True
            except:
                text = False
        elif args[0].lower() == "media":
            text = True
            try:
                if args[1][-1].lower() == "s":
                    time = datetime.now() + timedelta(seconds=int(args[1][:-1]))
                elif args[1][-1].lower() == "m":
                    time = datetime.now() + timedelta(minutes=int(args[1][:-1]))
                elif args[1][-1].lower() == "h":
                    time = datetime.now() + timedelta(hours=int(args[1][:-1]))
                elif args[1][-1].lower() == "d":
                    time = datetime.now() + timedelta(days=int(args[1][:-1]))
            except:
                time = None
    else:
        text = False
        time = None

    if adm_sql.get_admin(chat_id) is not None:
        groups = adm_sql.get_all_groups(chat_id)
    else:
        groups = None

    if groups is None:
        try:
            bot.restrict_chat_member(chat_id, replied_user, until_date=time, can_send_messages=text, can_send_media_messages=False, can_send_other_messages=False, can_add_web_page_previews=False)
            output = "👌 Mago {} muteado correctamente!".format(name)
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Desmutear", callback_data='rm_mute({})'.format(replied_user))]])
            bot.sendMessage(
                chat_id=chat_id,
                text=output,
                parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup=keyboard)
        except:
            bot.sendMessage(
                chat_id=chat_id,
                text="❌ No he podido mutear al Mago. Puede que sea administrador.",
                parse_mode=telegram.ParseMode.MARKDOWN)
            return

        ladmin = adm_sql.get_particular_admin(chat_id)
        if ladmin is not None and ladmin.ejections:
            chat = bot.get_chat(chat_id)
            admin = adm_sql.get_admin_from_linked(chat_id)
            if admin is not None and admin.ejections and admin.admin_bot:
                config = get_config()
                adm_bot = Bot(token=config["telegram"]["admin_token"])
                replace_pogo = support.replace(replied_user, name, admin=True)
                adm_bot.sendMessage(
                    chat_id=admin.id,
                    text="ℹ️ {}\n👤 {} ha sido muteado".format(chat.title, replace_pogo),
                    parse_mode=telegram.ParseMode.MARKDOWN)
            elif admin is not None and admin.ejections :
                replace_pogo = support.replace(replied_user, name, admin=True)
                bot.sendMessage(
                    chat_id=admin.id,
                    text="ℹ️ {}\n👤 {} ha sido muteado".format(chat.title, replace_pogo),
                    parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        for group in groups:
            chat_id = group.linked_id
            try:
                bot.restrict_chat_member(chat_id, replied_user, until_date=time, can_send_messages=text, can_send_media_messages=False, can_send_other_messages=False, can_add_web_page_previews=False)
                output = "👌 Mago {} muteado correctamente!".format(name)
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Desmutear", callback_data='rm_mute({})'.format(replied_user))]])
                bot.sendMessage(
                    chat_id=chat_id, 
                    text=output,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    reply_markup=keyboard)
            except:
                bot.sendMessage(
                    chat_id=chat_id,
                    text="❌ No he podido mutear al Mago. Puede que sea administrador.",
                    parse_mode=telegram.ParseMode.MARKDOWN)
                return

            ladmin = adm_sql.get_particular_admin(chat_id)
            if ladmin is not None and ladmin.ejections:
                chat = bot.get_chat(chat_id)
                admin = adm_sql.get_admin_from_linked(chat_id)
                if admin is not None and admin.ejections and admin.admin_bot:
                    config = get_config()
                    adm_bot = Bot(token=config["telegram"]["admin_token"])
                    replace_pogo = support.replace(replied_user, name, admin=True)
                    adm_bot.sendMessage(
                        chat_id=admin.id,
                        text="ℹ️ {}\n👤 {} ha sido muteado".format(chat.title, replace_pogo),
                        parse_mode=telegram.ParseMode.MARKDOWN)
                elif admin is not None and admin.ejections :
                    replace_pogo = support.replace(replied_user, name, admin=True)
                    bot.sendMessage(
                        chat_id=admin.id,
                        text="ℹ️ {}\n👤 {} ha sido muteado".format(chat.title, replace_pogo),
                        parse_mode=telegram.ParseMode.MARKDOWN)


@run_async
def unmute_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    name = ""
    if message.reply_to_message is not None:
        if message.reply_to_message.forward_from is not None:
            if args is not None and len(args)!=0 and args[0] is "f":
                replied_user = message.reply_to_message.from_user.id
                name = message.reply_to_message.from_user.first_name
                del args[0]
            else:
                replied_user = message.reply_to_message.forward_from.id
                name = message.reply_to_message.forward_from.first_name
        elif message.reply_to_message.from_user is not None:
            replied_user = message.reply_to_message.from_user.id
            name = message.reply_to_message.from_user.first_name
        logging.debug('%s', args)
    elif args is not None and len(args) > 0:
        if len(args) > 1 and args[0][0] is '-':
            if adm_sql.get_linked_admin(chat_id, args[0]):
                chat_id = args[0]
                del args[0]
            else:
                bot.sendMessage(
                    chat_id=chat_id,
                    text="❌ Ese grupo no esta vinculado a este",
                    parse_mode=telegram.ParseMode.MARKDOWN)
                return
        if args[0].isdigit():
            user = get_user(args[0])
            if user and user.alias:
                name = user.alias
            else:
                name = args[0]
            replied_user = args[0]
            del args[0]
        else:
            args[0] = re.sub("@", "", args[0])
            user = get_user_by_name(args[0])
            del args[0]
            if user:
                name = user.alias
                replied_user = user.id
            else:
                return
    else:
        return

    if args is not None and len(args) > 0:
        r = re.search(r'^\d+[smhd]$', args[0])
        print(args)
        if r is not None:
            if args[0][-1].lower() == "s":
                time = datetime.now() + timedelta(seconds=int(args[0][:-1]))
            elif args[0][-1].lower() == "m":
                time = datetime.now() + timedelta(minutes=int(args[0][:-1]))
            elif args[0][-1].lower() == "h":
                time = datetime.now() + timedelta(hours=int(args[0][:-1]))
            elif args[0][-1].lower() == "d":
                time = datetime.now() + timedelta(days=int(args[0][:-1]))
            try:
                if args[1].lower() == "media":
                    text = True
            except:
                text = False
        elif args[0].lower() == "media":
            text = True
            try:
                if args[1][-1].lower() == "s":
                    time = datetime.now() + timedelta(seconds=int(args[1][:-1]))
                elif args[1][-1].lower() == "m":
                    time = datetime.now() + timedelta(minutes=int(args[1][:-1]))
                elif args[1][-1].lower() == "h":
                    time = datetime.now() + timedelta(hours=int(args[1][:-1]))
                elif args[1][-1].lower() == "d":
                    time = datetime.now() + timedelta(days=int(args[1][:-1]))
            except:
                time = None
    else:
        text = False
        time = None

    if adm_sql.get_admin(chat_id) is not None:
        groups = adm_sql.get_all_groups(chat_id)
    else:
        groups = None

    if groups is None:
        try:
            bot.restrict_chat_member(chat_id, replied_user, until_date=time, can_send_messages=text, can_send_media_messages=False, can_send_other_messages=False, can_add_web_page_previews=False)
            output = "👌 Mago {} muteado correctamente!".format(name)
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Desmutear", callback_data='rm_mute({})'.format(replied_user))]])
            bot.sendMessage(
                chat_id=chat_id,
                text=output,
                parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup=keyboard)
        except:
            bot.sendMessage(
                chat_id=chat_id,
                text="❌ No he podido mutear al Mago. Puede que sea administrador.",
                parse_mode=telegram.ParseMode.MARKDOWN)
            return

        ladmin = adm_sql.get_particular_admin(chat_id)
        if ladmin is not None and ladmin.ejections:
            chat = bot.get_chat(chat_id)
            admin = adm_sql.get_admin_from_linked(chat_id)
            if admin is not None and admin.ejections and admin.admin_bot:
                config = get_config()
                adm_bot = Bot(token=config["telegram"]["admin_token"])
                replace_pogo = support.replace(replied_user, name, admin=True)
                adm_bot.sendMessage(
                    chat_id=admin.id,
                    text="ℹ️ {}\n👤 {} ha sido muteado".format(chat.title, replace_pogo),
                    parse_mode=telegram.ParseMode.MARKDOWN)
            elif admin is not None and admin.ejections :
                replace_pogo = support.replace(replied_user, name, admin=True)
                bot.sendMessage(
                    chat_id=admin.id,
                    text="ℹ️ {}\n👤 {} ha sido muteado".format(chat.title, replace_pogo),
                    parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        for group in groups:
            chat_id = group.linked_id
            try:
                bot.restrict_chat_member(chat_id, replied_user, until_date=time, can_send_messages=text, can_send_media_messages=False, can_send_other_messages=False, can_add_web_page_previews=False)
                output = "👌 Mago {} muteado correctamente!".format(name)
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Desmutear", callback_data='rm_mute({})'.format(replied_user))]])
                bot.sendMessage(
                    chat_id=chat_id, 
                    text=output,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    reply_markup=keyboard)
            except:
                bot.sendMessage(
                    chat_id=chat_id,
                    text="❌ No he podido mutear al Mago. Puede que sea administrador.",
                    parse_mode=telegram.ParseMode.MARKDOWN)
                return

            ladmin = adm_sql.get_particular_admin(chat_id)
            if ladmin is not None and ladmin.ejections:
                chat = bot.get_chat(chat_id)
                admin = adm_sql.get_admin_from_linked(chat_id)
                if admin is not None and admin.ejections and admin.admin_bot:
                    config = get_config()
                    adm_bot = Bot(token=config["telegram"]["admin_token"])
                    replace_pogo = support.replace(replied_user, name, admin=True)
                    adm_bot.sendMessage(
                        chat_id=admin.id,
                        text="ℹ️ {}\n👤 {} ha sido muteado".format(chat.title, replace_pogo),
                        parse_mode=telegram.ParseMode.MARKDOWN)
                elif admin is not None and admin.ejections :
                    replace_pogo = support.replace(replied_user, name, admin=True)
                    bot.sendMessage(
                        chat_id=admin.id,
                        text="ℹ️ {}\n👤 {} ha sido muteado".format(chat.title, replace_pogo),
                        parse_mode=telegram.ParseMode.MARKDOWN)

@run_async
def whois_id(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or are_banned(user_id, chat_id):
        return

    if args is not None and len(args)== 1:
        args[0] = re.sub("@", "", args[0])
        user = get_user_by_name(args[0])
        if user is not None:
            replied_id = user.id
        elif args[0].isdigit():
            user = get_user(args[0])
            replied_id = user.id
        else:
                output = "❌ No he encontrado el mago que buscas."
                bot.sendMessage(
                    chat_id=chat_id,
                    text=output,
                    parse_mode=telegram.ParseMode.MARKDOWN
                )
                return
    elif message.reply_to_message is not None:
        if message.reply_to_message.forward_from is not None:
            user = get_user(message.reply_to_message.forward_from.id)
            if user is not None:
                replied_id = user.id
            else:
                output = "❌ No he encontrado el mago que buscas."
                bot.sendMessage(
                    chat_id=chat_id,
                    text=output,
                    parse_mode=telegram.ParseMode.MARKDOWN
                )
                return
        elif message.reply_to_message.from_user is not None:
            user = get_user(message.reply_to_message.from_user.id)
            if user is not None:
                replied_id = user.id
            else:
                output = "❌ No he encontrado el mago que buscas."
                bot.sendMessage(
                    chat_id=chat_id,
                    text=output,
                    parse_mode=telegram.ParseMode.MARKDOWN
                )
                return
    else:
        output = "❌ No has especificado ningún mago."
        bot.sendMessage(
            chat_id=chat_id,
            text=output,
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return
    if user and user.alias is not None:
        text_alias = escape_markdown("@{}".format(user.alias))
    elif user.alias is None:
        text_alias = f"[{escape_markdown(user.first_name)}](tg://user?id={user_id})"
    else:
        text_alias = "_Desconocido_"

    if user is None:
        output = "❌ No puedo darte información sobre este mago."
        bot.sendMessage(
            chat_id=user_id,
            text=output,
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        return

    if user is None or user.house is Houses.NONE.value and (user.level is None or user.profession is Professions.NONE.value or user.profession_level is None):
        text_house = "🖤"
    elif user.house is Houses.NONE.value:
        text_house = "🙈"
    elif user.house is Houses.GRYFFINDOR.value:
        text_house = "🦁"
    elif user.house is Houses.HUFFLEPUFF.value:
        text_house = "🦡"
    elif user.house is Houses.RAVENCLAW.value:
        text_house = "🦅"
    elif user.house is Houses.SLYTHERIN.value:
        text_house = "🐍"
    elif user.house is Houses.BOTS.value:
        text_house = "💻"

    if user is None or user.profession is Professions.NONE.value:
        text_prof = "_Desconocida_"
    elif user.profession is Professions.AUROR.value:
        text_prof = "⚔"
    elif user.profession is Professions.MAGIZOOLOGIST.value:
        text_prof = "🐾"
    elif user.profession is Professions.PROFESSOR.value:
        text_prof = "📚"
    elif user.profession is Professions.BOT.value:
        text_prof = "🤖"

    text_validationstatus = "✅"
    if user and user.banned:
        text_validationstatus = "⛔️"

    text_flag = "\n*Flags*: "
    if user and user.flag is not None:
        text_flag = text_flag + f"{user.flag} "
    else:
        text_flag = ""

    output = "*ID:* `{}`\n*Alias:* {}\n*Casa:* {}\n*Profesión:* {}\n*Estado:* {}{}".format(
        replied_id,
        text_alias,
        text_house, 
        text_prof,
        text_validationstatus,
        text_flag
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
