from uuid import uuid4

from telegram import InlineQueryResultArticle, InputTextMessageContent, \
    InlineQueryResultCachedSticker as Sticker

import card as c
from utils import *


def add_choose_color(results):
    for color in c.COLORS:
        results.append(
            InlineQueryResultArticle(
                id=color,
                title="Choose Color",
                description=display_color(color),
                input_message_content=
                InputTextMessageContent(display_color(color))
            )
        )


def add_other_cards(playable, player, results, game):
    if not playable:
        playable = list()

    players = player_list(game)

    results.append(
        InlineQueryResultArticle(
            "hand",
            title="Cards (tap for game state):",
            description=', '.join([repr(card) for card in
                                   list_subtract(player.cards, playable)]),
            input_message_content=InputTextMessageContent(
                "Current player: " + display_name(game.current_player.user) +
                "\n" +
                "Last card: " + repr(game.last_card) + "\n" +
                "Players: " + " -> ".join(players))
        )
    )


def player_list(game):
    players = list()
    for player in game.players:
        add_player(player, players)
    return players


def add_no_game(results):
    results.append(
        InlineQueryResultArticle(
            "nogame",
            title="You are not playing",
            input_message_content=
            InputTextMessageContent('Not playing right now. Use /new to start '
                                    'a game or /join to join the current game '
                                    'in this group')
        )
    )


def add_not_started(results):
    results.append(
        InlineQueryResultArticle(
            "nogame",
            title="The game wasn't started yet",
            input_message_content=
            InputTextMessageContent('Start the game with /start')
        )
    )


def add_draw(player, results):
    results.append(
        Sticker(
            "draw", sticker_file_id=c.STICKERS['option_draw'],
            input_message_content=
            InputTextMessageContent('Drawing %d card(s)'
                                    % (player.game.draw_counter or 1))
        )
    )


def add_gameinfo(game, results):
    players = player_list(game)

    results.append(
        Sticker(
            "gameinfo",
            sticker_file_id=c.STICKERS['option_info'],
            input_message_content=InputTextMessageContent(
                "Current player: " + display_name(game.current_player.user) +
                "\n" +
                "Last card: " + repr(game.last_card) + "\n" +
                "Players: " + " -> ".join(players))
        )
    )


def add_pass(results):
    results.append(
        Sticker(
            "pass", sticker_file_id=c.STICKERS['option_pass'],
            input_message_content=InputTextMessageContent('Pass')
        )
    )


def add_call_bluff(results):
    results.append(
        Sticker(
            "call_bluff",
            sticker_file_id=c.STICKERS['option_bluff'],
            input_message_content=
            InputTextMessageContent("I'm calling your bluff!")
        )
    )


def add_play_card(game, card, results, can_play):
    players = player_list(game)

    if can_play:
        results.append(
            Sticker(str(card), sticker_file_id=c.STICKERS[str(card)])
        )
    else:
        results.append(
            Sticker(str(uuid4()), sticker_file_id=c.STICKERS_GREY[str(card)],
                    input_message_content=InputTextMessageContent(
                        "Current player: " + display_name(
                            game.current_player.user) +
                        "\n" +
                        "Last card: " + repr(game.last_card) + "\n" +
                        "Players: " + " -> ".join(players)))
        )


def add_player(itplayer, players):
    players.append(itplayer.user.first_name + " (%d cards)"
                   % len(itplayer.cards))

