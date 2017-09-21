# UNO Bot

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](./LICENSE)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/0d29a306f9ea4fbc94a2a28f9f52141c)](https://www.codacy.com/app/J4RV/mau_mau_bot?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=J4RV/mau_mau_bot&amp;utm_campaign=Badge_Grade)

Telegram Bot that allows you to play the popular card game UNO via inline queries. The bot currently runs as [@unobot](http://telegram.me/unobot).

To run the bot yourself, you will need: 
- Python (tested with 3.4+)
- The [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) module
- [Pony ORM](https://ponyorm.com/)

## Setup
- Get a bot token from [@BotFather](http://telegram.me/BotFather) and change configurations in `config.json`.
- Convert all language files from `.po` files to `.mo` by executing the bash script `compile.sh` located in the `locales` folder.
  Another option is: `find . -maxdepth 2 -type d -name 'LC_MESSAGES' -exec bash -c 'msgfmt {}/unobot.po -o {}/unobot.mo' \;`.
- Use `/setinline` and `/setinlinefeedback` with BotFather for your bot.
- Install requirements (using a `virtualenv` is recommended): `pip install -r requirements.txt`

Then run the bot with `python3 bot.py`.

Code documentation is minimal but there.
