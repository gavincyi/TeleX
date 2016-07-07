#!/bin/python

import datetime

class txn():
    def __init__(self, session = 0, inid = 0, inchatid = ''):
        curr_datetime = datetime.datetime.now()
        self.date = curr_datetime.strftime("%Y%m%d")
        self.time = curr_datetime.strftime("%H:%M:%S.%f %z")
        self.session = session
        self.in_id = inid
        self.in_chat_id = inchatid
        self.out_id = 0
        self.out_chat_id = ''

    def str(self):
        out = "'%s','%s',%d,%d,'%s',%d,'%s'" % \
              (self.date, self.time, self.session, self.out_id, \
               self.out_chat_id, self.in_id, self.in_chat_id)
        return out

    @staticmethod
    def from_txn_record(record, set_curr_time = True):
        """
        Convert a db record to a txn record
        :param record: Database record
        :param set_curr_time: Indicate if current date and time is set
        """        
        if not record:
            ret = txn()
        else:
            ret = txn(record[txn.session_index()], record[txn.in_id_index()], record[txn.in_chat_id_index()])
            ret.out_id = record[txn.out_id_index()]
            ret.out_chat_id = record[txn.out_chat_id_index()]
            if not set_curr_time:
                ret.date = record[txn.date_index()]
                ret.time = record[txn.time_index()]
            
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
    def out_id_index():
        return 3

    @staticmethod
    def out_chat_id_index():
        return 4

    @staticmethod
    def in_id_index():
        return 5

    @staticmethod
    def in_chat_id_index():
        return 6





