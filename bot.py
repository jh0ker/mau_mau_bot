#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
from telegram.ext import InlineQueryHandler, ChosenInlineResultHandler, \
    CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram.ext.dispatcher import run_async

from start_bot import start_bot
from results import (add_call_bluff, add_choose_color, add_draw, add_gameinfo,
                     add_no_game, add_not_started, add_other_cards, add_pass,
                     add_card)
from user_setting import UserSetting
from utils import display_name
import card as c
from errors import (NoGameInChatError, LobbyClosedError, AlreadyJoinedError,
                    NotEnoughPlayersError, DeckEmptyError)
from utils import send_async, answer_async, error, TIMEOUT
from shared_vars import botan, gm, updater, dispatcher
from internationalization import _, __, user_locale, game_locales
import simple_commands
import settings

from simple_commands import help


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


@user_locale
def notify_me(bot, update):
    """Handler for /notify_me command, pm people for next game"""
    chat_id = update.message.chat_id
    if update.message.chat.type == 'private':
        send_async(bot,
                   chat_id,
                   text=_("Send this command in a group to be notified "
                          "when a new game is started there."))
    else:
        try:
            gm.remind_dict[chat_id].add(update.message.from_user.id)
        except KeyError:
            gm.remind_dict[chat_id] = {update.message.from_user.id}


@user_locale
def new_game(bot, update):
    """Handler for the /new command"""
    chat_id = update.message.chat_id

    if update.message.chat.type == 'private':
        help(bot, update)

    else:

        if update.message.chat_id in gm.remind_dict:
            for user in gm.remind_dict[update.message.chat_id]:
                send_async(bot,
                           user,
                           text=_("A new game has been started in {title}").format(
                                title=update.message.chat.title))

            del gm.remind_dict[update.message.chat_id]

        game = gm.new_game(update.message.chat)
        game.owner = update.message.from_user
        send_async(bot, chat_id,
                   text=_("Created a new game! Join the game with /join "
                          "and start the game with /start"))

        if botan:
            botan.track(update.message, 'New games')


@user_locale
def join_game(bot, update):
    """Handler for the /join command"""
    chat = update.message.chat

    if update.message.chat.type == 'private':
        help(bot, update)
        return

    try:
        gm.join_game(update.message.from_user, chat)

    except LobbyClosedError:
            send_async(bot, chat.id, text=_("The lobby is closed"))

    except NoGameInChatError:
        send_async(bot, chat.id,
                   text=_("No game is running at the moment. "
                          "Create a new game with /new"),
                   reply_to_message_id=update.message.message_id)

    except AlreadyJoinedError:
        send_async(bot, chat.id,
                   text=_("You already joined the game. Start the game "
                          "with /start"),
                   reply_to_message_id=update.message.message_id)

    except DeckEmptyError:
        send_async(bot, chat.id,
                   text=_("There are not enough cards left in the deck for "
                          "new players to join."),
                   reply_to_message_id=update.message.message_id)

    else:
        send_async(bot, chat.id,
                   text=_("Joined the game"),
                   reply_to_message_id=update.message.message_id)


@user_locale
def leave_game(bot, update):
    """Handler for the /leave command"""
    chat = update.message.chat
    user = update.message.from_user

    player = gm.player_for_user_in_chat(user, chat)

    if player is None:
        send_async(bot, chat.id, text=_("You are not playing in a game in "
                                        "this group."),
                   reply_to_message_id=update.message.message_id)
        return

    game = player.game
    user = update.message.from_user

    try:
        gm.leave_game(user, chat)

    except NoGameInChatError:
        send_async(bot, chat.id, text=_("You are not playing in a game in "
                                        "this group."),
                   reply_to_message_id=update.message.message_id)

    except NotEnoughPlayersError:
        gm.end_game(chat, user)
        send_async(bot, chat.id, text=__("Game ended!", multi=game.translate))

    else:
        send_async(bot, chat.id,
                   text=__("Okay. Next Player: {name}",
                           multi=game.translate).format(
                       name=display_name(game.current_player.user)),
                   reply_to_message_id=update.message.message_id)


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
        send_async(bot,
                   update.callback_query.message.chat_id,
                   text=_("Game not found."))
        return

    @run_async
    def selected(bot):
        back = [[InlineKeyboardButton(text=_("Back to last group"),
                                      switch_inline_query='')]]
        bot.answerCallbackQuery(update.callback_query.id,
                                text=_("Please switch to the group you selected!"),
                                show_alert=False,
                                timeout=TIMEOUT)

        bot.editMessageText(chat_id=update.callback_query.message.chat_id,
                            message_id=update.callback_query.message.message_id,
                            text=_("Selected group: {group}\n"
                                   "<b>Make sure that you switch to the correct "
                                   "group!</b>").format(
                                group=gm.userid_current[user_id].game.chat.title),
                            reply_markup=InlineKeyboardMarkup(back),
                            parse_mode=ParseMode.HTML,
                            timeout=TIMEOUT)

    selected(bot)


