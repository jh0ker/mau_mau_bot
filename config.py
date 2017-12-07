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

with open("config.json","r") as f:
    config = json.loads(f.read())

TOKEN=config.get("token")
WORKERS=config.get("workers", 32)
ADMIN_LIST = config.get("admin_list", None)
OPEN_LOBBY = config.get("open_lobby", True)
ENABLE_TRANSLATIONS = config.get("enable_translations", False)
DEFAULT_GAMEMODE = config.get("default_gamemode", "fast")
WAITING_TIME = config.get("waiting_time", 120)
TIME_REMOVAL_AFTER_SKIP = config.get("time_removal_after_skip", 20)
MIN_FAST_TURN_TIME = config.get("min_fast_turn_time", 15)
MIN_PLAYERS = config.get("min_players", 2)
