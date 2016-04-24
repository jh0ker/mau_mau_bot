import logging

from game import Game
from player import Player


class GameManager(object):
    """ Manages all running games by using a confusing amount of dicts """

    def __init__(self):
        self.chatid_game = dict()
        self.userid_players = dict()
        self.userid_current = dict()
        self.logger = logging.getLogger(__name__)

    def new_game(self, chat):
        """
        Generate a game join link with a unique ID and connect the game to the
        group chat
        """
        chat_id = chat.id

        self.logger.info("Creating new game with id " + str(chat_id))
        game = Game(chat)
        self.chatid_game[chat_id] = game
        self.chatid_game[game] = chat_id

    def join_game(self, chat_id, user):
        """ Create a player from the Telegram user and add it to the game """
        self.logger.info("Joining game with id " + str(chat_id))
        try:
            game = self.chatid_game[chat_id]
        except KeyError:
            return None

        players = self.userid_players.get(user.id, list())

        if not players:
            self.userid_players[user.id] = players
        else:
            self.leave_game(user, chat_id)

        if game not in [player.game for player in players]:
            try:
                player = Player(game, user)
            except AttributeError:
                return None

            players.append(player)
            self.userid_current[user.id] = player
            return True
        else:
            return False

    def leave_game(self, user, chat_id):
        """ Remove a player from its current game """
        try:
            players = self.userid_players[user.id]

            for player in list(players):
                if player.game.chat.id == chat_id:
                    player.leave()
                    players.remove(player)
                    if self.userid_current[user.id] is player:
                        if len(players):
                            self.userid_current[user.id] = players[0]
                        else:
                            del self.userid_current[user.id]
                    break
            else:
                return False

            return True
        except KeyError:
            self.logger.info("Leaving game failed")
            return False

    def end_game(self, chat_id, user):
        """
        Generate a game join link with a unique ID and connect the game to the
        group chat
        """

        self.logger.info("Game with id " + str(chat_id) + " ended")
        players = self.userid_players[user.id]
        for player in players:
            if not player.game.chat.id == chat_id:
                game = player.game
                del self.chatid_game[game]
                break

        self.leave_game(user, chat_id)
