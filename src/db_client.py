#!/bin/python

import sqlite3
from src.channel import channel
from src.message import message
from src.user_state import user_state
from src.contact import contact

class db_client():
    """
    Simple sqlite database client
    """
    def __init__(self, logger, conf = None):
        self.logger = logger
        self.db_file = conf.db_path
        self.cold = conf.mode == 'COLD'

        # Channels
        self.channels_table_name = 'Channels'
        self.create_channels_table_sql = \
            '''create table if not exists %s (%s)''' \
            % (self.channels_table_name, channel.field_str())
        self.create_channels_index_sql = \
            '''create unique index %s_idx on %s(%s)''' \
            % (self.channels_table_name, self.channels_table_name, \
               channel.key_str())
        self.create_channels_index2_sql = \
            '''create unique index %s_idx2 on %s(%s)''' \
            % (self.channels_table_name, self.channels_table_name, \
               channel.key2_str())        

        # user_states
        self.user_states_table_name = 'User_States'
        self.create_user_states_table_sql = \
            '''create table if not exists %s (%s)''' \
            % (self.user_states_table_name, user_state.field_str())
        self.create_user_states_index_sql = \
            '''create unique index %s_idx on %s(%s)''' \
            % (self.user_states_table_name, self.user_states_table_name, \
               user_state.key_str())

        # messages
        self.messages_table_name = 'Messages'
        self.create_messages_table_sql = \
            '''create table if not exists %s (%s)''' \
            % (self.messages_table_name, message.field_str())
        self.create_messages_index_sql = \
            '''create unique index %s_idx on %s(%s)''' \
            % (self.messages_table_name, self.messages_table_name, \
               message.key_str())

        # contacts
        self.contacts_table_name = 'Contacts'
        self.create_contacts_table_sql = \
            '''create table if not exists %s (%s)''' \
            % (self.contacts_table_name, contact.field_str())
        self.create_contacts_index_sql = \
            '''create unique index %s_idx on %s(%s)''' \
            % (self.contacts_table_name, self.contacts_table_name, \
               contact.key_str())

    def init(self):
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

        # Create tables`
        self.cursor.execute(self.create_channels_table_sql)
        self.logger.info('Table %s is created' % self.channels_table_name)        

        self.cursor.execute(self.create_user_states_table_sql)
        self.logger.info('Table %s is created' % self.user_states_table_name)

        self.cursor.execute(self.create_messages_table_sql)
        self.logger.info('Table %s is created' % self.create_messages_table_sql)

        self.cursor.execute(self.create_contacts_table_sql)
        self.logger.info('Table %s is created' % self.create_contacts_table_sql)

        # During cold start
        if self.cold:
            self.logger.info('Database is cold started')

            self.cursor.execute(self.create_channels_index_sql)
            self.cursor.execute(self.create_channels_index2_sql)
            self.logger.info('Table %s index is created' % self.channels_table_name)            

            self.cursor.execute(self.create_user_states_index_sql)
            self.logger.info('Table %s index is created' % self.user_states_table_name)

            self.cursor.execute(self.create_messages_index_sql)
            self.logger.info('Table %s index is created' % self.messages_table_name)

            self.cursor.execute(self.create_contacts_index_sql)
            self.logger.info('Table %s index is created' % self.contacts_table_name)

        self.conn.commit()

        return True

    def insert(self, table, value):
        self.cursor.execute('''insert into %s values (%s)''' % (table, value))
        self.conn.commit()

    def insert_or_replace(self, table, value):
        self.cursor.execute('''insert or replace into %s values (%s)''' % (table, value))
        self.conn.commit()

    def selectone(self, table, fields, where = "", orderby = ""):
        self.cursor.execute('''select %s from %s %s %s''' % \
                            (fields, \
                             table, \
                             "where %s"%where if where != "" else "",
                             "order by %s"%orderby if orderby != "" else ""))

        return self.cursor.fetchone()

    def selectall(self, table, fields, where = "", orderby = ""):
        self.cursor.execute('''select %s from %s %s %s''' % \
                            (fields, \
                             table, \
                             "where %s"%where if where != "" else "",
                             "order by %s"%orderby if orderby != "" else ""))

        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
        return True


