#!/bin/python

from telegram.ext import Updater, CommandHandler
from functools import partial
from src.handler import handler
from src.db_client import db_client
import logging

api_token = '234912431:AAFHuswajr72Bq9Ub4DncfGH5NonkOZrWe8'

if __name__ == '__main__':
    # Set up logger
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    logger.info("Process is started")

    # Set up db client
    database_client = db_client(logger)
    if not database_client.init():
        logger.warn('Database is failed to initialise')

    # Set up handler
    msg_handler = handler(logger)
    msg_handler.init_db(database_client)

    # Set up telegram bot
    updater = Updater(api_token)
    updater.dispatcher.add_handler(CommandHandler('start', partial(msg_handler.start_handler, logger)))
    updater.dispatcher.add_handler(CommandHandler(handler.query_handler_name(), partial(msg_handler.query_handler, logger)))
    updater.dispatcher.add_handler(CommandHandler(handler.response_handler_name(), partial(msg_handler.response_handler, logger)))
    updater.dispatcher.add_handler(CommandHandler(handler.help_handler_name(), partial(msg_handler.help_handler, logger)))

    logger.info("Polling is started")
    updater.start_polling()
    updater.idle()
