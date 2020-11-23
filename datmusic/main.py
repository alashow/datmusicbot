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

from telegram import InlineQueryResultAudio, InlineQueryResultGif, InputTextMessageContent, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import logging

import settings
import text
from constants import DATMUSIC_API_ENDPOINT
from constants import INLINE_QUERY_CACHE_TIME
from constants import DEFAULT_HEADERS

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def inlinequery(bot, update):
    query = update.inline_query.query
    results = list()

    cache_time = INLINE_QUERY_CACHE_TIME
    audios = search(query); 
    print(f"Found {len(audios)} results for query '{query}'")
    try:
        if not audios:
            cache_time = 300
            results.append(InlineQueryResultGif(id=uuid4(),
                                           gif_url='https://media.giphy.com/media/sS8YbjrTzu4KI/giphy.gif',
                                           thumb_url='https://media.giphy.com/media/sS8YbjrTzu4KI/giphy.gif',
                                            title="Failed You",
                                            input_message_content=InputTextMessageContent(f"youtube.com/results?search_query={query}")))
        else:
            # trim result to 50, which is max result count for inline query answer
            for audio in audios[:50]:
                results.append(
                    InlineQueryResultAudio(
                        id=uuid4(),
                        audio_url=audio['download'],
                        title=audio["title"],
                        performer=audio["artist"],
                        audio_duration=audio["duration"]
                    )
                )
        update.inline_query.answer(results=results, cache_time=cache_time)
    except Exception as e:
        error(bot, update, e)

def search(query):
    if len(query.strip()) < 1:
        query = text.get_random_artist()

    logger.info("Search query is '%s'" % query)

    payload = {'q': query};
    result = requests.get(DATMUSIC_API_ENDPOINT, params=payload, headers=DEFAULT_HEADERS);
    
    try:
        response = result.json()["data"];
    except:
        print(f"Failed to parse response: {result.json()}") 
    
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