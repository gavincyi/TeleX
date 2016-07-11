#!/bin/python

import unittest
import os
from src.handler import handler
from src.config import config
from src.db_client import db_client

class logger_test():
    """
    Logger class for unit test
    """
    def __init__(self):
        pass
    def info(self, text):
        print("Info - %s" % text)
    def warn(self, text):
        print("Warn - %s" % text)
        
class update_test():
    """
    Update class for unit test
    """
    class message_test():
        
        class from_user_test():
            def __init__(self, first_name=''):
                self.first_name = first_name
            
        def __init__(self, chat_id='', text='', first_name=''):
            self.chat_id = chat_id
            self.text = text
            self.from_user = update_test.message_test.from_user_test(first_name=first_name)
            
    def __init__(self, chat_id='', text='', first_name=''):
        self.message = update_test.message_test(chat_id, text, first_name=first_name)
        
class bot_test():
    """
    Bot class for unit test
    """
    def __init__(self):
        self.msg_map = {}
    def sendMessage(self, chat_id, text, parse_mode=None, disable_web_page_preview=None, **kwargs):
        if chat_id in self.msg_map.keys():
            self.msg_map[chat_id] += text + "\n";
        else:
            self.msg_map[chat_id] = text + "\n"
    def clear_msg_map(self):
        self.msg_map.clear()   
        
class handler_test(unittest.TestCase):
 
            
    def test_start(self):
        conf = config(os.path.abspath(__file__ + "/../../test/config_test.yaml"))
        conf.mode = 'COLD'
        logger = logger_test()
        hd = handler(logger, conf)
        db = db_client(logger, conf)
        
        if os.path.isfile(db.db_file):
            os.remove(db.db_file)       
        
        # Initialize db and hd    
        self.assertTrue(db.init())
        hd.init_db(db)
        bot = bot_test()
        
        out_chat_id = '12345678'
        in_chat_id = '87654321'
        first_name = "David"
        
        update = update_test(chat_id=in_chat_id, text="/start", first_name=first_name)
        hd.start_handler(bot, update)
        self.assertTrue(len(bot.msg_map) > 0)

        # Close the connection
        db.close()

        # Remove the file
        os.remove(db.db_file)        

if __name__ == '__main__':
    unittest.main()    
            
        