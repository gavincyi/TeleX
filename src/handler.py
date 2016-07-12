#!/bin/python
from src.channel import channel
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
        self.source_id = 0
        self.channel_id = 0
        self.message_id = 0
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

        # Get the latest channel id
        row = self.database_client.selectone(self.database_client.channels_table_name,
                                             "*",
                                             orderby="channelid desc")
        channel_record = channel.from_channel_record(row)
        self.channel_id = channel_record.channel_id
        self.logger.info("Channel id = %d" % self.channel_id)
        
        # Get the latest message id
        row = self.database_client.selectone(self.database_client.messages_table_name,
                                             "*",
                                             orderby="msgid desc")
        message_record = message.from_message_record(row)                                             
        self.message_id = message_record.msg_id
        self.logger.info("Message id = %d" % self.message_id)
        
        # Get the latest source/target id
        row = self.database_client.selectone(self.database_client.messages_table_name,
                                             "*",
                                             orderby="sourceid desc")
        message_record = message.from_message_record(row)                                             
        self.source_id = message_record.source_id         
        self.logger.info("Source id = %d" % self.source_id)
        
    def get_next_channel_id(self):
        self.channel_id += 1
        return self.channel_id
        
    def get_next_message_id(self):
        self.message_id += 1
        return self.message_id
        
    def get_next_source_id(self):
        self.source_id += 1
        return self.source_id        

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
        us = user_state(chat_id=local_chat_id, 
                        state=user_state.states.START,
                        last_channel_id=0)
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
            row = self.database_client.selectone(self.database_client.channels_table_name,
                                                 "*",
                                                 "channelid=%d" % user_state_record.last_channel_id)
            channel_record = channel.from_channel_record(row)

            if channel_record.last_msg_id == 0:
                # Error case of missing record in Channels
                self.logger.warn("Cannot find channel.\nChannel id = %d\nChat id=%d" \
                                 % (user_state_record.last_channel_id, local_chat_id))

                # Handle same as "No" for error case
                self.no_handler(bot, update)
                return

            row = self.database_client.selectone(self.database_client.messages_table_name,
                                                 "*",
                                                 "msgid=%d" % channel_record.last_msg_id)
            message_record = message.from_message_record(row)

            if message_record.source_chat_id != str(local_chat_id):
                # Error case of missing record in Messages
                self.logger.warn("Cannot find message.\nMessage id = %d\nChat id=%d" \
                                 % (channel_record.last_msg_id, local_chat_id))

                # Handle same as "No" for error case
                self.no_handler(bot, update)
                return

            # Update user state
            self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                                   user_state_record.str())

            # Acknowledge the user
            bot.sendMessage(local_chat_id,
                            text="Source %d has sent to channel" % message_record.source_id)

            # Change the state of the user first
            self.start_handler(bot, update)

            # Broadcast it in the channel
            bot.sendMessage(self.channel_name,
                            text="Time: %s %s\nSource ID: %d\nQuery: %s"%
                                 (message_record.date, \
                                  message_record.time[:-8], \
                                  message_record.source_id, \
                                  message_record.msg))

        elif user_state_record.prev_state == user_state.states.RESPONSE_PENDING_CONFIRM:
            row = self.database_client.selectone(self.database_client.channels_table_name,
                                                 "*",
                                                 "channelid=%d" % user_state_record.last_channel_id)
            channel_record = channel.from_channel_record(row)

            if channel_record.channel_id != user_state_record.last_channel_id or \
               channel_record.source_chat_id != str(local_chat_id):
                # Error case for not finding channel id
                self.logger.warn("Channel id %d / Src id %d is not found." \
                                 % (user_state_record.last_channel_id, channel_record.source_chat_id))
                self.no_handler(bot, update)
                return

            if channel_record.live == 0:
                # The counterparty has closed the channel
                bot.sendMessage(local_chat_id,
                                text="Target ID %d is no longer valid" % channel_record.target_id,
                                reply_markup=telegram.ReplyKeyboardHide())
                self.no_handler(bot, update)
                return

            row = self.database_client.selectone(self.database_client.messages_table_name,
                                                 "*",
                                                 "msgid=%d" % channel_record.last_msg_id)
            message_record = message.from_message_record(row)

            if message_record.source_chat_id != str(local_chat_id):
                # Error case of not finding source id in message
                self.logger.warn("Src id %d is not found in message" % message_record.source_chat_id)
                self.no_handler(bot, update)
                return

            # Update user state
            self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                                   user_state_record.str())

            # Acknowledge the user
            bot.sendMessage(local_chat_id,
                            text="Target ID %d has sent." % channel_record.target_id)

            # Change the state of the user first
            self.start_handler(bot, update)

            # Send it back to the target id
            bot.sendMessage(channel_record.target_chat_id,
                            text="Time: %s %s\nSource : %d\nResponse : %s"%
                            (message_record.date, \
                             message_record.time, \
                             message_record.source_id,
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
        row = self.database_client.selectone(self.database_client.channels_table_name,
                                             "*",
                                             "channelid=%d" % user_state_record.last_channel_id)
        channel_record = channel.from_channel_record(row)

        if channel_record.source_chat_id != str(local_chat_id) or \
           channel_record.live == 0:
            # The channel is suddenly shutted down by the requester. Need to cancel the action
            bot.sendMessage(local_chat_id,
                            text="Target ID %d is no longer valid." % channel_record.target_id,
                            reply_markup=telegram.ReplyKeyboardHide())
            self.no_handler(bot, update)
            return

        # Update message first
        msg = update.message.text
        message_id = self.get_next_message_id()
        message_record = message(msg_id=message_id,
                                 channel_id=channel_record.channel_id,
                                 source_id=channel_record.source_id,
                                 source_chat_id=channel_record.source_chat_id,
                                 msg=msg)
        self.database_client.insert_or_replace(self.database_client.messages_table_name,
                                               message_record.str())

        # Update channel
        # WARNING: Beware of the race condition! The requester may have blocked the channel
        #          when the message is still storing. Late update on channel!
        channel_record.last_msg_id = message_id
        self.database_client.insert_or_replace(self.database_client.channels_table_name,
                                               channel_record.str())

        # Update user state
        self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                               user_state_record.str())

        bot.sendMessage(local_chat_id,
                        text=("Confirm your response:\n" + \
                              ("Target ID: %d\n" % channel_record.target_id) + \
                              ("Response: %s" % msg)),
                        reply_markup=self.yes_no_keyboard)

    def response_msg_set_value_handler(self, bot, update, user_state_record):
        """
        Free text on state RESPONSE_PENDING_MSG handler
        :param bot: Callback bot
        :param update: Callback update
        :param user_state_record: User state object
        """
        local_chat_id = update.message.chat_id
        target_id = int(update.message.text)

        row = self.database_client.selectone(self.database_client.channels_table_name,
                                             "*",
                                             "targetid=%d and sourcechatid='%d'" % (target_id, local_chat_id))
        channel_row = channel.from_channel_record(row)

        if channel_row.target_id == target_id and channel_row.source_chat_id == str(local_chat_id):
            # Channel has been opened between the two users
            if channel_row.live == 0:
                # The communication is no longer live. Need to reject it
                bot.sendMessage(local_chat_id,
                                text="Target ID %d has been closed." % target_id,
                                reply_markup=telegram.ReplyKeyboardHide())
                self.no_handler(bot, update)
                return

            # The communication is still live. No new rows needed to be added in Channels.
            # Update channels
            channel_row.last_msg_id = 0
            self.database_client.insert_or_replace(self.database_client.channels_table_name,
                                                   channel_row.str())

            # Update last channel id on user_state
            user_state_record.last_channel_id = channel_row.channel_id
        else:
            # Channel is not opened between the two users. Need to check whether the
            # target_id points to a query
            row = self.database_client.selectone(self.database_client.channels_table_name,
                                                 "*",
                                                 "targetid=%d and sourcechatid=''" % target_id)
            channel_row = channel.from_channel_record(row)

            if channel_row.target_id == target_id and \
               channel_row.public == 1 and \
               channel_row.live == 1:
                # Target id point to a valid query
                source_id = self.get_next_source_id()

                # Update channels
                channel_id = self.get_next_channel_id()
                channel_src2tar = channel(channel_id=channel_id,
                                          source_id=source_id,
                                          source_chat_id=str(local_chat_id),
                                          target_id=channel_row.target_id,
                                          target_chat_id=channel_row.target_chat_id,
                                          last_msg_id=0,
                                          public=0,
                                          live=1)
                self.database_client.insert_or_replace(self.database_client.channels_table_name,
                                                       channel_src2tar.str())

                channel_id = self.get_next_channel_id()
                channel_tar2src = channel(channel_id=channel_id,
                                          target_id=source_id,
                                          target_chat_id=str(local_chat_id),
                                          source_id=channel_row.target_id,
                                          source_chat_id=channel_row.target_chat_id,
                                          last_msg_id=0,
                                          public=0,
                                          live=1)
                self.database_client.insert_or_replace(self.database_client.channels_table_name,
                                                       channel_tar2src.str())

                # Update last channel id on user_state
                user_state_record.last_channel_id = channel_src2tar.channel_id
            else:
                # The communication is no longer live. Need to reject it
                bot.sendMessage(local_chat_id,
                                text="Target ID %d is invalid or no longer live" % target_id,
                                reply_markup=telegram.ReplyKeyboardHide())
                self.no_handler(bot, update)
                pass


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
        question = update.message.text
        source_id = self.get_next_source_id()
        channel_id = self.get_next_channel_id()
        message_id = self.get_next_message_id()

        # Insert the message into database
        message_record = message(msg_id=message_id,
                                 channel_id=channel_id,
                                 source_id=source_id,
                                 source_chat_id=local_chat_id,
                                 msg=question)
        self.database_client.insert(self.database_client.messages_table_name,
                                    message_record.str())                                 

        # Insert the channel into database
        channel_record = channel(channel_id=channel_id,
                                 target_id=source_id,
                                 target_chat_id=local_chat_id,
                                 last_msg_id=message_id,
                                 public=1,
                                 live=1)
        self.database_client.insert(self.database_client.channels_table_name,
                                    channel_record.str())

        # print out
        self.logger.info(("Source id=%d\n"%source_id) + \
                         ("Channel id=%d\n"%channel_id) + \
                         ("Message id=%d\n"%message_id) + \
                         ("Message=%s\n"%question))

        # Update user state
        user_state_record.last_channel_id = channel_id
        self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                               user_state_record.str())

        # Acknowledge the demand
        bot.sendMessage(update.message.chat_id,
                        text="Confirm your question:\n%s"%question,
                        reply_markup=self.yes_no_keyboard)

