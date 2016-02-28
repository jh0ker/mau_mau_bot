
from telegram import Updater, InlineQueryResultPhoto

from game_manager import GameManager
import card as c
from credentials import TOKEN

gm = GameManager()
u = Updater(TOKEN)
dp = u.dispatcher


def new_game(bot, update):
    chat_id = update.message.chat_id
    link = gm.generate_invite_link(u.bot.getMe().username, chat_id)
    bot.sendMessage(chat_id,
                    text="Click this link to join the game: %s" % link)


def start(bot, update, args):
    if args:
        gm.join_game(args[0], update.message.from_user)
    else:
        bot.sendMessage(update.message.chat_id,
                        text="Please invite me to a group and "
                             "issue the /start command there.")


def inline(bot, update):
    if update.inline_query:
        user_id = update.inline_query.from_user.id
        player = gm.userid_player[user_id]

        playable = list()
        for card in player.playable_cards():
            playable.append(
                InlineQueryResultPhoto(str(card),
                                       card.get_image_link(),
                                       card.get_thumb_link())
            )

        bot.answerInlineQuery(update.inline_query.id, playable)

    else:
        user_id = update.chosen_inline_result.from_user.id
        game = gm.userid_game[user_id]
        game.play_card(c.from_str(update.chosen_inline_result.id))
