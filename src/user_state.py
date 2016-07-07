#!/bin/python

import datetime

class user_state:
    class states:
        UNDEF = 0
        START = 1
        QUERY_PENDING_MSG = 2
        QUERY_PENDING_CONFIRM = 3
        RESPONSE_PENDING_ID = 4
        RESPONSE_PENDING_MSG = 5
        RESPONSE_PENDING_CONFIRM = 6

        @staticmethod
        def from_str(state):
            return user_state.states.__dict__[state]

        @staticmethod
        def to_str(state):
            for key, value in user_state.states.__dict__.items():
                if value == state:
                    return key
            return 'UNDEF'


    class transitions:
        YES = 1
        NO = 2
        QUERYING = 3
        RESPONSING = 4

    graph = \
    {
        states.UNDEF: {},
        states.START:
            {
                transitions.QUERYING : states.QUERY_PENDING_MSG,
                transitions.RESPONSING : states.RESPONSE_PENDING_ID
            },
        states.QUERY_PENDING_MSG:
            {
                transitions.YES : states.QUERY_PENDING_CONFIRM,
                transitions.NO : states.START
            },
        states.QUERY_PENDING_CONFIRM:
            {
                transitions.YES : states.START,
                transitions.NO : states.START
            },
        states.RESPONSE_PENDING_ID:
            {
                transitions.YES : states.RESPONSE_PENDING_MSG,
                transitions.NO : states.START
            },
        states.RESPONSE_PENDING_MSG:
            {
                transitions.YES : states.RESPONSE_PENDING_CONFIRM,
                transitions.NO : states.START
            },
        states.RESPONSE_PENDING_CONFIRM:
            {
                transitions.YES : states.START,
                transitions.NO : states.START
            }
    }

    def __init__(self, chat_id='', state=0, dbrow=None):
        curr_datetime = datetime.datetime.now()
        self.date = curr_datetime.strftime("%Y%m%d")
        self.time = curr_datetime.strftime("%H:%M:%S.%f %z")
        self.chat_id = ''
        self.state = user_state.states.UNDEF

        if not dbrow:
            self.chat_id = chat_id
            self.state = state
        else:
            self.chat_id = dbrow[2]
            self.state = user_state.states.from_str(dbrow[3])

        self.prev_state = user_state.states.UNDEF

    def str(self):
        out = "'%s','%s','%s','%s'" % \
              (self.date, self.time, self.chat_id, user_state.states.to_str(self.state))
        return out

    def jump(self, trans, undef_callback=None):
        """
        Transite the state
        :param trans: Transition
        :param undef_callback: Callback function if the state is undefined
        """
        if self.state not in user_state.graph.keys():
            self.state = self.states.UNDEF
        else:
            branches = user_state.graph[self.state]

            if trans in branches.keys():
                self.state = branches[trans]
            else:
                self.state = self.states.UNDEF

        if self.state == self.states.UNDEF and undef_callback:
            undef_callback()
            self.state = self.states.START
            
    @staticmethod
    def from_user_state_record(record, set_curr_time = True):
        """
        Convert a db record to a user_state record
        :param record: Database record
        :param set_curr_time: Indicate if current date and time is set
        """
        if not record:
            ret = user_state()
        else:
            ret = user_state(chat_id=record[user_state.chat_id_index()],
                             state=user_state.states.from_str(record[user_state.state_index()]))
            if not set_curr_time:
                ret.date = record[user_state.date_index()]
                ret.time = record[user_state.time_index()]
            
        return ret
    
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
    def state_index():
        return 3        


