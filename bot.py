import logging

from telegram import Updater, InlineQueryResultPhoto, InlineQueryResultArticle

from game_manager import GameManager
import card as c
from credentials import TOKEN

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)
logger = logging.getLogger(__name__)

gm = GameManager()
u = Updater(TOKEN)
dp = u.dispatcher


def list_subtract(list1, list2):
    list1 = list1.copy()

    for x in list2:
        list1.remove(x)

    return list1


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
                             "issue the /new command there.")


def inline(bot, update):
    if update.inline_query:
        user_id = update.inline_query.from_user.id
        player = gm.userid_player[user_id]

        results = list()
        playable = player.playable_cards()

        if playable:
            for card in playable:
                results.append(
                    InlineQueryResultPhoto(str(card),
                                           card.get_image_link(),
                                           card.get_thumb_link(),
                                           title="Play card",
                                           description="<Card type goes here>")
                )

            results.append(
                InlineQueryResultPhoto(
                    "hand",
                    c.IMAGE_PATTERN % 'thinking',
                    c.THUMB_PATTERN % 'thinking',
                    title="Other cards:",
                    description=', '.join([repr(card) for card in
                                           list_subtract(player.cards, playable)]),
                )
            )
        else:
            results.append(
                InlineQueryResultArticle(
                    "draw",
                    title="No suitable cards...",
                    description="Draw!",
                    message_text='Drawing %d card(s)' % player.game.draw_counter
                )
            )

            results.append(
                InlineQueryResultArticle(
                    "hand",
                    title="Other cards:",
                    description=', '.join([repr(card) for card in
                                           list_subtract(player.cards, playable)]),
                    message_text='Just checking cards'
                )
            )

        [logger.info(str(result)) for result in results]

        bot.answerInlineQuery(update.inline_query.id, results, cache_time=0)

    else:
        user_id = update.chosen_inline_result.from_user.id
        game = gm.userid_game[user_id]
        player = gm.userid_player[user_id]
        result_id = update.chosen_inline_result.result_id
        logger.info("Selected result: " + result_id)

        if result_id is 'hand':
            pass
        elif result_id is 'draw':
            for n in range(game.draw_counter):
                player.cards.append(game.deck.draw())
        else:
            card = c.from_str(result_id)
            game.play_card(card)
            player.cards.remove(card)


def error(bot, update, error):
    logger.exception(error)


dp.addTelegramInlineHandler(inline)
dp.addTelegramCommandHandler('start', start)
dp.addTelegramCommandHandler('new', new_game)
dp.addErrorHandler(error)

u.start_polling()
u.idle()
