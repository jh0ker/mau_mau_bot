from random import shuffle
import card as c
from card import Card
import logging


class Deck(object):
    """ This class represents a deck of cards """

    def __init__(self):
        self.cards = list()
        self.graveyard = list()
        self.logger = logging.getLogger(__name__)

        # Fill deck
        for color in c.COLORS:
            for value in c.VALUES:
                self.cards.append(Card(color, value))
                if not value == c.ZERO:
                    self.cards.append(Card(color, value))

        for special in c.SPECIALS * 4:
            self.cards.append(Card(None, None, special=special))

        self.logger.debug(self.cards)
        self.shuffle()

    def shuffle(self):
        """ Shuffle the deck """
        self.logger.debug("Shuffling Deck")
        shuffle(self.cards)

    def draw(self):
        """ Draw a card from this deck """
        try:
            card = self.cards.pop()
            self.logger.debug("Drawing card " + str(card))
            return card
        except IndexError:
            while len(self.graveyard):
                self.cards.append(self.graveyard.pop())
            self.shuffle()
            return self.draw()

    def dismiss(self, card):
        """ All played cards should be returned into the deck """
        self.graveyard.append(card)
