#!/bin/python

import unittest
import os
import time
from src.handler import handler
from src.config import config
from src.db_client import db_client
from src.screen_messages import screen_messages


class logger_test():
    """
    Logger class for unit test
    """
    def __init__(self):
        pass
    def info(self, text):
        pass
    def warn(self, text):
        pass


class update_test():
    """
    Update class for unit test
    """
    class message_test():

        class from_user_test():
            def __init__(self, first_name=''):
                self.first_name = first_name

        class contact_test():
            def __init__(self, phone_number='', first_name='', last_name=''):
                self.phone_number = phone_number
                self.first_name = first_name
                self.last_name = last_name

        def __init__(self, chat_id='', text='', first_name='', last_name='', phone_number=''):
            self.chat_id = chat_id
            self.text = text
            self.from_user = update_test.message_test.from_user_test(first_name=first_name)
            self.contact = update_test.message_test.contact_test(phone_number=phone_number,
                                                                 first_name=first_name,
                                                                 last_name=last_name)

    def __init__(self, chat_id='', text='', first_name='', last_name='', phone_number=''):
        self.message = update_test.message_test(chat_id, text, first_name=first_name, \
                                                phone_number=phone_number, last_name=last_name)


class bot_test():
    """
    Bot class for unit test
    """
    def __init__(self):
        self.msg_map = {}
    def sendMessage(self, chat_id, text, parse_mode=None, disable_web_page_preview=None, **kwargs):
        if chat_id in self.msg_map.keys():
            self.msg_map[chat_id].append(text)
        else:
            self.msg_map[chat_id] = [text]

    def clear_msg_map(self):
        self.msg_map.clear()


