import logging

import card as c


class Player(object):

    def __init__(self, game, user):
        """

        :param game:
        :type game Game
        :return:
        """
        self.cards = list()
        self.game = game
        self.user = user
        self.logger = logging.getLogger(__name__)

        if game.current_player:
            self.next = game.current_player
            self.prev = game.current_player.prev
            game.current_player.prev.next = self
            game.current_player.prev = self
        else:
            self._next = self
            self._prev = self
            game.current_player = self

        for i in range(6):
            self.cards.append(self.game.deck.draw())

    def leave(self):
        self.next.prev = self.prev
        self.prev.next = self.next
        self.next = None
        self.prev = None

    def __repr__(self):
        return repr(self.user)

    def __str__(self):
        return str(self.user)

    @property
    def next(self):
        return self._next if not self.game.reversed else self._prev

    @next.setter
    def next(self, player):
        if not self.game.reversed:
            self._next = player
        else:
            self._prev = player

    @property
    def prev(self):
        return self._prev if not self.game.reversed else self._next

    @prev.setter
    def prev(self, player):
        if not self.game.reversed:
            self._prev = player
        else:
            self._next = player

    def playable_cards(self):

        if self.game.current_player.user.id is not self.user.id:
            self.logger.debug("Player is not current player")
            return False

        playable = list()
        last = self.game.last_card

        self.logger.debug("Last card was" + str(last))

        for card in self.cards:
            self.logger.debug("Checking card " + str(card))
            if (card.color != last.color and card.value != last.value and
                    not card.special):
                self.logger.debug("Card's color or value doesn't match")
                continue

            if last.value == c.DRAW_TWO and not \
                    (card.value == c.DRAW_TWO or
                     card.special == c.DRAW_FOUR or
                     not self.game.draw_counter):
                self.logger.debug("Player has to draw and can't counter")
                continue

            if last.special == c.DRAW_FOUR and self.game.draw_counter:
                self.logger.debug("Player has to draw and can't counter")
                continue

            if not last.color or card in playable:
                self.logger.debug("Last card has no color or the card was "
                                  "already added to the list")
                continue

            self.logger.debug("Matching!")
            playable.append(card)

        return playable
