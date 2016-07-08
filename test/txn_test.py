#!/bin/python

import unittest
import logging
import os
import sys
from src.txn import txn

class txn_test(unittest.TestCase):
    def test_from_txn_record(self):
        txn_record = txn(session=1,
                         in_id=10,
                         in_chat_id='689689',
                         out_id=12,
                         out_chat_id='444444')
        row = txn_record.str().split(',')
        txn_record_from_row = txn.from_txn_record(row, False)
        
        ## Positive test
        self.assertEqual(txn_record.date, txn_record_from_row.date.replace("'", ""))
        self.assertEqual(txn_record.time, txn_record_from_row.time.replace("'", ""))
        self.assertEqual(txn_record.session, int(txn_record_from_row.session))
        self.assertEqual(txn_record.out_id, int(txn_record_from_row.out_id))
        self.assertEqual(txn_record.out_chat_id, txn_record_from_row.out_chat_id.replace("'", ""))
        self.assertEqual(txn_record.in_id, int(txn_record_from_row.in_id))
        self.assertEqual(txn_record.in_chat_id, txn_record_from_row.in_chat_id.replace("'", ""))
        
        ## Negative test
        txn_record_from_row = txn.from_txn_record(None)
        self.assertEqual(0, int(txn_record_from_row.session))
        self.assertEqual(0, int(txn_record_from_row.out_id))
        self.assertEqual('', txn_record_from_row.out_chat_id.replace("'", ""))
        self.assertEqual(0, int(txn_record_from_row.in_id))
        self.assertEqual('', txn_record_from_row.in_chat_id.replace("'", ""))        

if __name__ == '__main__':
    unittest.main()        