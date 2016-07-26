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
        self.assertEqual(s.prev_state, user_state.states.START)
        self.assertEqual(s.transition, user_state.transitions.QUERYING)
        s.jump(user_state.transitions.NO, print_callback)
        self.assertEqual(s.state, user_state.states.START)
        self.assertEqual(s.prev_state, user_state.states.QUERY_PENDING_MSG)
        self.assertEqual(s.transition, user_state.transitions.NO)        

        s.jump(user_state.transitions.QUERYING, print_callback)
        self.assertEqual(s.state, user_state.states.QUERY_PENDING_MSG)
        self.assertEqual(s.prev_state, user_state.states.START)
        self.assertEqual(s.transition, user_state.transitions.QUERYING)        
        s.jump(user_state.transitions.YES, print_callback)
        self.assertEqual(s.state, user_state.states.QUERY_PENDING_CONFIRM)
        self.assertEqual(s.prev_state, user_state.states.QUERY_PENDING_MSG)
        self.assertEqual(s.transition, user_state.transitions.YES)              
        s.jump(user_state.transitions.YES, print_callback)
        self.assertEqual(s.state, user_state.states.START)
        self.assertEqual(s.prev_state, user_state.states.QUERY_PENDING_CONFIRM)
        self.assertEqual(s.transition, user_state.transitions.YES)                      

        s.jump(user_state.transitions.QUERYING, print_callback)
        self.assertEqual(s.state, user_state.states.QUERY_PENDING_MSG)
        self.assertEqual(s.prev_state, user_state.states.START)
        self.assertEqual(s.transition, user_state.transitions.QUERYING)         
        s.jump(user_state.transitions.YES, print_callback)
        self.assertEqual(s.state, user_state.states.QUERY_PENDING_CONFIRM)
        self.assertEqual(s.prev_state, user_state.states.QUERY_PENDING_MSG)
        self.assertEqual(s.transition, user_state.transitions.YES)                
        s.jump(user_state.transitions.NO, print_callback)
        self.assertEqual(s.state, user_state.states.START)
        self.assertEqual(s.prev_state, user_state.states.QUERY_PENDING_CONFIRM)
        self.assertEqual(s.transition, user_state.transitions.NO)              

    def test_from_user_state_record(self):
        user_state_record = user_state(chat_id='45567845',
                                       state=user_state.states.QUERY_PENDING_MSG,
                                       prev_state=user_state.states.START,
                                       transition=user_state.transitions.QUERYING,
                                       last_target_id=123,
                                       last_msg_id=456)
        row = user_state_record.str().split(',')
        row = [e.replace("'", "") if e.find("'") > -1 else int(e) for e in row]
        user_state_record_from_row = user_state.from_user_state_record(row, False)
        
        ## Positive test
        self.assertEqual(user_state_record.date, user_state_record_from_row.date)
        self.assertEqual(user_state_record.time, user_state_record_from_row.time)
        self.assertEqual(user_state_record.chat_id, user_state_record_from_row.chat_id)
        self.assertEqual(user_state_record.state, user_state_record_from_row.state)
        self.assertEqual(user_state_record.prev_state, user_state_record_from_row.prev_state)
        self.assertEqual(user_state_record.transition, user_state_record_from_row.transition)
        self.assertEqual(user_state_record.last_target_id, user_state_record_from_row.last_target_id)
        self.assertEqual(user_state_record.last_msg_id, user_state_record_from_row.last_msg_id)

        ## Negative test
        user_state_record_from_row = user_state.from_user_state_record(None)
        self.assertEqual('', user_state_record_from_row.chat_id)
        self.assertEqual(user_state.states.UNDEF, user_state_record_from_row.state) 
        self.assertEqual(user_state.states.UNDEF, user_state_record_from_row.prev_state)
        self.assertEqual(user_state.transitions.UNDEF, user_state_record_from_row.transition)        
        self.assertEqual(0, user_state_record_from_row.last_target_id)
        self.assertEqual(0, user_state_record_from_row.last_msg_id)

if __name__ == '__main__':
    unittest.main()