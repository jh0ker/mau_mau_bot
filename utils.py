from telegram import Emoji


def list_subtract(list1, list2):
    """ Helper function to subtract two lists and return the sorted result """
    list1 = list1.copy()

    for x in list2:
        list1.remove(x)

    return list(sorted(list1))


def display_name(user):
    """ Get the current players name including their username, if possible """
    user_name = user.first_name
    if user.username:
        user_name += ' (@' + user.username + ')'
    return user_name


def display_color(color):
    """ Convert a color code to actual color name """
    if color == "r":
        return Emoji.HEAVY_BLACK_HEART + " Red"
    if color == "b":
        return Emoji.BLUE_HEART + " Blue"
    if color == "g":
        return Emoji.GREEN_HEART + " Green"
    if color == "y":
        return Emoji.YELLOW_HEART + " Yellow"
