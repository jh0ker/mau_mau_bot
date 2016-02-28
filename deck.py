from random import shuffle
import card
from card import Card
import logging


class Deck(object):

    def __init__(self):
        self.cards = list()
        self.graveyard = list()
        self.logger = logging.getLogger(__name__)

        for color in card.COLORS:
            for value in card.VALUES:
                self.cards.append(Card(color, value))
                if not value == card.ZERO:
                    self.cards.append(Card(color, value))

        for special in card.SPECIALS * 4:
            self.cards.append(Card(None, None, special=special))

        self.logger.debug(self.cards)
        self.shuffle()

    def shuffle(self):
        self.cards = shuffle(self.cards)

    def draw(self):
        try:
            return self.cards.pop()
        except IndexError:
            while len(self.graveyard):
                self.cards.append(self.graveyard.pop())
            self.shuffle()
            return self.draw()

    def dismiss(self, card):
        self.graveyard.append(card)
