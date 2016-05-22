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


import logging
from functools import wraps

from flufl.i18n import registry
from flufl.i18n import PackageStrategy

from telegram import Emoji
from telegram.ext.dispatcher import run_async
import locales
from database import db_session
from user_setting import UserSetting
from shared_vars import gm

strategy = PackageStrategy('unobot', locales)
application = registry.register(strategy)
_ = application._
logger = logging.getLogger(__name__)

TIMEOUT = 2.5


def __(string, multi_translate):
    """Translates text into all locales on the stack"""
    translations = list()
    locales = list()

    if not multi_translate:
        _.push('en_US')
        translations.append(_(string))
        _.pop()

    else:
        while _.code:
            translation = _(string)

            if translation not in translations:
                translations.append(translation)

            locales.append(_.code)
            _.pop()

        for l in reversed(locales):
            _.push(l)

    return '\n'.join(translations)


def list_subtract(list1, list2):
    """ Helper function to subtract two lists and return the sorted result """
    list1 = list1.copy()

    for x in list2:
        list1.remove(x)

    return list(sorted(list1))


def display_name(user):
    """ Get the current players name including their username, if possible """
    user_name = user.first_name
    if user.username:
        user_name += ' (@' + user.username + ')'
    return user_name


def display_color(color):
    """ Convert a color code to actual color name """
    if color == "r":
        return _("{emoji} Red").format(emoji=Emoji.HEAVY_BLACK_HEART)
    if color == "b":
        return _("{emoji} Blue").format(emoji=Emoji.BLUE_HEART)
    if color == "g":
        return _("{emoji} Green").format(emoji=Emoji.GREEN_HEART)
    if color == "y":
        return _("{emoji} Yellow").format(emoji=Emoji.YELLOW_HEART)


def display_color_group(color, game):
    """ Convert a color code to actual color name """
    if color == "r":
        return __("{emoji} Red", game.translate).format(
            emoji=Emoji.HEAVY_BLACK_HEART)
    if color == "b":
        return __("{emoji} Blue", game.translate).format(
            emoji=Emoji.BLUE_HEART)
    if color == "g":
        return __("{emoji} Green", game.translate).format(
            emoji=Emoji.GREEN_HEART)
    if color == "y":
        return __("{emoji} Yellow", game.translate).format(
            emoji=Emoji.YELLOW_HEART)


def error(bot, update, error):
    """Simple error handler"""
    logger.exception(error)


@run_async
def send_async(bot, *args, **kwargs):
    """Send a message asynchronously"""
    if 'timeout' not in kwargs:
        kwargs['timeout'] = TIMEOUT

    try:
        bot.sendMessage(*args, **kwargs)
    except Exception as e:
        error(None, None, e)


@run_async
def answer_async(bot, *args, **kwargs):
    """Answer an inline query asynchronously"""
    if 'timeout' not in kwargs:
        kwargs['timeout'] = TIMEOUT

    try:
        bot.answerInlineQuery(*args, **kwargs)
    except Exception as e:
        error(None, None, e)


def user_locale(func):
    @wraps(func)
    @db_session
    def wrapped(bot, update, *pargs, **kwargs):
        user, chat = _user_chat_from_update(update)

        with db_session:
            us = UserSetting.get(id=user.id)

            if us:
                _.push(us.lang)
            else:
                _.push('en_US')

        result = func(bot, update, *pargs, **kwargs)
        _.pop()
        return result
    return wrapped


def game_locales(func):
    @wraps(func)
    @db_session
    def wrapped(bot, update, *pargs, **kwargs):
        user, chat = _user_chat_from_update(update)
        player = gm.player_for_user_in_chat(user, chat)
        locales = list()

        if player:
            for player in player.game.players:
                us = UserSetting.get(id=player.user.id)

                if us:
                    loc = us.lang
                else:
                    loc = 'en_US'

                if loc in locales:
                    continue

                _.push(loc)
                locales.append(loc)

        result = func(bot, update, *pargs, **kwargs)

        for i in locales:
            _.pop()
        return result
    return wrapped


def _user_chat_from_update(update):

    try:
        user = update.message.from_user
        chat = update.message.chat
    except (NameError, AttributeError):
        try:
            user = update.inline_query.from_user
            chat = gm.userid_current[user.id].game.chat
        except KeyError:
            chat = None
        except (NameError, AttributeError):
            try:
                user = update.chosen_inline_result.from_user
                chat = gm.userid_current[user.id].game.chat
            except (NameError, AttributeError):
                chat = None

    return user, chat
