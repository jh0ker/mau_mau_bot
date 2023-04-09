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


# Colors
RED = 'r'
BLUE = 'b'
GREEN = 'g'
YELLOW = 'y'
BLACK = 'x'

COLORS = (RED, BLUE, GREEN, YELLOW)

COLOR_ICONS = {
    RED: '❤️',
    BLUE: '💙',
    GREEN: '💚',
    YELLOW: '💛',
    BLACK: '⬛️'
}

# Values
ZERO = '0'
ONE = '1'
TWO = '2'
THREE = '3'
FOUR = '4'
FIVE = '5'
SIX = '6'
SEVEN = '7'
EIGHT = '8'
NINE = '9'
DRAW_TWO = 'draw'
REVERSE = 'reverse'
SKIP = 'skip'

VALUES = (ZERO, ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, DRAW_TWO,
          REVERSE, SKIP)
WILD_VALUES = (ONE, TWO, THREE, FOUR, FIVE, DRAW_TWO, REVERSE, SKIP)

# Special cards
CHOOSE = 'colorchooser'
DRAW_FOUR = 'draw_four'

SPECIALS = (CHOOSE, DRAW_FOUR)

CARDS_CLASSIC = {
    "normal": {
        "b_0": "BQADBAAD2QEAAl9XmQAB--inQsYcLTsC",
        "b_1": "BQADBAAD2wEAAl9XmQABBzh4U-rFicEC",
        "b_2": "BQADBAAD3QEAAl9XmQABo3l6TT0MzKwC",
        "b_3": "BQADBAAD3wEAAl9XmQAB2y-3TSapRtIC",
        "b_4": "BQADBAAD4QEAAl9XmQABT6nhOuolqKYC",
        "b_5": "BQADBAAD4wEAAl9XmQABwRfmekGnpn0C",
        "b_6": "BQADBAAD5QEAAl9XmQABQITgUsEsqxsC",
        "b_7": "BQADBAAD5wEAAl9XmQABVhPF6EcfWjEC",
        "b_8": "BQADBAAD6QEAAl9XmQABP6baig0pIvYC",
        "b_9": "BQADBAAD6wEAAl9XmQAB0CQdsQs_pXIC",
        "b_draw": "BQADBAAD7QEAAl9XmQAB00Wii7R3gDUC",
        "b_skip": "BQADBAAD8QEAAl9XmQAB_RJHYKqlc-wC",
        "b_reverse": "BQADBAAD7wEAAl9XmQABo7D0B9NUPmYC",
        "g_0": "BQADBAAD9wEAAl9XmQABb8CaxxsQ-Y8C",
        "g_1": "BQADBAAD-QEAAl9XmQAB9B6ti_j6UB0C",
        "g_2": "BQADBAAD-wEAAl9XmQABYpLjOzbRz8EC",
        "g_3": "BQADBAAD_QEAAl9XmQABKvc2ZCiY-D8C",
        "g_4": "BQADBAAD_wEAAl9XmQABJB52wzPdHssC",
        "g_5": "BQADBAADAQIAAl9XmQABp_Ep1I4GA2cC",
        "g_6": "BQADBAADAwIAAl9XmQABaaMxxa4MihwC",
        "g_7": "BQADBAADBQIAAl9XmQABv5Q264Crz8gC",
        "g_8": "BQADBAADBwIAAl9XmQABjMH-X9UHh8sC",
        "g_9": "BQADBAADCQIAAl9XmQAB26fZ2fW7vM0C",
        "g_draw": "BQADBAADCwIAAl9XmQAB64jIZrgXrQUC",
        "g_skip": "BQADBAADDwIAAl9XmQAB17yhhnh46VQC",
        "g_reverse": "BQADBAADDQIAAl9XmQAB_xcaab0DkegC",
        "r_0": "BQADBAADEQIAAl9XmQABiUfr1hz-zT8C",
        "r_1": "BQADBAADEwIAAl9XmQAB5bWfwJGs6Q0C",
        "r_2": "BQADBAADFQIAAl9XmQABHR4mg9Ifjw0C",
        "r_3": "BQADBAADFwIAAl9XmQABYBx5O_PG2QIC",
        "r_4": "BQADBAADGQIAAl9XmQABTQpGrlvet3cC",
        "r_5": "BQADBAADGwIAAl9XmQABbdLt4gdntBQC",
        "r_6": "BQADBAADHQIAAl9XmQABqEI274p3lSoC",
        "r_7": "BQADBAADHwIAAl9XmQABCw8u67Q4EK4C",
        "r_8": "BQADBAADIQIAAl9XmQAB8iDJmLxp8ogC",
        "r_9": "BQADBAADIwIAAl9XmQAB_HCAww1kNGYC",
        "r_draw": "BQADBAADJQIAAl9XmQABuz0OZ4l3k6MC",
        "r_skip": "BQADBAADKQIAAl9XmQAC2AL5Ok_ULwI",
        "r_reverse": "BQADBAADJwIAAl9XmQABu2tIeQTpDvUC",
        "y_0": "BQADBAADKwIAAl9XmQAB_nWoNKe8DOQC",
        "y_1": "BQADBAADLQIAAl9XmQABVprAGUDKgOQC",
        "y_2": "BQADBAADLwIAAl9XmQABqyT4_YTm54EC",
        "y_3": "BQADBAADMQIAAl9XmQABGC-Xxg_N6fIC",
        "y_4": "BQADBAADMwIAAl9XmQABbc-ZGL8kApAC",
        "y_5": "BQADBAADNQIAAl9XmQAB67QJZIF6XAcC",
        "y_6": "BQADBAADNwIAAl9XmQABJg_7XXoITsoC",
        "y_7": "BQADBAADOQIAAl9XmQABVrd7OcS2k34C",
        "y_8": "BQADBAADOwIAAl9XmQABRpJSahBWk3EC",
        "y_9": "BQADBAADPQIAAl9XmQAB9MwJWKLJogYC",
        "y_draw": "BQADBAADPwIAAl9XmQABaPYK8oYg84cC",
        "y_skip": "BQADBAADQwIAAl9XmQABO_AZKtxY6IMC",
        "y_reverse": "BQADBAADQQIAAl9XmQABZdQFahGG6UQC",
        "draw_four": "BQADBAAD9QEAAl9XmQABVlkSNfhn76cC",
        "colorchooser": "BQADBAAD8wEAAl9XmQABl9rUOPqx4E4C",
    },
    "not_playable": {
        "b_0": "BQADBAADRQIAAl9XmQAB1IfkQ5xAiK4C",
        "b_1": "BQADBAADRwIAAl9XmQABbWvhTeKBii4C",
        "b_2": "BQADBAADSQIAAl9XmQABS1djHgyQokMC",
        "b_3": "BQADBAADSwIAAl9XmQABwQ6VTbgY-MIC",
        "b_4": "BQADBAADTQIAAl9XmQABAlKUYha8YccC",
        "b_5": "BQADBAADTwIAAl9XmQABMvx8xVDnhUEC",
        "b_6": "BQADBAADUQIAAl9XmQABDEbhP1Zd31kC",
        "b_7": "BQADBAADUwIAAl9XmQABXb5XQBBaAnIC",
        "b_8": "BQADBAADVQIAAl9XmQABgL5HRDLvrjgC",
        "b_9": "BQADBAADVwIAAl9XmQABtO3XDQWZLtYC",
        "b_draw": "BQADBAADWQIAAl9XmQAB2kk__6_2IhMC",
        "b_skip": "BQADBAADXQIAAl9XmQABEGJI6CaH3vcC",
        "b_reverse": "BQADBAADWwIAAl9XmQAB_kZA6UdHXU8C",
        "g_0": "BQADBAADYwIAAl9XmQABGD5a9oG7Yg4C",
        "g_1": "BQADBAADZQIAAl9XmQABqwABZHAXZIg0Ag",
        "g_2": "BQADBAADZwIAAl9XmQABTI3mrEhojRkC",
        "g_3": "BQADBAADaQIAAl9XmQABVi3rUyzWS3YC",
        "g_4": "BQADBAADawIAAl9XmQABZIf5ThaXnpUC",
        "g_5": "BQADBAADbQIAAl9XmQABNndVJSQCenIC",
        "g_6": "BQADBAADbwIAAl9XmQABpoy1c4ZkrvwC",
        "g_7": "BQADBAADcQIAAl9XmQABDeaT5fzxwREC",
        "g_8": "BQADBAADcwIAAl9XmQABLIQ06ZM5NnAC",
        "g_9": "BQADBAADdQIAAl9XmQABel-mC7eXGsMC",
        "g_draw": "BQADBAADdwIAAl9XmQABOHEpxSztCf8C",
        "g_skip": "BQADBAADewIAAl9XmQABDaQdMxjjPsoC",
        "g_reverse": "BQADBAADeQIAAl9XmQABek1lGz7SJNAC",
        "r_0": "BQADBAADfQIAAl9XmQABWrxoiXcsg0EC",
        "r_1": "BQADBAADfwIAAl9XmQABlav-bkgSgRcC",
        "r_2": "BQADBAADgQIAAl9XmQABDjZkqfJ4AdAC",
        "r_3": "BQADBAADgwIAAl9XmQABT7lH7VVcy3MC",
        "r_4": "BQADBAADhQIAAl9XmQAB1arPC5x0LrwC",
        "r_5": "BQADBAADhwIAAl9XmQABWvs7xkCDldkC",
        "r_6": "BQADBAADiQIAAl9XmQABjwABH5ZonWn8Ag",
        "r_7": "BQADBAADiwIAAl9XmQABjekJfm4fBDIC",
        "r_8": "BQADBAADjQIAAl9XmQABqFjchpsJeEkC",
        "r_9": "BQADBAADjwIAAl9XmQAB-sKdcgABdNKDAg",
        "r_draw": "BQADBAADkQIAAl9XmQABtw9RPVDHZOQC",
        "r_skip": "BQADBAADlQIAAl9XmQABtG2GixCxtX4C",
        "r_reverse": "BQADBAADkwIAAl9XmQABz2qyEbabnVsC",
        "y_0": "BQADBAADlwIAAl9XmQABAb3ZwTGS1lMC",
        "y_1": "BQADBAADmQIAAl9XmQAB9v5qJk9R0x8C",
        "y_2": "BQADBAADmwIAAl9XmQABCsgpRHC2g-cC",
        "y_3": "BQADBAADnQIAAl9XmQAB3kLLXCv-qY0C",
        "y_4": "BQADBAADnwIAAl9XmQAB7R_y-NexNLIC",
        "y_5": "BQADBAADoQIAAl9XmQABl-7mwsjD-cMC",
        "y_6": "BQADBAADowIAAl9XmQABwbVsyv2MfPkC",
        "y_7": "BQADBAADpQIAAl9XmQABoBqC0JsemVwC",
        "y_8": "BQADBAADpwIAAl9XmQABpkwAAeh9ldlHAg",
        "y_9": "BQADBAADqQIAAl9XmQABpSBEUfd4IM8C",
        "y_draw": "BQADBAADqwIAAl9XmQABMt-2zW0VYb4C",
        "y_skip": "BQADBAADrwIAAl9XmQABIDf-_TuuxtEC",
        "y_reverse": "BQADBAADrQIAAl9XmQABm9M0Zh-_UwkC",
        "draw_four": "BQADBAADYQIAAl9XmQAB_HWlvZIscDEC",
        "colorchooser": "BQADBAADXwIAAl9XmQABY_ksDdMex-wC",
    },
}

