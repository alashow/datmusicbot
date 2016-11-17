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

from telegram import InlineQueryResultAudio, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import logging

import util
import settings
import text
from constants import DATMUSIC_API_ENDPOINT
from constants import INLINE_QUERY_CACHE_TIME

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def inlinequery(bot, update):
    query = update.inline_query.query
    results = list()

    audios = search(query);
    try:
        if audios:
            for audio in audios:
                audio_url = util.generateAudioUrl(audio["owner_id"], audio["aid"])
                results.append(
                    InlineQueryResultAudio(
                        id=uuid4(),
                        audio_url=audio_url,
                        title=text.decodeArtistTitle(audio["artist"]),
                        performer=text.decodeArtistTitle(audio["title"]),
                        audio_duration=audio["duration"],
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton(
                                text="Direct Link",
                                url=audio_url
                                )
                            ]])
                    )
                )
            bot.answerInlineQuery(update.inline_query.id, results=results, cache_time=INLINE_QUERY_CACHE_TIME)
    except Exception, e:
        error(bot, update, e)

def search(query):
    if len(query.strip()) < 1:
        query = text.get_random_artist()

    logger.info("Search query is '%s'" % query)

    payload = {'auto_complete': 1, 'sort': 2, 'count': 50, 'q': query};
    result = requests.get(DATMUSIC_API_ENDPOINT, params = payload);
    
    response = result.json()["response"];

    # remove count from response
    del response[0];
    
    return response;

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def add_update_handlers(dp):
    dp.add_handler(CommandHandler("start", text.start))
    dp.add_handler(CommandHandler("about", text.about))

    dp.add_handler(InlineQueryHandler(inlinequery))
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
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()