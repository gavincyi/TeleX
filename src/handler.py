#!/bin/python
from src.txn import txn
from src.user_state import user_state
from src.message import message
import telegram


class handler:
    def __init__(self, logger, conf):
        self.logger = logger
        self.conf = conf
        self.session = 0
        self.channel_name = conf.channel_name
        self.id = 0
        self.main_keyboard = telegram.ReplyKeyboardMarkup(
                              [['/' + handler.query_handler_name(), '/' + handler.response_handler_name()],
                               ['/' + handler.match_handler_name(), '/' + handler.no_match_handler_name(), '/' + handler.help_handler_name()]])
        self.back_keyboard = telegram.ReplyKeyboardMarkup(
                             [['/' + handler.back_handler_name()]])
        self.yes_no_keyboard = telegram.ReplyKeyboardMarkup(
                             [['/' + handler.yes_handler_name(), '/' + handler.no_handler_name()]])

    @staticmethod
    def query_handler_name():
        return 'Query'

    @staticmethod
    def response_handler_name():
        return 'Response'

    @staticmethod
    def help_handler_name():
        return 'Help'

    @staticmethod
    def yes_handler_name():
        return 'Yes'

    @staticmethod
    def no_handler_name():
        return 'No'

    @staticmethod
    def back_handler_name():
        return 'Back'

    @staticmethod
    def match_handler_name():
        return 'Match'

    @staticmethod
    def no_match_handler_name():
        return 'NoMatch'

    @staticmethod
    def back_handler_name():
        return 'Back'

    def init_db(self, database_client):
        self.database_client = database_client

        # Get the latest id
        row = self.database_client.selectone(self.database_client.txn_table_name,
                                             "*",
                                             "session = %d" % self.session,
                                             "session desc, inid desc")
        txn_record = txn.from_txn_record(row)

        if txn_record.session == self.session and self.id > 0:
            self.id = 0
        else:
            self.id = txn_record.in_id

        self.logger.info("Current Id = %d" % self.id)

    def get_user_next_state(self, bot, update, transition):
        """
        Get the next state from user_state record
        :param bot: Callback bot
        :param update: Callback update
        :param transition: Transition state
        :return:
        local_chat_id - The chat id of the update
        user_state_record - The updated user_state
        """
        local_chat_id = update.message.chat_id
        row = self.database_client.selectone(self.database_client.user_states_table_name,
                                             "*",
                                             "chatid=%s"%local_chat_id)

        user_state_record = user_state.from_user_state_record(row)
        user_state_record.jump(transition)

        return local_chat_id, user_state_record


    def start_handler(self, bot, update):
        """
        Start handler
        :param bot: Callback bot
        :param update: Callback update
        """
        # Update user state
        local_chat_id = update.message.chat_id
        us = user_state(local_chat_id, user_state.states.START)
        self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                               us.str())

        # Welcome message
        print_out = 'Welcome to TeleX, %s!\n'%update.message.from_user.first_name
        print_out += "TeleX is a community to connect demand and provider.\n"
        print_out += "The identity is not revealed until the request and response are matched.\n"

        # Send out message
        bot.sendMessage(local_chat_id,
                        text=print_out,
                        reply_markup = self.main_keyboard)

    def query_handler(self, bot, update):
        """
        Query handler
        :param bot: Callback bot
        :param update: Callback update
        """
        local_chat_id, user_state_record = self.get_user_next_state(bot, update, user_state.transitions.QUERYING)

        if user_state_record.chat_id == str(local_chat_id) and \
           user_state_record.state == user_state.states.QUERY_PENDING_MSG:
            # Update user state
            self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                                   user_state_record.str())
            # Send out message
            bot.sendMessage(local_chat_id,
                            text="Please tell me your query.",
                            reply_markup=self.back_keyboard)
        else:
            self.logger.warn("%s: No transition state for %s" % (local_chat_id, "QUERYING"))
            self.no_handler(bot, update)

    def response_handler(self, bot, update):
        """
        Response handler
        :param bot: Callback bot
        :param update: Callback update
        """
        local_chat_id, user_state_record = self.get_user_next_state(bot, update, user_state.transitions.RESPONSING)

        if user_state_record.chat_id == str(local_chat_id) and \
           user_state_record.state == user_state.states.RESPONSE_PENDING_ID:
            # Update user state
            self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                                   user_state_record.str())
            # Send out message
            bot.sendMessage(local_chat_id,
                            text="Please input the target ID.",
                            reply_markup=self.back_keyboard)
        else:
            self.logger.warn("%s: No transition state for %s" % (local_chat_id, "RESPONSING"))
            self.no_handler(bot, update)

    def yes_handler(self, bot, update):
        """
        Yes button handler
        :param bot: Callback bot
        :param update: Callback update
        """
        local_chat_id, user_state_record= self.get_user_next_state(bot, update, user_state.transitions.YES)

        if user_state_record.prev_state == user_state.states.QUERY_PENDING_CONFIRM:
            row = self.database_client.selectone(self.database_client.messages_table_name,
                                                 "*",
                                                 "session = %d and chatid = '%s'" % (self.session, local_chat_id),
                                                 "date desc, time desc")
            message_record = message.from_message_record(row)

            if message_record == 0:
                self.logger.warn("Cannot find message. (session = %d, chatid = %d)" %
                                 (self.session, local_chat_id))

                # Handle same as "No" for error case
                self.no_handler(bot, update)

            else:
                # Update user state
                self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                                       user_state_record.str())

                # Acknowledge the user
                bot.sendMessage(local_chat_id,
                                text="Query %d has sent to channel" % message_record.id)

                # Change the state of the user first
                self.start_handler(bot, update)

                # Broadcast it in the channel
                bot.sendMessage(self.channel_name,
                                text="Time: %s %s\nSource: %d\nQuery: %s"%
                                     (message_record.date, \
                                      message_record.time, \
                                      message_record.id, \
                                      message_record.msg))

        elif user_state_record.prev_state == user_state.states.RESPONSE_PENDING_CONFIRM:
            row = self.database_client.selectone(self.database_client.messages_table_name,
                                                 "*",
                                                 "session = %d and chatid = '%s'" % (self.session, local_chat_id),
                                                 "date desc, time desc")
            message_record = message.from_message_record(row)

            row = self.database_client.selectone(self.database_client.txn_table_name,
                                                 "*",
                                                 "session = %d and inchatid = '%s'" % (self.session,local_chat_id),
                                                 "date desc, time desc")
            txn_record = txn.from_txn_record(row)

            if message_record.id == 0 or txn_record.in_id == 0:
                if message_record.id == 0:
                    self.logger.warn("Cannot find message. (session = %d, chatid = %d)" %
                                     (self.session, local_chat_id))
                if txn_record.in_id == 0:
                    self.logger.warn("Cannot find txn. (session = %d, inchatid = '%s'" %
                                     (self.session, local_chat_id))

                # Handle same as "No" for error case
                self.no_handler(bot, update)

            else:
                out_id = txn_record.out_id
                out_chat_id = txn_record.out_chat_id
                msg = message_record.msg

                # Update user state
                self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                                       user_state_record.str())

                # Acknowledge the user
                bot.sendMessage(local_chat_id,
                                text="Target %d has sent" % out_id )

                # Change the state of the user first
                self.start_handler(bot, update)

                # Send it back to the target id
                bot.sendMessage(out_chat_id,
                                text="Time: %s %s\nSource : %d\nResponse : %s"%
                                (message_record.date, \
                                 message_record.time, \
                                 message_record.id, \
                                 message_record.msg))

    def no_handler(self, bot, update):
        """
        No button handler
        :param bot: Callback bot
        :param update: Callback update
        """
        local_chat_id, user_state_record = self.get_user_next_state(bot, update, user_state.transitions.NO)

        # Update user state
        self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                               user_state_record.str())

        # Send out message
        bot.sendMessage(local_chat_id,
                        text="Action has been canceled.",
                        reply_markup=telegram.ReplyKeyboardHide())
        self.start_handler(bot, update)

    def help_handler(self, bot, update):
        """
        Help handler
        :param bot: Callback bot
        :param update: Callback update
        """
        self.logger.info("Not yet implemented")

    def set_value_handler(self, bot, update):
        """
        Free text handler
        :param bot: Callback bot
        :param update: Callback update
        """
        local_chat_id, user_state_record = self.get_user_next_state(bot, update, user_state.transitions.YES)

        if user_state_record.chat_id == str(local_chat_id):
            if user_state_record.state == user_state.states.QUERY_PENDING_CONFIRM:
                self.query_set_value_handler(bot, update, user_state_record)
            elif user_state_record.state == user_state.states.RESPONSE_PENDING_MSG:
                self.response_msg_set_value_handler(bot, update, user_state_record)
            elif user_state_record.state == user_state.states.RESPONSE_PENDING_CONFIRM:
                self.response_confirm_set_value_handler(bot, update, user_state_record)

    def response_confirm_set_value_handler(self, bot, update, user_state_record):
        """
        Free text on state RESPONSE_PENDING_CONFIRM handler
        :param bot: Callback bot
        :param update: Callback update
        :param user_state_record: User state object
        """
        local_chat_id = update.message.chat_id
        row = self.database_client.selectone(self.database_client.messages_table_name,
                                             "*",
                                             "session = %d and chatid=%s and public=0" % (self.session, local_chat_id),
                                             "date desc, time desc")
        message_record = message.from_message_record(row)

        if message_record.id == 0:
            self.logger.warn("Cannot find the chatid (%s) from message" % local_chat_id)
            self.no_handler(bot, update)
            return

        row = self.database_client.selectone(self.database_client.txn_table_name,
                                             "*",
                                             "session = %d and inid = %d" % (self.session, message_record.id),
                                             "date desc, time desc")
        txn_record = txn.from_txn_record(row)

        if txn_record.in_id == 0:
            self.logger.warn("Cannot find the inchatid (%s) from txn" % local_chat_id)
            self.no_handler(bot, update)
            return
        else:
            # Store the message
            message_record = message(session=self.session,
                                     id=txn_record.in_id,
                                     chat_id=str(local_chat_id),
                                     msg=update.message.text,
                                     public=0)

            # Update message table
            self.database_client.insert_or_replace(self.database_client.messages_table_name,
                                                   message_record.str())

            # Update user state
            self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                                   user_state_record.str())

            bot.sendMessage(local_chat_id,
                            text="Confirm your response:\n%s"%message_record.msg,
                            reply_markup=self.yes_no_keyboard)

    def response_msg_set_value_handler(self, bot, update, user_state_record):
        """
        Free text on state RESPONSE_PENDING_MSG handler
        :param bot: Callback bot
        :param update: Callback update
        :param user_state_record: User state object
        """
        query_id = update.message.text
        local_chat_id = update.message.chat_id
        row = self.database_client.selectone(self.database_client.messages_table_name,
                                             "*",
                                             "session=%d and id=%s" % (self.session,query_id))
        message_record = message.from_message_record(row)

        row = self.database_client.selectone(self.database_client.txn_table_name,
                                             "*",
                                             "session=%d and outid=%s and inchatid='%d'"%
                                             (self.session, query_id, local_chat_id))
        txn_record = txn.from_txn_record(row)

        if message_record.public == 1:
            # Indicate it is to reply a query
            if txn_record.in_id == 0:
                # Indicate the response has not been built before
                self.id += 1
                txn_record = txn(session=self.session,
                                 out_id=message_record.id,
                                 out_chat_id=message_record.chat_id,
                                 in_id=self.id,
                                 in_chat_id=local_chat_id)
                self.database_client.insert_or_replace(self.database_client.txn_table_name,
                                                       txn_record.str())
            else:
                # Indicate the response has been built before
                self.database_client.insert_or_replace(self.database_client.txn_table_name,
                                                       txn_record.str())
        else:
            # Indicate it is to reply a response to its query
            if txn_record.in_id == 0:
                # Indicate the response has not been built before
                row = self.database_client.selectone(self.database_client.txn_table_name,
                                                     "*",
                                                     "session=%d and inid=%s and outchatid='%d'"%
                                                     (self.session, query_id, local_chat_id))
                txn_record = txn.from_txn_record(row)

                if txn_record.in_id == 0:
                    # query_id has not replied to the query before
                    bot.sendMessage(local_chat_id,
                                    text="Invalid target ID <%s>" % query_id,
                                    reply_markup=telegram.ReplyKeyboardHide())
                    return
                else:
                    txn_record = txn(session=self.session,
                                     out_id=txn_record.in_id,
                                     out_chat_id=txn_record.in_chat_id,
                                     in_id=txn_record.out_id,
                                     in_chat_id=txn_record.out_chat_id)
                    self.database_client.insert_or_replace(self.database_client.txn_table_name,
                                                           txn_record.str())

        # Update message
        message_record = message(session=self.session,
                                 id=self.id,
                                 chat_id=local_chat_id,
                                 msg='',
                                 public=0)
        self.database_client.insert_or_replace(self.database_client.messages_table_name,
                                               message_record.str())

        # Update user state
        self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                               user_state_record.str())

        bot.sendMessage(update.message.chat_id,
                        text="Please input the response.",
                        reply_markup=self.back_keyboard)

    def query_set_value_handler(self, bot, update, user_state_record):
        """
        Free text on state QUERY_PENDING_MSG handler
        :param bot: Callback bot
        :param update: Callback update
        :param user_state_record: User state object
        """
        local_chat_id = update.message.chat_id

        # Increment id to provide an unique id
        self.id += 1

        # Insert the transaction into database
        txn_record = txn(self.session, self.id, local_chat_id)
        self.database_client.insert(self.database_client.txn_table_name,
                                    txn_record.str())

        # print out
        question = update.message.text
        self.logger.info("Query <%d> ChatId <%s>: %s"%(self.id, \
                                                       update.message.chat_id, \
                                                       question))

        # Update user state
        self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                               user_state_record.str())

        # Insert question into messages
        message_record = message(session=self.session,
                                 id=self.id,
                                 chat_id=local_chat_id,
                                 public=1,
                                 msg=question)
        self.database_client.insert_or_replace(self.database_client.messages_table_name,
                                               message_record.str())

        # Acknowledge the demand
        bot.sendMessage(update.message.chat_id,
                        text="Confirm your question:\n%s"%question,
                        reply_markup=self.yes_no_keyboard)

