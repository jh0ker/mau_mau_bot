#!/usr/bin/env python3
#
# Telegram bot to play UNO in group chats
# Copyright (c) 2016 Jannes Höke <uno@jhoeke.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


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
from results import (add_call_bluff, add_choose_color, add_draw, add_gameinfo,
                     add_no_game, add_not_started, add_other_cards, add_pass,
                     add_card)
from utils import display_name
import card as c
from errors import (NoGameInChatError, LobbyClosedError, AlreadyJoinedError,
                    NotEnoughPlayersError, DeckEmptyError)
from database import db_session

TIMEOUT = 2.5

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)
logger = logging.getLogger(__name__)

gm = GameManager()
u = Updater(token=TOKEN, workers=32)
dp = u.dispatcher

botan = False
if BOTAN_TOKEN:
    botan = Botan(BOTAN_TOKEN)

help_text = ("Follow these steps:\n\n"
             "1. Add this bot to a group\n"
             "2. In the group, start a new game with /new or join an already"
             " running game with /join\n"
             "3. After at least two players have joined, start the game with"
             " /start\n"
             "4. Type <code>@mau_mau_bot</code> into your chat box and hit "
             "<b>space</b>, or click the <code>via @mau_mau_bot</code> text "
             "next to messages. You will see your cards (some greyed out), "
             "any extra options like drawing, and a <b>?</b> to see the "
             "current game state. The <b>greyed out cards</b> are those you "
             "<b>can not play</b> at the moment. Tap an option to execute "
             "the selected action.\n"
             "Players can join the game at any time. To leave a game, "
             "use /leave. If a player takes more than 90 seconds to play, "
             "you can use /skip to skip that player.\n\n"
             "Other commands (only game creator):\n"
             "/close - Close lobby\n"
             "/open - Open lobby\n\n"
             "<b>Experimental:</b> Play in multiple groups at the same time. "
             "Press the <code>Current game: ...</code> button and select the "
             "group you want to play a card in.\n"
             "If you enjoy this bot, "
             "<a href=\"https://telegram.me/storebot?start=mau_mau_bot\">"
             "rate me</a>, join the "
             "<a href=\"https://telegram.me/unobotupdates\">update channel</a>"
             " and buy an UNO card game.\n")

source_text = ("This bot is Free Software and licensed under the AGPL. "
               "The code is available here: \n"
               "https://github.com/jh0ker/mau_mau_bot")


@run_async
def send_async(bot, *args, **kwargs):
    """Send a message asynchronously"""
    if 'timeout' not in kwargs:
        kwargs['timeout'] = TIMEOUT

    try:
        bot.sendMessage(*args, **kwargs)
    except Exception as e:
        error(None, None, e)


@run_async
def answer_async(bot, *args, **kwargs):
    """Answer an inline query asynchronously"""
    if 'timeout' not in kwargs:
        kwargs['timeout'] = TIMEOUT

    try:
        bot.answerInlineQuery(*args, **kwargs)
    except Exception as e:
        error(None, None, e)


def error(bot, update, error):
    """Simple error handler"""
    logger.exception(error)


def new_game(bot, update):
    """Handler for the /new command"""
    chat_id = update.message.chat_id

    if update.message.chat.type == 'private':
        help(bot, update)

    else:
        game = gm.new_game(update.message.chat)
        game.owner = update.message.from_user
        send_async(bot, chat_id,
                   text="Created a new game! Join the game with /join "
                        "and start the game with /start")

        if botan:
            botan.track(update.message, 'New games')


def join_game(bot, update):
    """Handler for the /join command"""
    chat = update.message.chat

    if update.message.chat.type == 'private':
        help(bot, update)
        return

    try:
        gm.join_game(update.message.from_user, chat)

    except LobbyClosedError:
            send_async(bot, chat.id, text="The lobby is closed")

    except NoGameInChatError:
        send_async(bot, chat.id,
                   text="No game is running at the moment. "
                        "Create a new game with /new",
                   reply_to_message_id=update.message.message_id)

    except AlreadyJoinedError:
        send_async(bot, chat.id,
                   text="You already joined the game. Start the game "
                        "with /start",
                   reply_to_message_id=update.message.message_id)
    else:
        send_async(bot, chat.id,
                   text="Joined the game",
                   reply_to_message_id=update.message.message_id)