@game_locales
def status_update(bot, update):
    """Remove player from game if user leaves the group"""
    chat = update.message.chat

    if update.message.left_chat_member:
        user = update.message.left_chat_member

        try:
            gm.leave_game(user, chat)
            game = gm.player_for_user_in_chat(user, chat).game

        except NoGameInChatError:
            pass
        except NotEnoughPlayersError:
            gm.end_game(chat, user)
            send_async(bot, chat.id, text=__("Game ended!",
                                             multi=game.translate))
        else:
            send_async(bot, chat.id, text=__("Removing {name} from the game",
                                             multi=game.translate)
                       .format(name=display_name(user)))


@game_locales
@user_locale
def start_game(bot, update, args):
    """Handler for the /start command"""

    if update.message.chat.type != 'private':
        chat = update.message.chat

        try:
            game = gm.chatid_games[chat.id][-1]
        except (KeyError, IndexError):
            send_async(bot, chat.id,
                       text=_("There is no game running in this chat. Create "
                              "a new one with /new"))
            return

        if game.started:
            send_async(bot, chat.id, text=_("The game has already started"))

        elif len(game.players) < 2:
            send_async(bot, chat.id,
                       text=_("At least two players must /join the game "
                              "before you can start it"))

        else:
            game.play_card(game.last_card)
            game.started = True

            first_message = (
                __("First player: {name}\n"
                   "Use /close to stop people from joining the game.\n"
                   "Enable multi-translations with /enable_translations",
                   multi=game.translate)
                .format(name=display_name(game.current_player.user)))

            @run_async
            def send_first():
                """Send the first card and player"""

                bot.sendSticker(chat.id,
                                sticker=c.STICKERS[str(game.last_card)],
                                timeout=TIMEOUT)

                bot.sendMessage(chat.id,
                                text=first_message,
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
                   text=_('Please select the group you want to play in.'),
                   reply_markup=InlineKeyboardMarkup(groups))

    else:
        help(bot, update)


@user_locale
def close_game(bot, update):
    """Handler for the /close command"""
    chat = update.message.chat
    user = update.message.from_user
    games = gm.chatid_games.get(chat.id)

    if not games:
        send_async(bot, chat.id,
                   text=_("There is no running game in this chat."))
        return

    game = games[-1]

    if game.owner.id == user.id:
        game.open = False
        send_async(bot, chat.id, text=_("Closed the lobby. "
                                        "No more players can join this game."))
        return

    else:
        send_async(bot, chat.id,
                   text=_("Only the game creator ({name}) can do that.")
                   .format(name=game.owner.first_name),
                   reply_to_message_id=update.message.message_id)
        return


@user_locale
def open_game(bot, update):
    """Handler for the /open command"""
    chat = update.message.chat
    user = update.message.from_user
    games = gm.chatid_games.get(chat.id)

    if not games:
        send_async(bot, chat.id,
                   text=_("There is no running game in this chat."))
        return

    game = games[-1]

    if game.owner.id == user.id:
        game.open = True
        send_async(bot, chat.id, text=_("Opened the lobby. "
                                        "New players may /join the game."))
        return
    else:
        send_async(bot, chat.id,
                   text=_("Only the game creator ({name}) can do that")
                   .format(name=game.owner.first_name),
                   reply_to_message_id=update.message.message_id)
        return


@user_locale
def enable_translations(bot, update):
    """Handler for the /enable_translations command"""
    chat = update.message.chat
    user = update.message.from_user
    games = gm.chatid_games.get(chat.id)

    if not games:
        send_async(bot, chat.id,
                   text=_("There is no running game in this chat."))
        return

    game = games[-1]

    if game.owner.id == user.id:
        game.translate = True
        send_async(bot, chat.id, text=_("Enabled multi-translations. "
                                        "Disable with /disable_translations"))
        return

    else:
        send_async(bot, chat.id,
                   text=_("Only the game creator ({name}) can do that")
                   .format(name=game.owner.first_name),
                   reply_to_message_id=update.message.message_id)
        return


