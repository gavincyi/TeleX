#!/bin/python

import datetime

class contact:
    def __init__(self, chat_id='', phone_number='', first_name='', last_name=''):
        """
        Constructor
        """
        curr_datetime = datetime.datetime.now()
        self.date = curr_datetime.strftime("%Y%m%d")
        self.time = curr_datetime.strftime("%H:%M:%S.%f %z")
        self.chat_id = chat_id
        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name

    def str(self):
        """
        Output the object into a comma separated string
        """        
        return "'%s','%s','%s','%s','%s','%s'" % \
               (self.date, \
                self.time, \
                self.chat_id, \
                self.phone_number, \
                self.first_name, \
                self.last_name)

    @staticmethod
    def from_contact_record(row, set_curr_time=True):
        """
        Convert a db record to a channel record
        :param record: Database record
        :param set_curr_time: Indicate if current date and time is set
        """                
        if not row or len(row) <= 1:
            return contact()
        else:
            ret = contact(chat_id=row[contact.chat_id_index()],
                          phone_number=row[contact.phone_number_index()],
                          first_name=row[contact.first_name_index()],
                          last_name=row[contact.last_name_index()])

            if not set_curr_time:
                ret.date = row[contact.date_index()]
                ret.time = row[contact.time_index()]
            
            return ret

    @staticmethod
    def field_str():
        return "date text, time text, chatid text, phonenumber text, " + \
               "firstname text, lastname text"

    @staticmethod
    def key_str():
        return "chatid"

    @staticmethod
    def date_index():
        return 0

    @staticmethod
    def time_index():
        return 1

    @staticmethod
    def chat_id_index():
        return 2

    @staticmethod
    def phone_number_index():
        return 3

    @staticmethod
    def first_name_index():
        return 4

    @staticmethod
    def last_name_index():
        return 5

