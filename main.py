#!/bin/python

from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from functools import partial
from src.handler import handler
from src.db_client import db_client
from src.config import config
import logging
import sys

def validate_args():
    conf = config()

    print_usage = False
    is_config = False
    for i in range(0, len(sys.argv)):
        if sys.argv[i] == "COLD":
            conf.mode = "COLD"
        elif sys.argv[i] == "-c":
            is_config = True
        elif is_config:
            conf = config(sys.argv[i])
            is_config = False
        elif i != 0:
            print("Invalid arguments")
            print_usage = True

    if print_usage:
        print("Usage: %s [COLD]" % print_usage)

    return conf


if __name__ == '__main__':
    conf = validate_args()

    # Set up logger
    if len(conf.log_file) > 0:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            filename=conf.log_file)
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger = logging.getLogger()
    logger.info("Process is started")

    # Set up db client
    database_client = db_client(logger, conf)
    if not database_client.init():
        logger.warn('Database is failed to initialise')

    # Set up handler
    msg_handler = handler(logger, conf)
    msg_handler.init_db(database_client)

    # Set up telegram bot
    updater = Updater(conf.api_token)
    updater.dispatcher.add_handler(CommandHandler('start', msg_handler.start_handler))
    updater.dispatcher.add_handler(CommandHandler(handler.query_handler_name(), msg_handler.query_handler))
    updater.dispatcher.add_handler(CommandHandler(handler.response_handler_name(), msg_handler.response_handler))
    updater.dispatcher.add_handler(CommandHandler(handler.help_handler_name(), msg_handler.help_handler))
    updater.dispatcher.add_handler(CommandHandler(handler.yes_handler_name(), msg_handler.yes_handler))
    updater.dispatcher.add_handler(CommandHandler(handler.no_handler_name(), msg_handler.no_handler))
    updater.dispatcher.add_handler(CommandHandler(handler.back_handler_name(), msg_handler.no_handler))
    updater.dispatcher.add_handler(CommandHandler(handler.match_handler_name(), msg_handler.match_handler))
    updater.dispatcher.add_handler(CommandHandler(handler.unmatch_handler_name(), msg_handler.unmatch_handler))
    updater.dispatcher.add_handler(MessageHandler([Filters.text], msg_handler.set_value_handler))

    logger.info("Polling is started")
    updater.start_polling()
    updater.idle()
