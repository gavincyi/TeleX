#!/bin/python

import unittest
import os
from src.handler import handler
from src.config import config
from src.db_client import db_client
from src.user_interface import user_interface


class logger_test():
    """
    Logger class for unit test
    """
    def __init__(self):
        pass
    def info(self, text):
        print(text)
    def warn(self, text):
        print(text)
    def debug(self, text):
        print(text)


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
    @staticmethod
    def contact_str(phone_number='', first_name='', last_name=''):
        return "Contact received. PhoneNum=%s, Firstname=%s, Lastname=%s" \
               % (phone_number, first_name, last_name)
    
    def __init__(self):
        self.msg_map = {}
    def sendMessage(self, chat_id, text, parse_mode=None, disable_web_page_preview=None, **kwargs):
        if chat_id in self.msg_map.keys():
            self.msg_map[chat_id].append(text)
        else:
            self.msg_map[chat_id] = [text]
            
    def sendContact(self, chat_id=0, phone_number='', first_name='', last_name=''):
        text = bot_test.contact_str(phone_number, first_name, last_name)
        if chat_id in self.msg_map.keys():
            self.msg_map[chat_id].append(text)
        else:
            self.msg_map[chat_id] = [text]        

    def clear_msg_map(self):
        self.msg_map.clear()


class fail_reason():
    UNDEFINED = 0
    INVALID_TARGET_ID = 1
    INACTIVATED_TARGET_ID = 2
    REPEATED_ACTION = 3

