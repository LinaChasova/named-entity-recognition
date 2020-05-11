import sys
sys.path.append('/usr/local/lib/python3.7/site-packages')

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import requests
import re
from constants import TOKEN, REQUEST_KWARGS, HELLO_MESSAGE, WRONG_LANG_MESSAGE
from search import search
from model import Event_tagger

from langdetect import detect

import warnings
from telegram.vendor.ptb_urllib3.urllib3.exceptions import InsecureRequestWarning
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
warnings.simplefilter('ignore', InsecureRequestWarning)


def start_callback(update, context):
    print('--- start callback chat id {} ---'.format(update.message.chat_id))
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=HELLO_MESSAGE)
    
def get_news_callback(update, context):
    print('--- search callback started ---')
    text = update.message.text 
    if not text.isnumeric() and detect(text) == 'en':
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=WRONG_LANG_MESSAGE)
    else:
        messages = search(text)
        for message in messages:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=message, parse_mode=telegram.ParseMode.HTML)

def main():
    print('--- bot started ---')
    updater = Updater(TOKEN, use_context=True, request_kwargs=REQUEST_KWARGS)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start_callback))
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), get_news_callback))
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()



