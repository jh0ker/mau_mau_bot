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

from game_manager import GameManager
from database import db

db.bind('sqlite', 'uno.sqlite3', create_db=True)
db.generate_mapping(create_tables=True)

gm = GameManager()
with open("config.json","r") as f:
    config = json.loads(f.read())
updater = Updater(token=config.get("token"), workers=config.get("workers", 32))
dispatcher = updater.dispatcher


class botan_wrapper:

    """In order to modify less code.
    """

    def __init__(self, token):		
        self.token = token

    def track(self, message, event_name='event'):
        uid = message.from_user
        message_dict = message.to_dict()
        print botan_sdk.track(token, uid, message_dict, event_name)


if config.get("botan_token"):

    try:
        from botan import botan as botan_sdk
    except ModuleNotFoundError:
        botan = None
        print("A botan token is set but the submodule can't be found. Botan is disabled.")
    else:
        botan = botan_wrapper(config.get("botan_token"))

else:
    botan = None
