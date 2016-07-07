#!/bin/python

import datetime

class txn():
    def __init__(self, session, inid, inchatid):
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





