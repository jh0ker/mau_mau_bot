FROM python:alpine

RUN apk add --no-cache gettext

WORKDIR /app/
COPY . .

RUN cd locales && find . -maxdepth 2 -type d -name 'LC_MESSAGES' -exec ash -c 'msgfmt {}/unobot.po -o {}/unobot.mo' \;

RUN pip install -r requirements.txt

ENTRYPOINT python3 ./bot.py
