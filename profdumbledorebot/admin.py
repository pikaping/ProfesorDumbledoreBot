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
import time
import logging
import telegram

import profdumbledorebot.sql.admin as adm_support
import profdumbledorebot.sql.support as sql_support
import profdumbledorebot.supportmethods as support

from datetime import datetime
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import escape_markdown
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Admin Group

@run_async
def settings_admin_cmd(bot, update):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.support.is_admin(chat_id, user_id, bot) or sql_support.are_banned(user_id, chat_id):
        return

    group = adm_support.get_admin(chat_id)
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

    if not support.is_admin(chat_id, user_id, bot) or sql_support.are_banned(user_id, chat_id):
        return

    if adm_support.get_admin(chat_id) is None:
        adm_support.set_admin(chat_id)
        output = "👌 Grupo configuado exitosamente. Continua vinculando grupos con este ID: `{}`\nNo olvides activar las alertas con `/settings_admin`.".format(chat_id)
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

    if not support.is_admin(chat_id, user_id, bot) or sql_support.are_banned(user_id, chat_id):
        return

    if adm_support.get_admin(chat_id) is not None:
        adm_support.rm_admin(chat_id)
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

    if sql_support.are_banned(user_id, chat_id):
        return

    groups = adm_support.get_all_groups(chat_id)
    output = "*Listado de grupos vinculados:*"

    if groups is None:
        output = "❌ No he encontrado grupos vinculados a este."

    elif support.is_admin(chat_id, user_id, bot):
        for k in groups:
            if k.link is not None and re.match('@?[a-zA-Z]([a-zA-Z0-9_]+)$', k.link) is None:
                output = output + "\n🏥 [{}]({}) - `{}`".format(k.label or k.title, k.link, k.linked_id)
            elif k.link is not None and re.match('@?[a-zA-Z]([a-zA-Z0-9_]+)$', k.link) is not None:
                output = output + "\n🏥 {} - {} - `{}`".format(k.label or k.title, k.link, k.linked_id)
            else:
                output = output + "\n🏥 {} - `{}`".format(k.label or k.title, k.linked_id)

    else:
        for k in groups:
            if k.group_type not in [GroupType.RED, GroupType.BLUE, GroupType.YELLOW]:
                if k.link is not None and re.match('@?[a-zA-Z]([a-zA-Z0-9_]+)$', k.link) is None:
                    output = output + "\n🏥 [{}]({})".format(k.label or k.title, k.link)
                elif k.link is not None and re.match('@?[a-zA-Z]([a-zA-Z0-9_]+)$', k.link) is not None:
                    output = output + "\n🏥 {} - {}".format(k.label or k.title, k.link)
                else:
                    output = output + "\n🏥 {}".format(k.label or k.title)

    if chat_type != "private":
        group = adm_support.get_group_settings(chat_id)
        if group.reply_on_group:
            dest_id = chat_id
        else:
            dest_id = user_id
    else:
        dest_id = user_id

    bot.sendMessage(
        chat_id=user_id,
        text=output,
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_web_page_preview=True)


@run_async
def add_url_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = extract_update_info(update)

    if not support.is_admin(chat_id, user_id, bot) or sql_support.are_banned(user_id, chat_id):
        return

    if args is None or len(args) != 1 or args[0] != '-' and (len(args[0]) < 3 or len(args[0]) > 60 or re.match("@?[a-zA-Z]([a-zA-Z0-9_]+)$|https://t\.me/joinchat/[a-zA-Z0-9_-]+$", args[0]) is None):
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Necesito que me pases el alias del grupo o un enlace de `t.me` de un grupo privado. Por ejemplo: `@telegram` o `https://t.me/joinchat/XXXXERK2ZfB3ntXXSiWUx`.",
            parse_mode=telegram.ParseMode.MARKDOWN)
        return

    if args[0] != '-':
        enlace = args[0]
        add_tlink(chat_id, enlace)
        bot.sendMessage(
            chat_id=chat_id,
            text="👌 Establecido el link del grupo a {}.".format(ensure_escaped(enlace)),
            parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        add_tlink(chat_id, None)
        bot.sendMessage(
            chat_id=chat_id,
            text="👌 Esto... Creo que acabo de olvidar el enlace del grupo...",
            parse_mode=telegram.ParseMode.MARKDOWN)


@run_async
def create_link_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)
    chat_title = message.chat.title

    if not support.is_admin(chat_id, user_id, bot) or sql_support.are_banned(user_id, chat_id):
        return

    if args is None or len(args) != 1 or get_admin(args[0]) is None:
        bot.sendMessage(
            chat_id=chat_id,
            text="❌ Parece ser que has introducido un ID incorrecto.",
            parse_mode=telegram.ParseMode.MARKDOWN)
        return

    new_link(args[0], chat_id, chat_title)
    bot.sendMessage(
        chat_id=chat_id,
        text="👌 El grupo ha sido registrado, continua el proceso desde el grupo de administracion.",
        parse_mode=telegram.ParseMode.MARKDOWN)

