import logging
from datetime import datetime
from random import randint

from telegram import ParseMode, Message, Chat, InlineKeyboardMarkup, \
    InlineKeyboardButton
from telegram.ext import Updater, InlineQueryHandler, \
    ChosenInlineResultHandler, CommandHandler, MessageHandler, Filters, \
    CallbackQueryHandler
from telegram.ext.dispatcher import run_async
from telegram.utils.botan import Botan

from game_manager import GameManager
from credentials import TOKEN, BOTAN_TOKEN
from start_bot import start_bot
from results import *
from utils import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

gm = GameManager()
u = Updater(TOKEN)
dp = u.dispatcher

botan = False
if BOTAN_TOKEN:
    botan = Botan(BOTAN_TOKEN)

help_text = "Follow these steps:\n\n" \
            "1. Add this bot to a group\n" \
            "2. In the group, start a new game with /new or join an already" \
            " running game with /join\n" \
            "3. After at least two players have joined, start the game with" \
            " /start\n" \
            "4. Type <code>@mau_mau_bot</code> into your chat box and hit " \
            "space, or click the <code>via @mau_mau_bot</code> text next to " \
            "messages. You will see your cards (some greyed out), any extra " \
            "options like drawing, and a <b>?</b> to see the current game " \
            "state. The greyed out cards are those you can not play at the " \
            "moment. Tap an option to execute the selected action. \n" \
            "Players can join the game at any time. To leave a game, " \
            "use /leave.\n\n" \
            "Other commands (only game creator):\n" \
            "/close - Close lobby\n" \
            "/open - Open lobby\n" \
            "/skip - Skip current player\n\n" \
            "<b>Experimental:</b> Play in multiple groups at the same time. " \
            "Press the <code>Current game: </code> button and select the " \
            "group you want to play a card in.\n" \
            "If you enjoy this bot, " \
            "<a href=\"https://telegram.me/storebot?start=mau_mau_bot\">" \
            "rate me</a>, join the " \
            "<a href=\"https://telegram.me/unobotupdates\">update channel</a>"\
            " and buy an UNO card game.\n"


@run_async
def send_async(bot, *args, **kwargs):
    if 'timeout' not in kwargs:
        kwargs['timeout'] = 2.5
    bot.sendMessage(*args, **kwargs)


@run_async
def answer_async(bot, *args, **kwargs):
    if 'timeout' not in kwargs:
        kwargs['timeout'] = 2.5
    bot.answerInlineQuery(*args, **kwargs)


def error(bot, update, error):
    """ Simple error handler """
    logger.exception(error)


def new_game(bot, update):
    """ Handler for the /new command """
    chat_id = update.message.chat_id
    if update.message.chat.type == 'private':
        help(bot, update)
    else:
        gm.new_game(update.message.chat)
        send_async(bot, chat_id,
                   text="Created a new game! Join the game with /join "
                        "and start the game with /start")
        if botan:
            botan.track(update.message, 'New games')


def join_game(bot, update):
    """ Handler for the /join command """
    chat_id = update.message.chat_id
    if update.message.chat.type == 'private':
        help(bot, update)
    else:
        try:
            game = gm.chatid_games[chat_id][-1]
            if not game.open:
                send_async(bot, chat_id, text="The lobby is closed")
                return
        except (KeyError, IndexError):
            pass

        joined = gm.join_game(chat_id, update.message.from_user)
        if joined:
            send_async(bot, chat_id,
                       text="Joined the game",
                       reply_to_message_id=update.message.message_id)
        elif joined is None:
            send_async(bot, chat_id,
                       text="No game is running at the moment. "
                            "Create a new game with /new",
                       reply_to_message_id=update.message.message_id)
        else:
            send_async(bot, chat_id,
                       text="You already joined the game. Start the game "
                            "with /start",
                       reply_to_message_id=update.message.message_id)


def leave_game(bot, update):
    """ Handler for the /leave command """
    chat_id = update.message.chat_id
    user = update.message.from_user
    players = gm.userid_players.get(user.id, list())
    for player in players:
        if player.game.chat.id == chat_id:
            game = player.game
            break
    else:
        send_async(bot, chat_id, text="You are not playing in a game in "
                                      "this group.",
                   reply_to_message_id=update.message.message_id)
        return

    user = update.message.from_user

    if len(game.players) < 3:
        gm.end_game(chat_id, user)
        send_async(bot, chat_id, text="Game ended!")
    else:
        if gm.leave_game(user, chat_id):
            send_async(bot, chat_id,
                       text="Okay. Next Player: " +
                            display_name(game.current_player.user),
                       reply_to_message_id=update.message.message_id)
        else:
            send_async(bot, chat_id, text="You are not playing in a game in "
                                          "this group.",
                       reply_to_message_id=update.message.message_id)