def leave_game(bot, update):
    """Handler for the /leave command"""
    chat = update.message.chat
    user = update.message.from_user

    player = gm.player_for_user_in_chat(user, chat)

    if player is None:
        send_async(bot, chat.id, text="You are not playing in a game in "
                                      "this group.",
                   reply_to_message_id=update.message.message_id)
        return

    game = player.game
    user = update.message.from_user

    try:
        gm.leave_game(user, chat)

    except NoGameInChatError:
        send_async(bot, chat.id, text="You are not playing in a game in "
                                      "this group.",
                   reply_to_message_id=update.message.message_id)

    except NotEnoughPlayersError:
        gm.end_game(chat, user)
        send_async(bot, chat.id, text="Game ended!")

    else:
        send_async(bot, chat.id,
                   text="Okay. Next Player: " +
                        display_name(game.current_player.user),
                   reply_to_message_id=update.message.message_id)


@run_async
def select_game(bot, update):
    """Handler for callback queries to select the current game"""

    chat_id = int(update.callback_query.data)
    user_id = update.callback_query.from_user.id
    players = gm.userid_players[user_id]
    for player in players:
        if player.game.chat.id == chat_id:
            gm.userid_current[user_id] = player
            break
    else:
        bot.sendMessage(update.callback_query.message.chat_id,
                        text="Game not found.",
                        timeout=TIMEOUT)
        return

    back = [[InlineKeyboardButton(text='Back to last group',
                                  switch_inline_query='')]]

    bot.answerCallbackQuery(update.callback_query.id,
                            text="Please switch to the group you selected!",
                            show_alert=False,
                            timeout=TIMEOUT)

    bot.editMessageText(chat_id=update.callback_query.message.chat_id,
                        message_id=update.callback_query.message.message_id,
                        text="Selected group: %s\n"
                             "<b>Make sure that you switch to the correct "
                             "group!</b>"
                             % gm.userid_current[user_id].game.chat.title,
                        reply_markup=InlineKeyboardMarkup(back),
                        parse_mode=ParseMode.HTML,
                        timeout=TIMEOUT)


def status_update(bot, update):
    """Remove player from game if user leaves the group"""
    chat = update.message.chat

    if update.message.left_chat_member:
        try:
            user = update.message.left_chat_member
        except KeyError:
            return

        try:
            gm.leave_game(user, chat)
        except NoGameInChatError:
            pass
        except NotEnoughPlayersError:
            gm.end_game(chat, user)
            send_async(bot, chat.id, text="Game ended!")
        else:
            send_async(bot, chat.id, text="Removing %s from the game"
                                          % display_name(user))


def start_game(bot, update, args):
    """Handler for the /start command"""

    if update.message.chat.type != 'private':
        chat = update.message.chat

        try:
            game = gm.chatid_games[chat.id][-1]
        except (KeyError, IndexError):
            send_async(bot, chat.id, text="There is no game running in this "
                                          "chat. Create a new one with /new")
            return

        if game.started:
            send_async(bot, chat.id, text="The game has already started")

        elif len(game.players) < 2:
            send_async(bot, chat.id, text="At least two players must /join "
                                          "the game before you can start it")

        else:
            game.play_card(game.last_card)
            game.started = True

            @run_async
            def send_first():
                """Send the first card and player"""

                bot.sendSticker(chat.id,
                                sticker=c.STICKERS[str(game.last_card)],
                                timeout=TIMEOUT)

                bot.sendMessage(chat.id,
                                text="First player: %s\n"
                                     "Use /close to stop people from joining "
                                     "the game."
                                     % display_name(game.current_player.user),
                                timeout=TIMEOUT)

            send_first()

    elif len(args) and args[0] == 'select':
        players = gm.userid_players[update.message.from_user.id]

        groups = list()
        for player in players:
            title = player.game.chat.title

            if player is gm.userid_current[update.message.from_user.id]:
                title = '- %s -' % player.game.chat.title

            groups.append(
                [InlineKeyboardButton(text=title,
                                      callback_data=str(player.game.chat.id))]
            )

        send_async(bot, update.message.chat_id,
                   text='Please select the group you want to play in.',
                   reply_markup=InlineKeyboardMarkup(groups))

    else:
        help(bot, update)


