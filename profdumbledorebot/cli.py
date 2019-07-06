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
import time
import random
import signal
import logging
import argparse

import profumbledorebot.news as news
import profumbledorebot.admin as admin
import profumbledorebot.group as group
import profumbledorebot.rules as rules
import profumbledorebot.lists as lists
import profumbledorebot.model as model
import profumbledorebot.tablas as tablas
import profumbledorebot.config as config
import profumbledorebot.settings as settings
import profumbledorebot.supportmethods as support
from profumbledorebot.nanny import process_cmd, set_nanny
import profumbledorebot.profumbledorebot as profumbledorebot

from logging.handlers import  TimedRotatingFileHandler
from telegram.ext import Updater, CommandHandler, MessageHandler, InlineQueryHandler, CallbackQueryHandler, Filters


def start_bot():
    signal.signal(signal.SIGINT, support.cleanup)
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--cfg', default=config.get_default_config_path(),
        type=str,
        help='path to the Dumbledore bot config file (Default: %(default)s'
    )

    parser.add_argument(
        '--create-config', default=False,
        action='store_true',
        help=''
    )

    args = parser.parse_args()

    if args.create_config:
        config.create_default_config(args.cfg)
        sys.exit(0)

    config = config.get_config(args.cfg)
    support.create_needed_paths()
    model.create_databases()

    log = (
        os.path.expanduser(config['general'].get('log')) or
        os.path.join(os.getcwd(), 'debug.log')
    )

    log_handler = TimedRotatingFileHandler(
        log, when='d', interval=1, backupCount=5
    )

    logging.basicConfig(
        format="%(asctime)s %(name)s %(module)s:%(funcName)s:%(lineno)s - %(message)s",
        handlers=[log_handler],
        level=logging.DEBUG
    )

    logging.info("--------------------- Starting bot! -----------------------")

    updater = Updater(
        token=config["telegram"]["token"],
        workers=24,
        request_kwargs={'read_timeout': 15, 'connect_timeout': 15}
    )

    dispatcher = updater.dispatcher

    dispatcher.add_error_handler(support.error_callback)

    dispatcher.add_handler(CommandHandler('ping', ping_cmd))
    dispatcher.add_handler(CommandHandler(['fclist','fc'], fclist_cmd, Filters.group))
    dispatcher.add_handler(CommandHandler(['help','start'], start_cmd, pass_args=True))
    dispatcher.add_handler(CommandHandler(['quienes','whois'], whois_cmd, pass_args=True))

    dispatcher.add_handler(CallbackQueryHandler(profile_btn, pattern=r"^profile_"))
    dispatcher.add_handler(CommandHandler(['profile','perfil'], profile_cmd, Filters.private))
    dispatcher.add_handler(CommandHandler('set_friendid', set_friendid_cmd, Filters.private, pass_args=True))
    dispatcher.add_handler(CommandHandler(['register','registro',''], register_cmd, Filters.private))
    '''
    dispatcher.add_handler(CommandHandler('rm_cmd', rm_cmd_cmd, Filters.group))
    dispatcher.add_handler(CommandHandler('new_cmd', new_cmd_cmd, Filters.group))
    dispatcher.add_handler(CommandHandler('list_cmds', list_cmds_cmd, Filters.group))
    '''
    dispatcher.add_handler(CommandHandler('rm_admin', rm_admin_cmd, Filters.group))
    dispatcher.add_handler(CommandHandler('create_admin', create_admin_cmd, Filters.group))
    dispatcher.add_handler(CommandHandler('settings_admin', settings_admin_cmd, Filters.group))

    dispatcher.add_handler(CommandHandler('rm_link', rm_link_cmd, Filters.group))
    dispatcher.add_handler(CommandHandler('add_tag', add_tag_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('add_url', add_url_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('create_link', create_link_cmd, Filters.group, pass_args=True))
    
    dispatcher.add_handler(CommandHandler(['groups','grupos'], groups_cmd, Filters.group))

    dispatcher.add_handler(CommandHandler('ban', ban_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('kick', kick_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('warn', warn_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('unban', unban_cmd, Filters.group, pass_args=True))
    #dispatcher.add_handler(CommandHandler('unwarn', unwarn_cmd, Filters.group, pass_args=True))

    dispatcher.add_handler(CommandHandler('uv', uv_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('kickuv', kickuv_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('kickmsg', kickmsg_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('kickold', kickold_cmd, Filters.group, pass_args=True))

    dispatcher.add_handler(CommandHandler('rules', rules_cmd, Filters.group))   
    dispatcher.add_handler(CommandHandler('set_rules', set_rules_cmd, Filters.group))  
    dispatcher.add_handler(CommandHandler('clear_rules', clear_rules_cmd, Filters.group))

    dispatcher.add_handler(CommandHandler('list', list_cmd, Filters.group))  
    dispatcher.add_handler(CallbackQueryHandler(list_btn, pattern=r"^list_"))
    dispatcher.add_handler(CommandHandler('listopen', listopen_cmd, Filters.group))    
    dispatcher.add_handler(CommandHandler('listclose', listclose_cmd, Filters.group)) 
    dispatcher.add_handler(CommandHandler('listrefloat', listrefloat_cmd, Filters.group)) 

    dispatcher.add_handler(CommandHandler('settings', settings_cmd, Filters.group))
    dispatcher.add_handler(CommandHandler('set_nanny', set_nanny_cmd, Filters.group)) 
    dispatcher.add_handler(CommandHandler('set_welcome', set_welcome_cmd, Filters.group))
    dispatcher.add_handler(CommandHandler('set_zone', set_zone_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('set_cooldown', set_cooldown_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('set_maxmembers', set_maxmembers_cmd, Filters.group, pass_args=True))

    dispatcher.add_handler(InlineQueryHandler(tablas.inline_tablas))
    dispatcher.add_handler(CallbackQueryHandler(tablas.tablas_btn, pattern=r"^tabla_"))
    dispatcher.add_handler(CommandHandler('tablas', tablas.list_pics, Filters.chat(config["telegram"]["staff_id"])))
    dispatcher.add_handler(CommandHandler('nueva_tabla', tablas.new_pic, Filters.chat(config["telegram"]["staff_id"]),pass_args=True))
    dispatcher.add_handler(CommandHandler('borrar_tabla', tablas.rm_pic, Filters.chat(config["telegram"]["staff_id"]),pass_args=True))
    dispatcher.add_handler(CommandHandler('editar_tabla', tablas.edit_pic, Filters.chat(config["telegram"]["staff_id"]),pass_args=True))

    dispatcher.add_handler(CommandHandler('list_news', news.list_news_cmds, Filters.group))
    dispatcher.add_handler(CommandHandler('rm_news', news.rm_news_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('add_news', news.add_news_cmd, Filters.group, pass_args=True))

    dispatcher.add_handler(MessageHandler(Filters.group & Filters.status_update.new_chat_members, joined_chat, pass_job_queue=True)) 
 
    dispatcher.add_handler(MessageHandler(Filters.command, process_cmd))
    dispatcher.add_handler(MessageHandler(Filters.group & Filters.all, process_group_message))

    dispatcher.add_handler(MessageHandler(Filters.all, send_news))
    dispatcher.add_handler(CallbackQueryHandler(settingsbutton))
    
    job_queue = updater.job_queue
    updater.start_polling(timeout=25)
    
    sys.exit(0)

