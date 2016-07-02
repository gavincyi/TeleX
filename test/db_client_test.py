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
        obj = db_client(logger, conf)

        if os.path.isfile(obj.db_file):
            os.remove(obj.db_file)

        self.assertTrue(obj.init(True))

        ########################################################################
        # Txn
        # Check if table is created
        obj.cursor.execute('''delete from %s where 1 = 1''' % obj.txn_table_name)
        txn_record = txn(0, 3, "2345678")
        txn_record.outid = 2
        txn_record.outchatid = "1234567"
        obj.insert(obj.txn_table_name, txn_record.str())

        # Check if the row is inserted
        row = obj.selectone(obj.txn_table_name, "*")
        self.assertEqual(row[0], txn_record.date)
        self.assertEqual(row[1], txn_record.time)
        self.assertEqual(row[2], txn_record.session)
        self.assertEqual(row[3], txn_record.outid)
        self.assertEqual(row[4], txn_record.outchatid)
        self.assertEqual(row[5], txn_record.inid)
        self.assertEqual(row[6], txn_record.inchatid)

        # Update the row
        txn_record.outid = 5
        txn_record.outchatid = "0000001"
        obj.insert_or_replace(obj.txn_table_name, txn_record.str())

        # Check if the row is updated
        row = obj.selectone(obj.txn_table_name, "*")
        self.assertEqual(row[0], txn_record.date)
        self.assertEqual(row[1], txn_record.time)
        self.assertEqual(row[2], txn_record.session)
        self.assertEqual(row[3], txn_record.outid)
        self.assertEqual(row[4], txn_record.outchatid)
        self.assertEqual(row[5], txn_record.inid)
        self.assertEqual(row[6], txn_record.inchatid)

        ########################################################################
        # User_stats
        # Check if table is created
        obj.cursor.execute('''delete from %s where 1 = 1''' % obj.user_states_table_name)
        user_state_record = user_state(chat_id='1234', state=user_state.states.START)
        obj.insert(obj.user_states_table_name, user_state_record.str())

        # Check if the row is inserted
        row = obj.selectone(obj.user_states_table_name, "*")
        self.assertEqual(row[0], user_state_record.date)
        self.assertEqual(row[1], user_state_record.time)
        self.assertEqual(row[2], user_state_record.chatid)
        self.assertEqual(row[3], user_state.states.to_str(user_state_record.state))
        self.assertEqual(user_state.states.from_str(row[3]), user_state_record.state)

        ########################################################################
        # Messages
        # Check if table is created
        obj.cursor.execute('''delete from %s where 1 = 1''' % obj.messages_table_name)
        message_record = message(session=1, id=10, chat_id='23456')
        obj.insert(obj.messages_table_name, message_record.str())

        # Check if the row is inserted
        row = obj.selectone(obj.messages_table_name, "*")
        self.assertEqual(row[0], message_record.date)
        self.assertEqual(row[1], message_record.time)
        self.assertEqual(row[2], message_record.session)
        self.assertEqual(row[3], message_record.id)
        self.assertEqual(row[4], message_record.chat_id)
        self.assertEqual(row[5], message_record.msg)

        # Close the connection
        obj.close()

        # Remove the file
        os.remove(obj.db_file)

if __name__ == '__main__':
    unittest.main()