def select_game(bot, update):

    chat_id = int(update.callback_query.data)
    user_id = update.callback_query.from_user.id
    players = gm.userid_players[user_id]
    for player in players:
        if player.game.chat.id == chat_id:
            gm.userid_current[user_id] = player
            break
    else:
        send_async(bot, update.callback_query.message.chat_id,
                   text="Game not found :(")
        return

    back = [[InlineKeyboardButton(text='Back to last group',
                                  switch_inline_query='')]]

    bot.answerCallbackQuery(update.callback_query.id,
                            text="Please switch to the group you selected!",
                            show_alert=False)
    bot.editMessageText(chat_id=update.callback_query.message.chat_id,
                        message_id=update.callback_query.message.message_id,
                        text="Selected game: %s\n"
                             "<b>Make sure that you switch to the correct "
                             "group!</b>"
                             % gm.userid_current[user_id].game.chat.title,
                        reply_markup=InlineKeyboardMarkup(back),
                        parse_mode=ParseMode.HTML)


def status_update(bot, update):
    """ Remove player from game if user leaves the group """

    if update.message.left_chat_member:
        try:
            chat_id = update.message.chat_id
            user = update.message.left_chat_member
        except KeyError:
            return

        if gm.leave_game(user, chat_id):
            send_async(bot, chat_id, text="Removing %s from the game" 
                                          % display_name(user))


def start_game(bot, update, args):
    """ Handler for the /start command """

    if update.message.chat.type != 'private':
        # Show the first card
        chat_id = update.message.chat_id
        try:
            game = gm.chatid_games[chat_id][-1]
        except (KeyError, IndexError):
            send_async(bot, chat_id, text="There is no game running in this "
                                          "chat. Create a new one with /new")
            return

        if game.current_player is None or \
                game.current_player is game.current_player.next:
            send_async(bot, chat_id, text="At least two players must /join "
                                          "the game before you can start it")
        elif game.started:
            send_async(bot, chat_id, text="The game has already started")
        else:
            game.play_card(game.last_card)
            game.started = True
            bot.sendSticker(chat_id,
                            sticker=c.STICKERS[str(game.last_card)])
            send_async(bot, chat_id, 
                       text="First player: " + 
                            display_name(game.current_player.user))
    elif len(args) and args[0] == 'select':
        players = gm.userid_players[update.message.from_user.id]

        groups = list()
        for player in players:
            groups.append([InlineKeyboardButton(text=player.game.chat.title,
                                                callback_data=
                                                str(player.game.chat.id))])
        send_async(bot, update.message.chat_id,
                   text='Please select the group you want to play in. ',
                   reply_markup=InlineKeyboardMarkup(groups))
    else:
        help(bot, update)


def close_game(bot, update):
    """ Handler for the /close command """
    chat_id = update.message.chat_id
    user = update.message.from_user
    games = gm.chatid_games[chat_id]
    players = gm.userid_players[user.id]

    for game in games:
        for player in players:
            if player in game.players:
                if player is game.owner:
                    game.open = False
                    send_async(bot, chat_id, text="Closed the lobby")
                    return
                else:
                    send_async(bot, chat_id,
                               text="Only the game creator can do that",
                               reply_to_message_id=update.message.message_id)
                    return


def open_game(bot, update):
    """ Handler for the /open command """
    chat_id = update.message.chat_id
    user = update.message.from_user
    games = gm.chatid_games[chat_id]
    players = gm.userid_players[user.id]

    for game in games:
        for player in players:
            if player in game.players:
                if player is game.owner:
                    game.open = True
                    send_async(bot, chat_id, text="Opened the lobby")
                    return
                else:
                    send_async(bot, chat_id,
                               text="Only the game creator can do that",
                               reply_to_message_id=update.message.message_id)
                    return


def skip_player(bot, update):
    """ Handler for the /skip command """
    chat_id = update.message.chat_id
    user = update.message.from_user
    games = gm.chatid_games[chat_id]
    players = gm.userid_players[user.id]

    for game in games:
        for player in players:
            if player in game.players:
                if player is game.owner:
                    started = game.current_player.turn_started
                    now = datetime.now()
                    delta = (now - started).seconds

                    if delta < 120:
                        send_async(bot, chat_id,
                                   text="Please wait %d seconds"
                                        % (120 - delta),
                                   reply_to_message_id=
                                   update.message.message_id)
                        return

                    game.current_player.anti_cheat += 1
                    game.turn()
                    send_async(bot, chat_id,
                               text="Next player: %s"
                                    % display_name(game.current_player.user))
                    return
                else:
                    send_async(bot, chat_id,
                               text="Only the game creator can do that",
                               reply_to_message_id=update.message.message_id)
                    return


