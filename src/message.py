#!/bin/python

import datetime


class message():
    def __init__(self, session=0, id=0, chat_id='', msg='', public=0):
        curr_datetime = datetime.datetime.now()
        self.date = curr_datetime.strftime("%Y%m%d")
        self.time = curr_datetime.strftime("%H:%M:%S.%f %z")
        self.session = session
        self.id = id
        self.chat_id = chat_id
        self.msg = msg
        self.public = public

    def str(self):
        out = "'%s','%s',%d,%d,'%s','%s',%d" % \
              (self.date, self.time, self.session, self.id,
               self.chat_id, self.msg, self.public)
        return out
        
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
            ret = message(session=record[message.session_index()],
                          id=record[message.id_index()],
                          chat_id=record[message.chat_id_index()],
                          msg=record[message.msg_index()],
                          public=record[message.public_index()])
            if not set_curr_time:
                ret.date = record[message.date_index()]
                ret.time = record[message.time_index()]
        return ret    
        
    @staticmethod
    def date_index():
        return 0
            
    @staticmethod
    def time_index():
        return 1
            
    @staticmethod
    def session_index():
        return 2
            
    @staticmethod
    def id_index():
        return 3
            
    @staticmethod
    def chat_id_index():
        return 4
            
    @staticmethod
    def msg_index():
        return 5

    @staticmethod
    def public_index():
        return 6
