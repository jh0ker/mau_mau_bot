import logging

from game import Game
from player import Player


class GameManager(object):
    """ Manages all running games by using a confusing amount of dicts """

    def __init__(self):
        self.chatid_game = dict()
        self.userid_game = dict()
        self.userid_player = dict()
        self.logger = logging.getLogger(__name__)

    def new_game(self, chat_id):
        """
        Generate a game join link with a unique ID and connect the game to the
        group chat
        """

        self.logger.info("Creating new game with id " + str(chat_id))
        game = Game()
        self.chatid_game[chat_id] = game
        self.chatid_game[game] = chat_id

    def join_game(self, chat_id, user):
        """ Create a player from the Telegram user and add it to the game """
        self.logger.info("Joining game with id " + str(chat_id))
        try:
            game = self.chatid_game[chat_id]
        except KeyError:
            return None
        if user.id not in self.userid_game or \
                self.userid_game[user.id] is not game:
            self.leave_game(user)
            player = Player(game, user)
            self.userid_player[user.id] = player
            self.userid_game[user.id] = game
            return True
        else:
            return False

    def leave_game(self, user):
        """ Remove a player from its current game """
        try:
            player = self.userid_player[user.id]

            player.leave()
            del self.userid_player[user.id]
            del self.userid_game[user.id]
            return True
        except KeyError:
            return False

    def end_game(self, chat_id):
        """
        Generate a game join link with a unique ID and connect the game to the
        group chat
        """

        self.logger.info("Game with id " + str(chat_id) + " ended")
        game = self.chatid_game[chat_id]
        self.leave_game(game.current_player.user)
        del self.chatid_game[chat_id]
        del self.chatid_game[game]
