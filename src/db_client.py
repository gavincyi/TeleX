#!/bin/python

import sqlite3

class db_client():
    """
    Simple sqlite database client
    """
    def __init__(self, logger, conf = None):
        self.logger = logger
        self.db_file = conf.db_path
        self.cold = conf.mode == 'COLD'

        # txn
        self.txn_table_name = 'txn'
        self.create_txn_table_sql = \
             '''create table if not exists %s (date text, time text, session int, outid int, outchatid text, inid int, inchatid text)'''\
             % self.txn_table_name
        self.create_txn_index_sql = \
             '''create unique index %s_idx on %s(session, inid)''' % (self.txn_table_name, self.txn_table_name)

        # user_states
        self.user_states_table_name = 'user_states'
        self.create_user_states_table_sql = \
            '''create table if not exists %s (date text, time text, chatid text, state text, prevstate text, transit text)''' \
            % self.user_states_table_name
        self.create_user_states_index_sql = \
            '''create unique index %s_idx on %s(chatid)''' % (self.user_states_table_name, self.user_states_table_name)

        # messages
        self.messages_table_name = 'messages'
        self.create_messages_table_sql = \
            '''create table if not exists %s (date text, time text, session int, id int, chatid text, msg text, public int)''' \
            % self.messages_table_name
        self.create_messages_index_sql = \
            '''create unique index %s_idx on %s(id,chatid,public)''' % (self.messages_table_name, self.messages_table_name)

    def init(self):
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

        # Create tables`
        self.cursor.execute(self.create_txn_table_sql)
        self.logger.info('Table %s is created' % self.txn_table_name)

        self.cursor.execute(self.create_user_states_table_sql)
        self.logger.info('Table %s is created' % self.user_states_table_name)

        self.cursor.execute(self.create_messages_table_sql)
        self.logger.info('Table %s is created' % self.create_messages_table_sql)

        # During cold start
        if self.cold:
            self.logger.info('Database is cold started')

            self.cursor.execute(self.create_txn_index_sql)
            self.logger.info('Table %s index is created' % self.txn_table_name)

            self.cursor.execute(self.create_user_states_index_sql)
            self.logger.info('Table %s index is created' % self.user_states_table_name)

            self.cursor.execute(self.create_messages_index_sql)
            self.logger.info('Table %s index is created' % self.messages_table_name)

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


