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


"""Defines a dict of all available locales to the language name"""

OFFSET = 127462 - ord('A')


def flag(code):
    return chr(ord(code[0]) + OFFSET) + chr(ord(code[1]) + OFFSET)


available_locales = {'en_US': flag('US') + ' English (US)',
                     'de_DE': flag('DE') + ' Deutsch (DE)',
                     'es_ES': flag('ES') + ' Español (ES)',
                     'id_ID': flag('ID') + ' Bahasa Indonesia',
                     'it_IT': flag('IT') + ' Italiano',
                     'pt_BR': flag('BR') + ' Português Brasileiro',
                     'ru_RU': flag('RU') + ' Русский язык',
                     'zh_CN': flag('CN') + ' 中文(简体)',
                     'zh_HK': flag('HK') + ' 廣東話',
                     'zh_TW': flag('TW') + ' 中文(香港)'}
