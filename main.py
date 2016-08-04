#!/bin/python

from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from src.handler import handler
from src.db_client import db_client
from src.config import config
from src.user_interface import user_interface
import logging
import sys


def usage(error=''):
    ret = ""

    if error != '':
        ret += error + "\n"

    ret += "Usage: main.py -c <config_file> -i <interface_file> [-m COLD]\n"
    ret += "Arguments:\n"
    ret += "    -c      Configuration file path.\n"
    ret += "    -i      Interface file path.\n"
    ret += "    -m      Cold start mode. Run it in the first time.\n"

    return ret


def validate_args():
    if len(sys.argv) % 2 == 0:
        print(usage("Invalid number of arguments"))
        exit(1)

    conf_path = ''
    ui_path = ''
    mode = 'NORMAL'

    for i in range(1, len(sys.argv)-1, 2):
        arg_item = sys.argv[i]
        arg_val = sys.argv[i+1]

        if arg_item == "-c":
            conf_path = arg_val
        elif arg_item == "-i":
            ui_path = arg_val
        elif arg_item == "-m":
            if arg_val == "COLD":
                mode = arg_val
            else:
                print(usage("Currently only supports cold start mode."))
                exit(1)

    conf = config(conf_path, mode=mode)
    ui = user_interface(conf.platform, conf.channel_name, ui_path)

    return conf, ui

if __name__ == '__main__':
    conf, ui = validate_args()

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
    msg_handler = handler(logger, conf, ui)
    msg_handler.init_db(database_client)

    # Set up telegram bot
    updater = Updater(conf.api_token)
    updater.dispatcher.add_handler(CommandHandler('start', msg_handler.start_handler))
    updater.dispatcher.add_handler(CommandHandler(msg_handler.ui.query_key_name(False), msg_handler.query_handler))
    updater.dispatcher.add_handler(CommandHandler(msg_handler.ui.response_key_name(False), msg_handler.response_handler))
    updater.dispatcher.add_handler(CommandHandler(msg_handler.ui.help_key_name(False), msg_handler.help_handler))
    updater.dispatcher.add_handler(CommandHandler(msg_handler.ui.yes_key_name(False), msg_handler.yes_handler))
    updater.dispatcher.add_handler(CommandHandler(msg_handler.ui.no_key_name(False), msg_handler.no_handler))
    updater.dispatcher.add_handler(CommandHandler(msg_handler.ui.back_key_name(False), msg_handler.no_handler))
    updater.dispatcher.add_handler(CommandHandler(msg_handler.ui.match_key_name(False), msg_handler.match_handler))
    updater.dispatcher.add_handler(CommandHandler(msg_handler.ui.unmatch_key_name(False), msg_handler.unmatch_handler))
    updater.dispatcher.add_handler(MessageHandler([Filters.text], msg_handler.set_value_handler))
    updater.dispatcher.add_handler(MessageHandler([Filters.contact], msg_handler.yes_handler))

    logger.info("Polling is started")
    updater.start_polling()
    updater.idle()
