#!/bin/python

import unittest
import logging
import os
from src.user_interface import user_interface

class config_test(unittest.TestCase):
    def test_constructor(self):
        ui = user_interface('TeleXTest', 
                            'TeleXHelpChannel', 
                            os.path.abspath(__file__+ "/../../test/user_interface_test.yaml"))
        self.assertEqual(ui.console['QueryButton'], "Query")
        self.assertEqual(ui.console['ResponseButton'], "Response")
        self.assertEqual(ui.console['MatchButton'], "Match")
        self.assertEqual(ui.console['UnmatchButton'], "Unmatch")
        self.assertEqual(ui.console['HelpButton'], "Help")
        
    def test_constructor_file(self):
        try:
            ui = user_interface('TeleXTest', 
                                'TeleXHelpChannel',
                                os.path.abspath(__file__+ "/../../test/user_interface_fail_test.yaml"))        
            self.assertEqual(1, 2)
        except SystemError as se:
            s = "The following fields are missing in user interface:\n"
            missing_fields = user_interface.mandatory_messages()
            missing_fields.remove('QueryButton')
            missing_fields.remove('ResponseButton')
            missing_fields.remove('MatchButton')
            missing_fields.remove('UnmatchButton')
            missing_fields.remove('HelpButton')
            s += '\n'.join(missing_fields)
            self.assertEqual(str(se), s)

if __name__ == '__main__':
    unittest.main()