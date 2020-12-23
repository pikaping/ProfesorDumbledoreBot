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

import argparse
import logging
import os
import signal
import sys
from logging.handlers import TimedRotatingFileHandler
from datetime import timedelta
from time import time
import pickle
from threading import Event

from telegram.ext import Updater, CommandHandler, MessageHandler, InlineQueryHandler, CallbackQueryHandler, Filters

import profdumbledorebot.admin as admin
import profdumbledorebot.config as config_file
import profdumbledorebot.group as group
import profdumbledorebot.lists as lists
import profdumbledorebot.model as model
import profdumbledorebot.nanny as nanny
import profdumbledorebot.news as news
import profdumbledorebot.profdumbledorebot as profdumbledorebot
import profdumbledorebot.rules as rules
import profdumbledorebot.settings as settings
import profdumbledorebot.supportmethods as support
import profdumbledorebot.tablas as tablas
import profdumbledorebot.games as games
import profdumbledorebot.greenhouses as greenhouses
import profdumbledorebot.welcome as welcome
import profdumbledorebot.sighting as sighting
import profdumbledorebot.fortress as fortress
import profdumbledorebot.staff as staff

def save_jobs_job(job, context):
    support.save_jobs(context.job_queue)

def start_bot():
    signal.signal(signal.SIGINT, support.cleanup)
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--cfg', default=config_file.get_default_config_path(),
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
        config_file.create_default_config(args.cfg)
        sys.exit(0)

    config = config_file.get_config(args.cfg)
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

    dispatcher.add_handler(CommandHandler('games', games.utils.game_spawn_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('ppt', games.rps.rps_user_cmd, Filters.group, pass_args=True, pass_job_queue=True))
    #dispatcher.add_handler(CommandHandler('duel', games.duel_cmd, Filters.group)) HAHANOPE
    dispatcher.add_handler(CallbackQueryHandler(games.utils.btn_parser, pattern=r"^g\*"))

    #Juego Cumple Nelu
    #dispatcher.add_handler(CommandHandler('nelu', nelu.nelu_cmd, Filters.user(int(config["telegram"]["saray"])), pass_job_queue=True))
    #dispatcher.add_handler(CallbackQueryHandler(nelu.nelu_btn, pattern=r"^nelu_"))

    dispatcher.add_handler(CommandHandler(['fort','fortaleza'], fortress.fort_list_cmd, Filters.group, pass_args=True))
    #dispatcher.add_handler(CommandHandler(['fort_refloat', 'fortrefloat'], fortress.fort_refloat_cmd, Filters.group))
    #dispatcher.add_handler(CommandHandler(['fort_delete', 'fortremove', 'rm_fort'], fortress.fort_remove_cmd, Filters.group))
    dispatcher.add_handler(CallbackQueryHandler(fortress.fort_btn, pattern=r"^fort_", pass_job_queue=True))

    #TBRdispatcher.add_handler(CommandHandler('avistamiento', sighting.sighting_cmd, Filters.group))
    dispatcher.add_handler(CallbackQueryHandler(sighting.sighting_btn, pattern=r"^sighting_"))

    dispatcher.add_handler(CommandHandler(['add_plant','addplant'], greenhouses.add_ingredients_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler(['rm_plant','rmplant'], greenhouses.rem_plant_cmd, Filters.group, pass_args=True, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler(['plantaciones','plant_list'], greenhouses.plants_list_cmd, Filters.group))
    dispatcher.add_handler(CallbackQueryHandler(greenhouses.gh_btn, pattern=r"^gh_", pass_job_queue=True))

    dispatcher.add_handler(CommandHandler(['add_poi','addpoi'], profdumbledorebot.add_poi_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler(['rm_poi','rmpoi'], profdumbledorebot.rem_poi_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler(['poi_list','poilist'], profdumbledorebot.poi_list_cmd, Filters.group))
    dispatcher.add_handler(CallbackQueryHandler(profdumbledorebot.poi_btn, pattern=r"^poi_"))

    dispatcher.add_handler(CommandHandler(['midepollas','flipaos'], profdumbledorebot.ranking_spain_cmd, Filters.chat(int(config["telegram"]["spain_id"])) & Filters.user(int(config["telegram"]["ranking_admin_id"]))))
    #TBRdispatcher.add_handler(CommandHandler('puntos', profdumbledorebot.points_cmd, Filters.private))
    dispatcher.add_handler(CommandHandler('ranking', profdumbledorebot.private_ranking_cmd, Filters.group))

    dispatcher.add_handler(CommandHandler('ping', profdumbledorebot. ping_cmd))
    dispatcher.add_handler(CommandHandler(['fclist','fc'], profdumbledorebot.fclist_cmd, Filters.group))
    dispatcher.add_handler(CommandHandler(['help','start'], profdumbledorebot.start_cmd, pass_args=True))
    dispatcher.add_handler(CommandHandler(['whois','informe','info'], profdumbledorebot.whois_cmd, pass_args=True))

    dispatcher.add_handler(CallbackQueryHandler(profdumbledorebot.register_btn, pattern=r"^reg_"))
    dispatcher.add_handler(CallbackQueryHandler(profdumbledorebot.passport_btn, pattern=r"^profile_"))
    dispatcher.add_handler(CommandHandler(['passport','pasaporte','profile','perfil'], profdumbledorebot.passport_cmd, Filters.private))
    dispatcher.add_handler(CommandHandler('set_friendid', profdumbledorebot.set_friendid_cmd, Filters.private, pass_args=True))
    dispatcher.add_handler(CommandHandler(['register','registro','cucuruchodecucarachas'], profdumbledorebot.register_cmd, Filters.private))
    '''
    dispatcher.add_handler(CommandHandler('rm_cmd', rm_cmd_cmd, Filters.group))
    dispatcher.add_handler(CommandHandler('new_cmd', new_cmd_cmd, Filters.group))
    dispatcher.add_handler(CommandHandler('list_cmds', list_cmds_cmd, Filters.group))
    '''
    dispatcher.add_handler(CommandHandler('rm_admin', admin.rm_admin_cmd, Filters.group))
    dispatcher.add_handler(CommandHandler('create_admin', admin.create_admin_cmd, Filters.group))
    dispatcher.add_handler(CommandHandler('settings_admin', admin.settings_admin_cmd, Filters.group))

    dispatcher.add_handler(CommandHandler('rm_link', admin.rm_link_cmd, Filters.group))
    dispatcher.add_handler(CommandHandler('add_tag', admin.add_tag_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('add_url', admin.add_url_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('create_link', admin.create_link_cmd, Filters.group, pass_args=True))
    
    dispatcher.add_handler(CommandHandler(['groups','grupos'], admin.groups_cmd, Filters.group))

    dispatcher.add_handler(CommandHandler('ban', admin.ban_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('kick', admin.kick_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('warn', admin.warn_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('unban', admin.unban_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('id', admin.whois_id, pass_args=True))
    #dispatcher.add_handler(CommandHandler('group_id', admin.whois_group, pass_args=True))
    #dispatcher.add_handler(CommandHandler('mute', admin.mute_cmd, Filters.group, pass_args=True))
    #dispatcher.add_handler(CommandHandler('unwarn', unwarn_cmd, Filters.group, pass_args=True))

    dispatcher.add_handler(CommandHandler('dumbleuv', admin.uv_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('dumblekickuv', admin.kickuv_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('dumblekickmsg', admin.kickmsg_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('dumblekickold', admin.kickold_cmd, Filters.group, pass_args=True))

    dispatcher.add_handler(CommandHandler('rules', rules.rules, Filters.group))   
    dispatcher.add_handler(CommandHandler('set_rules', rules.set_rules, Filters.group))  
    dispatcher.add_handler(CommandHandler('clear_rules', rules.clear_rules, Filters.group))

    dispatcher.add_handler(CommandHandler('list', lists.list_cmd, Filters.group))  
    dispatcher.add_handler(CallbackQueryHandler(lists.list_btn, pattern=r"^list_"))
    dispatcher.add_handler(CommandHandler('listopen', lists.listopen_cmd, Filters.group))    
    dispatcher.add_handler(CommandHandler('listclose', lists.listclose_cmd, Filters.group)) 
    dispatcher.add_handler(CommandHandler('listrefloat', lists.listrefloat_cmd, Filters.group)) 

    dispatcher.add_handler(CommandHandler('settings', settings.settings, Filters.group))
    dispatcher.add_handler(CommandHandler('set_pince', nanny.set_nanny, Filters.group)) 
    dispatcher.add_handler(CommandHandler('set_welcome', settings.set_welcome, Filters.group))
    #TBRdispatcher.add_handler(CommandHandler('test_welcome', welcome.test_welcome, Filters.group))
    dispatcher.add_handler(CommandHandler('set_zone', settings.set_zone, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('set_cooldown', settings.set_cooldown, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('set_maxmembers', settings.set_maxmembers, Filters.group, pass_args=True))

    dispatcher.add_handler(InlineQueryHandler(tablas.inline_tablas))
    dispatcher.add_handler(CallbackQueryHandler(tablas.tablas_btn, pattern=r"^tabla_"))
    dispatcher.add_handler(CommandHandler('tablas', tablas.list_pics, Filters.chat(int(config["telegram"]["staff_id"])),pass_args=True))
    dispatcher.add_handler(CommandHandler('nueva_tabla', tablas.new_pic, Filters.chat(int(config["telegram"]["staff_id"])),pass_args=True))
    dispatcher.add_handler(CommandHandler('borrar_tabla', tablas.rm_pic, Filters.chat(int(config["telegram"]["staff_id"])),pass_args=True))
    dispatcher.add_handler(CommandHandler('editar_tabla', tablas.edit_pic, Filters.chat(int(config["telegram"]["staff_id"])),pass_args=True))

    dispatcher.add_handler(CommandHandler('list_news', news.list_news, Filters.group))
    dispatcher.add_handler(CommandHandler('rm_news', news.rm_news, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('add_news', news.add_news, Filters.group, pass_args=True))

    dispatcher.add_handler(CommandHandler('add_staff', staff.add_staff_cmd, pass_args=True))
    dispatcher.add_handler(CommandHandler('rm_staff', staff.rm_staff_cmd, pass_args=True))
    dispatcher.add_handler(CommandHandler('add_ghost', staff.add_ghost_cmd, pass_args=True))
    dispatcher.add_handler(CommandHandler('rm_ghost', staff.rm_ghost_cmd, pass_args=True))
    dispatcher.add_handler(CommandHandler('r', staff.staff_register_cmd, pass_args=True))

    dispatcher.add_handler(MessageHandler(Filters.group & Filters.status_update.new_chat_members, group.joined_chat, pass_job_queue=True)) 
 
    dispatcher.add_handler(MessageHandler(Filters.command, nanny.process_cmd, pass_job_queue=True))
    dispatcher.add_handler(MessageHandler(Filters.group & Filters.all, group.process_group_message, pass_job_queue=True))

    dispatcher.add_handler(MessageHandler(Filters.private & Filters.all, games.utils.potato_process))

    dispatcher.add_handler(MessageHandler(Filters.all, news.send_news))
    dispatcher.add_handler(CallbackQueryHandler(settings.settingsbutton))
    
    job_queue = updater.job_queue
    job_queue.run_repeating(save_jobs_job, timedelta(minutes=5))
    try:
        support.load_jobs(job_queue)

    except FileNotFoundError:
        # First run
        pass

    updater.start_polling(timeout=25)
    
    support.save_jobs(job_queue)

    sys.exit(0)

