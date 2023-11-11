"""
Promote other UNO bots
"""
import random


# Promotion messages and their weights
PROMOTIONS = {
    """
For a more modern UNO experience, <a href="https://t.me/uno9bot/uno">try out</a> the new <a href="https://t.me/uno9bot?start=ref-unobot">@uno9bot</a>.
""": 2.0,
    """
Also check out @UnoDemoBot, a newer version of this bot with exclusive modes and features!
""": 1.0,
}

def get_promotion():
    """ Get a random promotion message """
    return random.choices(list(PROMOTIONS.keys()), weights=list(PROMOTIONS.values()))[0]

def send_promotion(chat, chance=1.0):
    """ (Maybe) send a promotion message """
    if random.random() <= chance:
        chat.send_message(get_promotion(), parse_mode='HTML')


def send_promotion_async(chat, chance=1.0):
    """ Send a promotion message asynchronously """

    from utils import dispatcher, error
    try:
        dispatcher.run_async(send_promotion, chat, chance=chance)
    except Exception as e:
        error(None, None, e)