@user_locale
def disable_translations(bot, update):
    """Handler for the /disable_translations command"""
    chat = update.message.chat
    user = update.message.from_user
    games = gm.chatid_games.get(chat.id)

    if not games:
        send_async(bot, chat.id,
                   text=_("There is no running game in this chat."))
        return

    game = games[-1]

    if game.owner.id == user.id:
        game.translate = False
        send_async(bot, chat.id, text=_("Disabled multi-translations. "
                                        "Enable them again with "
                                        "/enable_translations"))
        return

    else:
        send_async(bot, chat.id,
                   text=_("Only the game creator ({name}) can do that")
                   .format(name=game.owner.first_name),
                   reply_to_message_id=update.message.message_id)
        return


@game_locales
@user_locale
def skip_player(bot, update):
    """Handler for the /skip command"""
    chat = update.message.chat
    user = update.message.from_user

    player = gm.player_for_user_in_chat(user, chat)
    if not player:
        send_async(bot, chat.id,
                   text=_("You are not playing in a game in this chat."))
        return

    game = player.game
    skipped_player = game.current_player
    next_player = game.current_player.next

    started = skipped_player.turn_started
    now = datetime.now()
    delta = (now - started).seconds

    if delta < skipped_player.waiting_time:
        n = skipped_player.waiting_time - delta
        send_async(bot, chat.id,
                   text=_("Please wait {time} second",
                          "Please wait {time} seconds",
                          n)
                   .format(time=n),
                   reply_to_message_id=update.message.message_id)

    elif skipped_player.waiting_time > 0:
        skipped_player.anti_cheat += 1
        skipped_player.waiting_time -= 30
        try:
            skipped_player.draw()
        except DeckEmptyError:
            pass

        n = skipped_player.waiting_time
        send_async(bot, chat.id,
                   text=__("Waiting time to skip this player has "
                           "been reduced to {time} second.\n"
                           "Next player: {name}",
                           "Waiting time to skip this player has "
                           "been reduced to {time} seconds.\n"
                           "Next player: {name}",
                           n,
                           multi=game.translate)
                   .format(time=n,
                           name=display_name(next_player.user)))
        game.turn()

    else:
        try:
            gm.leave_game(skipped_player.user, chat)
            send_async(bot, chat.id,
                       text=__("{name1} was skipped four times in a row "
                               "and has been removed from the game.\n"
                               "Next player: {name2}", multi=game.translate)
                       .format(name1=display_name(skipped_player.user),
                               name2=display_name(next_player.user)))

        except NotEnoughPlayersError:
            send_async(bot, chat.id,
                       text=__("{name} was skipped four times in a row "
                               "and has been removed from the game.\n"
                               "The game ended.", multi=game.translate)
                       .format(name=display_name(skipped_player.user)))

            gm.end_game(chat.id, skipped_player.user)


@game_locales
@user_locale
def reply_to_query(bot, update):
    """
    Handler for inline queries.
    Builds the result list for inline queries and answers to the client.
    """
    results = list()
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
                add_choose_color(results, game)
                add_other_cards(player, results, game)
            else:
                if not player.drew:
                    add_draw(player, results)

                else:
                    add_pass(results, game)

                if game.last_card.special == c.DRAW_FOUR and game.draw_counter:
                    add_call_bluff(results, game)

                playable = player.playable_cards()
                added_ids = list()  # Duplicates are not allowed

                for card in sorted(player.cards):
                    add_card(game, card, results,
                             can_play=(card in playable and
                                            str(card) not in added_ids))
                    added_ids.append(str(card))

                add_gameinfo(game, results)

        elif user_id != game.current_player.user.id or not game.started:
            for card in sorted(player.cards):
                add_card(game, card, results, can_play=False)

        else:
            add_gameinfo(game, results)

        for result in results:
            result.id += ':%d' % player.anti_cheat

        if players and game and len(players) > 1:
            switch = _('Current game: {game}').format(game=game.chat.title)

    answer_async(bot, update.inline_query.id, results, cache_time=0,
                 switch_pm_text=switch, switch_pm_parameter='select')


