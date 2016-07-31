#!/bin/python

import yaml
import os
import datetime
import sys

class config():
    def __init__(self, \
                 conf_file = os.path.abspath(__file__ + "/../../config/config.yaml"),
                 mode='NORMAL'):
        self.mode = mode
        self.api_token = ''
        self.channel_name = ''
        self.log_file = ''
        self.db_path = ''
        self.help_channel_name = ''

        with open(conf_file) as stream:
            try:
                d = yaml.load(stream)

                if 'api_token' in d:
                    self.api_token = d['api_token']
                else:
                    raise SystemError("Error: API token is not found in the configuration file")

                if 'channel_name' in d:
                    self.channel_name = d['channel_name']
                else:
                    raise SystemError("Error: Channel name is not found in the configuration file")

                if 'log_path' in d and 'log_prefix' in d:
                    log_path = d['log_path']
                    if log_path[0:6] == '/./../':
                        log_path = os.path.abspath(__file__ + log_path)

                    log_prefix = d['log_prefix']

                    self.log_file = os.path.join(log_path, log_prefix + "_" + \
                                                 datetime.datetime.now().strftime("%Y%m%d") + ".log")
                else:
                    raise SystemError("Error: Log path or prefix is not found in the configuration file")

                if 'db_path' in d:
                    self.db_path = os.path.abspath(__file__ + d['db_path'])
                else:
                    raise SystemError("Error: Database path is not found in the configuration file")

                if 'help_channel_name' in d:
                    self.help_channel_name = d['help_channel_name']
                else:
                    raise SystemError("Error: Help channel name is not found in the configuration file")

            except yaml.YAMLError as exc:
                print("Error in configuation initialization: %s" % exc)
