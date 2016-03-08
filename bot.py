import logging

from telegram import Updater, InlineQueryResultArticle, ParseMode

from game_manager import GameManager
import card as c
from credentials import TOKEN
from start_bot import start_bot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

gm = GameManager()
u = Updater(TOKEN)
dp = u.dispatcher

help_text = "Follow these steps:\n\n" \
            "1. Add this bot to a group\n" \
            "2. In the group, start a new game with /new\n" \
            "3. The bot will send a link into the group. " \
            "Click the link and then on the <b>Start</b> " \
            "button to join the game.\n" \
            "4. Go back to the group chat and wait for at least one " \
            "other person to join the game (you can also play alone, " \
            "but it's no fun)\n" \
            "5. Type <code>@mau_mau_bot</code> into your chat box and hit " \
            "space. You will see the cards that you can play, any extra " \
            "options like drawing, your other cards (those you can not play " \
            "at the moment) and an option to see the current game state.\n\n" \
            "Players can join the game at any time, though you currently " \
            "can not play more than one game at a time. To leave a game, " \
            "send /leave into the group."


def list_subtract(list1, list2):
    """ Helper function to subtract two lists and return the sorted result """
    list1 = list1.copy()

    for x in list2:
        list1.remove(x)

    return list(sorted(list1))


def display_name(game):
    """ Get the current players name including their username, if possible """
    user = game.current_player.user
    user_name = user.first_name
    if user.username:
        user_name += ' (@' + user.username + ')'
    return user_name


def display_color(color):
    """ Convert a color code to actual color name """
    if color == "r":
        return "Red"
    if color == "b":
        return "Blue"
    if color == "g":
        return "Green"
    if color == "y":
        return "Yellow"


def error(bot, update, error):
    """ Simple error handler """
    logger.exception(error)


def new_game(bot, update):
    """ Handler for the /new command """
    chat_id = update.message.chat_id
    link = gm.generate_invite_link(u.bot.getMe().username, chat_id)
    bot.sendMessage(chat_id,
                    text="Click this link to join the game: %s" % link)


def leave_game(bot, update):
    """ Handler for the /leave command """
    chat_id = update.message.chat_id
    game_id = gm.chatid_gameid[chat_id]
    game = gm.gameid_game[game_id]
    user = update.message.from_user

    if game.current_player.user.id == user.id:
        bot.sendMessage(chat_id,
                        text="You can't leave the game if it's your turn")
    else:
        gm.leave_game(user)
        bot.sendMessage(chat_id, text="Okay")


def start(bot, update, args):
    """ Handler for the /start command """
    if args:
        game_id = args[0]  # Contains the game id
        gm.join_game(game_id, update.message.from_user)
        game = gm.gameid_game[game_id]
        groupchat = gm.chatid_gameid[game_id]
        bot.sendMessage(update.message.chat_id,
                        text="Joined game! Please go back to the group chat "
                             "and play there, via inline commands.")
        bot.sendMessage(groupchat,
                        text=update.message.from_user.first_name +
                             " joined the game!")

        # Check if user is the first player to join and if, show the first card
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
    """ Handler for all inline stuff """
    if update.inline_query:
        reply_to_query(bot, update)
    else:
        process_result(bot, update)


def help(bot, update):
    """ Handler for the /help command """
    bot.sendMessage(update.message.chat_id,
                    text=help_text,
                    parse_mode=ParseMode.HTML)


def reply_to_query(bot, update):
    """ Builds the result list for inline queries and answers to the client """
    user_id = update.inline_query.from_user.id
    player = gm.userid_player[user_id]
    game = gm.userid_game[user_id]
    results = list()
    playable = list()

    if user_id == game.current_player.user.id:
        if game.choosing_color:
            add_choose_color(results)
        else:
            playable = list(sorted(player.playable_cards()))

            for card in playable:
                add_play_card(card, results)

            if not player.drew:
                add_draw(player, results, could_play_card=bool(len(playable)))

            else:
                add_pass(results)

            if game.last_card.special == c.DRAW_FOUR and game.draw_counter:
                add_call_bluff(results)

    add_other_cards(playable, player, results)

    add_gameinfo(game, results)

    bot.answerInlineQuery(update.inline_query.id, results, cache_time=0)


def add_choose_color(results):
    for color in c.COLORS:
        results.append(
            InlineQueryResultArticle(
                id=color,
                title="Choose Color",
                message_text=display_color(color),
                description=display_color(color)
            )
        )


