#!/bin/python

import datetime

class channel:
    def __init__(self, channel_id=0, source_id=0, source_chat_id='',\
                 target_id=0, target_chat_id='', last_msg_id=0,
                 public=0, live=1):
        """
        Constructor
        """
        curr_datetime = datetime.datetime.now()
        self.date = curr_datetime.strftime("%Y%m%d")
        self.time = curr_datetime.strftime("%H:%M:%S.%f %z")
        self.channel_id = channel_id
        self.source_id = source_id
        self.source_chat_id = source_chat_id
        self.target_id = target_id
        self.target_chat_id = target_chat_id
        self.last_msg_id = last_msg_id
        self.public = public
        self.live = live

    def str(self):
        """
        Output the object into a comma separated string
        """        
        return "'%s','%s',%d,%d,'%s',%d,'%s',%d,%d,%d" % \
               (self.date, \
                self.time, \
                self.channel_id, \
                self.source_id, \
                self.source_chat_id, \
                self.target_id, \
                self.target_chat_id, \
                self.last_msg_id, \
                self.public, \
                self.live)

    @staticmethod
    def from_channel_record(row, set_curr_time=True):
        """
        Convert a db record to a channel record
        :param record: Database record
        :param set_curr_time: Indicate if current date and time is set
        """                
        if not row:
            return channel()
        else:
            ret = channel(channel_id=row[channel.channel_id_index()],
                          source_id=row[channel.source_id_index()],
                          source_chat_id=row[channel.source_chat_id_index()],
                          target_id=row[channel.target_id_index()],
                          target_chat_id=row[channel.target_chat_id_index()],
                          last_msg_id=row[channel.last_msg_id_index()],
                          public=row[channel.public_index()],
                          live=row[channel.live_index()])
            if not set_curr_time:
                ret.date = row[channel.date_index()]
                ret.time = row[channel.time_index()]
            
            return ret

    @staticmethod
    def field_str():
        return "date text, time text, channelid int, sourceid int, " + \
               "sourcechatid text, targetid int, targetchatid text, " + \
               "lastmsgid int, public int, live int"
        
    @staticmethod
    def key_str():
        return "channelid"        
        
    @staticmethod
    def key2_str():
        return "targetid, sourcechatid"

    @staticmethod
    def date_index():
        return 0

    @staticmethod
    def time_index():
        return 1

    @staticmethod
    def channel_id_index():
        return 2

    @staticmethod
    def source_id_index():
        return 3

    @staticmethod
    def source_chat_id_index():
        return 4

    @staticmethod
    def target_id_index():
        return 5

    @staticmethod
    def target_chat_id_index():
        return 6

    @staticmethod
    def last_msg_id_index():
        return 7        
        
    @staticmethod
    def public_index():
        return 8
        
    @staticmethod
    def live_index():
        return 9