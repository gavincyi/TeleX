#!/bin/python

import unittest
import logging
import os
from src.db_client import db_client
from src.channel import channel
from src.user_state import user_state
from src.message import message
from src.contact import contact
from src.config import config

class db_client_test(unittest.TestCase):
    def test_init(self):
        #Initialization
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger()
        conf = config(os.path.abspath(__file__ + "/../../test/config_test.yaml"))
        conf.mode = 'COLD'
        obj = db_client(logger, conf)

        if os.path.isfile(obj.db_file):
            os.remove(obj.db_file)

        self.assertTrue(obj.init())

        ########################################################################
        # Channels
        # Check if table is created
        obj.cursor.execute('''delete from %s where 1 = 1''' % obj.channels_table_name)
        channel_record = channel(channel_id=7,
                                 source_id=10,
                                 source_chat_id='123456',
                                 target_id=15,
                                 target_chat_id='654321',
                                 public=1,
                                 live=1)
        obj.insert(obj.channels_table_name, channel_record.str())                                 
        
        # Check if the row is inserted
        row = obj.selectone(obj.channels_table_name, "*")
        channel_record_from_row = channel.from_channel_record(row, False)
        
        self.assertEqual(channel_record_from_row.date, channel_record.date)
        self.assertEqual(channel_record_from_row.time, channel_record.time)
        self.assertEqual(channel_record_from_row.channel_id, channel_record.channel_id)
        self.assertEqual(channel_record_from_row.source_id, channel_record.source_id)
        self.assertEqual(channel_record_from_row.source_chat_id, channel_record.source_chat_id)
        self.assertEqual(channel_record_from_row.target_id, channel_record.target_id)
        self.assertEqual(channel_record_from_row.target_chat_id, channel_record.target_chat_id)
        self.assertEqual(channel_record_from_row.public, channel_record.public)
        self.assertEqual(channel_record_from_row.live, channel_record.live)
        
        # Update the row
        channel_record.public = 0
        channel_record.live = 0
        obj.insert_or_replace(obj.channels_table_name, channel_record.str())
        
        # Check if the row is inserted
        row = obj.selectone(obj.channels_table_name, "*")
        channel_record_from_row = channel.from_channel_record(row, False)
        self.assertEqual(channel_record_from_row.channel_id, channel_record.channel_id)
        self.assertEqual(channel_record_from_row.source_id, channel_record.source_id)
        self.assertEqual(channel_record_from_row.source_chat_id, channel_record.source_chat_id)
        self.assertEqual(channel_record_from_row.target_id, channel_record.target_id)
        self.assertEqual(channel_record_from_row.target_chat_id, channel_record.target_chat_id)
        self.assertEqual(channel_record_from_row.public, channel_record.public)
        self.assertEqual(channel_record_from_row.live, channel_record.live)
        
        row = obj.selectone(obj.channels_table_name, "*", "targetchatid='654321' and sourceid=10")
        channel_record_from_row = channel.from_channel_record(row, False)        
        
        self.assertEqual(channel_record_from_row.channel_id, channel_record.channel_id)
        self.assertEqual(channel_record_from_row.source_id, channel_record.source_id)
        self.assertEqual(channel_record_from_row.source_chat_id, channel_record.source_chat_id)
        self.assertEqual(channel_record_from_row.target_id, channel_record.target_id)
        self.assertEqual(channel_record_from_row.target_chat_id, channel_record.target_chat_id)
        self.assertEqual(channel_record_from_row.public, channel_record.public)
        self.assertEqual(channel_record_from_row.live, channel_record.live)

        ########################################################################
        # User_states
        # Check if table is created
        obj.cursor.execute('''delete from %s where 1 = 1''' % obj.user_states_table_name)
        user_state_record = user_state(chat_id='1234', 
                                       state=user_state.states.START,
                                       last_target_id=123,
                                       last_msg_id=456)
        obj.insert(obj.user_states_table_name, user_state_record.str())

        # Check if the row is inserted
        row = obj.selectone(obj.user_states_table_name, "*")
        user_state_record_from_row = user_state.from_user_state_record(row, False)
        self.assertEqual(user_state_record_from_row.date, user_state_record.date)
        self.assertEqual(user_state_record_from_row.time, user_state_record.time)
        self.assertEqual(user_state_record_from_row.chat_id, user_state_record.chat_id)
        self.assertEqual(user_state_record_from_row.state, user_state_record.state)
        self.assertEqual(user_state_record_from_row.last_target_id, user_state_record.last_target_id)
        self.assertEqual(user_state_record_from_row.last_msg_id, user_state_record.last_msg_id)

        ########################################################################
        # Messages
        # Check if table is created
        obj.cursor.execute('''delete from %s where 1 = 1''' % obj.messages_table_name)
        message_record = message(msg_id=50,
                                 channel_id=30,
                                 source_id=29,
                                 source_chat_id='111111',
                                 msg='Hello world')
        obj.insert(obj.messages_table_name, message_record.str())

        # Check if the row is inserted
        row = obj.selectone(obj.messages_table_name, "*")
        message_record_from_row = message.from_message_record(row, False)
        self.assertEqual(message_record_from_row.date, message_record.date)
        self.assertEqual(message_record_from_row.time, message_record.time)
        self.assertEqual(message_record_from_row.msg_id, message_record.msg_id)
        self.assertEqual(message_record_from_row.channel_id, message_record.channel_id)
        self.assertEqual(message_record_from_row.source_id, message_record.source_id)
        self.assertEqual(message_record_from_row.source_chat_id, message_record.source_chat_id)
        self.assertEqual(message_record_from_row.msg, message_record.msg)

        ########################################################################
        # Contaccts
        # Check if table is created
        obj.cursor.execute('''delete from %s where 1 = 1''' % obj.contacts_table_name)
        contact_record = contact(chat_id='123456',
                                 phone_number='21223422',
                                 first_name='David',
                                 last_name='Jones')
        obj.insert(obj.contacts_table_name, contact_record.str())

        # Check if the row is inserted
        row = obj.selectone(obj.contacts_table_name, "*")
        contact_record_from_row = contact.from_contact_record(row, False)
        self.assertEqual(contact_record_from_row.date, contact_record.date)
        self.assertEqual(contact_record_from_row.time, contact_record.time)
        self.assertEqual(contact_record_from_row.chat_id, contact_record.chat_id)
        self.assertEqual(contact_record_from_row.phone_number, contact_record.phone_number)
        self.assertEqual(contact_record_from_row.first_name, contact_record.first_name)
        self.assertEqual(contact_record_from_row.last_name, contact_record.last_name)

        # Close the connection
        obj.close()

        # Remove the file
        os.remove(obj.db_file)

if __name__ == '__main__':
    unittest.main()