class handler_test(unittest.TestCase):
    conf = config(os.path.abspath(__file__ + "/../../test/handler_test_config.yaml"), mode='COLD')
    logger = logger_test()
    db = db_client(logger, conf)
    db_is_init = False

    @classmethod
    def setUpClass(cls):
        handler_test.db.init()
        handler_test.db_is_init = True

        cls.hd = handler(handler_test.logger, handler_test.conf)
        cls.hd.init_db(cls.db)

        cls.my_chat_id = 12345678
        cls.my_first_name = 'David'
        cls.my_last_name = 'Jones'
        cls.my_phone_number = '85291111111'

        cls.his_chat_id = 87654321
        cls.his_first_name = 'Ken'
        cls.his_last_name = 'Johnson'
        cls.his_phone_number = '85297777777'

    @classmethod
    def tearDownClass(cls):
        # Close the connection
        handler_test.db.close()

        # Remove the file
        os.remove(handler_test.db.db_file)

    def check_start(self, bot, update):
        self.hd.start_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], \
                         screen_messages.welcome(update.message.from_user.first_name))
        bot.clear_msg_map()

    def check_query(self, bot, update, query):
        update.message.text = "/" + self.hd.query_handler_name()
        self.hd.query_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], screen_messages.ask_query())
        bot.clear_msg_map()

        # Send query question
        update.message.text = query
        self.hd.set_value_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], screen_messages.ask_confirming_query(query))
        bot.clear_msg_map()

        # Send yes to confirm the query
        update.message.text = "/" + handler.yes_handler_name()
        self.hd.yes_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], screen_messages.confirm_send_query(self.hd.source_id, query))
        self.assertEqual(bot.msg_map[update.message.chat_id][1], screen_messages.welcome(update.message.from_user.first_name))
        self.assertEqual(bot.msg_map[handler_test.conf.channel_name][0].split('\n')[1], "Source ID: %d" % self.hd.source_id)
        self.assertEqual(bot.msg_map[handler_test.conf.channel_name][0].split('\n')[2], "Query: " + query)
        bot.clear_msg_map()

    def check_response(self, bot, update, opp_update, target_id, response):
        update.message.text = "/" + self.hd.response_handler_name()
        self.hd.response_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], screen_messages.ask_target_id())
        bot.clear_msg_map()

        # Response target id
        update.message.text = "%s" % target_id
        self.hd.set_value_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], screen_messages.ask_response())
        bot.clear_msg_map()

        # Response message
        update.message.text = response
        self.hd.set_value_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], screen_messages.ask_confirming_response(target_id, response))
        bot.clear_msg_map()

        # Confirm response message
        update.message_test = "/" + self.hd.yes_handler_name()
        self.hd.yes_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], screen_messages.confirm_send_response_to_target(target_id))
        self.assertEqual(bot.msg_map[update.message.chat_id][1], screen_messages.welcome(self.his_first_name))
        self.assertEqual(bot.msg_map[opp_update.message.chat_id][0].split("\n")[1], "Source ID: %d" % self.hd.source_id)
        self.assertEqual(bot.msg_map[opp_update.message.chat_id][0].split("\n")[2], "Response: %s" % response)
        bot.clear_msg_map()

    def test_start(self):
        # Initialize db and hd
        bot = bot_test()
        update = update_test(chat_id=self.my_chat_id, text="/start", first_name=self.my_first_name)
        self.check_start(bot, update)

    def test_query_cancel(self):
        # Initialize db and hd
        bot = bot_test()
        query = "Where can I find something?"

        # Start first
        update = update_test(chat_id=self.my_chat_id, text="/start", first_name=self.my_first_name)
        self.check_start(bot, update)

        # Send /Query
        update.message.text = "/" + self.hd.query_handler_name()
        self.hd.query_handler(bot, update)
        self.assertEqual(bot.msg_map[self.my_chat_id][0], screen_messages.ask_query())
        bot.clear_msg_map()

        # Send /No
        update.message.text = "/" + self.hd.no_handler_name()
        self.hd.no_handler(bot, update)
        self.assertEqual(bot.msg_map[self.my_chat_id][0], screen_messages.cancel_action())
        self.assertEqual(bot.msg_map[self.my_chat_id][1], screen_messages.welcome(self.my_first_name))
        bot.clear_msg_map()

        # Send /Query again
        update.message.text = "/" + self.hd.query_handler_name()
        self.hd.query_handler(bot, update)
        self.assertEqual(bot.msg_map[self.my_chat_id][0], screen_messages.ask_query())
        bot.clear_msg_map()

        # Send query question
        update.message.text = query
        self.hd.set_value_handler(bot, update)
        self.assertEqual(bot.msg_map[self.my_chat_id][0], screen_messages.ask_confirming_query(query))
        bot.clear_msg_map()

        # Send /No
        update.message.text = "/" + self.hd.no_handler_name()
        self.hd.no_handler(bot, update)
        self.assertEqual(bot.msg_map[self.my_chat_id][0], screen_messages.cancel_action())
        self.assertEqual(bot.msg_map[self.my_chat_id][1], screen_messages.welcome(self.my_first_name))
        bot.clear_msg_map()

    def test_query(self):
        # Initialize db and hd
        bot = bot_test()
        query = "Where can I find something?"

        # Start first
        update = update_test(chat_id=self.my_chat_id, text="/start", first_name=self.my_first_name)
        self.check_start(bot, update)

        # Send /Query
        self.check_query(bot, update, query)

    def test_response_cancel(self):
        # Initialize db and hd
        bot = bot_test()
        query = "Where can I find something?"
        response = "Nowhere."

        # Start first
        update = update_test(chat_id=self.my_chat_id, text="/start", first_name=self.my_first_name)
        self.check_start(bot, update)

        # Send /Query
        self.check_query(bot, update, query)

        # Store my target id
        target_id = self.hd.source_id

        # Start another user
        update = update_test(chat_id=self.his_chat_id, text="/start", first_name=self.his_first_name)
        self.check_start(bot, update)

        # Response
        update.message.text = "/" + self.hd.response_handler_name()
        self.hd.response_handler(bot, update)
        self.assertEqual(bot.msg_map[self.his_chat_id][0], screen_messages.ask_target_id())
        bot.clear_msg_map()

        # Cancel response
        update.message.text = "/" + self.hd.no_handler_name()
        self.hd.no_handler(bot, update)
        self.assertEqual(bot.msg_map[self.his_chat_id][0], screen_messages.cancel_action())
        self.assertEqual(bot.msg_map[self.his_chat_id][1], screen_messages.welcome(self.his_first_name))
        bot.clear_msg_map()

        # Response again
        update.message.text = "/" + self.hd.response_handler_name()
        self.hd.response_handler(bot, update)
        self.assertEqual(bot.msg_map[self.his_chat_id][0], screen_messages.ask_target_id())
        bot.clear_msg_map()

        # Response target id
        update.message.text = "%s" % target_id
        self.hd.set_value_handler(bot, update)
        self.assertEqual(bot.msg_map[self.his_chat_id][0], screen_messages.ask_response())
        bot.clear_msg_map()

        # No again
        update.message.text = "/" + self.hd.no_handler_name()
        self.hd.no_handler(bot, update)
        self.assertEqual(bot.msg_map[self.his_chat_id][0], screen_messages.cancel_action())
        self.assertEqual(bot.msg_map[self.his_chat_id][1], screen_messages.welcome(self.his_first_name))
        bot.clear_msg_map()

        # Response again
        update.message.text = "/" + self.hd.response_handler_name()
        self.hd.response_handler(bot, update)
        self.assertEqual(bot.msg_map[self.his_chat_id][0], screen_messages.ask_target_id())
        bot.clear_msg_map()

        # Response target id
        update.message.text = "%s" % target_id
        self.hd.set_value_handler(bot, update)
        self.assertEqual(bot.msg_map[self.his_chat_id][0], screen_messages.ask_response())
        bot.clear_msg_map()

        # Response message
        update.message.text = response
        self.hd.set_value_handler(bot, update)
        self.assertEqual(bot.msg_map[self.his_chat_id][0], screen_messages.ask_confirming_response(target_id, response))
        bot.clear_msg_map()

        # No again
        update.message.text = "/" + self.hd.no_handler_name()
        self.hd.no_handler(bot, update)
        self.assertEqual(bot.msg_map[self.his_chat_id][0], screen_messages.cancel_action())
        self.assertEqual(bot.msg_map[self.his_chat_id][1], screen_messages.welcome(self.his_first_name))
        bot.clear_msg_map()

    def test_response(self):
        # Initialize db and hd
        bot = bot_test()
        query = "Where can I find something?"
        response = "Nowhere."

        # Start first
        update = update_test(chat_id=self.my_chat_id, text="/start", first_name=self.my_first_name)
        self.check_start(bot, update)

        # Send /Query
        self.check_query(bot, update, query)

        # Store my source id
        target_id = self.hd.source_id

        # Start another user
        update_opp = update_test(chat_id=self.his_chat_id, text="/start", first_name=self.his_first_name)
        self.check_start(bot, update_opp)

        # Response
        self.check_response(bot, update_opp, update, target_id, response)

    def test_match(self):
        # Initialize db and hd
        bot = bot_test()
        query = "Where can I find something?"
        response = "Nowhere."

        # Start first
        update = update_test(chat_id=self.my_chat_id, text="/start", first_name=self.my_first_name,
                             last_name=self.my_last_name, phone_number=self.my_phone_number)
        self.check_start(bot, update)

        # Send /Query
        self.check_query(bot, update, query)

        # Store my source id
        my_source_id = self.hd.source_id

        # Start another user
        update_opp = update_test(chat_id=self.his_chat_id, text="/start", first_name=self.his_first_name,
                                 last_name=self.his_last_name, phone_number=self.his_phone_number)
        self.check_start(bot, update_opp)

        # Response
        self.check_response(bot, update_opp, update, my_source_id, response)

        # Store his source id
        his_source_id = self.hd.source_id

        # I match
        update.message.text = "/" + self.hd.match_handler_name()
        self.hd.match_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], screen_messages.ask_target_id())
        bot.clear_msg_map()

        # Match id
        update.message.text = his_source_id
        self.hd.set_value_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], screen_messages.ask_confirming_match(his_source_id))
        bot.clear_msg_map()

        # Match confirm
        update.message.text = "/" + self.hd.yes_handler_name()
        self.hd.yes_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], screen_messages.confirm_match(his_source_id))
        self.assertEqual(bot.msg_map[update.message.chat_id][1], screen_messages.match_and_wait_counterparty(his_source_id))
        self.assertEqual(bot.msg_map[update.message.chat_id][2], screen_messages.welcome(update.message.from_user.first_name))
        bot.clear_msg_map()

if __name__ == '__main__':
    unittest.main()

