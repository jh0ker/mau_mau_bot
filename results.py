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


"""Defines helper functions to build the inline result list"""

from uuid import uuid4

from telegram import InlineQueryResultArticle, InputTextMessageContent, \
    InlineQueryResultCachedSticker as Sticker

import card as c
from utils import *


def add_choose_color(results):
    """Add choose color options"""
    for color in c.COLORS:
        results.append(
            InlineQueryResultArticle(
                id=color,
                title="Choose Color",
                description=display_color(color),
                input_message_content=
                InputTextMessageContent(display_color(color))
            )
        )


def add_other_cards(playable, player, results, game):
    """Add hand cards when choosing colors"""
    if not playable:
        playable = list()

    players = player_list(game)

    results.append(
        InlineQueryResultArticle(
            "hand",
            title="Cards (tap for game state):",
            description=', '.join([repr(card) for card in
                                   list_subtract(player.cards, playable)]),
            input_message_content=InputTextMessageContent(
                "Current player: " + display_name(game.current_player.user) +
                "\n" +
                "Last card: " + repr(game.last_card) + "\n" +
                "Players: " + " -> ".join(players))
        )
    )


def player_list(game):
    """Generate list of player strings"""
    return [player.user.first_name + " (%d cards)" % len(player.cards)
            for player in game.players]



def add_no_game(results):
    """Add text result if user is not playing"""
    results.append(
        InlineQueryResultArticle(
            "nogame",
            title="You are not playing",
            input_message_content=
            InputTextMessageContent('Not playing right now. Use /new to start '
                                    'a game or /join to join the current game '
                                    'in this group')
        )
    )


def add_not_started(results):
    """Add text result if the game has not yet started"""
    results.append(
        InlineQueryResultArticle(
            "nogame",
            title="The game wasn't started yet",
            input_message_content=
            InputTextMessageContent('Start the game with /start')
        )
    )


def add_draw(player, results):
    """Add option to draw"""
    results.append(
        Sticker(
            "draw", sticker_file_id=c.STICKERS['option_draw'],
            input_message_content=
            InputTextMessageContent('Drawing %d card(s)'
                                    % (player.game.draw_counter or 1))
        )
    )


def add_gameinfo(game, results):
    """Add option to show game info"""
    players = player_list(game)

    results.append(
        Sticker(
            "gameinfo",
            sticker_file_id=c.STICKERS['option_info'],
            input_message_content=InputTextMessageContent(
                "Current player: " + display_name(game.current_player.user) +
                "\n" +
                "Last card: " + repr(game.last_card) + "\n" +
                "Players: " + " -> ".join(players))
        )
    )


def add_pass(results):
    """Add option to pass"""
    results.append(
        Sticker(
            "pass", sticker_file_id=c.STICKERS['option_pass'],
            input_message_content=InputTextMessageContent('Pass')
        )
    )


def add_call_bluff(results):
    """Add option to call a bluff"""
    results.append(
        Sticker(
            "call_bluff",
            sticker_file_id=c.STICKERS['option_bluff'],
            input_message_content=
            InputTextMessageContent("I'm calling your bluff!")
        )
    )


def add_card(game, card, results, can_play):
    """Add an option that represents a card"""
    players = player_list(game)

    if can_play:
        results.append(
            Sticker(str(card), sticker_file_id=c.STICKERS[str(card)])
        )
    else:
        results.append(
            Sticker(str(uuid4()), sticker_file_id=c.STICKERS_GREY[str(card)],
                    input_message_content=InputTextMessageContent(
                        "Current player: " + display_name(
                            game.current_player.user) +
                        "\n" +
                        "Last card: " + repr(game.last_card) + "\n" +
                        "Players: " + " -> ".join(players)))
        )

