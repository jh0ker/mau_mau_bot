#!/usr/bin/env python3
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

from game import Game
from player import Player


class GameManager(object):
    """ Manages all running games by using a confusing amount of dicts """

    def __init__(self):
        self.chatid_games = dict()
        self.userid_players = dict()
        self.userid_current = dict()
        self.logger = logging.getLogger(__name__)

    def new_game(self, chat):
        """
        Create a new game in this chat
        """
        chat_id = chat.id

        self.logger.info("Creating new game with id " + str(chat_id))
        game = Game(chat)

        if chat_id not in self.chatid_games:
            self.chatid_games[chat_id] = list()

        self.chatid_games[chat_id].append(game)
        return game

    def join_game(self, chat_id, user):
        """ Create a player from the Telegram user and add it to the game """
        self.logger.info("Joining game with id " + str(chat_id))
        try:
            game = self.chatid_games[chat_id][-1]
        except (KeyError, IndexError):
            return None

        if user.id not in self.userid_players:
            self.userid_players[user.id] = list()

        players = self.userid_players[user.id]

        # Don not re-add a player and remove the player from previous games in
        # this chat
        for player in players:
            if player in game.players:
                return False
        else:
            self.leave_game(user, chat_id)

        player = Player(game, user)

        players.append(player)
        self.userid_current[user.id] = player
        return True

    def leave_game(self, user, chat_id):
        """ Remove a player from its current game """
        try:
            players = self.userid_players[user.id]
            games = self.chatid_games[chat_id]

            for player in players:
                for game in games:
                    if player in game.players:
                        if player is game.current_player:
                            game.turn()

                        player.leave()
                        players.remove(player)

                        # If this is the selected game, switch to another
                        if self.userid_current[user.id] is player:
                            if len(players):
                                self.userid_current[user.id] = players[0]
                            else:
                                del self.userid_current[user.id]
                        return True
            else:
                return False

        except KeyError:
            return False

    def end_game(self, chat_id, user):
        """
        End a game
        """

        self.logger.info("Game in chat " + str(chat_id) + " ended")
        players = self.userid_players[user.id]
        games = self.chatid_games[chat_id]
        the_game = None

        # Find the correct game instance to end
        for player in players:
            for game in games:
                if player in game.players:
                    the_game = game
                    break
            if the_game:
                break
        else:
            return

        for player in the_game.players:
            this_users_players = self.userid_players[player.user.id]
            this_users_players.remove(player)
            if len(this_users_players) is 0:
                del self.userid_players[player.user.id]
                del self.userid_current[player.user.id]
            else:
                self.userid_current[player.user.id] = this_users_players[0]

        self.chatid_games[chat_id].remove(the_game)
        return
