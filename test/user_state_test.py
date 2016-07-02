#!/bin/python

import unittest
import logging
import os
from src.user_state import user_state

class user_state_test(unittest.TestCase):
    def test_query_state(self):
        s = user_state('12345', user_state.states.START)

        print_callback = lambda : print("Undefined behaviour")

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

if __name__ == '__main__':
    unittest.main()