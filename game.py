from deck import Deck
from card import Card
import card as c
from player import Player


class Game(object):
    """ This class represents a game of mau mau

    :type current_player: Player
    """
    current_player = None
    reversed = False
    draw_counter = 1
    choosing_color = False

    def __init__(self):
        self.deck = Deck()
        self.last_card = self.deck.draw()

    def reverse(self):
        self.reversed = not self.reversed

    def turn(self):
        self.current_player = self.current_player.next

    def play_card(self, card):
        """

        :param card:
        :type card: Card
        :return:
        """
        self.deck.dismiss(self.last_card)
        self.last_card = card
        if card.value is c.SKIP:
            self.current_player = self.current_player.next.next
        elif card.special is c.DRAW_FOUR:
            self.draw_counter += 4
        elif card.value is c.DRAW_TWO:
            self.draw_counter += 2
        elif card.value is c.REVERSE:
            self.reverse()

        if card.special not in (c.CHOOSE, c.DRAW_FOUR):
            self.current_player = self.current_player.next
        else:
            self.choosing_color = True

    def choose_color(self, color):
        self.last_card.color = color
        self.current_player = self.current_player.next
        self.choosing_color = False
