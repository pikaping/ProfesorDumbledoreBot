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
import configparser

from os.path import expanduser


__CONFIG = None


class ConfigurationNotLoaded(Exception):
    pass


def get_default_config_path():
    return expanduser('~/.config/dumbledore/config.ini')


def create_default_config(config_dest):
    configdir = os.path.dirname(config_dest)

    if not os.path.exists(configdir):
        os.makedirs(configdir)

    if os.path.exists(config_dest):
        os.rename(config_dest, config_dest + '~')

    with open(config_dest, "w") as f:
        f.write("""[general]
log=/var/local/profdumbledore/log/debug.log
jsondir=/var/local/profdumbledore/json/
mediadir=/var/local/profdumbledore/media/
[database]
debug=False
host=localhost
port=3306
user=####
password=####
schema=dumbledore
[telegram]
token=####
admin_token=####
website=profesordumbledore.com
news_id=####
news_url=####
help_url=####
staff_id=####
spain_id=####
ranking_id=####
ranking_admin_id=####
bot_alias=ProfesorDumbledoreBot
""")

    print("Configuration file has been created on «{}».\nPlease check "
          "the configuration and change it as your wishes.".format(
              config_dest))


def get_config(config_path=None):
    global __CONFIG

    if __CONFIG is not None:
        return __CONFIG

    if not config_path:
        print('Error: no configuration path is provided')
        return None

    if not os.path.isfile(config_path):
        return None

    __CONFIG = configparser.ConfigParser()
    __CONFIG.read(config_path)

    return __CONFIG
