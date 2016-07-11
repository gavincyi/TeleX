#!/bin/python

import datetime


class message():
    def __init__(self, msg_id=0, channel_id=0, source_id=0, source_chat_id='',\
                 msg=''):
        curr_datetime = datetime.datetime.now()
        self.date = curr_datetime.strftime("%Y%m%d")
        self.time = curr_datetime.strftime("%H:%M:%S.%f %z")
        self.msg_id = msg_id
        self.channel_id = channel_id
        self.source_id = source_id
        self.source_chat_id = source_chat_id
        self.msg = msg

    def str(self):
        return "'%s','%s',%d,%d,%d,'%s','%s'" \
              % (self.date, \
                 self.time, \
                 self.msg_id, \
                 self.channel_id, \
                 self.source_id, \
                 self.source_chat_id, \
                 self.msg)
        
    @staticmethod
    def from_message_record(record, set_curr_time = True):
        """
        Convert a db record to a message record
        :param record: Database record
        :param set_curr_time: Indicate if current date and time is set
        """        
        if not record:
            ret = message()
        else:
            ret = message(msg_id=record[message.msg_id_index()],
                          channel_id=record[message.channel_id_index()],
                          source_id=record[message.source_id_index()],
                          source_chat_id=record[message.source_chat_id_index()],
                          msg=record[message.msg_index()])
            if not set_curr_time:
                ret.date = record[message.date_index()]
                ret.time = record[message.time_index()]
        return ret    
        
    @staticmethod
    def field_str():
        return "date text, time text, msgid int, channelid int, " + \
               "sourceid int, sourcechatid text, msg text"
               
    @staticmethod
    def key_str():
        return "msgid"
        
    @staticmethod
    def date_index():
        return 0
            
    @staticmethod
    def time_index():
        return 1
            
    @staticmethod
    def msg_id_index():
        return 2
            
    @staticmethod
    def channel_id_index():
        return 3
            
    @staticmethod
    def source_id_index():
        return 4
            
    @staticmethod
    def source_chat_id_index():
        return 5

    @staticmethod
    def msg_index():
        return 6
