from constants import __version__

import logging
import re

from telegram import ParseMode
from telegram.ext import ConversationHandler

START_TEXT = """
Usage: search music by typing {bot_name} in a chat.

/about - to see about page

Subscribe to news: https://telegram.me/datmusicnews
"""

ABOUT_TEXT = """<b>{bot_name} version {version}</b>
Created by @alashow
Source code is available at <a href="https://github.com/alashow/datmusicbot">github</a>."""

def start(bot, update):
    bot.send_message(chat_id=update.message.chat.id, text=START_TEXT.format(bot_name=bot.name))

def about(bot, update):
    bot.send_message(chat_id=update.message.chat.id, text=ABOUT_TEXT.format(bot_name=bot.name, version=__version__),
                     parse_mode=ParseMode.HTML)