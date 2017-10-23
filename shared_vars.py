#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Telegram bot to play UNO in group chats
# Copyright (c) 2016 Jannes Höke <uno@jhoeke.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import json

import logging
from telegram.ext import Updater
from telegram.contrib.botan import Botan

from game_manager import GameManager
from database import db

db.bind('sqlite', 'uno.sqlite3', create_db=True)
db.generate_mapping(create_tables=True)

gm = GameManager()
with open("config.json","r") as f:
    config = json.loads(f.read())
updater = Updater(token=config.get("token"), workers=config.get("workers", 32))
dispatcher = updater.dispatcher

if config.get("botan_token"):
    botan = Botan(config.get("botan_token"))
else:
    botan = None