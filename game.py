import logging
from datetime import datetime

from deck import Deck
import card as c


class Game(object):
    """ This class represents a game of UNO """
    current_player = None
    reversed = False
    draw_counter = 0
    choosing_color = False
    started = False
    owner = None
    open = True

    def __init__(self, chat):
        self.chat = chat
        self.deck = Deck()
        self.last_card = self.deck.draw()

        while self.last_card.special:
            self.deck.dismiss(self.last_card)
            self.deck.shuffle()
            self.last_card = self.deck.draw()

        self.logger = logging.getLogger(__name__)

    @property
    def players(self):
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

    def reverse(self):
        """ Reverse the direction of play """
        self.reversed = not self.reversed

    def turn(self):
        """ Mark the turn as over and change the current player """
        self.logger.debug("Next Player")
        self.current_player = self.current_player.next
        self.current_player.drew = False
        self.current_player.turn_started = datetime.now()

    def play_card(self, card):
        """ Play a card and trigger its effects """
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
        """ Carries out the color choosing and turns the game """
        self.last_card.color = color
        self.turn()
        self.choosing_color = False
