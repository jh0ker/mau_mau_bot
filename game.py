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
from config import (ADMIN_LIST, OPEN_LOBBY, DEFAULT_GAMEMODE,
                    ENABLE_TRANSLATIONS, SCORE_WIN)
from datetime import datetime

from deck import Deck
import card as c

class Game(object):
    """ This class represents a game of UNO """
    current_player = None
    reversed = False
    choosing_color = False
    started = False
    draw_counter = 0
    players_won = 0
    starter = None
    mode = DEFAULT_GAMEMODE
    job = None
    owner = ADMIN_LIST
    open = OPEN_LOBBY
    translate = ENABLE_TRANSLATIONS
    scores = dict()
    last_round_score = list()
    win_score = SCORE_WIN

    def __init__(self, chat):
        self.chat = chat
        self.last_card = None

        self.deck = Deck()

        self.logger = logging.getLogger(__name__)

    @property
    def players(self):
        """Returns a list of all players in this game"""
        players = list()
        if not self.current_player:
            return players

        current_player = self.current_player
        itplayer = current_player.next
        players.append(current_player)
        while itplayer and itplayer is not current_player:
            players.append(itplayer)
            itplayer = itplayer.next
        return players

    def start(self):
        if self.mode == None or self.mode != "wild":
            self.deck._fill_classic_()
        else:
            self.deck._fill_wild_()

        self._first_card_()
        self.started = True

    def set_mode(self, mode):
        self.mode = mode

    def reverse(self):
        """Reverses the direction of game"""
        self.reversed = not self.reversed

    def turn(self):
        """Marks the turn as over and change the current player"""
        self.logger.debug("Next Player")
        self.current_player = self.current_player.next
        self.current_player.drew = False
        self.current_player.turn_started = datetime.now()
        self.choosing_color = False

    def _first_card_(self):
        # In case that the player did not select a game mode
        if not self.deck.cards:
            self.set_mode(DEFAULT_GAMEMODE)

        # The first card should not be a special card
        while not self.last_card or self.last_card.special:
            self.last_card = self.deck.draw()
            # If the card drawn was special, return it to the deck and loop again
            if self.last_card.special:
                self.deck.dismiss(self.last_card)

        self.play_card(self.last_card)

    def play_card(self, card):
        """
        Plays a card and triggers its effects.
        Should be called only from Player.play or on game start to play the
        first card
        """
        self.deck.dismiss(self.last_card)
        self.last_card = card

        self.logger.info("Playing card " + repr(card))
        if card.value == c.SKIP:
            self.turn()
        elif card.special == c.DRAW_FOUR:
            self.draw_counter += 4
            self.logger.debug("Draw counter increased by 4")
        elif card.value == c.DRAW_TWO:
            self.draw_counter += 2
            self.logger.debug("Draw counter increased by 2")
        elif card.value == c.REVERSE:
            # Special rule for two players
            if self.current_player is self.current_player.next.next:
                self.turn()
            else:
                self.reverse()

        # Don't turn if the current player has to choose a color
        if card.special not in (c.CHOOSE, c.DRAW_FOUR):
            self.turn()
        else:
            self.logger.debug("Choosing Color...")
            self.choosing_color = True

    def choose_color(self, color):
        """Carries out the color choosing and turns the game"""
        self.last_card.color = color
        self.turn()

    def add_score(self, player):
        """Add total value of all card in every players hand
        to the winner's score."""
        scores = 0
        self.last_round_score.clear()
        for player in self.players:
            for card in player.cards:
                sc = c.CARD_SCORES[card.value or card.special]
                self.last_round_score.append((sc, card))
                scores += sc
        try:
            self.scores[player.user.id] += scores
        except KeyError:
            self.scores[player.user.id] = scores

    def reset_cards(self):
        """Reset game deck and player's hand"""
        players_cache = self.players
        # clear player's card, might as well use player.cards.clear()
        for player in players_cache:
            for card in player.cards:
                self.deck.dismiss(card)
            player.cards = list()
        # fill deck with normal cards set
        self.deck._fill_classic_()
        # draw player's hand
        for player in players_cache:
            player.draw_first_hand()

    def new_round(self):
        lc = self.last_card
        while self.last_card == lc or not self.last_card or self.last_card.special:
            self.last_card = self.deck.draw()
            # If the card drawn was special, return it to the deck and loop again
            if self.last_card.special:
                self.deck.dismiss(self.last_card)
        self.play_card(self.last_card)

    def get_score(self, player):
        try:
            return self.scores[player.user.id]
        except KeyError:
            self.scores[player.user.id] = 0
            return 0

    def get_scores(self):
        return [(player, self.get_score(player))for player in self.players]
