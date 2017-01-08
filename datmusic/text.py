# -*- coding: utf-8 -*-

from constants import __version__

import logging
import re
import random

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

# derived from https://github.com/alashow/music/blob/master/js/app.js#L213
artists = ["2 Cellos", "Agnes Obel", "Aloe Black", "Andrew Belle", "Angus Stone", "Aquilo", "Arctic Monkeys",
           "Avicii", "Balmorhea", "Barcelona", "Bastille", "Ben Howard", "Benj Heard", "Birdy", "Broods",
           "Calvin Harris", "Charlotte OC", "City of The Sun", "Civil Twilight", "Clint Mansell", "Coldplay",
           "Daft Punk", "Damien Rice", "Daniela Andrade", "Daughter", "David O'Dowda", "Dawn Golden", "Dirk Maassen",
           "Ed Sheeran", "Eminem", "Fabrizio Paterlini", "Fink", "Fleurie", "Florence and The Machine", "Gem club",
           "Glass Animals", "Greg Haines", "Greg Maroney", "Groen Land", "Halsey", "Hans Zimmer", "Hozier",
           "Imagine Dragons", "Ingrid Michaelson", "Jamie XX", "Jarryd James", "Jasmin Thompson", "Jaymes Young",
           "Jessie J", "Josef Salvat", "Julia Kent", "Kai Engel", "Keaton Henson", "Kendra Logozar", "Kina Grannis",
           "Kodaline", "Kygo", "Kyle Landry", "Lana Del Rey", "Lera Lynn", "Lights & Motion", "Linus Young", "Lo-Fang",
           "Lorde", "Ludovico Einaudi", "M83", "MONO", "MS MR", "Macklemore", "Mammals", "Maroon 5", "Martin Garrix",
           "Mattia Cupelli", "Max Richter", "Message To Bears", "Mogwai", "Mumford & Sons", "Nils Frahm", "ODESZA", "Oasis",
           "Of Monsters and Men", "Oh Wonder", "Philip Glass", "Phoebe Ryan", "Rachel Grimes", "Radiohead", "Ryan Keen",
           "Sam Smith", "Seinabo Sey", "Sia", "Takahiro Kido", "The Irrepressibles", "The Neighbourhood", "The xx",
           "VLNY", "Wye Oak", "X ambassadors", "Yann Tiersen", "Yiruma", "Young Summer", "Zack Hemsey", "Zinovia",
           "deadmau5", "pg.lost", "Ólafur Arnalds"]

def start(bot, update):
    update.message.reply_text(START_TEXT.format(bot_name=bot.name))

def about(bot, update):
    update.message.reply_text(ABOUT_TEXT.format(bot_name=bot.name, version=__version__),
                     parse_mode=ParseMode.HTML)

def get_random_artist():
	return random.choice(artists)