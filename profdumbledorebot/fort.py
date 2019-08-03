import re

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.utils.helpers import escape_markdown

import profdumbledorebot.global_vars
import profdumbledorebot.sql.support as support
import profdumbledorebot.supportmethods as supportmethods
from profdumbledorebot.sql import user as user_handler


def get_fortress_message(time, place, creator, users):
    header = ('Fortaleza organizada por: @{creator}\n*Hora*: {time}\n*Lugar*: {place}'.format(
        creator=escape_markdown(creator.alias),
        time=time,
        place=place
    ))
    if len(users) == 0:
        body = 'No hay apuntados.'
    else:
        body = '\n'.join(['L{lv}{profession}{house} @{alias}'.format(
            lv=user.level,
            profession=supportmethods.get_profession_icon(user.profession),
            house=supportmethods.get_house_icon(user.house),
            alias=escape_markdown(user.alias)
        ) for user in users])
    return '{}\n\n{}'.format(header, body)


def get_group_from_regexp(regexp, text, group):
    matches = re.search(regexp, text)
    if matches:
        return matches.group(group)
    return None


def remove_time_from_text(time, text):
    left_side_space = get_group_from_regexp('(\s*){}'.format(time), text, 1)
    right_side_space = get_group_from_regexp('{}(\s*)'.format(time), text, 1)
    if left_side_space and right_side_space:
        return re.sub('\s*{}\s*'.format(time), " ", text)
    else:
        return re.sub('\s*{}\s*'.format(time), "", text)


def get_time_place(fort_text):
    re.purge()
    searches_full_time = get_group_from_regexp(r"(\d+\:\d{2})", fort_text, 1)
    re.purge()
    searches_partial_time = get_group_from_regexp(r"(\d+)", fort_text, 1)
    time = searches_full_time or searches_partial_time
    if time:
        text_without_command = re.sub(r"^/fort\s*", "", fort_text)
        place = remove_time_from_text(time, text_without_command)
        if time == searches_partial_time:
            time += ':00'
    else:
        place = re.sub(r"^/fort\s*", "", fort_text)
    return [time, place]

def start(bot, update):
    """Start fortress"""
    chat_id, chat_type, user_id, text, message = supportmethods.extract_update_info(update)
    supportmethods.delete_message(chat_id, message.message_id, bot)
    if support.are_banned(user_id, chat_id):
        profdumbledorebot.global_vars.message_queue.append("El usuario ha sido baneado y no puede realizar esta acción.")
        return
    [ time, place ] = get_time_place(text)
    button_list = [[
        InlineKeyboardButton(text="🏃 Voy", callback_data='fort_join'),
        InlineKeyboardButton(text="+1", callback_data='fort_plusone'),
        InlineKeyboardButton(text="-1", callback_data='fort_minsone')
    ],[
        InlineKeyboardButton(text="⌛ Tardaré", callback_data='fort_late'),
        InlineKeyboardButton(text="✔ Ya estoy", callback_data='fort_there')
    ]]
    user = user_handler.get_user(user_id)
    bot.sendMessage(
        chat_id=chat_id,
        text=get_fortress_message(time, place, user, []),
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(button_list))