@run_async
def add_tag_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or sql_support.are_banned(user_id, chat_id):
        return

    if get_groups(chat_id) is not None:
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
        set_tag(chat_id, message)
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

    if not support.is_admin(chat_id, user_id, bot) or sql_support.are_banned(user_id, chat_id):
        return

    rm_link(chat_id)
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


def last_run(chat_id, cmdtype):
    if cmdtype is 'uv':
        if str(chat_id) in uv_last_check:
            lastpress = uv_last_check[str(chat_id)]
        else:
            lastpress = None
        uv_last_check[str(chat_id)] = datetime.now()
    elif cmdtype is 'kickuv':

        if str(chat_id) in kickuv_last_check:
            lastpress = kickuv_last_check[str(chat_id)]
        else:
            lastpress = None
        kickuv_last_check[str(chat_id)] = datetime.now()
    elif cmdtype is 'kicklvl':

        if str(chat_id) in kicklvl_last_check:
            lastpress = kicklvl_last_check[str(chat_id)]
        else:
            lastpress = None
        kicklvl_last_check[str(chat_id)] = datetime.now()
    elif cmdtype is 'kickmsg':

        if str(chat_id) in kickmsg_last_check:
            lastpress = kickmsg_last_check[str(chat_id)]
        else:
            lastpress = None
        kickmsg_last_check[str(chat_id)] = datetime.now()
    elif cmdtype is 'kickold':

        if str(chat_id) in kickold_last_check:
            lastpress = kickold_last_check[str(chat_id)]
        else:
            lastpress = None
        kickold_last_check[str(chat_id)] = datetime.now()

    if lastpress is not None:
        difftime = datetime.now() - lastpress
        if difftime.days == 0:
            return True

    return False


@run_async
def kickmsg_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or sql_support.are_banned(user_id, chat_id):
        return

    if args is None or len(args) != 1 or not args[0].isdigit():
        return

    if last_run(chat_id, 'kickmsg'):
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
    
    if not support.is_admin(chat_id, user_id, bot) or sql_support.are_banned(user_id, chat_id):
        return

    if args is None or len(args) != 1 or not args[0].isdigit():
        return

    if last_run(chat_id, 'kickold'):
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

    if not support.is_admin(chat_id, user_id, bot) or sql_support.are_banned(user_id, chat_id):
        return

    uv = 0
    print_uv = False

    if args is not None and args[0] == "all":
        print_uv = True

    if last_run(chat_id, 'uv'):
        bot.sendMessage(
            chat_id=chat_id,
            text="Hace menos de un dia que se usó el comando.",
            parse_mode=telegram.ParseMode.HTML)
        return

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
            info = get_user(user.user_id)
            if info is None or info.team is Team.NONE:
                uv += 1
                if print_uv:
                    output = output + ' <a href="tg://user?id={1}">{0}</a>'.format(
                        escape_markdown(data.user.first_name),
                        user.user_id)
                    outn += 1

            if outn == 100:
                bot.sendMessage(
                    chat_id=chat_id,
                    text=output,
                    parse_mode=telegram.ParseMode.HTML)
                output = ''
                outn = 0

            time.sleep(0.01)

    tlgrm = tlgrm - total - 1
    output = "🖤 Unvalidated: {}\n❓ Unknown: {}".format(uv, tlgrm) + output
    bot.sendMessage(
        chat_id=chat_id,
        text=output,
        parse_mode=telegram.ParseMode.HTML)