CARDS_CLASSIC_COLORBLIND = {
    "normal": {
        "colorchooser": "CAADBAADrg4AAvX2mVEpx_BiDIE5nQI",
        "draw_four": "CAADBAADYRAAArnkmVGmqXHhjWEBxAI",
        "r_0": "CAADBAAD6A8AAn_ckVHPWHqiBR_3jAI",
        "r_1": "CAADBAAD5Q0AAg-ImVEx-blQI88RrQI",
        "r_2": "CAADBAAD1g0AAuMjmVEkQsVhN49DMAI",
        "r_3": "CAADBAADlhAAAqy4mVHWovoaWfQG_gI",
        "r_4": "CAADBAADCRoAAqf_kVFnl8ACL1rjpwI",
        "r_5": "CAADBAADVw8AAjmamVEEv2TVeL9cpQI",
        "r_6": "CAADBAADHQ4AAuuUkVH2I-yn6nRBVAI",
        "r_7": "CAADBAADNQ8AArP1kVF5rqHtk0pQ-AI",
        "r_8": "CAADBAAD1BAAAuQDkVEPiIodUi6WvwI",
        "r_9": "CAADBAAD2Q4AAq1nkFHM6z5C0Kff2QI",
        "r_draw": "CAADBAADvQ8AAqZukFGEmkRSoSZQEwI",
        "r_reverse": "CAADBAAD5RAAAg89mVE8-EY_2DifcAI",
        "r_skip": "CAADBAADRg4AAp8bmVFOC6xdEZZRwwI",
        "g_0": "CAADBAADTg4AAoQxmFF07jR_vfB4xgI",
        "g_1": "CAADBAADQg4AAhkgmFGlsif9nNtXwgI",
        "g_2": "CAADBAAD2BUAAue_mFGENiPSjZxbiQI",
        "g_3": "CAADBAADpw4AAjO9mFHAOz8KD2n7BwI",
        "g_4": "CAADBAADRhAAAqF7kFEcwLalLfDfaAI",
        "g_5": "CAADBAADAg8AAqXLmFHJyg2F_ybbvwI",
        "g_6": "CAADBAADVhYAAtK7mVGigRq_EkCuVgI",
        "g_7": "CAADBAAD2RIAArccmFEj-8LIVNAbsgI",
        "g_8": "CAADBAAD6AwAAuvmmFHBRarMimOWawI",
        "g_9": "CAADBAADExEAAsNkmVFr8DaHGOwsggI",
        "g_draw": "CAADBAADhA8AArxYmVH9ch5Jp00AAboC",
        "g_reverse": "CAADBAADMhAAAvVOmFGH284LIY7cegI",
        "g_skip": "CAADBAADbBcAAqinkVEOwkJtDRfk2gI",
        "b_0": "CAADBAAD-BAAAkj8kFG61GJdw29QOAI",
        "b_1": "CAADBAADcRMAAu-EmFFT1i4LcqO4OQI",
        "b_2": "CAADBAAD0xQAAqVhmVHyrFSAbxtfjwI",
        "b_3": "CAADBAADNg0AAn-xmFHev8IdF_ie0wI",
        "b_4": "CAADBAADlQ4AAjZamVFcIL_pVB5cFwI",
        "b_5": "CAADBAADrgwAAuL5mVHvEBZ8CG5p5QI",
        "b_6": "CAADBAADDhUAAuGRmVGQYvmEOxczBAI",
        "b_7": "CAADBAADIxEAAv_dmFEuVt39kkgZgwI",
        "b_8": "CAADBAAD2w0AAoE6kVHG7WscV4F2hwI",
        "b_9": "CAADBAADvQ0AArRMmVErWaSRP_giKQI",
        "b_draw": "CAADBAADlw4AAjF_kFHPWSoYKBwtwQI",
        "b_reverse": "CAADBAADog8AAqDJmVEJQp5WocnUnQI",
        "b_skip": "CAADBAAD-QwAAgbZmFGltUlnslDNUQI",
        "y_0": "CAADBAADrQ4AAr5WmVHNf69eBn2YOAI",
        "y_1": "CAADBAADcg8AAmqKmVHfVeUI3u_i7AI",
        "y_2": "CAADBAADkA4AAuDImFEQ8qjFlcKplQI",
        "y_3": "CAADBAAD-QwAAmromFGAqVn-Y8N72wI",
        "y_4": "CAADBAADjQ4AAmNLmFG80k7kfgx1NAI",
        "y_5": "CAADBAADqQ8AAmgYmFH1_ey_bMQNYwI",
        "y_6": "CAADBAADdQ0AAuWcmFEbG_gm1wGYCQI",
        "y_7": "CAADBAAD6QwAApQAAZhRI8OfRvLX3vkC",
        "y_8": "CAADBAADARAAAi-2kVEifJ-O9WVilgI",
        "y_9": "CAADBAADxA0AAhQ8mFHjnl9tUCHSLAI",
        "y_draw": "CAADBAADzw4AAncZmVEhLhX17eqX8AI",
        "y_reverse": "CAADBAADTxAAAqgFmVEJRBw4eWgnDwI",
        "y_skip": "CAADBAADPhYAAiGbkFG9hptFPLgj7wI",
    },
    "not_playable": {
        "colorchooser": "CAADBAADpQ4AAlfDmFFHGkwyGFeCFQI",
        "draw_four": "CAADBAADMRMAAv7amFHvKGLoNyFbNQI",
        "r_0": "CAADBAADsBMAAuGdkFHTZ-jl4eNn-gI",
        "r_1": "CAADBAADVA4AAhpfkFEKt19qveGSPgI",
        "r_2": "CAADBAADrw0AAoWsmVHguULNoYJwUwI",
        "r_3": "CAADBAADzxMAAjvkkFFdtKJu5WGwUgI",
        "r_4": "CAADBAAD1Q8AAoHZkFFvyQnFHzfwiQI",
        "r_5": "CAADBAADWxEAAvkHkFGUo86qxKV0kwI",
        "r_6": "CAADBAAD_hIAAjx0mVGmlm-b_FHQBAI",
        "r_7": "CAADBAADmhEAAslomFHOv7bqcDJkDAI",
        "r_8": "CAADBAADtw0AAgqVmVG2HdSbcJYxZgI",
        "r_9": "CAADBAADNxEAAuF6mVE3WzTMJkSVAgI",
        "r_draw": "CAADBAADVxAAAiNukFE1K2xORNnfMwI",
        "r_reverse": "CAADBAADQxMAAvH0mVHKznpt-uu9ngI",
        "r_skip": "CAADBAADZA4AApbPkFFB9E2Px-HFpgI",
        "g_0": "CAADBAAD8w4AAjDEmFG7DwKggUEj9QI",
        "g_1": "CAADBAAD2g0AAo_DmVHIPG84WdIo1wI",
        "g_2": "CAADBAADEhEAAoRXmVGIG2nuN45P6AI",
        "g_3": "CAADBAADug8AAsSRmFFzk0TcRuG8VAI",
        "g_4": "CAADBAADrQ8AAvgmkFESfo9BjF7-3gI",
        "g_5": "CAADBAADVhAAAnPqkFFtxtFX9HlT-AI",
        "g_6": "CAADBAADMg8AAiSBmFHIQw1jFjv6UwI",
        "g_7": "CAADBAADvREAAv0BkVGDq3H1DCq_DQI",
        "g_8": "CAADBAADWQ4AAhOEkVG96JDgCtFrEwI",
        "g_9": "CAADBAAD2xYAAruDmFFAUMFryEwjoAI",
        "g_draw": "CAADBAADLA4AAu9tkVGTzBbeeYydIQI",
        "g_reverse": "CAADBAADVAwAAhYYmFExJS0ozE8-rAI",
        "g_skip": "CAADBAADYg4AAulsmFHxOkaz9OsTiwI",
        "b_0": "CAADBAADVxUAAtnOkFEIAAGw5CZEIxgC",
        "b_1": "CAADBAAD1RAAAnQqkFF9kDqD0wp3ngI",
        "b_2": "CAADBAADZg4AAvcUmVHTXwldirf1hAI",
        "b_3": "CAADBAADfBAAAkX1mVHw0CWX0h31iQI",
        "b_4": "CAADBAADPBAAAuTCmFFDpvXzes4qjwI",
        "b_5": "CAADBAADTQ4AAsWQmVHcrxDQUWOB4AI",
        "b_6": "CAADBAAD_hAAAoUhmVG8kjd65J8EngI",
        "b_7": "CAADBAADlRAAArtjkFGko5TuFNnncwI",
        "b_8": "CAADBAADZQ8AAltEmFE_fDYIXBrV3QI",
        "b_9": "CAADBAADrhAAAtM-mVGwhrWTD9IaYgI",
        "b_draw": "CAADBAADtQ0AAnVbmFGC1hI60JaOQQI",
        "b_reverse": "CAADBAADShEAAlcOmFHStPeFzfVIEwI",
        "b_skip": "CAADBAAD_xEAAgZFmVFMRA1J8Y1gxAI",
        "y_0": "CAADBAAD7xAAAqjjmFHnCu7eKJvSBgI",
        "y_1": "CAADBAADJQwAAp6tmFE2zDPVMieQ2QI",
        "y_2": "CAADBAADNA4AAl2mmVFpQOxJ41gk_gI",
        "y_3": "CAADBAAD3A4AAsxPmFGyZFv42UlxAQI",
        "y_4": "CAADBAADwg8AAm88kVEc9HZpl2gmzQI",
        "y_5": "CAADBAAD5hIAAkQ6mFHS-aGVuYZAnAI",
        "y_6": "CAADBAADvQ8AAs3RmVHVkVBfEF7eIwI",
        "y_7": "CAADBAAD1gwAAjlbmFGGH6rBdqP8QQI",
        "y_8": "CAADBAADbg8AAqvXkVH1ESeZFcGVrgI",
        "y_9": "CAADBAADOQ8AAnjokVG96pmCP7aZ3AI",
        "y_draw": "CAADBAAD6w4AAgsJmVETUteFwqTVJgI",
        "y_reverse": "CAADBAADtg8AAqiFmFFwothyN9TrXwI",
        "y_skip": "CAADBAADSxEAAhcSmFGu_F5LffmsZgI",
    },
}

