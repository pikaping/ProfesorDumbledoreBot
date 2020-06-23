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
import os
import re
import time

import emoji
import telegram
from pytz import all_timezones
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError
from telegram.utils.helpers import escape_markdown
import pickle
from threading import Event


import profdumbledorebot.model as model
from profdumbledorebot.config import ConfigurationNotLoaded, get_config
from profdumbledorebot.mwt import MWT
from profdumbledorebot.sql.admin import get_particular_admin, get_admin
from profdumbledorebot.sql.news import get_verified_providers, is_news_subscribed
from profdumbledorebot.sql.settings import get_join_settings, get_nanny_settings, get_group_settings, set_nanny
from profdumbledorebot.sql.user import get_user, get_real_user, get_user_by_name
from profdumbledorebot.sql.group import set_plant_alerted, delete_plant, get_poi
from profdumbledorebot.sql.welcome import get_welcome_settings

MATCH_MD = re.compile(r'\*(.*?)\*|'
                      r'_(.*?)_|'
                      r'`(.*?)`|'
                      r'(?<!\\)(\[.*?\])(\(.*?\))|'
                      r'(?P<esc>[*_`\[])')

LINK_REGEX = re.compile(r'(?<!\\)\[.+?\]\((.*?)\)')

BTN_URL_REGEX = re.compile(r"(\[([^\[]+?)\]\(buttonurl:(?:/{0,2})(.+?)(:same)?\))")


def replace(user_id, name=None, admin=False, frce=False):
    if frce:
        user = get_real_user(user_id)
    else:
        user = get_user(user_id)

    if user is None or user.house is model.Houses.NONE.value and (user.level is None or user.profession is model.Professions.NONE.value or user.profession_level is None):
        text_house = "🖤"
    elif user.house is model.Houses.NONE.value:
        text_house = "🙈"
    elif user.house is model.Houses.GRYFFINDOR.value:
        text_house = "🦁"
    elif user.house is model.Houses.HUFFLEPUFF.value:
        text_house = "🦡"
    elif user.house is model.Houses.RAVENCLAW.value:
        text_house = "🦅"
    elif user.house is model.Houses.SLYTHERIN.value:
        text_house = "🐍"
    elif user.house is model.Houses.BOTS.value:
        text_house = "💻"

    if user is None or user.profession is model.Professions.NONE.value:
        text_prof = "_Desconocido_"
    elif user.profession is model.Professions.AUROR.value:
        text_prof = "⚔"
    elif user.profession is model.Professions.MAGIZOOLOGIST.value:
        text_prof = "🐾"
    elif user.profession is model.Professions.PROFESSOR.value:
        text_prof = "📚"
    elif user.profession is model.Professions.BOT.value:
        text_prof = "🤖"

    if user and user.alias is not None:
        text_alias = escape_markdown("@{}".format(user.alias))
    elif name is not None:
        text_alias = f"[{escape_markdown(name)}](tg://user?id={user_id})"
    else:
        text_alias = "_Desconocido_"

    text_level = ("*{}*".format(user.level) if user and user.level else "*??*")
    text_profession_level = ("*{}*".format(user.profession_level) if user and user.profession_level else "*??*")
    
    text_validationstatus = "✅"
    if user and user.banned:
        text_validationstatus = "⛔️"

    if user and user.flag is not None:
        text_flag = f"{user.flag} "
    else:
        text_flag = ""

    if user and user.staff == True:
        staff_flag = "🧙‍♂️"
    else:
        staff_flag = ""


    replace_pogo = "{0} - *L*{1}  {2}{3}  {4}  {5}  {6}{7}".format(
        text_alias,
        text_level,
        text_prof,
        text_profession_level,
        text_house,
        text_validationstatus,
        text_flag,
        staff_flag
        )

    if admin:
        replace_pogo = replace_pogo + " `{0}`".format(user_id)

    return replace_pogo

