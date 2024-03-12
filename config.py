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


import os
import json

try:
    with open("config.json", "r") as f:
        config = json.load(f)
except FileNotFoundError:
    config = {}

TOKEN = os.getenv("TOKEN", config.get("token"))
WORKERS = int(os.getenv("WORKERS", config.get("workers", 32)))
ADMIN_LIST = os.getenv("ADMIN_LIST", config.get("admin_list", None))

if isinstance(ADMIN_LIST, str):
    ADMIN_LIST = set(int(x) for x in ADMIN_LIST.split())

OPEN_LOBBY = os.getenv("OPEN_LOBBY", config.get("open_lobby", True))
ENABLE_TRANSLATIONS = os.getenv("ENABLE_TRANSLATIONS", config.get("enable_translations", False))

if isinstance(OPEN_LOBBY, str):
    OPEN_LOBBY = OPEN_LOBBY.lower() in ("yes", "true", "t", "1")

if isinstance(ENABLE_TRANSLATIONS, str):
    ENABLE_TRANSLATIONS = ENABLE_TRANSLATIONS.lower() in ("yes", "true", "t", "1")

DEFAULT_GAMEMODE = os.getenv("DEFAULT_GAMEMODE", config.get("default_gamemode", "fast"))
WAITING_TIME = int(os.getenv("WAITING_TIME", config.get("waiting_time", 120)))
TIME_REMOVAL_AFTER_SKIP = int(os.getenv("TIME_REMOVAL_AFTER_SKIP", config.get("time_removal_after_skip", 20)))
MIN_FAST_TURN_TIME = int(os.getenv("MIN_FAST_TURN_TIME", config.get("min_fast_turn_time", 15)))
MIN_PLAYERS = int(os.getenv("MIN_PLAYERS", config.get("min_players", 2)))