STICKERS_OPTIONS = {
    "option_draw": "BQADBAAD-AIAAl9XmQABxEjEcFM-VHIC",
    "option_pass": "BQADBAAD-gIAAl9XmQABcEkAAbaZ4SicAg",
    "option_bluff": "BQADBAADygIAAl9XmQABJoLfB9ntI2UC",
    "option_info": "BQADBAADxAIAAl9XmQABC5v3Z77VLfEC",
}

# TODO: Support multiple card packs
# For now, just use classic colorblind
STICKERS = {
    **CARDS_CLASSIC_COLORBLIND["normal"],
    **STICKERS_OPTIONS,
}

STICKERS_GREY = {
    **CARDS_CLASSIC_COLORBLIND["not_playable"],
}


class Card(object):
    """This class represents an UNO card"""

    def __init__(self, color, value, special=None):
        self.color = color
        self.value = value
        self.special = special

    def __str__(self):
        if self.special:
            return self.special
        else:
            return '%s_%s' % (self.color, self.value)

    def __repr__(self):
        if self.special:
            return '%s%s%s' % (COLOR_ICONS.get(self.color, ''),
                               COLOR_ICONS[BLACK],
                               ' '.join([s.capitalize()
                                         for s in self.special.split('_')]))
        else:
            return '%s%s' % (COLOR_ICONS[self.color], self.value.capitalize())

    def __eq__(self, other):
        """Needed for sorting the cards"""
        return str(self) == str(other)

    def __lt__(self, other):
        """Needed for sorting the cards"""
        return str(self) < str(other)


def from_str(string):
    """Decodes a Card object from a string"""
    if string not in SPECIALS:
        color, value = string.split('_')
        return Card(color, value)
    else:
        return Card(None, None, string)