def close_game(bot, update):
    """Handler for the /close command"""
    chat = update.message.chat
    user = update.message.from_user
    games = gm.chatid_games.get(chat.id)

    if not games:
        send_async(bot, chat.id, text="There is no running game in this chat.")
        return

    game = games[-1]

    if game.owner.id == user.id:
        game.open = False
        send_async(bot, chat.id, text="Closed the lobby. "
                                      "No more players can join this game.")
        return

    else:
        send_async(bot, chat.id,
                   text="Only the game creator (%s) can do that"
                        % game.owner.first_name,
                   reply_to_message_id=update.message.message_id)
        return


def open_game(bot, update):
    """Handler for the /open command"""
    chat = update.message.chat
    user = update.message.from_user
    games = gm.chatid_games.get(chat.id)

    if not games:
        send_async(bot, chat.id, text="There is no running game in this chat.")
        return

    game = games[-1]

    if game.owner.id == user.id:
        game.open = True
        send_async(bot, chat.id, text="Opened the lobby. "
                                      "New players may /join the game.")
        return
    else:
        send_async(bot, chat.id,
                   text="Only the game creator (%s) can do that."
                        % game.owner.first_name,
                   reply_to_message_id=update.message.message_id)
        return


def skip_player(bot, update):
    """Handler for the /skip command"""
    chat = update.message.chat
    user = update.message.from_user

    player = gm.player_for_user_in_chat(user, chat)
    if not player:
        send_async(bot, chat.id, text="You are not playing in a game in this "
                                      "chat.")
        return

    game = player.game
    skipped_player = game.current_player
    next_player = game.current_player.next

    started = skipped_player.turn_started
    now = datetime.now()
    delta = (now - started).seconds

    if delta < skipped_player.waiting_time:
        send_async(bot, chat.id,
                   text="Please wait %d seconds"
                        % (skipped_player.waiting_time - delta),
                   reply_to_message_id=update.message.message_id)

    elif skipped_player.waiting_time > 0:
        skipped_player.anti_cheat += 1
        skipped_player.waiting_time -= 30
        try:
            skipped_player.draw()
        except DeckEmptyError:
            pass

        send_async(bot, chat.id,
                   text="Waiting time to skip this player has "
                        "been reduced to %d seconds.\n"
                        "Next player: %s"
                        % (skipped_player.waiting_time,
                           display_name(next_player.user)))
        game.turn()

    else:
        try:
            gm.leave_game(skipped_player.user, chat)
            send_async(bot, chat.id,
                       text="%s was skipped four times in a row "
                            "and has been removed from the game.\n"
                            "Next player: %s"
                            % (display_name(skipped_player.user),
                               display_name(next_player.user)))

        except NotEnoughPlayersError:
            send_async(bot, chat.id,
                       text="%s was skipped four times in a row "
                            "and has been removed from the game.\n"
                            "The game ended."
                            % display_name(skipped_player.user))

            gm.end_game(chat.id, skipped_player.user)


