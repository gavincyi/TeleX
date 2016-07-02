#!/bin/python

import datetime


class message():
    def __init__(self, session, id, chat_id):
        curr_datetime = datetime.datetime.now()
        self.date = curr_datetime.strftime("%Y%m%d")
        self.time = curr_datetime.strftime("%H:%M:%S.%f %z")
        self.session = session
        self.id = id
        self.chat_id = chat_id
        self.msg = ''

    def str(self):
        out = "'%s','%s',%d,%d,'%s','%s'" % \
              (self.date, self.time, self.session, self.id,
               self.chat_id, self.msg)
        return out