def replace_plants(plant_type):
    plant = ""
    if plant_type == 0:
        plant = "You shouldn't be seeing this 👀"
    elif plant_type == 1:
        plant = "Ajenjo"
    elif plant_type == 2:
        plant = "Campanilla de invierno"
    elif plant_type == 3:
        plant = "Grano de sopóforo"
    elif plant_type == 4:
        plant = "Raíz de jengibre"
    elif plant_type == 5:
        plant = "Coclearia"
    elif plant_type == 6:
        plant = "Raíz de valeriana"
    elif plant_type == 7:
        plant = "Raíz amarga"
    elif plant_type == 8:
        plant = "Ligústico"
    elif plant_type == 9:
        plant = "Tármica"
    elif plant_type == 10:
        plant = "Hongo saltarín"
    elif plant_type == 11:
        plant = "Cristoforiana"
    elif plant_type == 12:
        plant = "Trompeta de ángel"
    return plant

class DeleteContext:
  def __init__(self, chat_id, message_id):
    self.chat_id = chat_id
    self.message_id = message_id

class SendContext:
  def __init__(self, chat_id, message_text):
    self.chat_id = chat_id
    self.message_text = message_text

class AlertPlantContext:
  def __init__(self, chat_id, message_text, alerted, plant_id):
    self.chat_id = chat_id
    self.message_text = message_text
    self.alerted = alerted
    self.plant_id = plant_id

class DeletePlantContext:
  def __init__(self, plant_id):
    self.plant_id = plant_id

class AlertFortressContext:
  def __init__(self, chat_id, message_text, message_id, poi_id):
    self.chat_id = chat_id
    self.message_text = message_text
    self.message_id = message_id
    self.poi_id = poi_id

def callback_delete(bot, job):
    try:
        bot.deleteMessage(
            chat_id=job.context.chat_id, 
            message_id=job.context.message_id
        )
        return
    except:
        return

