#!/bin/python

import unittest
import logging
import os
import sys
from src.message import message

class message_test(unittest.TestCase):
    def test_from_message_record(self):
        message_record = message(session=1,
                         id=53,
                         chat_id='45567845')
        message_record.msg = "Hello world"
        row = message_record.str().split(',')
        message_record_from_row = message.from_message_record(row, False)
        
        ## Positive test
        self.assertEqual(message_record.date, message_record_from_row.date.replace("'", ""))
        self.assertEqual(message_record.time, message_record_from_row.time.replace("'", ""))
        self.assertEqual(message_record.id, int(message_record_from_row.id))
        self.assertEqual(message_record.chat_id, message_record_from_row.chat_id.replace("'", ""))
        self.assertEqual(message_record.msg, message_record_from_row.msg.replace("'", ""))
        
        ## Negative test
        message_record_from_row = message.from_message_record(None)
        self.assertEqual(0, message_record_from_row.id)
        self.assertEqual('', message_record_from_row.chat_id)
        self.assertEqual('', message_record_from_row.msg)        

if __name__ == '__main__':
    unittest.main()        