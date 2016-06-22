#!/bin/python

import unittest
import logging
import os
from src.db_client import db_client, txn

class db_client_test(unittest.TestCase):
    def test_init(self):
        #Initialization
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger()
        obj = db_client(logger)
        obj.db_file = os.path.abspath(obj.db_file + "/../telex_test.sqlite")
        self.assertTrue(obj.init())

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

        # Close the connection
        obj.close()

        # Remove the file
        os.remove(obj.db_file)

if __name__ == '__main__':
    unittest.main()