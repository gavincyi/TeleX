#!/bin/python

import unittest
import logging
import os
from src.db_client import db_client
from src.txn import txn
from src.user_state import user_state
from src.message import message
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
        # Txn
        # Check if table is created
        obj.cursor.execute('''delete from %s where 1 = 1''' % obj.txn_table_name)
        txn_record = txn(0, 3, "2345678")
        txn_record.out_id = 2
        txn_record.out_chat_id = "1234567"
        obj.insert(obj.txn_table_name, txn_record.str())

        # Check if the row is inserted
        row = obj.selectone(obj.txn_table_name, "*")
        txn_record_from_row = txn.from_txn_record(row, False)
        
        self.assertEqual(txn_record_from_row.date, txn_record.date)
        self.assertEqual(txn_record_from_row.time, txn_record.time)
        self.assertEqual(txn_record_from_row.session, txn_record.session)
        self.assertEqual(txn_record_from_row.out_id, txn_record.out_id)
        self.assertEqual(txn_record_from_row.out_chat_id, txn_record.out_chat_id)
        self.assertEqual(txn_record_from_row.in_id, txn_record.in_id)
        self.assertEqual(txn_record_from_row.in_chat_id, txn_record.in_chat_id)

        # Update the row
        txn_record.out_id = 5
        txn_record.out_chat_id = "0000001"
        obj.insert_or_replace(obj.txn_table_name, txn_record.str())

        # Check if the row is updated
        row = obj.selectone(obj.txn_table_name, "*")
        txn_record_from_row = txn.from_txn_record(row, False)
        
        self.assertEqual(txn_record_from_row.date, txn_record.date)
        self.assertEqual(txn_record_from_row.time, txn_record.time)
        self.assertEqual(txn_record_from_row.session, txn_record.session)
        self.assertEqual(txn_record_from_row.out_id, txn_record.out_id)
        self.assertEqual(txn_record_from_row.out_chat_id, txn_record.out_chat_id)
        self.assertEqual(txn_record_from_row.in_id, txn_record.in_id)
        self.assertEqual(txn_record_from_row.in_chat_id, txn_record.in_chat_id)
        
        row = obj.selectone(obj.txn_table_name, "*", "inid = 10000")
        txn_record_from_row = txn.from_txn_record(row, False)
        self.assertEqual(txn_record_from_row.session, 0)
        self.assertEqual(txn_record_from_row.out_id, 0)
        self.assertEqual(txn_record_from_row.out_chat_id, '')
        self.assertEqual(txn_record_from_row.in_id, 0)
        self.assertEqual(txn_record_from_row.in_chat_id, '')        

        ########################################################################
        # User_stats
        # Check if table is created
        obj.cursor.execute('''delete from %s where 1 = 1''' % obj.user_states_table_name)
        user_state_record = user_state(chat_id='1234', state=user_state.states.START)
        obj.insert(obj.user_states_table_name, user_state_record.str())

        # Check if the row is inserted
        row = obj.selectone(obj.user_states_table_name, "*")
        user_state_record_from_row = user_state.from_user_state_record(row, False)
        self.assertEqual(user_state_record_from_row.date, user_state_record.date)
        self.assertEqual(user_state_record_from_row.time, user_state_record.time)
        self.assertEqual(user_state_record_from_row.chatid, user_state_record.chatid)
        self.assertEqual(user_state_record_from_row.state, user_state_record.state)

        ########################################################################
        # Messages
        # Check if table is created
        obj.cursor.execute('''delete from %s where 1 = 1''' % obj.messages_table_name)
        message_record = message(session=1, id=10, chat_id='23456')
        obj.insert(obj.messages_table_name, message_record.str())

        # Check if the row is inserted
        row = obj.selectone(obj.messages_table_name, "*")
        message_record_from_row = message.from_message_record(row, False)
        self.assertEqual(message_record_from_row.date, message_record.date)
        self.assertEqual(message_record_from_row.time, message_record.time)
        self.assertEqual(message_record_from_row.session, message_record.session)
        self.assertEqual(message_record_from_row.id, message_record.id)
        self.assertEqual(message_record_from_row.chat_id, message_record.chat_id)
        self.assertEqual(message_record_from_row.msg, message_record.msg)

        # Close the connection
        obj.close()

        # Remove the file
        os.remove(obj.db_file)

if __name__ == '__main__':
    unittest.main()