class handler_test(unittest.TestCase):
    conf = config(os.path.abspath(__file__ + "/../../test/handler_test_config.yaml"), mode='COLD')
    ui = user_interface(conf.platform, 
                        conf.channel_name, 
                        os.path.abspath(__file__ + "/../../test/user_interface_test.yaml"))
    logger = logger_test()
    db = db_client(logger, conf)
    db_is_init = False

    @classmethod
    def setUpClass(cls):
        handler_test.db.init()
        handler_test.db_is_init = True

        cls.hd = handler(handler_test.logger, handler_test.conf, handler_test.ui)
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
                         self.hd.ui.welcome(update))
        bot.clear_msg_map()

    def check_query_action(self, bot, update):
        self.hd.query_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], self.hd.ui.ask_query(update))
        bot.clear_msg_map()        

    def check_query_question(self, bot, update, query):
        self.hd.set_value_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], self.hd.ui.ask_confirm_query(update, query))
        bot.clear_msg_map()    
        
    def check_query_confirm(self, bot, update, query):
        self.hd.yes_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], self.hd.ui.confirm_query(update, self.hd.source_id, query))
        self.assertEqual(bot.msg_map[update.message.chat_id][1], self.hd.ui.welcome(update))
        self.assertEqual(bot.msg_map[handler_test.conf.channel_name][0].split('\n')[1].split("=")[0].strip(), "Source ID")
        self.assertEqual(bot.msg_map[handler_test.conf.channel_name][0].split('\n')[1].split("=")[1].strip(), str(self.hd.source_id))
        self.assertEqual(bot.msg_map[handler_test.conf.channel_name][0].split('\n')[2].split("=")[0].strip(), "Query")
        self.assertEqual(bot.msg_map[handler_test.conf.channel_name][0].split('\n')[2].split("=")[1].strip(), query)
        bot.clear_msg_map()        
        
    def check_response_action(self, bot, update):      
        self.hd.response_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], self.hd.ui.ask_target_id(update))
        bot.clear_msg_map()        
        
    def check_response_target_id(self, bot, update):
        self.hd.set_value_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], self.hd.ui.ask_response(update))
        bot.clear_msg_map()    
        
    def check_response_message(self, bot, update, target_id):
        self.hd.set_value_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], \
                         self.hd.ui.ask_confirm_response(update, target_id, update.message.text))
        bot.clear_msg_map()    
        
    def check_response_confirm(self, bot, update, opp_update, target_id, response):
        self.hd.yes_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], self.hd.ui.confirm_response(update, target_id, response))
        self.assertEqual(bot.msg_map[update.message.chat_id][1], self.hd.ui.welcome(update))
        self.assertEqual(bot.msg_map[opp_update.message.chat_id][0].split('\n')[1].split("=")[0].strip(), "Source ID")
        self.assertEqual(bot.msg_map[opp_update.message.chat_id][0].split('\n')[1].split("=")[1].strip(), str(self.hd.source_id))        
        self.assertEqual(bot.msg_map[opp_update.message.chat_id][0].split('\n')[2].split("=")[0].strip(), "Response")
        self.assertEqual(bot.msg_map[opp_update.message.chat_id][0].split('\n')[2].split("=")[1].strip(), response)        
        bot.clear_msg_map()    
        
    def check_target_id_decline(self, bot, update, target_id):
        self.hd.yes_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], self.hd.ui.invalid_target_id(update, target_id))
        self.assertEqual(bot.msg_map[update.message.chat_id][1], self.hd.ui.cancel(update))
        self.assertEqual(bot.msg_map[update.message.chat_id][2], self.hd.ui.welcome(update))
        bot.clear_msg_map()          
        
    def check_match_action(self, bot, update):
        self.hd.match_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], self.hd.ui.ask_target_id(update))
        bot.clear_msg_map()        
        
    def check_match_target_id(self, bot, update):
        self.hd.set_value_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], self.hd.ui.ask_confirm_match(update, update.message.text))
        bot.clear_msg_map()
        
    def check_match_one_side(self, bot, update, target_id):
        self.hd.yes_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], self.hd.ui.confirm_match(update, target_id))
        self.assertEqual(bot.msg_map[update.message.chat_id][1], self.hd.ui.match_and_wait(update, target_id))
        self.assertEqual(bot.msg_map[update.message.chat_id][2], self.hd.ui.welcome(update))
        bot.clear_msg_map()       
    
    def check_match_two_side(self, bot, update, opp_update, target_id, source_id):
        self.hd.yes_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], self.hd.ui.confirm_match(update, target_id))
        self.assertEqual(bot.msg_map[update.message.chat_id][1], self.hd.ui.match_and_exchange(update, target_id))
        self.assertEqual(bot.msg_map[update.message.chat_id][2], \
                         bot_test.contact_str(phone_number=opp_update.message.contact.phone_number,
                                              first_name=opp_update.message.contact.first_name,
                                              last_name=opp_update.message.contact.last_name))
        self.assertEqual(bot.msg_map[update.message.chat_id][3], self.hd.ui.welcome(update))
        self.assertEqual(bot.msg_map[opp_update.message.chat_id][0], self.hd.ui.match_and_exchange(update, source_id))
        self.assertEqual(bot.msg_map[opp_update.message.chat_id][1], \
                         bot_test.contact_str(phone_number=update.message.contact.phone_number,
                                              first_name=update.message.contact.first_name,
                                              last_name=update.message.contact.last_name))
        bot.clear_msg_map()

    def check_match_repeated_decline(self, bot, update, target_id):
        self.hd.yes_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], self.hd.ui.reject_multiply_match(update, target_id))
        self.assertEqual(bot.msg_map[update.message.chat_id][1], self.hd.ui.cancel(update))
        self.assertEqual(bot.msg_map[update.message.chat_id][2], self.hd.ui.welcome(update))
        bot.clear_msg_map()

    def check_unmatch_action(self, bot, update):
        self.hd.unmatch_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], self.hd.ui.ask_target_id(update))
        bot.clear_msg_map()

    def check_unmatch_target_id(self, bot, update):
        self.hd.set_value_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0],\
                         self.hd.ui.ask_confirm_unmatch(update, int(update.message.text)))
        bot.clear_msg_map()

    def check_unmatch_confirm(self, bot, update, target_id):
        self.hd.yes_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0],\
                         self.hd.ui.confirm_unmatch(update, target_id))
        bot.clear_msg_map()

    def check_unmatch_repeated_decline(self, bot, update, target_id):
        self.hd.yes_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], self.hd.ui.reject_multiply_unmatch(update, target_id))
        self.assertEqual(bot.msg_map[update.message.chat_id][1], self.hd.ui.cancel(update))
        self.assertEqual(bot.msg_map[update.message.chat_id][2], self.hd.ui.welcome(update))
        bot.clear_msg_map()

    def check_invalid_target_id(self, bot, update, target_id):
        self.hd.set_value_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], self.hd.ui.invalid_target_id(update, target_id))
        self.assertEqual(bot.msg_map[update.message.chat_id][1], self.hd.ui.cancel(update))
        self.assertEqual(bot.msg_map[update.message.chat_id][2], self.hd.ui.welcome(update))
        bot.clear_msg_map()

    def check_help_action(self, bot, update):
        self.hd.help_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], self.hd.ui.ask_help(update))
        bot.clear_msg_map()

    def check_help_question(self, bot, update, msg):
        self.hd.set_value_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], self.hd.ui.ask_confirm_help(update, msg))
        bot.clear_msg_map()

    def check_help_confirm(self, bot, update, msg):
        self.hd.yes_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], self.hd.ui.confirm_help(update, self.hd.source_id, msg))
        self.assertEqual(bot.msg_map[update.message.chat_id][1], self.hd.ui.welcome(update))
        self.assertEqual(bot.msg_map[handler_test.conf.help_channel_name][0].split('\n')[1].split("=")[0].strip(), "Channel")
        self.assertEqual(bot.msg_map[handler_test.conf.help_channel_name][0].split('\n')[1].split("=")[1].strip(), str(self.hd.channel_name))                
        self.assertEqual(bot.msg_map[handler_test.conf.help_channel_name][0].split('\n')[2].split("=")[0].strip(), "Source ID")
        self.assertEqual(bot.msg_map[handler_test.conf.help_channel_name][0].split('\n')[2].split("=")[1].strip(), str(self.hd.source_id))
        self.assertEqual(bot.msg_map[handler_test.conf.help_channel_name][0].split('\n')[3].split("=")[0].strip(), "Chat ID")
        self.assertEqual(bot.msg_map[handler_test.conf.help_channel_name][0].split('\n')[3].split("=")[1].strip(), str(update.message.chat_id))
        self.assertEqual(bot.msg_map[handler_test.conf.help_channel_name][0].split('\n')[4].split("=")[0].strip(), "Response")
        self.assertEqual(bot.msg_map[handler_test.conf.help_channel_name][0].split('\n')[4].split("=")[1].strip(), msg)                  
        bot.clear_msg_map()

    def check_query(self, bot, update, query):
        self.check_start(bot, update)
        
        # Action query
        update.message.text = self.hd.ui.query_key_name()
        self.check_query_action(bot, update)

        # Send query question
        update.message.text = query
        self.check_query_question(bot, update, query)

        # Send yes to confirm the query
        update.message.text = self.hd.ui.yes_key_name()
        self.check_query_confirm(bot, update, query)

    def check_response(self, bot, update, opp_update, target_id, response):
        self.check_start(bot, update)
        
        # Action response
        update.message.text = self.hd.ui.response_key_name()
        self.check_response_action(bot, update)

        # Response target id
        update.message.text = "%s" % target_id
        self.check_response_target_id(bot, update)

        # Response message
        update.message.text = response
        self.check_response_message(bot, update, target_id)

        # Confirm response message
        update.message_test = self.hd.ui.yes_key_name()
        self.check_response_confirm(bot, update, opp_update, target_id, response)

    def check_match(self, bot, update, target_id, opp_update=None, source_id=None):
        self.check_start(bot, update)

        # Match action
        update.message.text = self.hd.ui.match_key_name()
        self.check_match_action(bot, update)

        # Match id
        update.message.text = target_id
        self.check_match_target_id(bot, update)

        # Match confirm
        update.message.text = self.hd.ui.yes_key_name()
        if not opp_update or not source_id:
            self.check_match_one_side(bot, update, target_id)
        else:
            self.check_match_two_side(bot, update, opp_update, target_id, source_id)

    def check_unmatch(self, bot, update, target_id):
        update.message.text = self.hd.ui.unmatch_key_name()
        self.check_unmatch_action(bot, update)

        update.message.text = str(target_id)
        self.check_unmatch_target_id(bot, update)

        update.message.text = self.hd.ui.yes_key_name()
        self.check_unmatch_confirm(bot, update, target_id)

    def check_help(self, bot, update, msg):
        self.check_start(bot, update)

        # Action query
        update.message.text = self.hd.ui.help_key_name()
        self.check_help_action(bot, update)

        # Send query question
        update.message.text = msg
        self.check_help_question(bot, update, msg)

        # Send yes to confirm the query
        update.message.text = self.hd.ui.yes_key_name()
        self.check_help_confirm(bot, update, msg)

    def check_response_fail(self, bot, update, target_id, response, failure=fail_reason.UNDEFINED):
        self.check_start(bot, update)

        # Action response
        update.message.text = self.hd.ui.response_key_name()
        self.check_response_action(bot, update)

        # Response target id
        update.message.text = "%s" % target_id
        if failure == fail_reason.INVALID_TARGET_ID:
            self.check_invalid_target_id(bot, update, target_id)
        else:
            self.check_response_target_id(bot, update)

            # Response message
            update.message.text = response
            self.check_response_message(bot, update, target_id)

            # Confirm response message
            update.message_test = self.hd.ui.yes_key_name()
            if failure == fail_reason.INACTIVATED_TARGET_ID:
                self.check_target_id_decline(bot, update, target_id)
            else:
                self.assertTrue(0 == "Incorrect failure reason")

    def check_match_fail(self, bot, update, target_id, opp_update=None, source_id=None, failure=fail_reason.UNDEFINED):
        self.check_start(bot, update)

        # Match action
        update.message.text = self.hd.ui.match_key_name()
        self.check_match_action(bot, update)

        # Match id
        try:
            update.message.text = "%d" % target_id
        except:
            update.message.text = "%s" % target_id

        if failure == fail_reason.INVALID_TARGET_ID:
            self.check_invalid_target_id(bot, update, target_id)
        else:
            self.check_match_target_id(bot, update)

            # Match confirm
            update.message.text = self.hd.ui.yes_key_name()

            if failure == fail_reason.INACTIVATED_TARGET_ID:
                self.check_target_id_decline(bot, update, target_id)
            else:
                self.check_match_repeated_decline(bot, update, target_id)

    def check_unmatch_fail(self, bot, update, target_id, opp_update=None, source_id=None, failure=fail_reason.UNDEFINED):
        self.check_start(bot, update)

        # Match action
        update.message.text = self.hd.ui.unmatch_key_name()
        self.check_unmatch_action(bot, update)

        # Match id
        try:
            update.message.text = "%d" % target_id
        except:
            update.message.text = "%s" % target_id

        if failure == fail_reason.INVALID_TARGET_ID:
            self.check_invalid_target_id(bot, update, target_id)
        else:
            self.check_unmatch_target_id(bot, update)

            # Match confirm
            update.message.text = self.hd.ui.yes_key_name()

            if failure == fail_reason.INACTIVATED_TARGET_ID:
                self.check_target_id_decline(bot, update, target_id)
            else:
                self.check_unmatch_repeated_decline(bot, update, target_id)

    def check_match_invalid_id(self, bot, update, target_id):
        self.check_start(bot, update)
        
        # Action response
        update.message.text = self.hd.ui.match_key_name()
        self.check_unmatch_action(bot, update)   
        
        # Response target id
        update.message.text = "%s" % target_id
        self.check_invalid_target_id(bot, update, target_id)    
        
    def check_unmatch_invalid_id(self, bot, update, target_id):            
        self.check_start(bot, update)
        
        # Action response
        update.message.text = self.hd.ui.unmatch_key_name()
        self.check_unmatch_action(bot, update)   
        
        # Response target id
        update.message.text = "%s" % target_id
        self.check_invalid_target_id(bot, update, target_id)        
        
    def check_response_invalid_id(self, bot, update, target_id):            
        self.check_start(bot, update)
        
        # Action response
        update.message.text = self.hd.ui.response_key_name()
        self.check_response_action(bot, update)   
        
        # Response target id
        update.message.text = "%s" % target_id
        self.check_invalid_target_id(bot, update, target_id)

    def check_no(self, bot, update):
        self.hd.no_handler(bot, update)
        self.assertEqual(bot.msg_map[update.message.chat_id][0], self.hd.ui.cancel(update))
        self.assertEqual(bot.msg_map[update.message.chat_id][1], self.hd.ui.welcome(update))
        bot.clear_msg_map()

    def check_complete_conversation(self, bot, update, his_update, query, response):
        self.check_start(bot, update)

        # Send /Query
        self.check_query(bot, update, query)

        # Store my source id
        my_source_id = self.hd.source_id

        # Start another user
        self.check_start(bot, his_update)

        # Response
        self.check_response(bot, his_update, update, my_source_id, response)

        # Store his source id
        his_source_id = self.hd.source_id

        return my_source_id, his_source_id

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
        update.message.text = self.hd.ui.query_key_name()
        self.check_query_action(bot, update)

        # Send /No
        update.message.text = self.hd.ui.no_key_name()
        self.check_no(bot, update)

        # Send /Query again
        update.message.text = self.hd.ui.query_key_name()
        self.check_query_action(bot, update)

        # Send query question
        update.message.text = query
        self.check_query_question(bot, update, query)
        
        # Send /No
        update.message.text = self.hd.ui.no_key_name()
        self.check_no(bot, update)

    def test_query(self):
        # Initialize db and hd
        bot = bot_test()
        query = "Where can I find something?"

        # Start first
        update = update_test(chat_id=self.my_chat_id, text="/start", first_name=self.my_first_name)

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
        his_update = update_test(chat_id=self.his_chat_id, text="/start", first_name=self.his_first_name)
        self.check_start(bot, his_update)

        # Response
        his_update.message.text = self.hd.ui.response_key_name()
        self.check_response_action(bot, his_update)

        # Cancel response
        his_update.message.text = self.hd.ui.no_key_name()
        self.check_no(bot, his_update)

        # Response again
        his_update.message.text = self.hd.ui.response_key_name()
        self.check_response_action(bot, his_update)

        # Response target id
        his_update.message.text = "%s" % target_id
        self.check_response_target_id(bot, his_update)

        # No again
        his_update.message.text = self.hd.ui.no_key_name()
        self.check_no(bot, his_update)

        # Response again
        his_update.message.text = self.hd.ui.response_key_name()
        self.check_response_action(bot, his_update)

        # Response target id
        his_update.message.text = "%s" % target_id
        self.check_response_target_id(bot, his_update)

        # Response message
        his_update.message.text = response
        self.check_response_message(bot, his_update, target_id)

        # No again
        his_update.message.text = self.hd.ui.no_key_name()
        self.check_no(bot, his_update)

    def test_response(self):
        # Initialize db and hd
        bot = bot_test()
        query = "Where can I find something?"
        response = "Nowhere."

        update = update_test(chat_id=self.my_chat_id, text="/start", first_name=self.my_first_name,
                             last_name=self.my_last_name, phone_number=self.my_phone_number)
        his_update = update_test(chat_id=self.his_chat_id, text="/start", first_name=self.his_first_name,
                                 last_name=self.his_last_name, phone_number=self.his_phone_number)
        my_source_id, his_source_id = self.check_complete_conversation(bot, update, his_update, query, response)

    def test_match(self):
        # Initialize db and hd
        bot = bot_test()
        query = "Where can I find something?"
        response = "Nowhere."

        update = update_test(chat_id=self.my_chat_id, text="/start", first_name=self.my_first_name,
                             last_name=self.my_last_name, phone_number=self.my_phone_number)
        his_update = update_test(chat_id=self.his_chat_id, text="/start", first_name=self.his_first_name,
                                 last_name=self.his_last_name, phone_number=self.his_phone_number)
        my_source_id, his_source_id = self.check_complete_conversation(bot, update, his_update, query, response)

        # I match
        self.check_match(bot, update, his_source_id)

        # He matches
        self.check_match(bot, his_update, my_source_id, update, his_source_id)

        # Fail to match again
        self.check_match_fail(bot, update, his_source_id, failure=fail_reason.REPEATED_ACTION)

    def test_help(self):
        # Initialize db and hd
        bot = bot_test()
        message = "Come on. There are some bugs."

        # Start first
        update = update_test(chat_id=self.my_chat_id, text="/start", first_name=self.my_first_name)

        # Send /Query
        self.check_help(bot, update, message)

    def test_unmatch_initiated_requester(self):
        # Initialize db and hd
        bot = bot_test()
        query = "Where can I find something?"
        response = "Nowhere."

        update = update_test(chat_id=self.my_chat_id, text="/start", first_name=self.my_first_name,
                             last_name=self.my_last_name, phone_number=self.my_phone_number)
        his_update = update_test(chat_id=self.his_chat_id, text="/start", first_name=self.his_first_name,
                                 last_name=self.his_last_name, phone_number=self.his_phone_number)
        my_source_id, his_source_id = self.check_complete_conversation(bot, update, his_update, query, response)

        # Unmatch by the requestor
        self.check_unmatch(bot, update, his_source_id)
        
        # Check the channel is dead
        self.check_response_fail(bot, update, his_source_id, response, fail_reason.INACTIVATED_TARGET_ID)
        self.check_response_fail(bot, his_update, my_source_id, response, fail_reason.INACTIVATED_TARGET_ID)

    def test_unmatch_initiated_responser(self):
        # Initialize db and hd
        bot = bot_test()
        query = "Where can I find something?"
        response = "Nowhere."

        update = update_test(chat_id=self.my_chat_id, text="/start", first_name=self.my_first_name,
                             last_name=self.my_last_name, phone_number=self.my_phone_number)
        his_update = update_test(chat_id=self.his_chat_id, text="/start", first_name=self.his_first_name,
                                 last_name=self.his_last_name, phone_number=self.his_phone_number)
        my_source_id, his_source_id = self.check_complete_conversation(bot, update, his_update, query, response)

        # Unmatch by the requestor
        self.check_unmatch(bot, his_update, my_source_id)
        
        # Check the channel is dead
        self.check_response_fail(bot, update, his_source_id, response, fail_reason.INACTIVATED_TARGET_ID)
        self.check_response_fail(bot, his_update, my_source_id, response, fail_reason.INACTIVATED_TARGET_ID)

    def test_unmatch_query(self):
        # Initialize db and hd
        bot = bot_test()
        query = "Where can I find something?"
        response = "Nowhere."

        update = update_test(chat_id=self.my_chat_id, text="/start", first_name=self.my_first_name,
                             last_name=self.my_last_name, phone_number=self.my_phone_number)
        his_update = update_test(chat_id=self.his_chat_id, text="/start", first_name=self.his_first_name,
                                 last_name=self.his_last_name, phone_number=self.his_phone_number)

        # Query first
        self.check_query(bot, update, query)                             
        
        # Store my source id
        my_source_id = self.hd.source_id        

        # Unmatch by the requestor
        self.check_unmatch(bot, update, my_source_id)
        
        # Check the channel is dead
        self.check_response_fail(bot, his_update, my_source_id, response, fail_reason.INACTIVATED_TARGET_ID)

    def test_invalid_response(self):
        # Initialize db and hd
        bot = bot_test()
        query = "Where can I find something?"
        response = "Nowhere."

        update = update_test(chat_id=self.my_chat_id, text="/start", first_name=self.my_first_name,
                             last_name=self.my_last_name, phone_number=self.my_phone_number)
        his_update = update_test(chat_id=self.his_chat_id, text="/start", first_name=self.his_first_name,
                                 last_name=self.his_last_name, phone_number=self.his_phone_number)        
                                 
        # Query first
        self.check_query(bot, update, query)                             
        
        # Store my source id
        my_source_id = self.hd.source_id                                    
        
        # Check the response fails
        self.check_response_fail(bot, his_update, 'abcd', response, failure=fail_reason.INVALID_TARGET_ID)

        # Check the response fails
        self.check_response_fail(bot, his_update, '0', response, failure=fail_reason.INVALID_TARGET_ID)

        # Check the response fails
        self.check_response_fail(bot, his_update, '-123', response, failure=fail_reason.INVALID_TARGET_ID)

        # Check the response fails
        self.check_response_fail(bot, his_update, 12345678, response, failure=fail_reason.INACTIVATED_TARGET_ID)

    def test_invalid_match(self):
        # Initialize db and hd
        bot = bot_test()
        query = "Where can I find something?"
        response = "Nowhere."

        update = update_test(chat_id=self.my_chat_id, text="/start", first_name=self.my_first_name,
                             last_name=self.my_last_name, phone_number=self.my_phone_number)
        his_update = update_test(chat_id=self.his_chat_id, text="/start", first_name=self.his_first_name,
                                 last_name=self.his_last_name, phone_number=self.his_phone_number)
        my_source_id, his_source_id = self.check_complete_conversation(bot, update, his_update, query, response)
        
        # Check the unmatch fails
        self.check_match_fail(bot, his_update, 'abcd', failure=fail_reason.INVALID_TARGET_ID)

        # Check the unmatch fails
        self.check_match_fail(bot, his_update, 0, failure=fail_reason.INVALID_TARGET_ID)

        # Check the unmatch fails
        self.check_match_fail(bot, his_update, -123, failure=fail_reason.INVALID_TARGET_ID)

        # Check the unmatch fails
        self.check_match_fail(bot, his_update, 12345678, failure=fail_reason.INACTIVATED_TARGET_ID)

    def test_invalid_unmatch(self):
        # Initialize db and hd
        bot = bot_test()
        query = "Where can I find something?"
        response = "Nowhere."

        update = update_test(chat_id=self.my_chat_id, text="/start", first_name=self.my_first_name,
                             last_name=self.my_last_name, phone_number=self.my_phone_number)
        his_update = update_test(chat_id=self.his_chat_id, text="/start", first_name=self.his_first_name,
                                 last_name=self.his_last_name, phone_number=self.his_phone_number)        
        my_source_id, his_source_id = self.check_complete_conversation(bot, update, his_update, query, response)                                 
        
        # Check the unmatch fails
        self.check_unmatch_fail(bot, his_update, 'abcd', failure=fail_reason.INVALID_TARGET_ID)

        # Check the unmatch fails
        self.check_unmatch_fail(bot, his_update, '0', failure=fail_reason.INVALID_TARGET_ID)

        # Check the unmatch fails
        self.check_unmatch_fail(bot, his_update, '-123', failure=fail_reason.INVALID_TARGET_ID)

        # Check the unmatch fails
        self.check_unmatch_fail(bot, his_update, '12345678', failure=fail_reason.INACTIVATED_TARGET_ID)

if __name__ == '__main__':
    unittest.main()

