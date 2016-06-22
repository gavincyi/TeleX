#!/bin/python

import sqlite3
import os
import datetime

class db_client():
    def __init__(self, logger):
        self.logger = logger
        self.db_file = os.path.abspath(__file__ + "/../../db/telex.sqlite")

        # const
        self.txn_table_name = 'txn'
        self.create_txn_table_sql = \
             '''create table if not exists %s (date text, time text, session int, outid int, outchatid text, inid int, inchatid text)'''\
             % self.txn_table_name
        self.create_txn_index_sql = \
             '''create unique index %s_idx on %s(session, inid)''' % (self.txn_table_name, self.txn_table_name)

    def init(self, cold_start = False):
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

        # Create tables`
        self.cursor.execute(self.create_txn_table_sql)

        # During cold start
        if cold_start:
            self.cursor.execute(self.create_txn_index_sql)

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

