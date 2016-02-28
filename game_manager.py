from uuid import uuid4
from game import Game
from player import Player

LINK_PATTERN = 'https://telegram.me/%s?start=%s'


class GameManager(object):

    def __init__(self):
        self.gameid_game = dict()
        self.userid_game = dict()
        self.chatid_gameid = dict()
        self.userid_user = dict()
        self.userid_player = dict()

    def generate_invite_link(self, bot_name, chat_id):
        game_id = uuid4()
        game = Game()
        self.gameid_game[game_id] = game
        self.chatid_gameid[chat_id] = game_id

        return LINK_PATTERN % (bot_name, game_id)

    def join_game(self, game_id, user):
        game = self.gameid_game[game_id]
        player = Player(game, user)
        self.userid_player[user.id] = player
        self.userid_game[user.id] = game
