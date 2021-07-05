#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple telegram bot to download music from datmusic (https://github.com/alashow/music).
# Currently just works with inline queries.
# Beta! Code is litte bit too simple :)

import os
import sys
import re
import requests
from uuid import uuid4;

from telegram import InlineQueryResultAudio, InlineQueryResultPhoto, InlineQueryResultArticle, InlineQueryResultGif, InputTextMessageContent, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import logging

import time

import settings
import text
from constants import DATMUSIC_API_ENDPOINT
from constants import INLINE_QUERY_CACHE_TIME
from constants import DEFAULT_HEADERS
from constants import LINKS_MODE_SUFFIX

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

captchaLocked = False
captchaLockParams = {}

def handleInlineQuery(bot, update):
    callerName = update.inline_query.from_user.name
    query = update.inline_query.query

    linksMode = query.endswith(LINKS_MODE_SUFFIX)
    if linksMode:
        chopPoint = len(query)-len(LINKS_MODE_SUFFIX)
        query = query[:chopPoint]

    logger.info(f"Search query from {callerName}: {query}, linksMode={linksMode}")
    search(query, linksMode, bot, update); 

def replyAudioSearchResults(audios, query, linksMode, bot, update):
    cache_time = INLINE_QUERY_CACHE_TIME
    results = list()
    try:
        if not audios:
            cache_time = 300
            print(f"Empty results for query: {query}")
            results.append(InlineQueryResultGif(id=uuid4(),
                                           gif_url='https://media.giphy.com/media/sS8YbjrTzu4KI/giphy.gif',
                                           thumb_url='https://media.giphy.com/media/sS8YbjrTzu4KI/giphy.gif',
                                            title="Failed You",
                                            input_message_content=InputTextMessageContent(f"youtube.com/results?search_query={query}")))
        else:
            print(f"Found {len(audios)} results for query: {query}")
            results = buildInlineAudioResults(audios, linksMode)
        update.inline_query.answer(results=results, cache_time=cache_time)
    except Exception as e:
        logError(bot, update, e)

def buildInlineAudioResults(audios, linksMode):
    durationText = lambda duration: time.strftime('%M:%S', time.gmtime(duration))
    albumOrDuration = lambda audio: f"Album: {audio['album']}" if ('album' in audio) else f"Duration: {durationText(audio['duration'])}"

    audiosMapper = lambda audio: InlineQueryResultAudio(
                        id=uuid4(),
                        audio_url=audio['download'],
                        title=audio["title"],
                        performer=audio["artist"],
                        audio_duration=audio["duration"]
                )
    articleMapper = lambda audio: InlineQueryResultArticle(
                        id=uuid4(),
                        thumb_url=audio.get('cover_url_small') or audio.get('cover'),
                        hide_url=True,
                        url=audio['download'],
                        title=audio["title"],
                        description="Artist: {}\n{}".format(audio['artist'], albumOrDuration(audio)),
                        audio_duration=audio["duration"],
                        input_message_content=InputTextMessageContent(audio['download'])
                )
    return list(map(articleMapper if linksMode else audiosMapper, audios[:50]))

def onCaptchaLock(error, query):
    global captchaLocked, captchaLockParams
    captchaLockParams.update(error)
    if not captchaLocked:
        captchaLockParams.update({'q': query})
    captchaLocked = True

def replyCaptchaInline(query, bot, update):
    if captchaLocked and captchaLockParams:
        input_message = InputTextMessageContent(f"youtube.com/results?search_query={query}")
        results = [InlineQueryResultPhoto(
                        id=uuid4(),
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

def search(query, linksMode, bot, update):
    global captchaLocked, captchaLockParams
    if len(query.strip()) < 1:
        query = text.get_random_artist()

    payload = {'q': query};

    if captchaLocked:
        payload.update(captchaLockParams)
        payload.update({'captcha_key': query})

    result = requests.get(DATMUSIC_API_ENDPOINT, params=payload, headers=DEFAULT_HEADERS);
    try:
        response = result.json();
        if response['status'] == 'ok':
            response = response["data"];
            captchaLocked = False
            captchaLockParams = {}
            replyAudioSearchResults(response, query, linksMode, bot, update)
        else:
            error = response['error']
            
            if error and 'captcha_id' in error:
                onCaptchaLock(error, query)
                replyCaptchaInline(query, bot, update)
    except ValueError as e:
        println("Failed to parse result:")
        print(e)

def logError(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def add_update_handlers(dp):
    dp.add_handler(CommandHandler("start", text.start))
    dp.add_handler(CommandHandler("about", text.about))

    dp.add_handler(InlineQueryHandler(handleInlineQuery))
    return dp

def main():
    token = os.getenv("DATMUSIC_BOT_TOKEN")
    if not token:
        logging.critical('NO TOKEN FOUND!')
        sys.exit()

    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    add_update_handlers(dp)

    # log all errors
    dp.add_error_handler(logError)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()