def add_other_cards(playable, player, results):
    if not playable:
        playable = list()

    results.append(
        InlineQueryResultArticle(
            "hand",
            title="Other cards:",
            description=', '.join([repr(card) for card in
                                   list_subtract(player.cards, playable)]),
            message_text='Just checking cards'
        )
    )


def add_draw(player, results, could_play_card):
    results.append(
        InlineQueryResultArticle(
            "draw",
            title=("No suitable cards..." if not could_play_card else
                   "I don't want to play a card..."),
            description="Draw!",
            message_text='Drawing %d card(s)'
                         % (player.game.draw_counter or 1)
        )
    )


def add_pass(results):
    results.append(
        InlineQueryResultArticle(
            "pass",
            title="Pass",
            description="Don't play a card",
            message_text='Pass'
        )
    )


def add_call_bluff(results):
    results.append(
        InlineQueryResultArticle(
            "call_bluff",
            title="Call their bluff!",
            description="Risk it!",
            message_text="I'm calling your bluff!"
        )
    )


def add_play_card(card, results):
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


def add_gameinfo(game, results):
    players = list()
    current_player = game.current_player
    itplayer = current_player.next
    add_player(current_player, players)

    while itplayer is not current_player:
        add_player(itplayer, players)
        itplayer = itplayer.next

    results.append(
        InlineQueryResultArticle(
            "gameinfo",
            title="Show game info",
            description="Tap to see the current player, player order, "
                        "card amounts and last played card",
            message_text="Current player: " + display_name(game) + "\n" +
                         "Last card: " + repr(game.last_card) + "\n" +
                         "Players: " + " -> ".join(players)
        )
    )


def add_player(itplayer, players):
    players.append(itplayer.user.first_name + " (%d cards)"
                   % len(itplayer.cards))


def process_result(bot, update):
    """ Check the players actions and act accordingly """
    user = update.chosen_inline_result.from_user
    game = gm.userid_game[user.id]
    player = gm.userid_player[user.id]
    result_id = update.chosen_inline_result.result_id
    chat_id = gm.chatid_gameid[game]
    logger.debug("Selected result: " + result_id)

    if result_id in ('hand', 'gameinfo'):
        return
    elif result_id == 'call_bluff':
        do_call_bluff(bot, chat_id, game, player)
    elif result_id == 'draw':
        do_draw(game, player)
    elif result_id == 'pass':
        game.turn()
    elif result_id in c.COLORS:
        game.choose_color(result_id)
    else:
        do_play_card(bot, chat_id, game, player, result_id, user)

    bot.sendMessage(chat_id, text="Next player: " + display_name(game))


def do_play_card(bot, chat_id, game, player, result_id, user):
    card = c.from_str(result_id)
    game.play_card(card)
    player.cards.remove(card)
    if game.choosing_color:
        bot.sendMessage(chat_id, text="Please choose a color")
    if len(player.cards) == 1:
        bot.sendMessage(chat_id, text="Last Card!")
    if len(player.cards) == 0:
        gm.leave_game(user)
        bot.sendMessage(chat_id, text="Player won!")


def do_draw(game, player):
    draw_counter_before = game.draw_counter
    for n in range(game.draw_counter or 1):
        player.cards.append(game.deck.draw())
    game.draw_counter = 0
    player.drew = True
    if game.last_card.value == c.DRAW_TWO and draw_counter_before > 0:
        game.turn()


def do_call_bluff(bot, chat_id, game, player):
    if player.prev.bluffing:
        bot.sendMessage(chat_id, text="Bluff called! Giving %d cards to %s"
                                      % (game.draw_counter,
                                         player.prev.user.first_name))
        for i in range(game.draw_counter):
            player.prev.cards.append(game.deck.draw())
    else:
        bot.sendMessage(chat_id, text="%s didn't bluff! Giving %d cards to"
                                      " %s"
                                      % (player.prev.user.first_name,
                                         game.draw_counter + 2,
                                         player.user.first_name))
        for i in range(game.draw_counter + 2):
            player.cards.append(game.deck.draw())
    game.draw_counter = 0
    game.turn()


# Add all handlers to the dispatcher and run the bot
dp.addTelegramInlineHandler(inline)
dp.addTelegramCommandHandler('start', start)
dp.addTelegramCommandHandler('new', new_game)
dp.addTelegramCommandHandler('leave', leave_game)
dp.addTelegramCommandHandler('help', help)
dp.addErrorHandler(error)

start_bot(u)
u.idle()
