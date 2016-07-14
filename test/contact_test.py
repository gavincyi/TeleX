#!/bin/python

import unittest
import logging
import os
import sys
from src.contact import contact

class contact_test(unittest.TestCase):
    def test_from_contact_record(self):
        contact_record = contact(chat_id='123456',
                                 phone_number='21444485',
                                 first_name='Peter',
                                 last_name='Jones')
        row = contact_record.str().split(',')
        row = [e.replace("'", "") if e.find("'") > -1 else int(e) for e in row]
        contact_record_from_row = contact.from_contact_record(row, False)
        
        ## Positive test
        self.assertEqual(contact_record.date, contact_record_from_row.date)
        self.assertEqual(contact_record.time, contact_record_from_row.time)
        self.assertEqual(contact_record.chat_id, contact_record_from_row.chat_id)
        self.assertEqual(contact_record.phone_number, contact_record_from_row.phone_number)
        self.assertEqual(contact_record.first_name, contact_record_from_row.first_name)
        self.assertEqual(contact_record.last_name, contact_record_from_row.last_name)
        
        ## Negative test
        contact_record_from_row = contact.from_contact_record(None)
        self.assertEqual('', contact_record_from_row.chat_id)
        self.assertEqual('', contact_record_from_row.phone_number)
        self.assertEqual('', contact_record_from_row.first_name)
        self.assertEqual('', contact_record_from_row.last_name)

if __name__ == '__main__':
    unittest.main()        