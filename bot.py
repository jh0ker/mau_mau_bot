import logging

from telegram import Updater, InlineQueryResultPhoto, InlineQueryResultArticle, ParseMode

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
        game_id = args[0]
        gm.join_game(game_id, update.message.from_user)
        game = gm.gameid_game[game_id]
        groupchat = gm.chatid_gameid[game_id]
        bot.sendMessage(update.message.chat_id, text="Joined game!")
        bot.sendMessage(groupchat, text=update.message.from_user.first_name +
                                        " joined the game!")

        if game.current_player is game.current_player.next:
            game.play_card(game.last_card)
            bot.sendPhoto(groupchat,
                          photo=game.last_card.get_image_link(),
                          caption="First Card")
    else:
        bot.sendMessage(update.message.chat_id,
                        text="Please invite me to a group and "
                             "issue the /new command there.")


def inline(bot, update):
    if update.inline_query:
        user_id = update.inline_query.from_user.id
        player = gm.userid_player[user_id]
        game = gm.userid_game[user_id]
        results = list()
        playable = list()

        if game.choosing_color:
            for color in c.COLORS:
                results.append(
                    InlineQueryResultArticle(
                        id=color,
                        title="Choose Color",
                        message_text=color,
                        description=color.upper()
                    )
                )
        else:
            playable = player.playable_cards()

        if playable is False:
            results.append(
                InlineQueryResultArticle(
                    "not_your_turn",
                    title="Not your turn",
                    description="Tap to see the current player",
                    message_text="Current player: " +
                                 game.current_player.user.first_name
                )
            )
        elif playable:
            for card in playable:
                results.append(
                    InlineQueryResultArticle(str(card),
                                             title="Play card",
                                             message_text=
                                             ('<a href="%s">\xad</a>'
                                              'Played card ' + repr(card))
                                             % card.get_image_link(),
                                             thumb_url=card.get_thumb_link(),
                                             description=repr(card),
                                             parse_mode=ParseMode.HTML)
                )
        elif not game.choosing_color:
            results.append(
                InlineQueryResultArticle(
                    "draw",
                    title="No suitable cards...",
                    description="Draw!",
                    message_text='Drawing %d card(s)'
                                 % (player.game.draw_counter or 1)
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
        user = update.chosen_inline_result.from_user
        game = gm.userid_game[user.id]
        player = gm.userid_player[user.id]
        result_id = update.chosen_inline_result.result_id
        chat_id = gm.chatid_gameid[game]

        logger.info("Selected result: " + result_id)

        if result_id == 'hand':
            pass
        elif result_id == 'draw':
            for n in range(game.draw_counter or 1):
                player.cards.append(game.deck.draw())
            game.draw_counter = 0
        elif result_id in c.COLORS:
            game.choose_color(result_id)
        else:
            card = c.from_str(result_id)
            game.play_card(card)
            player.cards.remove(card)
            if game.choosing_color:
                bot.sendMessage(chat_id, text="Please choose a color")
            elif len(player.cards) == 1:
                bot.sendMessage(chat_id, text="Last Card!")
            elif len(player.cards) == 0:
                gm.leave_game(user)
                bot.sendMessage(chat_id, text="Player won!")

        bot.sendMessage(chat_id,
                        text="Next player: " +
                             game.current_player.user.first_name)


def error(bot, update, error):
    logger.exception(error)


dp.addTelegramInlineHandler(inline)
dp.addTelegramCommandHandler('start', start)
dp.addTelegramCommandHandler('new', new_game)
dp.addErrorHandler(error)

u.start_polling()
u.idle()
