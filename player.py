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

        if self.game.current_player is not self:
            return False

        playable = list()
        last = self.game.last_card

        for card in self.cards:
            if (card.color is last.color or card.value is last.value) and \
                    not last.special:
                playable.append(card)

        return playable