@run_async
def kickuv_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or sql_support.are_banned(user_id, chat_id):
        return

    if last_run(chat_id, 'kickuv'):
        bot.sendMessage(
            chat_id=chat_id,
            text="Hace menos de un dia que se usó el comando.",
            parse_mode=telegram.ParseMode.HTML)
        return

    uv = 0
    users = get_users_from_group(chat_id)
    for user in users:
        try:
            data = bot.get_chat_member(chat_id, user.user_id)
        except:
            data = None
            pass
        if data and data.status not in ['kicked', 'left'] and not data.user.is_bot:
            info = get_user(user.user_id)
            if info is None or info.team is Team.NONE:
                try:
                    bot.kickChatMember(chat_id, user.user_id)
                    bot.unbanChatMember(chat_id, user.user_id)
                    uv += 1
                except:
                    pass
                time.sleep(0.01)

    bot.sendMessage(
        chat_id=chat_id,
        text="Han sido expulsados {} usuarios.".format(uv),
        parse_mode=telegram.ParseMode.MARKDOWN)


@run_async
def warn_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or sql_support.are_banned(user_id, chat_id):
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
            if get_linked_admin(chat_id, args[0]):
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
            if user and user.trainer_name:
                name = user.trainer_name
            elif user and user.username:
                name = user.username
            else:
                name = args[0]
            replied_user = args[0]
            del args[0]
        else:
            args[0] = re.sub("@", "", args[0])
            user = get_user_by_name(args[0])
            del args[0]
            if user:
                name = user.trainer_name
                replied_user = user.id
            else:
                return
    else:
        return

    if args is not None and len(args) > 0:
        reason = " ".join(args)

    if get_admin(chat_id) is not None:
        groups = get_all_groups(chat_id)
    else:
        groups = None

    if groups is None:
        if not exists_user_group(replied_user, chat_id):
            set_user_group(replied_user, chat_id)

        warning = warn_user(chat_id, replied_user, 1)
        group = get_group_settings(chat_id)
        if warning < group.warn:
            output = "👌 Entrenador [{0}](tg://user?id={1}) advertido correctamente! {2}/{3}".format(name, replied_user, warning, group.warn)
            if reason is not "":
                output = output + "\nMotivo: {}".format(reason)
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Eliminar warn", callback_data='rm_warn({})'.format(replied_user))]])
            bot.sendMessage(
                chat_id=chat_id, 
                text=output,
                parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup=keyboard)
        else:
            output = "👌 Entrenador {} baneado correctamente!\nAlcanzado número máximo de advertencias.".format(name)
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

        ladmin = get_particular_admin(chat_id)
        if ladmin is not None and ladmin.ejections:
            admin = get_admin_from_linked(chat_id)
            if admin is not None and admin.ejections is True:
                replace_pogo = replace(replied_user, name)
                bot.sendMessage(
                    chat_id=admin.id,
                    text="ℹ️ {}\n👤 {} ha sido advertido {}/{}".format(message.chat.title, replace_pogo, warning, group.warn),
                    parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        for group in groups:
            chat_id = group.linked_id
            if not exists_user_group(replied_user, chat_id):
                set_user_group(replied_user, chat_id)

            warning = warn_user(chat_id, replied_user, 1)
            group = get_group_settings(chat_id)
            if warning < group.warn:
                output = "👌 Entrenador [{0}](tg://user?id={1}) advertido correctamente! {2}/{3}".format(name, replied_user, warning, group.warn)
                if reason is not "":
                    output = output + '\nMotivo: {}'.format(reason)
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Eliminar warn', callback_data='rm_warn({})'.format(replied_user))]])
                bot.sendMessage(
                    chat_id=chat_id,
                    text=output,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    reply_markup=keyboard)
            else:
                output = "👌 Entrenador {} baneado correctamente!\nAlcanzado número máximo de advertencias.".format(name)
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
                    output = "❌ No tengo los permisos necesarios."
                    bot.sendMessage(
                        chat_id=chat_id,
                        text=output,
                        parse_mode=telegram.ParseMode.MARKDOWN)
                    return

            ladmin = get_particular_admin(chat_id)
            if ladmin is not None and ladmin.ejections:
                admin = get_admin_from_linked(chat_id)
                if admin is not None and admin.ejections is True:
                    replace_pogo = replace(replied_user, name)
                    bot.sendMessage(
                        chat_id=admin.id,
                        text="ℹ️ {}\n👤 {} ha sido advertido {}/{}".format(message.chat.title, replace_pogo, warning, group.warn),
                        parse_mode=telegram.ParseMode.MARKDOWN)


@run_async
def kick_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or sql_support.are_banned(user_id, chat_id):
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
            if get_linked_admin(chat_id, args[0]):
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
            if user and user.trainer_name:
                name = user.trainer_name
            elif user and user.username:
                name = user.username
            else:
                name = args[0]
            replied_user = args[0]
            del args[0]
        else:
            args[0] = re.sub("@", "", args[0])
            user = get_user_by_name(args[0])
            del args[0]
            if user:
                name = user.trainer_name
                replied_user = user.id
            else:
                return
    else:
        return

    if args is not None and len(args) > 0:
        reason = ' '.join(args)

    if get_admin(chat_id) is not None:
        groups = get_all_groups(chat_id)
    else:
        groups = None

    if groups is None:
        try:
            bot.kickChatMember(chat_id, replied_user)
            bot.unbanChatMember(chat_id, replied_user)
            output = "👌 Entrenador {} expulsado correctamente!".format(name)
            if reason is not "":
                output = output + "\nMotivo: {}".format(reason)
            bot.sendMessage(
                chat_id=chat_id,
                text=output,
                parse_mode=telegram.ParseMode.MARKDOWN)
        except:
            bot.sendMessage(
                chat_id=chat_id,
                text="❌ No he podido expulsar al entrenador. Puede que sea administrador o ya no forme parte del grupo.",
                parse_mode=telegram.ParseMode.MARKDOWN)
            return

        ladmin = get_particular_admin(chat_id)
        if ladmin is not None and ladmin.ejections:
            admin = get_admin_from_linked(chat_id)
            if admin is not None and admin.ejections is True:
                replace_pogo = replace(replied_user, name)
                bot.sendMessage(
                    chat_id=admin.id,
                    text="ℹ️ {}\n👤 {} ha sido expulsado".format(message.chat.title, replace_pogo),
                    parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        for group in groups:
            chat_id = group.linked_id
            try:
                bot.kickChatMember(chat_id, replied_user)
                bot.unbanChatMember(chat_id, replied_user)
                output = "👌 Entrenador {} expulsado correctamente!".format(name)
                if reason is not "":
                    output = output + "\nMotivo: {}".format(reason)
            except:
                bot.sendMessage(
                    chat_id=chat_id,
                    text="❌ No he podido expulsar al entrenador. Puede que sea administrador o ya no forme parte del grupo.",
                    parse_mode=telegram.ParseMode.MARKDOWN)
                return

            bot.sendMessage(chat_id=chat_id, text=output,
                            parse_mode=telegram.ParseMode.MARKDOWN)
            ladmin = get_particular_admin(chat_id)
            if ladmin is not None and ladmin.ejections:
                admin = get_admin_from_linked(chat_id)
                if admin is not None and admin.ejections is True:
                    replace_pogo = replace(replied_user, name)
                    bot.sendMessage(
                        chat_id=admin.id,
                        text="ℹ️ {}\n👤 {} ha sido expulsado".format(message.chat.title, replace_pogo),
                        parse_mode=telegram.ParseMode.MARKDOWN)


@run_async
def ban_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or sql_support.are_banned(user_id, chat_id):
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
            if get_linked_admin(chat_id, args[0]):
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
            if user and user.trainer_name:
                name = user.trainer_name
            elif user and user.username:
                name = user.username
            else:
                name = args[0]
            replied_user = args[0]
            del args[0]
        else:
            args[0] = re.sub("@", "", args[0])
            user = get_user_by_name(args[0])
            del args[0]
            if user:
                name = user.trainer_name
                replied_user = user.id
            else:
                return
    else:
        return

    if args is not None and len(args) > 0:
        reason = ' '.join(args)

    if get_admin(chat_id) is not None:
        groups = get_all_groups(chat_id)
    else:
        groups = None

    if groups is None:
        try:
            bot.kickChatMember(chat_id, replied_user)
            output = "👌 Entrenador {} baneado correctamente!".format(name)
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
                text="❌ No he podido expulsar al entrenador. Puede que sea administrador.",
                parse_mode=telegram.ParseMode.MARKDOWN)
            return
            
        ladmin = get_particular_admin(chat_id)
        if ladmin is not None and ladmin.ejections:
            admin = get_admin_from_linked(chat_id)
            if admin is not None and admin.ejections is True:
                replace_pogo = replace(replied_user, name)
                bot.sendMessage(
                    chat_id=admin.id,
                    text="ℹ️ {}\n👤 {} ha sido baneado".format(message.chat.title, replace_pogo),
                    parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        for group in groups:
            chat_id = group.linked_id
            try:
                bot.kickChatMember(chat_id, replied_user)
                output = "👌 Entrenador {} baneado correctamente!".format(name)
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
                    text="❌ No he podido expulsar al entrenador. Puede que sea administrador.",
                    parse_mode=telegram.ParseMode.MARKDOWN)
                return

            ladmin = get_particular_admin(chat_id)
            if ladmin is not None and ladmin.ejections:
                admin = get_admin_from_linked(chat_id)
                if admin is not None and admin.ejections is True:
                    replace_pogo = replace(replied_user, name)
                    bot.sendMessage(
                        chat_id=admin.id,
                        text="ℹ️ {}\n👤 {} ha sido baneado".format(message.chat.title, replace_pogo),
                        parse_mode=telegram.ParseMode.MARKDOWN)


@run_async
def unban_cmd(bot, update, args=None):
    (chat_id, chat_type, user_id, text, message) = support.extract_update_info(update)
    support.delete_message(chat_id, message.message_id, bot)

    if not support.is_admin(chat_id, user_id, bot) or sql_support.are_banned(user_id, chat_id):
        return

    reason = ""
    if message.reply_to_message is not None:
        if message.reply_to_message.forward_from is not None:
            if args is not None and len(args)!=0 and args[0] is "f":
                replied_user = message.reply_to_message.from_user.id
                name = message.reply_to_message.from_user.first_name
                del args[0]
        elif message.reply_to_message.from_user is not None:
            replied_user = message.reply_to_message.from_user.id
            name = message.reply_to_message.from_user.first_name
        if args and len(args) > 0:
            reason = ' '.join(args)
    elif args is not None and len(args) > 0:
        if len(args) > 1 and args[0][0] is '-':
            if get_linked_admin(chat_id, args[0]):
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
            if user and user.trainer_name:
                name = user.trainer_name
            elif user and user.username:
                name = user.username
            else:
                name = args[0]
            replied_user = args[0]
            del args[0]
        else:
            args[0] = re.sub("@", "", args[0])
            user = get_user_by_name(args[0])
            del args[0]
            if user:
                name = user.trainer_name
                replied_user = user.id
            else:
                return
        if len(args) > 0:
            reason = ' '.join(args)
    else:
        return
    if get_admin(chat_id) is not None:
        groups = get_all_groups(chat_id)
    else:
        groups = None

    if groups is None:
        try:
            bot.unbanChatMember(chat_id, replied_user)
            output = "👌 Entrenador {} desbaneado correctamente!".format(name)
            if reason is not "":
                output = output + "\nMotivo: {}".format(reason)
            bot.sendMessage(
                chat_id=chat_id, 
                text=output,
                parse_mode=telegram.ParseMode.MARKDOWN)
        except:
            bot.sendMessage(
                chat_id=chat_id,
                text="❌ No he podido desbanear al entrenador",
                parse_mode=telegram.ParseMode.MARKDOWN)
            return
            
        ladmin = get_particular_admin(chat_id)
        if ladmin is not None and ladmin.ejections:
            admin = get_admin_from_linked(chat_id)
            if admin is not None and admin.ejections is True:
                replace_pogo = replace(replied_user, name)
                bot.sendMessage(
                    chat_id=admin.id,
                    text="ℹ️ {}\n👤 {} ha sido desbaneado".format(message.chat.title, replace_pogo),
                    parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        for group in groups:
            chat_id = group.linked_id
            try:
                bot.unbanChatMember(chat_id, replied_user)
                output = "👌 Entrenador {} desbaneado correctamente!".format(name)
                if reason is not "":
                    output = output + "\nMotivo: {}".format(reason)
                bot.sendMessage(
                    chat_id=chat_id,
                    text=output,
                    parse_mode=telegram.ParseMode.MARKDOWN)
            except:
                bot.sendMessage(
                    chat_id=chat_id,
                    text="❌ No he podido desbanear al entrenador",
                    parse_mode=telegram.ParseMode.MARKDOWN)
                return

            ladmin = get_particular_admin(chat_id)
            if ladmin is not None and ladmin.ejections:
                admin = get_admin_from_linked(chat_id)
                if admin is not None and admin.ejections is True:
                    replace_pogo = replace(replied_user, name)
                    bot.sendMessage(
                        chat_id=admin.id,
                        text="ℹ️ {}\n👤 {} ha sido desbaneado".format(message.chat.title, replace_pogo),
                        parse_mode=telegram.ParseMode.MARKDOWN)

