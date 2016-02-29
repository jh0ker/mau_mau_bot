import logging


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
            if (card.color is last.color or card.value is last.value or
                    card.special) and \
                    not last.special and card not in playable:
                self.logger.debug("Matching!")
                playable.append(card)

        return playable
