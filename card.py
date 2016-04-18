from telegram.emoji import Emoji

# Colors
RED = 'r'
BLUE = 'b'
GREEN = 'g'
YELLOW = 'y'

COLORS = (RED, BLUE, GREEN, YELLOW)

COLOR_ICONS = {
    RED: Emoji.HEAVY_BLACK_HEART,
    BLUE: Emoji.BLUE_HEART,
    GREEN: Emoji.GREEN_HEART,
    YELLOW: Emoji.YELLOW_HEART,
}

# Values
ZERO = '0'
ONE = '1'
TWO = '2'
THREE = '3'
FOUR = '4'
FIVE = '5'
SIX = '6'
SEVEN = '7'
EIGHT = '8'
NINE = '9'
DRAW_TWO = 'draw'
REVERSE = 'reverse'
SKIP = 'skip'

VALUES = (ZERO, ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, DRAW_TWO,
          REVERSE, SKIP)

# Special cards
CHOOSE = 'colorchooser'
DRAW_FOUR = 'draw_four'

SPECIALS = (CHOOSE, DRAW_FOUR)

IMAGE_PATTERN = 'https://raw.githubusercontent.com/jh0ker/mau_mau_bot/' \
                'master/images/jpg/%s.jpg'
THUMB_PATTERN = 'https://raw.githubusercontent.com/jh0ker/mau_mau_bot/' \
                'master/images/thumb/%s.jpg'


class Card(object):
    """
    This class represents a card.
    """

    def __init__(self, color, value, special=None):
        self.color = color
        self.value = value
        self.special = special

    def __str__(self):
        if self.special:
            return self.special
        else:
            return '%s_%s' % (self.color, self.value)

    def __repr__(self):
        if self.special:
            return '%s%s' % (Emoji.BROKEN_HEART,
                             ' '.join([s.capitalize()
                                       for s in self.special.split('_')]))
        else:
            return '%s%s' % (COLOR_ICONS[self.color], self.value.capitalize())

    def __eq__(self, other):
        """ Needed for sorting the cards """
        return str(self) == str(other)

    def __lt__(self, other):
        """ Needed for sorting the cards """
        return str(self) < str(other)

    def get_image_link(self):
        """ Returns a link to the image of this card """
        return IMAGE_PATTERN % str(self)

    def get_thumb_link(self):
        """ Returns a link to the thumbnail-image of this card """
        return THUMB_PATTERN % str(self)


def from_str(string):
    """ Decode a Card object from a string """
    if string not in SPECIALS:
        color, value = string.split('_')
        return Card(color, value)
    else:
        return Card(None, None, string)
