FROM python:3.11-alpine

RUN apk add --no-cache gettext

WORKDIR /app/
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN cd locales && find . -maxdepth 2 -type d -name 'LC_MESSAGES' -exec ash -c 'msgfmt {}/unobot.po -o {}/unobot.mo' \;


VOLUME /app/data
ENV UNO_DB /app/data/uno.sqlite3

ENTRYPOINT python3 ./bot.py