def help(bot, update):
    """ Handler for the /help command """
    send_async(bot, update.message.chat_id, text=help_text, 
               parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def news(bot, update):
    """ Handler for the /news command """
    send_async(bot, update.message.chat_id, 
               text="All news here: https://telegram.me/unobotupdates",
               disable_web_page_preview=True)


def reply_to_query(bot, update):
    """ Builds the result list for inline queries and answers to the client """
    results = list()
    playable = list()
    switch = None

    try:
        user_id = update.inline_query.from_user.id
        players = gm.userid_players[user_id]
        player = gm.userid_current[user_id]
        game = player.game
    except KeyError:
        add_no_game(results)
    else:
        if not game.started:
            add_not_started(results)
        elif user_id == game.current_player.user.id:
            if game.choosing_color:
                add_choose_color(results)
            else:
                if not player.drew:
                    add_draw(player, results)

                else:
                    add_pass(results)

                if game.last_card.special == c.DRAW_FOUR and game.draw_counter:
                    add_call_bluff(results)

                playable = player.playable_cards()
                added_ids = list()

                for card in sorted(player.cards):
                    add_play_card(game, card, results,
                                  can_play=(card in playable and
                                            str(card) not in added_ids))
                    added_ids.append(str(card))

        if False or game.choosing_color:
            add_other_cards(playable, player, results, game)
        elif user_id != game.current_player.user.id or not game.started:
            for card in sorted(player.cards):
                add_play_card(game, card, results, can_play=False)
        else:
            add_gameinfo(game, results)

        for result in results:
            result.id += ':%d' % player.anti_cheat

        if players and game and len(players) > 1:
            switch = 'Current game: %s' % game.chat.title

    answer_async(bot, update.inline_query.id, results, cache_time=0,
                 switch_pm_text=switch, switch_pm_parameter='select')


def process_result(bot, update):
    """ Check the players actions and act accordingly """
    try:
        user = update.chosen_inline_result.from_user
        player = gm.userid_current[user.id]
        game = player.game
        result_id = update.chosen_inline_result.result_id
        chat_id = game.chat.id
    except KeyError:
        return

    logger.debug("Selected result: " + result_id)

    result_id, anti_cheat = result_id.split(':')
    last_anti_cheat = player.anti_cheat
    player.anti_cheat += 1

    if result_id in ('hand', 'gameinfo', 'nogame'):
        return
    elif len(result_id) == 36:  # UUID result
        return
    elif int(anti_cheat) != last_anti_cheat:
        send_async(bot, chat_id, 
                   text="Cheat attempt by %s" % display_name(player.user))
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

    if game in gm.chatid_games.get(chat_id, list()):
        send_async(bot, chat_id, text="Next player: " +
                                      display_name(game.current_player.user))


def do_play_card(bot, chat_id, game, player, result_id, user):
    card = c.from_str(result_id)
    game.play_card(card)
    player.cards.remove(card)
    if game.choosing_color:
        send_async(bot, chat_id, text="Please choose a color")
    if len(player.cards) == 1:
        send_async(bot, chat_id, text="UNO!")
    if len(player.cards) == 0:
        send_async(bot, chat_id, text="%s won!" % user.first_name)
        if len(game.players) < 3:
            send_async(bot, chat_id, text="Game ended!")
            gm.end_game(chat_id, user)
        else:
            gm.leave_game(user, chat_id)

    if botan:
        botan.track(Message(randint(1, 1000000000), user, datetime.now(),
                            Chat(chat_id, 'group')),
                    'Played cards')


def do_draw(game, player):
    draw_counter_before = game.draw_counter
    for n in range(game.draw_counter or 1):
        player.cards.append(game.deck.draw())
    game.draw_counter = 0
    player.drew = True
    if (game.last_card.value == c.DRAW_TWO or
        game.last_card.special == c.DRAW_FOUR) and \
            draw_counter_before > 0:
        game.turn()


def do_call_bluff(bot, chat_id, game, player):
    if player.prev.bluffing:
        send_async(bot, chat_id, text="Bluff called! Giving %d cards to %s"
                                      % (game.draw_counter,
                                         player.prev.user.first_name))
        for i in range(game.draw_counter):
            player.prev.cards.append(game.deck.draw())
    else:
        send_async(bot, chat_id, text="%s didn't bluff! Giving %d cards to %s"
                                      % (player.prev.user.first_name,
                                         game.draw_counter + 2,
                                         player.user.first_name))
        for i in range(game.draw_counter + 2):
            player.cards.append(game.deck.draw())
    game.draw_counter = 0
    game.turn()


# Add all handlers to the dispatcher and run the bot
dp.addHandler(InlineQueryHandler(reply_to_query))
dp.addHandler(ChosenInlineResultHandler(process_result))
dp.addHandler(CallbackQueryHandler(select_game))
dp.addHandler(CommandHandler('start', start_game, pass_args=True))
dp.addHandler(CommandHandler('new', new_game))
dp.addHandler(CommandHandler('join', join_game))
dp.addHandler(CommandHandler('leave', leave_game))
dp.addHandler(CommandHandler('open', open_game))
dp.addHandler(CommandHandler('close', close_game))
dp.addHandler(CommandHandler('skip', skip_player))
dp.addHandler(CommandHandler('help', help))
dp.addHandler(CommandHandler('news', news))
dp.addHandler(MessageHandler([Filters.status_update], status_update))
dp.addErrorHandler(error)

start_bot(u)
u.idle()