def callback_send(bot, job):
    try:
        bot.sendMessage(
            chat_id=job.context.chat_id, 
            text=job.context.message_text,
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return
    except:
        return

def callback_AlertPlant(bot, job):
    try:
        if job.context.alerted:
            set_plant_alerted(job.context.plant_id)
        bot.sendMessage(
            chat_id=job.context.chat_id, 
            text=job.context.message_text,
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return
    except:
        return

def callback_DeletePlant(bot, job):
    try:
        try:
            alert15PlantJob = job_queue.get_jobs_by_name("{}_plantJob15".format(job.context.plant_id))
            alert15PlantJob[0].schedule_removal()
        except:
            pass
        try:
            alertPlantJob = job_queue.get_jobs_by_name("{}_plantJob".format(job.context.plant_id))
            alertPlantJob[0].schedule_removal()
        except:
            pass
        delete_plant(job.context.plant_id)
        return
    except:
        return

#Zero width char:​
def callback_AlertFortress(bot, job):
    try:
        poi_id = job.context.poi_id
        poi = get_poi(poi_id)
        lat = poi.latitude
        lon = poi.longitude
        button_list = [
            [(InlineKeyboardButton("🙋‍♀️ Voy", callback_data=f'fort_yes_{poi.id}')),
            (InlineKeyboardButton("🕒 Tardo", callback_data=f'fort_late_{poi.id}')),
            (InlineKeyboardButton("❌ No voy", callback_data=f'fort_no_{poi.id}'))],
            [(InlineKeyboardButton("✅ Estoy", callback_data=f'fort_here_{poi.id}')),
            (InlineKeyboardButton("📍 Ubicación", callback_data=f'fort_ubi_{poi.id}')),
            (InlineKeyboardButton("⚠️ Aviso​", callback_data=f'fort_alert_{poi.id}'))]
        ]
        fort_message = bot.edit_message_reply_markup(
            chat_id=job.context.chat_id,
            message_id=job.context.message_id,
            reply_markup=InlineKeyboardMarkup(button_list)
        )
        ent = fort_message.parse_entities(["mention"])
        for mention in ent:
            username = fort_message.parse_entity(mention)
            string = r'\n(🙋‍♀️|✅|🕒|❌) 🧙(\d|\d\d|\?\?) (🍮|⚔|🐾|📚)(\d|\d\d|\?\?) {}'.format(username)
            search = re.search(string, fort_message.text)
            if search.group(1) == "❌":
                continue
            user = get_user_by_name(username[1:])
            bot.sendMessage(
                chat_id=user.id,
                text=job.context.message_text,
                parse_mode=telegram.ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
        return
    except:
        return

def delete_message(chat_id, message_id, bot):
    try:
        bot.deleteMessage(chat_id=chat_id, message_id=message_id)
        return True

    except:
        return False

def message_url(message, message_id, text):
    if message.chat.username:
        chat_username = message.chat.username
        chat_text = f"[{text}](https://t.me/{chat_username}/{message_id})"
    elif str(message.chat.id)[:4] == "-100":
        chat_username = "c/" + str(message.chat.id)[4:]
        chat_text = f"[{text}](https://t.me/{chat_username}/{message_id})"
    else:
        chat_text = f"{text}"
    return chat_text


def build_keyboard(buttons):
    keyb = []
    for btn in buttons:
        if btn.same_line and keyb:
            keyb[-1].append(InlineKeyboardButton(btn.name, url=btn.url))
        else:
            keyb.append([InlineKeyboardButton(btn.name, url=btn.url)])

    return keyb


def get_welcome_type(msg, cmd=False):
    data_type = None
    content = None
    text = ""
    offset = 0

    if cmd and msg.text is not None:
        msg.text = "keyword " + msg.text
        offset = 8
    if msg.text is None:
        msg.text = "keyword "
        offset = 0
        
    args = msg.text.split(None, 1)

    buttons = []

    if msg.reply_to_message:
        message = msg.reply_to_message
    else:
        message = msg
    
    if len(args) >= 2:
        offset = len(args[1]) - len(msg.text) - offset
        text, buttons = button_markdown_parser(args[1], entities=msg.parse_entities(), offset=offset)
        if buttons:
            data_type = model.Types.BUTTON_TEXT
        else:
            data_type = model.Types.TEXT

    elif message and message.sticker:
        content = message.sticker.file_id
        text = message.text
        data_type = model.Types.STICKER

    elif message and message.document:
        content = message.document.file_id
        text = message.text
        data_type = model.Types.DOCUMENT

    elif message and message.photo:
        content = message.photo[-1].file_id
        text = message.text
        data_type = model.Types.PHOTO

    elif message and message.audio:
        content = message.audio.file_id
        text = message.text
        data_type = model.Types.AUDIO

    elif message and message.voice:
        content = message.voice.file_id
        text = message.text
        data_type = model.Types.VOICE

    elif message and message.video:
        content = message.video.file_id
        text = message.text
        data_type = model.Types.VIDEO
        
    return text, data_type, content, buttons


def button_markdown_parser(txt, entities=None, offset=0):
    markdown_note = markdown_parser(txt, entities, offset)
    prev = 0
    note_data = ""
    buttons = []
    for match in BTN_URL_REGEX.finditer(markdown_note):

        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and markdown_note[to_check] == "\\":
            n_escapes += 1
            to_check -= 1


        if n_escapes % 2 == 0:
            buttons.append((match.group(2), match.group(3), bool(match.group(4))))
            note_data += markdown_note[prev:match.start(1)]
            prev = match.end(1)
        else:
            note_data += markdown_note[prev:to_check]
            prev = match.start(1) - 1
    else:
        note_data += markdown_note[prev:]

    return note_data, buttons


def _calc_emoji_offset(to_calc):
    emoticons = emoji.get_emoji_regexp().finditer(to_calc)
    return sum(len(e.group(0).encode('utf-16-le')) // 2 - 1 for e in emoticons)


def markdown_parser(txt, entities= None, offset=0):
    if not entities:
        entities = {}
    if not txt:
        return ""

    prev = 0
    res = ""
    for ent, ent_text in entities.items():
        if ent.offset < -offset:
            continue

        start = ent.offset + offset
        end = ent.offset + offset + ent.length - 1

        if ent.type in ("code", "url", "text_link"):
            count = _calc_emoji_offset(txt[:start])
            start -= count
            end -= count

            if ent.type == "url":
                if any(match.start(1) <= start and end <= match.end(1) for match in LINK_REGEX.finditer(txt)):
                    continue
                else:
                    res += _selective_escape(txt[prev:start] or "") + escape_markdown(ent_text)

            elif ent.type == "code":
                res += _selective_escape(txt[prev:start]) + '`' + ent_text + '`'

            elif ent.type == "text_link":
                res += _selective_escape(txt[prev:start]) + "[{}]({})".format(ent_text, ent.url)

            end += 1

        else:
            continue

        prev = end

    res += _selective_escape(txt[prev:])
    return res


def _selective_escape(to_parse):
    offset = 0
    for match in MATCH_MD.finditer(to_parse):
        if match.group('esc'):
            ent_start = match.start()
            to_parse = to_parse[:ent_start + offset] + '\\' + to_parse[ent_start + offset:]
            offset += 1
    return to_parse


def escape_invalid_curly_brackets(text, valids):
    new_text = ""
    idx = 0
    while idx < len(text):
        if text[idx] == "{":
            if idx + 1 < len(text) and text[idx + 1] == "{":
                idx += 2
                new_text += "{{{{"
                continue
            else:
                success = False
                for v in valids:
                    if text[idx:].startswith('{' + v + '}'):
                        success = True
                        break
                if success:
                    new_text += text[idx: idx + len(v) + 2]
                    idx += len(v) + 2
                    continue
                else:
                    new_text += "{{"

        elif text[idx] == "}":
            if idx + 1 < len(text) and text[idx + 1] == "}":
                idx += 2
                new_text += "}}}}"
                continue
            else:
                new_text += "}}"

        else:
            new_text += text[idx]
        idx += 1

    return new_text


def cleanup(signum, frame):
    logging.info("Closing bot!")
    exit(0)


@MWT(timeout=60*60)
def is_admin(chat_id, user_id, bot):
    is_admin = False
    for admin in bot.get_chat_administrators(chat_id):
      if user_id == admin.user.id:
        is_admin = True
    return is_admin


@MWT(timeout=60*60)
def get_usergroup_tlg(chat_id, user_id, bot):
    return bot.get_chat_member(chat_id, user_id)


def extract_update_info(update):
    try:
        message = update.message
    except:
        message = update.channel_post
    if message is None:
        message = update.channel_post
    text = message.text
    try:
        user_id = message.from_user.id
    except:
        user_id = None
    chat_id = message.chat.id
    chat_type = message.chat.type
    return (chat_id, chat_type, user_id, text, message)


def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized:
        logging.debug("TELEGRAM ERROR: Unauthorized - %s" % error)
    except BadRequest:
        logging.debug("TELEGRAM ERROR: Bad Request - %s" % error)
    except TimedOut:
        logging.debug("TELEGRAM ERROR: Slow connection problem - %s" % error)
    except NetworkError:
        logging.debug("TELEGRAM ERROR: Other connection problems - %s" % error)
    except ChatMigrated as e:
        logging.debug("TELEGRAM ERROR: Chat ID migrated?! - %s" % error)
    except TelegramError:
        logging.debug("TELEGRAM ERROR: Other error - %s" % error)
    except:
        logging.debug("TELEGRAM ERROR: Unknown - %s" % error)


def get_settings_keyboard(chat_id, keyboard="main"):
    if keyboard == "main":
        settings_keyboard = [
            [InlineKeyboardButton("👷‍♂️ Administración »", callback_data='settings_goto_ladmin')],
            [InlineKeyboardButton("🛠 Ajustes »", callback_data='settings_goto_general')],
            [InlineKeyboardButton("👋 Bienvenida »", callback_data='settings_goto_welcome')],
            [InlineKeyboardButton("🚪 Entrada »", callback_data='settings_goto_join')],
            [InlineKeyboardButton("📯 Noticias »", callback_data='settings_goto_news')],
            [InlineKeyboardButton("🏫 Modo biblioteca »", callback_data='settings_goto_nanny')],
            [InlineKeyboardButton("Terminado", callback_data='settings_done')]
        ]
    
    #2.GROUP SETTINGS
    elif keyboard == "general":
        group = get_group_settings(chat_id)
        if group.games == 1:
            games_text = "✅ Juegos"
        else:
            games_text = "▪️ Juegos"
        if group.hard == 1:
            hard_text = "✅ Ban (Warns)"
        else:
            hard_text = "▪️ Kick (Warns)"
        if group.reply_on_group == 1:
            reply_on_group_text = "✅ Respuestas en el grupo"
        else:
            reply_on_group_text = "▪️ Respuestas al privado"
        if group.warn is model.WarnLimit.SO_EXTRICT.value:
            warn_text = "Limite de warns: 3"
        elif group.warn is model.WarnLimit.EXTRICT.value:
            warn_text = "Limite de warns: 5"
        elif group.warn is model.WarnLimit.LOW_PERMISIVE.value:
            warn_text = "Limite de warns: 10"
        elif group.warn is model.WarnLimit.MED_PERMISIVE.value:
            warn_text = "Limite de warns: 25"
        elif group.warn is model.WarnLimit.HIGH_PERMISIVE.value:
            warn_text = "Limite de warns: 50"
        elif group.warn is model.WarnLimit.SO_TOLERANT.value:
            warn_text = "Limite de warns: 100"

        settings_keyboard = [
            [InlineKeyboardButton(games_text, callback_data='settings_general_games')],
            [InlineKeyboardButton(hard_text, callback_data='settings_general_hard')],
            [InlineKeyboardButton(reply_on_group_text, callback_data='settings_general_reply')],
            [InlineKeyboardButton(warn_text, callback_data='settings_general_warn')],
            [InlineKeyboardButton("« Menú principal", callback_data='settings_goto_main')]
        ]   

    #3.JOIN SETTINGS
    elif keyboard == "join":
        join = get_join_settings(chat_id)
        if join.requirment is model.ValidationRequiered.NO_VALIDATION.value:
            validationrequired_text = "▪️ Grupo abierto"
        elif join.requirment is model.ValidationRequiered.VALIDATION.value:
            validationrequired_text = "✅ Validación obligatoria"
        elif join.requirment is model.ValidationRequiered.PROFESSOR.value:
            validationrequired_text = "📚 Profesor"
        elif join.requirment is model.ValidationRequiered.MAGIZOOLOGIST.value:
            validationrequired_text = "🐾 Magizoologo"
        elif join.requirment is model.ValidationRequiered.AUROR.value:
            validationrequired_text = "⚔ Auror"
        elif join.requirment is model.ValidationRequiered.GRYFFINDOR.value:
            validationrequired_text = "🦁 Gryffindor"
        elif join.requirment is model.ValidationRequiered.HUFFLEPUFF.value:
            validationrequired_text = "🦡 Hufflepuff"
        elif join.requirment is model.ValidationRequiered.RAVENCLAW.value:
            validationrequired_text = "🦅 Ravenclaw"
        elif join.requirment is model.ValidationRequiered.SLYTHERIN.value:
            validationrequired_text = "🐍 Slytherin"

        if join.val_alert is True:
            mute_text = "✅ Expulsiones silenciosas"
        else:
            mute_text = "▪️ Expulsiones notificadas"

        if join.delete_header is True:
            silence_text = "✅ Borrar -> entró al grupo"
        else:
            silence_text = "▪️ Borrar -> entró al grupo"

        settings_keyboard = [
            [InlineKeyboardButton(mute_text, callback_data='settings_join_mute')],
            [InlineKeyboardButton(silence_text, callback_data='settings_join_silence')],
            [InlineKeyboardButton(validationrequired_text, callback_data='settings_join_val')],
            [InlineKeyboardButton("« Menú principal", callback_data='settings_goto_main')]
        ]
    
    #5.NEWS SETTINGS
    elif keyboard == "news":
        providers = get_verified_providers()
        settings_keyboard = []
        for k in providers:
            if is_news_subscribed(chat_id, k.id):
                status = "✅ @"
            else:
                status = "▪️ @"
            text = status + k.alias
            settings_keyboard.append(
                [InlineKeyboardButton(
                    text,
                    callback_data='settings_news_{}'.format(k.id))
                ]
            )

        settings_keyboard.append(
            [InlineKeyboardButton(
                "« Menú principal",
                callback_data='settings_goto_main')
            ]
        )

    #6.WELCOME SETTINGS
    elif keyboard == "welcome":
        welcome = get_welcome_settings(chat_id)
        if welcome.should_welcome == 1:
            welcome_text = "✅ Bienvenida"
        else:
            welcome_text = "▪️ Bienvenida"
        settings_keyboard = [
            [InlineKeyboardButton(welcome_text, callback_data='settings_welcome_welcome')],
            [InlineKeyboardButton("« Menú principal", callback_data='settings_goto_main')]
        ]
    
    #7.NANNY SETTINGS
    elif keyboard == "nanny":
        nanny = get_nanny_settings(chat_id)
        if nanny is None:
            set_nanny(chat_id)
            nanny = get_nanny_settings(chat_id)
            
        if nanny.voice == 1:
            voice_text = "✅ Audio y Voz"
        else:
            voice_text = "▪️ Audio y Voz"
        if nanny.command == 1:
            comandos_text = "✅ Comandos"
        else:
            comandos_text = "▪️ Comandos"
        if nanny.contact == 1:
            contact_text = "✅ Contactos"
        else:
            contact_text = "▪️ Contactos"
        if nanny.animation == 1:
            animation_text = "✅ GIFs y Documentos"
        else:
            animation_text = "▪️ GIFs y Documentos"
        if nanny.photo == 1:
            photo_text = "✅ Imagenes"
        else:
            photo_text = "▪️ Imagenes"
        if nanny.games == 1:
            games_text = "✅ Juegos"
        else:
            games_text = "▪️ Juegos"
        if nanny.text == 1:
            text_text = "✅ Mensajes"
        else:
            text_text = "▪️ Mensajes"
        if nanny.sticker == 1:
            sticker_text = "✅ Stickers"
        else:
            sticker_text = "▪️ Stickers"
        if nanny.location == 1:
            location_text = "✅ Ubicaciones"
        else:
            location_text = "▪️ Ubicaciones"
        if nanny.urls == 1:
            url_text = "✅ URLs"
        else:
            url_text = "▪️ URLs"
        if nanny.video == 1:
            video_text = "✅ Video"
        else:
            video_text = "▪️ Video"
        if nanny.warn == 1:
            warn_text = "✅ Warns"
        else:
            warn_text = "▪️ Warns"
        if nanny.admin_too == 1:
            admin_too_text = "️✅ Mensajes de administradores"
        else:
            admin_too_text = "️️️▪️ Mensajes de administradores"

        settings_keyboard = [
            [InlineKeyboardButton(voice_text, callback_data='settings_nanny_voice')],
            [InlineKeyboardButton(comandos_text, callback_data='settings_nanny_command')],
            [InlineKeyboardButton(contact_text, callback_data='settings_nanny_contact')],
            [InlineKeyboardButton(animation_text, callback_data='settings_nanny_animation')],
            [InlineKeyboardButton(photo_text, callback_data='settings_nanny_photo')],
            [InlineKeyboardButton(games_text, callback_data='settings_nanny_games')],
            [InlineKeyboardButton(text_text, callback_data='settings_nanny_text')],
            [InlineKeyboardButton(sticker_text, callback_data='settings_nanny_sticker')],
            [InlineKeyboardButton(location_text, callback_data='settings_nanny_location')],
            [InlineKeyboardButton(url_text, callback_data='settings_nanny_url')],
            [InlineKeyboardButton(video_text, callback_data='settings_nanny_video')],
            [InlineKeyboardButton(warn_text, callback_data='settings_nanny_warn')],
            [InlineKeyboardButton(admin_too_text, callback_data='settings_nanny_admin_too')],
            [InlineKeyboardButton("« Menú principal", callback_data='settings_goto_main')]
        ] 

    #8. LOCAL ADMIN
    elif keyboard == "ladmin":
        adgroup = get_particular_admin(chat_id)
        if adgroup.admin == 1:
            admin_text = "✅ @admin"
        else:
            admin_text = "▪️ @admin"
        if adgroup.welcome == 1:
            welcome_text = "✅ Entrada de usuarios"
        else:
            welcome_text = "▪️ Entrada de usuarios"
        if adgroup.ejections == 1:
            ejections_text = "✅ Expulsiones"
        else:
            ejections_text = "▪️ Expulsiones"

        settings_keyboard = [
            [InlineKeyboardButton(admin_text, callback_data='settings_ladmin_admin')],
            [InlineKeyboardButton(welcome_text, callback_data='settings_ladmin_welcome')],
            [InlineKeyboardButton(ejections_text, callback_data='settings_ladmin_ejections')],
            [InlineKeyboardButton("« Menú principal", callback_data='settings_goto_main')]
        ] 

    #0. ADMIN
    elif keyboard == "admin":
        adgroup = get_admin(chat_id)
        if adgroup.admin == 1:
            admin_text = "✅ @admin"
        else:
            admin_text = "▪️ @admin"
        if adgroup.welcome == 1:
            welcome_text = "✅ Entrada de usuarios"
        else:
            welcome_text = "▪️ Entrada de usuarios"
        if adgroup.ejections == 1:
            ejections_text = "✅ Expulsiones"
        else:
            ejections_text = "▪️ Expulsiones"
        
        spy_mode = "🦅 Fawkes"

        settings_keyboard = [
            [InlineKeyboardButton(admin_text, callback_data='settings_admin_admin')],
            [InlineKeyboardButton(welcome_text, callback_data='settings_admin_welcome')],
            [InlineKeyboardButton(ejections_text, callback_data='settings_admin_ejections')],
            [InlineKeyboardButton(spy_mode, callback_data='settings_admin_spy')],
            [InlineKeyboardButton("Terminado", callback_data='settings_done')]
        ] 

    settings_markup = InlineKeyboardMarkup(settings_keyboard)
    return settings_markup


def update_settings_message(chat_id, bot, message_id, keyboard = "main"):
    settings_markup = get_settings_keyboard(chat_id, keyboard=keyboard)

    text = (
        "Elige una categoría para ver las opciones disponibles. Cuando"
        " termines, pulsa el botón <b>Terminado</b> para borrar el "
        "mensaje."
    )
    time.sleep(0.5)

    return bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=settings_markup,
        parse_mode=telegram.ParseMode.HTML,
        disable_web_page_preview=True
    )


def get_unified_timezone(informal_timezone):
    regexp = re.compile(r'.*{}.*'.format(informal_timezone))

    return [tz for tz in all_timezones if regexp.match(tz)]


def create_needed_paths():
    config = get_config()

    if not config:
        logging.error(
            'Not configuration loaded. Please, use `create_needed_paths` '
            'only after loading a valid configuration'
        )

        raise ConfigurationNotLoaded()

    needed_dirs = []

    needed_dirs.append(os.path.dirname(os.path.expanduser(config['general'].get('log'))) or
        os.getcwd())

    needed_dirs.append(os.path.dirname(os.path.expanduser(config['general']['jsondir'])))
    needed_dirs.append(os.path.dirname(os.path.expanduser(config['general']['mediadir'])))

    for directory in needed_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)

    return True

def ensure_escaped(username):
    if username.find("_") != -1 and username.find("\\_") == -1:
        username = username.replace("_","\\_")
    return username

JOBS_PICKLE = 'job_tuples.pickle'

def load_jobs(jq):
    now = time.time()

    with open(JOBS_PICKLE, 'rb') as fp:
        while True:
            try:
                next_t, job = pickle.load(fp)
            except EOFError:
                break  # Loaded all job tuples

            # Create threading primitives
            enabled = job._enabled
            removed = job._remove

            job._enabled = Event()
            job._remove = Event()

            if enabled:
                job._enabled.set()

            if removed:
                job._remove.set()

            next_t -= now  # Convert from absolute to relative time

            jq._put(job, next_t)

def save_jobs(jq):
    if jq:
        job_tuples = jq._queue.queue
    else:
        job_tuples = []

    with open(JOBS_PICKLE, 'wb') as fp:
        for next_t, job in job_tuples:
            # Back up objects
            _job_queue = job._job_queue
            _remove = job._remove
            _enabled = job._enabled

            # Replace un-pickleable threading primitives
            job._job_queue = None  # Will be reset in jq.put
            job._remove = job.removed  # Convert to boolean
            job._enabled = job.enabled  # Convert to boolean

            # Pickle the job
            pickle.dump((next_t, job), fp)

            # Restore objects
            job._job_queue = _job_queue
            job._remove = _remove
            job._enabled = _enabled