#!/bin/python

import datetime

class txn():
    def __init__(self, session, inid, inchatid):
        curr_datetime = datetime.datetime.now()
        self.date = curr_datetime.strftime("%Y%m%d")
        self.time = curr_datetime.strftime("%H:%M:%S.%f %z")
        self.session = session
        self.inid = inid
        self.inchatid = inchatid
        self.outid = 0
        self.outchatid = ''

    def str(self):
        out = "'%s','%s',%d,%d,'%s',%d,'%s'" % \
              (self.date, self.time, self.session, self.outid, \
               self.outchatid, self.inid, self.inchatid)
        return out

    @staticmethod
    def outid_index():
        return 3

    @staticmethod
    def outchatid_index():
        return 4

    @staticmethod
    def inid_index():
        return 5

    @staticmethod
    def inchatid_index():
        return 6
