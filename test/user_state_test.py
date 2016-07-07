#!/bin/python

import unittest
import logging
import os
import sys
from src.user_state import user_state

class user_state_test(unittest.TestCase):
    def test_query_state(self):
        s = user_state('12345', user_state.states.START)

        print_callback = lambda : sys.stdout.write("Undefined behaviour")

        # Query
        s.jump(user_state.transitions.QUERYING, print_callback)
        self.assertEqual(s.state, user_state.states.QUERY_PENDING_MSG)
        s.jump(user_state.transitions.NO, print_callback)
        self.assertEqual(s.state, user_state.states.START)

        s.jump(user_state.transitions.QUERYING, print_callback)
        self.assertEqual(s.state, user_state.states.QUERY_PENDING_MSG)
        s.jump(user_state.transitions.YES, print_callback)
        self.assertEqual(s.state, user_state.states.QUERY_PENDING_CONFIRM)
        s.jump(user_state.transitions.YES, print_callback)
        self.assertEqual(s.state, user_state.states.START)

        s.jump(user_state.transitions.QUERYING, print_callback)
        self.assertEqual(s.state, user_state.states.QUERY_PENDING_MSG)
        s.jump(user_state.transitions.YES, print_callback)
        self.assertEqual(s.state, user_state.states.QUERY_PENDING_CONFIRM)
        s.jump(user_state.transitions.NO, print_callback)
        self.assertEqual(s.state, user_state.states.START)

    def test_from_user_state_record(self):
        user_state_record = user_state(chat_id='45567845',
                                       state=user_state.states.QUERY_PENDING_MSG)
        user_state_record.prev_state = user_state.states.START
        row = user_state_record.str().split(',')
        row = [e.replace("'", "") if e.find("'") > -1 else int(e) for e in row]
        user_state_record_from_row = user_state.from_user_state_record(row, False)
        
        ## Positive test
        self.assertEqual(user_state_record.date, user_state_record_from_row.date)
        self.assertEqual(user_state_record.time, user_state_record_from_row.time)
        self.assertEqual(user_state_record.chat_id, user_state_record_from_row.chat_id)
        self.assertEqual(user_state_record.state, user_state_record_from_row.state)
        
        ## Negative test
        user_state_record_from_row = user_state.from_user_state_record(None)
        self.assertEqual('', user_state_record_from_row.chat_id)
        self.assertEqual(user_state.states.UNDEF, user_state_record_from_row.state)        

if __name__ == '__main__':
    unittest.main()