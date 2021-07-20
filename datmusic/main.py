#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple telegram bot to download music from datmusic (https://github.com/alashow/music).

import logging
import os
import sys
import time
from uuid import uuid4

import requests
from telegram import InlineQueryResultAudio, InlineQueryResultPhoto, InlineQueryResultArticle, InlineQueryResultGif, InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler

import settings
import text
from constants import DATMUSIC_API_ENDPOINT
from constants import DEFAULT_HEADERS
from constants import INLINE_QUERY_CACHE_TIME
from constants import LINKS_MODE_SUFFIX

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

captchaLocked = False
captchaLockParams = {}


def handle_inline_query(bot, update):
    caller_name = update.inline_query.from_user.name
    query = update.inline_query.query

    links_mode = query.endswith(LINKS_MODE_SUFFIX)
    if links_mode:
        chop_point = len(query) - len(LINKS_MODE_SUFFIX)
        query = query[:chop_point]

    logger.info(f"Search query from {caller_name}: {query}, links_mode={links_mode}")
    search(query, links_mode, bot, update)


def reply_audio_search_results(audios, query, links_mode, bot, update):
    cache_time = INLINE_QUERY_CACHE_TIME
    results = list()
    try:
        if not audios:
            cache_time = 300
            print(f"Empty results for query: {query}")
            results.append(InlineQueryResultGif(id=str(uuid4()),
                                                gif_url='https://media.giphy.com/media/sS8YbjrTzu4KI/giphy.gif',
                                                thumb_url='https://media.giphy.com/media/sS8YbjrTzu4KI/giphy.gif',
                                                title="Failed You",
                                                input_message_content=InputTextMessageContent(
                                                    f"youtube.com/results?search_query={query}")))
        else:
            print(f"Found {len(audios)} results for query: {query}")
            results = build_inline_audio_results(audios, links_mode)
        update.inline_query.answer(results=results, cache_time=cache_time)
    except Exception as e:
        log_error(bot, update, e)


def duration_text(duration):
    return time.strftime('%M:%S', time.gmtime(duration))


def album_or_duration(audio):
    return f"Album: {audio['album']}" if ('album' in audio) else f"Duration: {duration_text(audio['duration'])}"


def audios_mapper(audio):
    return InlineQueryResultAudio(
        id=str(uuid4()),
        audio_url=audio['download'],
        title=audio["title"],
        performer=audio["artist"],
        audio_duration=audio["duration"]
    )


def article_mapper(audio):
    return InlineQueryResultArticle(
        id=str(uuid4()),
        thumb_url=audio.get('cover_url_small') or audio.get('cover'),
        hide_url=True,
        url=audio['download'],
        title=audio["title"],
        description="Artist: {}\n{}".format(audio['artist'], album_or_duration(audio)),
        audio_duration=audio["duration"],
        input_message_content=InputTextMessageContent(audio['download'])
    )


def build_inline_audio_results(audios, links_mode):
    return list(map(article_mapper if links_mode else audios_mapper, audios[:50]))


def on_captcha_lock(error, query):
    global captchaLocked, captchaLockParams
    captchaLockParams.update(error)
    if not captchaLocked:
        captchaLockParams.update({'q': query})
    captchaLocked = True


def reply_captcha_inline(query, bot, update):
    if captchaLocked and captchaLockParams:
        input_message = InputTextMessageContent(f"youtube.com/results?search_query={query}")
        results = [InlineQueryResultPhoto(
            id=str(uuid4()),
            photo_url=captchaLockParams['captcha_img'],
            thumb_url=captchaLockParams['captcha_img'],
            photo_width=130,
            photo_height=50,
            title="Please complete captcha",
            description="Please complete captcha",
            caption="Type symbols on the image. Do not click the image",
            input_message_content=input_message
        )]
        update.inline_query.answer(results=results, cache_time=0)


def search(query, links_mode, bot, update):
    global captchaLocked, captchaLockParams
    if len(query.strip()) < 1:
        query = text.get_random_artist()

    payload = {'q': query}

    if captchaLocked:
        payload.update(captchaLockParams)
        payload.update({'captcha_key': query})

    result = requests.get(DATMUSIC_API_ENDPOINT, params=payload, headers=DEFAULT_HEADERS)
    try:
        response = result.json()
        if response['status'] == 'ok':
            response = response["data"]
            captchaLocked = False
            captchaLockParams = {}
            reply_audio_search_results(response, query, links_mode, bot, update)
        else:
            error = response['error']

            if error and 'captcha_id' in error:
                on_captcha_lock(error, query)
                reply_captcha_inline(query, bot, update)
    except ValueError as e:
        print("Failed to parse result:")
        print(e)


def log_error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def add_update_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler("start", text.start))
    dispatcher.add_handler(CommandHandler("about", text.about))

    dispatcher.add_handler(InlineQueryHandler(handle_inline_query))
    return dispatcher


def main():
    token = os.getenv("DATMUSIC_BOT_TOKEN")
    if not token:
        logging.critical('NO TOKEN FOUND!')
        sys.exit()

    updater = Updater(token)
    dispatcher = updater.dispatcher
    add_update_handlers(dispatcher)
    dispatcher.add_error_handler(log_error)
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
