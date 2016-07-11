#!/bin/python

import unittest
import logging
import os
import sys
from src.message import message

class message_test(unittest.TestCase):
    def test_from_message_record(self):
        message_record = message(
                            msg_id=185,
                            channel_id=82,
                            source_id=50,
                            source_chat_id='111111',
                            msg='Hello world')
        row = message_record.str().split(',')
        row = [e.replace("'", "") if e.find("'") > -1 else int(e) for e in row]
        message_record_from_row = message.from_message_record(row, False)
        
        ## Positive test
        self.assertEqual(message_record.date, message_record_from_row.date)
        self.assertEqual(message_record.time, message_record_from_row.time)
        self.assertEqual(message_record.msg_id, message_record_from_row.msg_id)
        self.assertEqual(message_record.channel_id, message_record_from_row.channel_id)
        self.assertEqual(message_record.source_id, message_record_from_row.source_id)
        self.assertEqual(message_record.source_chat_id, message_record_from_row.source_chat_id)
        self.assertEqual(message_record.msg, message_record_from_row.msg)
        
        ## Negative test
        message_record_from_row = message.from_message_record(None)
        self.assertEqual(0, message_record_from_row.msg_id)
        self.assertEqual(0, message_record_from_row.channel_id)
        self.assertEqual(0, message_record_from_row.source_id)        
        self.assertEqual('', message_record_from_row.source_chat_id)        
        self.assertEqual('', message_record_from_row.msg)        

if __name__ == '__main__':
    unittest.main()        