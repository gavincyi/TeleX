#!/bin/python

import unittest
import logging
import os
from src.config import config

class config_test(unittest.TestCase):
    def test_constructor(self):
        conf = config(__file__+ "/../config_test.yaml")
        self.assertEqual(conf.mode, 'NORMAL')
        self.assertEqual(conf.api_token, '12345678')
        self.assertEqual(conf.channel_name, 'TestingChannel')
        self.assertEqual(conf.log_file[0:-12], os.path.abspath(__file__ + '/./../../log/telex_test_'))

if __name__ == '__main__':
    unittest.main()