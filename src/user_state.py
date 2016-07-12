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
        MATCH_PENDING_ID = 7
        MATCH_PENDING_CONFIRM = 8
        UNMATCH_PENDING_ID = 9
        UNMATCH_PENDING_CONFIRM = 10

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
        UNDEF = 0
        YES = 1
        NO = 2
        QUERYING = 3
        RESPONSING = 4
        MATCHING = 5
        UNMATCHING = 6

        @staticmethod
        def from_str(trans):
            return user_state.transitions.__dict__[trans]

        @staticmethod
        def to_str(trans):
            for key, value in user_state.transitions.__dict__.items():
                if value == trans:
                    return key
            return 'UNDEF'

    graph = \
    {
        states.UNDEF: {},
        states.START:
            {
                transitions.QUERYING : states.QUERY_PENDING_MSG,
                transitions.RESPONSING : states.RESPONSE_PENDING_ID,
                transitions.MATCHING : states.MATCH_PENDING_ID,
                transitions.UNMATCHING : states.UNMATCH_PENDING_ID,
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
            },
        states.MATCH_PENDING_ID:
            {
                transitions.YES : states.MATCH_PENDING_CONFIRM,
                transitions.NO : states.START
            },
        states.UNMATCH_PENDING_ID:
            {
                transitions.YES : states.UNMATCH_PENDING_CONFIRM,
                transitions.NO : states.START
            },
        states.MATCH_PENDING_CONFIRM:
            {
                transitions.YES : states.START,
                transitions.NO : states.START
            },
        states.UNMATCH_PENDING_CONFIRM:
            {
                transitions.YES : states.START,
                transitions.NO : states.START
            }
    }

    def __init__(self, chat_id='', \
                       state=states.UNDEF, \
                       prev_state=states.UNDEF,
                       transition=transitions.UNDEF,
                       last_channel_id=0):
        curr_datetime = datetime.datetime.now()
        self.date = curr_datetime.strftime("%Y%m%d")
        self.time = curr_datetime.strftime("%H:%M:%S.%f %z")
        self.chat_id = chat_id
        self.state = state
        self.prev_state = prev_state
        self.transition = transition
        self.last_channel_id = last_channel_id

    def str(self):
        """
        Output the object into a comma separated string
        """              
        return "'%s','%s','%s','%s','%s','%s',%d" % \
              (self.date, \
               self.time, \
               self.chat_id, \
               user_state.states.to_str(self.state),
               user_state.states.to_str(self.prev_state),
               user_state.transitions.to_str(self.transition),
               self.last_channel_id)

    def jump(self, trans, undef_callback=None):
        """
        Transite the state
        :param trans: Transition
        :param undef_callback: Callback function if the state is undefined
        """
        if self.state not in user_state.graph.keys():
            self.prev_state = self.states.UNDEF
            self.transition = self.transitions.UNDEF
            self.state = self.states.UNDEF
        else:
            self.prev_state = self.state
            branches = user_state.graph[self.state]

            if trans in branches.keys():
                self.transition = trans
                self.state = branches[trans]
            else:
                self.transition = self.transitions.UNDEF
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
                             state=user_state.states.from_str(record[user_state.state_index()]),
                             prev_state=user_state.states.from_str(record[user_state.prev_state_index()]),
                             transition=user_state.transitions.from_str(record[user_state.transition_index()]),
                             last_channel_id=record[user_state.last_channel_id_index()])
            if not set_curr_time:
                ret.date = record[user_state.date_index()]
                ret.time = record[user_state.time_index()]
            
        return ret
    
    @staticmethod
    def field_str():
        return "date text, time text, chatid text, state text, " + \
               "prevstate text, transit text, lastchannelid int"
               
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
    def state_index():
        return 3

    @staticmethod
    def prev_state_index():
        return 4

    @staticmethod
    def transition_index():
        return 5

    @staticmethod
    def last_channel_id_index():
        return 6

