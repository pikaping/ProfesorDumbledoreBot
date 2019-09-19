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

JOBS_PICKLE = 'job_tuples.pickle'

def load_jobs(jq):
    now = time()

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

def save_jobs_job(job, context):
    save_jobs(context.job_queue)

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

    #dispatcher.add_handler(CommandHandler('games', games.games_cmd, Filters.group))
    #dispatcher.add_handler(CommandHandler('duel', games.duel_cmd, Filters.group))
    dispatcher.add_handler(CallbackQueryHandler(games.btn, pattern=r"^g\*"))

    #Juego Cumple Nelu
    #dispatcher.add_handler(CommandHandler('nelu', nelu.nelu_cmd, Filters.user(int(config["telegram"]["saray"])), pass_job_queue=True))
    #dispatcher.add_handler(CallbackQueryHandler(nelu.nelu_btn, pattern=r"^nelu_"))

    dispatcher.add_handler(CommandHandler(['fort','fortaleza'], fortress.fort_list_cmd, Filters.group, pass_args=True))
    #dispatcher.add_handler(CommandHandler(['fort_refloat', 'fortrefloat'], fortress.fort_refloat_cmd, Filters.group))
    dispatcher.add_handler(CommandHandler(['fort_delete', 'fortremove', 'rm_fort'], fortress.fort_remove_cmd, Filters.group))
    dispatcher.add_handler(CallbackQueryHandler(fortress.fort_btn, pattern=r"^fort_", pass_job_queue=True))

    dispatcher.add_handler(CommandHandler('avistamiento', sighting.sighting_cmd, Filters.group & Filters.chat(int(config["telegram"]["beta_group"]))))
    dispatcher.add_handler(CallbackQueryHandler(sighting.sighting_btn, pattern=r"^sighting_"))

    dispatcher.add_handler(CommandHandler('add_plant', greenhouses.add_ingredients_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('rm_plant', greenhouses.rem_plant_cmd, Filters.group, pass_args=True, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler(['plantaciones','plant_list'], greenhouses.plants_list_cmd, Filters.group))
    dispatcher.add_handler(CallbackQueryHandler(greenhouses.gh_btn, pattern=r"^gh_", pass_job_queue=True))

    dispatcher.add_handler(CommandHandler('add_poi', profdumbledorebot.add_poi_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('rm_poi', profdumbledorebot.rem_poi_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('poi_list', profdumbledorebot.poi_list_cmd, Filters.group))
    dispatcher.add_handler(CallbackQueryHandler(profdumbledorebot.poi_btn, pattern=r"^poi_"))

    dispatcher.add_handler(CommandHandler(['midepollas','flipaos'], profdumbledorebot.ranking_spain_cmd, Filters.chat(int(config["telegram"]["spain_id"])) & Filters.user(int(config["telegram"]["ranking_admin_id"]))))
    dispatcher.add_handler(CommandHandler('puntos', profdumbledorebot.points_cmd, Filters.private))
    dispatcher.add_handler(CommandHandler('ranking', profdumbledorebot.private_ranking_cmd, Filters.group))

    dispatcher.add_handler(CommandHandler('ping', profdumbledorebot. ping_cmd))
    dispatcher.add_handler(CommandHandler(['fclist','fc'], profdumbledorebot.fclist_cmd, Filters.group))
    dispatcher.add_handler(CommandHandler(['help','start'], profdumbledorebot.start_cmd, pass_args=True))
    dispatcher.add_handler(CommandHandler(['informe','info'], profdumbledorebot.whois_cmd, pass_args=True))

    dispatcher.add_handler(CallbackQueryHandler(profdumbledorebot.register_btn, pattern=r"^reg_"))
    dispatcher.add_handler(CallbackQueryHandler(profdumbledorebot.passport_btn, pattern=r"^profile_"))
    dispatcher.add_handler(CommandHandler(['passport','pasaporte'], profdumbledorebot.passport_cmd, Filters.private))
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
    #dispatcher.add_handler(CommandHandler('mute', admin.mute_cmd, Filters.group, pass_args=True))
    #dispatcher.add_handler(CommandHandler('unwarn', unwarn_cmd, Filters.group, pass_args=True))

    dispatcher.add_handler(CommandHandler('uv', admin.uv_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('kickuv', admin.kickuv_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('kickmsg', admin.kickmsg_cmd, Filters.group, pass_args=True))
    dispatcher.add_handler(CommandHandler('kickold', admin.kickold_cmd, Filters.group, pass_args=True))

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
    dispatcher.add_handler(CommandHandler('test_welcome', welcome.test_welcome, Filters.group))
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

    dispatcher.add_handler(MessageHandler(Filters.group & Filters.status_update.new_chat_members, group.joined_chat, pass_job_queue=True)) 
 
    dispatcher.add_handler(MessageHandler(Filters.command, nanny.process_cmd, pass_job_queue=True))
    dispatcher.add_handler(MessageHandler(Filters.group & Filters.all, group.process_group_message, pass_job_queue=True))

    dispatcher.add_handler(MessageHandler(Filters.all, news.send_news))
    dispatcher.add_handler(CallbackQueryHandler(settings.settingsbutton))
    
    job_queue = updater.job_queue
    job_queue.run_repeating(save_jobs_job, timedelta(minutes=5))
    try:
        load_jobs(job_queue)

    except FileNotFoundError:
        # First run
        pass

    updater.start_polling(timeout=25)
    
    save_jobs(job_queue)

    sys.exit(0)