@game_locales
@user_locale
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
    except (KeyError, AttributeError):
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
                   text=__("Cheat attempt by {name}", multi=game.translate)
                   .format(name=display_name(player.user)))
        return
    elif result_id == 'call_bluff':
        reset_waiting_time(bot, player)
        do_call_bluff(bot, player)
    elif result_id == 'draw':
        reset_waiting_time(bot, player)
        do_draw(bot, player)
    elif result_id == 'pass':
        game.turn()
    elif result_id in c.COLORS:
        game.choose_color(result_id)
    else:
        reset_waiting_time(bot, player)
        do_play_card(bot, player, result_id)

    if game in gm.chatid_games.get(chat.id, list()):
        send_async(bot, chat.id,
                   text=__("Next player: {name}", multi=game.translate)
                   .format(name=display_name(game.current_player.user)))


def reset_waiting_time(bot, player):
    """Resets waiting time for a player and sends a notice to the group"""
    chat = player.game.chat

    if player.waiting_time < 90:
        player.waiting_time = 90
        send_async(bot, chat.id,
                   text=__("Waiting time for {name} has been reset to 90 "
                           "seconds", multi=player.game.translate)
                   .format(name=display_name(player.user)))


def do_play_card(bot, player, result_id):
    """Plays the selected card and sends an update to the group if needed"""
    card = c.from_str(result_id)
    player.play(card)
    game = player.game
    chat = game.chat
    user = player.user

    us = UserSetting.get(id=user.id)
    if not us:
        us = UserSetting(id=user.id)

    if us.stats:
        us.cards_played += 1

    if game.choosing_color:
        send_async(bot, chat.id, text=_("Please choose a color"))

    if len(player.cards) == 1:
        send_async(bot, chat.id, text="UNO!")

    if len(player.cards) == 0:
        send_async(bot, chat.id,
                   text=__("{name} won!", multi=game.translate)
                   .format(name=user.first_name))

        if us.stats:
            us.games_played += 1

            if game.players_won is 0:
                us.first_places += 1

        game.players_won += 1

        try:
            gm.leave_game(user, chat)
        except NotEnoughPlayersError:
            send_async(bot, chat.id,
                       text=__("Game ended!", multi=game.translate))

            us2 = UserSetting.get(id=game.current_player.user.id)
            if us2 and us2.stats:
                us2.games_played += 1

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
                   text=__("There are no more cards in the deck.",
                           multi=game.translate))

    if (game.last_card.value == c.DRAW_TWO or
        game.last_card.special == c.DRAW_FOUR) and \
            draw_counter_before > 0:
        game.turn()


def do_call_bluff(bot, player):
    """Handles the bluff calling"""
    game = player.game
    chat = game.chat

    if player.prev.bluffing:
        send_async(bot, chat.id,
                   text=__("Bluff called! Giving 4 cards to {name}",
                           multi=game.translate)
                   .format(name=player.prev.user.first_name))

        try:
            player.prev.draw()
        except DeckEmptyError:
            send_async(bot, player.game.chat.id,
                       text=__("There are no more cards in the deck.",
                               multi=game.translate))

    else:
        game.draw_counter += 2
        send_async(bot, chat.id,
                   text=__("{name1} didn't bluff! Giving 6 cards to {name2}",
                           multi=game.translate)
                   .format(name1=player.prev.user.first_name,
                           name2=player.user.first_name))
        try:
            player.draw()
        except DeckEmptyError:
            send_async(bot, player.game.chat.id,
                       text=__("There are no more cards in the deck.",
                               multi=game.translate))

    game.turn()


# Add all handlers to the dispatcher and run the bot
dispatcher.add_handler(InlineQueryHandler(reply_to_query))
dispatcher.add_handler(ChosenInlineResultHandler(process_result))
dispatcher.add_handler(CallbackQueryHandler(select_game))
dispatcher.add_handler(CommandHandler('start', start_game, pass_args=True))
dispatcher.add_handler(CommandHandler('new', new_game))
dispatcher.add_handler(CommandHandler('join', join_game))
dispatcher.add_handler(CommandHandler('leave', leave_game))
dispatcher.add_handler(CommandHandler('open', open_game))
dispatcher.add_handler(CommandHandler('close', close_game))
dispatcher.add_handler(CommandHandler('enable_translations',
                                      enable_translations))
dispatcher.add_handler(CommandHandler('disable_translations',
                                      disable_translations))
dispatcher.add_handler(CommandHandler('skip', skip_player))
dispatcher.add_handler(CommandHandler('notify_me', notify_me))
simple_commands.register()
settings.register()
dispatcher.add_handler(MessageHandler([Filters.status_update], status_update))
dispatcher.add_error_handler(error)

start_bot(updater)
updater.idle()