def help(bot, update):
    """Handler for the /help command"""
    send_async(bot, update.message.chat_id, text=help_text, 
               parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def source(bot, update):
    """Handler for the /help command"""
    send_async(bot, update.message.chat_id, text=source_text,
               parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def news(bot, update):
    """Handler for the /news command"""
    send_async(bot, update.message.chat_id, 
               text="All news here: https://telegram.me/unobotupdates",
               disable_web_page_preview=True)


def reply_to_query(bot, update):
    """
    Handler for inline queries.
    Builds the result list for inline queries and answers to the client.
    """
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
                add_other_cards(playable, player, results, game)
            else:
                if not player.drew:
                    add_draw(player, results)

                else:
                    add_pass(results)

                if game.last_card.special == c.DRAW_FOUR and game.draw_counter:
                    add_call_bluff(results)

                playable = player.playable_cards()
                added_ids = list()  # Duplicates are not allowed

                for card in sorted(player.cards):
                    add_card(game, card, results,
                             can_play=(card in playable and
                                            str(card) not in added_ids))
                    added_ids.append(str(card))

        elif user_id != game.current_player.user.id or not game.started:
            for card in sorted(player.cards):
                add_card(game, card, results, can_play=False)

        else:
            add_gameinfo(game, results)

        for result in results:
            result.id += ':%d' % player.anti_cheat

        if players and game and len(players) > 1:
            switch = 'Current game: %s' % game.chat.title

    answer_async(bot, update.inline_query.id, results, cache_time=0,
                 switch_pm_text=switch, switch_pm_parameter='select')


def process_result(bot, update):
    """
    Handler for chosen inline results.
    Checks the players actions and acts accordingly.
    """
    try:
        user = update.chosen_inline_result.from_user
        player = gm.userid_current[user.id]
        game = player.game
        result_id = update.chosen_inline_result.result_id
        chat = game.chat
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
        send_async(bot, chat.id,
                   text="Cheat attempt by %s" % display_name(player.user))
        return
    elif result_id == 'call_bluff':
        reset_waiting_time(bot, player)
        do_call_bluff(bot, player)
    elif result_id == 'draw':
        reset_waiting_time(bot, player)
        do_draw(player)
    elif result_id == 'pass':
        game.turn()
    elif result_id in c.COLORS:
        game.choose_color(result_id)
    else:
        reset_waiting_time(bot, player)
        do_play_card(bot, player, result_id)

    if game in gm.chatid_games.get(chat.id, list()):
        send_async(bot, chat.id, text="Next player: " +
                                      display_name(game.current_player.user))


def reset_waiting_time(bot, player):
    """Resets waiting time for a player and sends a notice to the group"""
    chat = player.game.chat

    if player.waiting_time < 90:
        player.waiting_time = 90
        send_async(bot, chat.id, text="Waiting time for %s has been reset to "
                                      "90 seconds" % display_name(player.user))


def do_play_card(bot, player, result_id):
    """Plays the selected card and sends an update to the group if needed"""
    card = c.from_str(result_id)
    player.play(card)
    game = player.game
    chat = game.chat
    user = player.user

    if game.choosing_color:
        send_async(bot, chat.id, text="Please choose a color")

    if len(player.cards) == 1:
        send_async(bot, chat.id, text="UNO!")

    if len(player.cards) == 0:
        send_async(bot, chat.id, text="%s won!" % user.first_name)
        try:
            gm.leave_game(user, chat)
        except NotEnoughPlayersError:
            send_async(bot, chat.id, text="Game ended!")
            gm.end_game(chat, user)

    if botan:
        botan.track(Message(randint(1, 1000000000), user, datetime.now(),
                            Chat(chat.id, 'group')),
                    'Played cards')


def do_draw(bot, player):
    """Does the drawing"""
    game = player.game
    draw_counter_before = game.draw_counter

    try:
        player.draw()
    except DeckEmptyError:
        send_async(bot, player.game.chat.id,
                   text="There are no more cards in the deck.")

    if (game.last_card.value == c.DRAW_TWO or
        game.last_card.special == c.DRAW_FOUR) and \
            draw_counter_before > 0:
        game.turn()


def do_call_bluff(bot, player):
    """Handles the bluff calling"""
    game = player.game
    chat = game.chat

    if player.prev.bluffing:
        send_async(bot, chat.id, text="Bluff called! Giving %d cards to %s"
                                      % (game.draw_counter,
                                         player.prev.user.first_name))

        try:
            player.prev.draw()
        except DeckEmptyError:
            send_async(bot, player.game.chat.id,
                       text="There are no more cards in the deck.")

    else:
        game.draw_counter += 2
        send_async(bot, chat.id, text="%s didn't bluff! Giving %d cards to %s"
                                      % (player.prev.user.first_name,
                                         game.draw_counter,
                                         player.user.first_name))
        try:
            player.draw()
        except DeckEmptyError:
            send_async(bot, player.game.chat.id,
                       text="There are no more cards in the deck.")

    game.turn()


# Add all handlers to the dispatcher and run the bot
dp.add_handler(InlineQueryHandler(reply_to_query))
dp.add_handler(ChosenInlineResultHandler(process_result))
dp.add_handler(CallbackQueryHandler(select_game))
dp.add_handler(CommandHandler('start', start_game, pass_args=True))
dp.add_handler(CommandHandler('new', new_game))
dp.add_handler(CommandHandler('join', join_game))
dp.add_handler(CommandHandler('leave', leave_game))
dp.add_handler(CommandHandler('open', open_game))
dp.add_handler(CommandHandler('close', close_game))
dp.add_handler(CommandHandler('skip', skip_player))
dp.add_handler(CommandHandler('help', help))
dp.add_handler(CommandHandler('source', source))
dp.add_handler(CommandHandler('news', news))
dp.add_handler(MessageHandler([Filters.status_update], status_update))
dp.add_error_handler(error)

start_bot(u)
u.idle()
