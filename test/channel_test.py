#!/bin/python

import unittest
import logging
import os
import sys
from src.channel import channel

class channel_test(unittest.TestCase):
    def test_from_channel_record(self):
        channel_record = channel(
                         channel_id=10,
                         source_id=7,
                         source_chat_id='123456',
                         target_id=11,
                         target_chat_id='654321',
                         public=1,
                         type=1,
                         match=1)
        row = channel_record.str().split(',')
        row = [e.replace("'", "") if e.find("'") > -1 else int(e) for e in row]
        channel_record_from_row = channel.from_channel_record(row, False)
        
        ## Positive test
        self.assertEqual(channel_record.date, channel_record_from_row.date)
        self.assertEqual(channel_record.time, channel_record_from_row.time)
        self.assertEqual(channel_record.channel_id, channel_record_from_row.channel_id)
        self.assertEqual(channel_record.source_id, channel_record_from_row.source_id)
        self.assertEqual(channel_record.source_chat_id, channel_record_from_row.source_chat_id)
        self.assertEqual(channel_record.target_id, channel_record_from_row.target_id)
        self.assertEqual(channel_record.target_chat_id, channel_record_from_row.target_chat_id)
        self.assertEqual(channel_record.public, channel_record_from_row.public)
        self.assertEqual(channel_record.type, channel_record_from_row.type)
        self.assertEqual(channel_record.match, channel_record_from_row.match)

        ## Negative test
        channel_record_from_row = channel.from_channel_record(None)
        self.assertEqual(0, channel_record_from_row.channel_id)
        self.assertEqual(0, channel_record_from_row.source_id)
        self.assertEqual('', channel_record_from_row.source_chat_id)
        self.assertEqual(0, channel_record_from_row.target_id)
        self.assertEqual('', channel_record_from_row.target_chat_id)        
        self.assertEqual(0, channel_record_from_row.public)
        self.assertEqual(0, channel_record_from_row.type)
        self.assertEqual(0, channel_record_from_row.match)

if __name__ == '__main__':
    unittest.main()        