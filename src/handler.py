#!/bin/python
from src.channel import channel
from src.user_state import user_state
from src.message import message
from src.screen_messages import screen_messages
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
                               ['/' + handler.match_handler_name(), '/' + handler.unmatch_handler_name(), '/' + handler.help_handler_name()]])
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
    def unmatch_handler_name():
        return 'Unmatch'

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

        # Send out message
        bot.sendMessage(local_chat_id,
                        text=screen_messages.welcome(update.message.from_user.first_name),
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
                            text=screen_messages.ask_query(),
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

    def match_handler(self, bot, update):
        """
        Match button handler
        :param bot: Callback bot
        :param update: Callback update
        """
        local_chat_id, user_state_record = self.get_user_next_state(bot, update, user_state.transitions.MATCHING)

        if user_state_record.chat_id == str(local_chat_id) and \
                        user_state_record.state == user_state.states.MATCH_PENDING_ID:
            self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                                   user_state_record.str())
            # Send out message
            bot.sendMessage(local_chat_id,
                            text=screen_messages.ask_target_id(),
                            reply_markup=self.back_keyboard)
        else:
            self.logger.warn("%s: No transition state for %s" % (local_chat_id, "MATCHING"))
            self.no_handler(bot, update)

    def unmatch_handler(self, bot, update):
        """
        NoMatch button handler
        :param bot: Callback bot
        :param update: Callback update
        """
        local_chat_id, user_state_record = self.get_user_next_state(bot, update, user_state.transitions.UNMATCHING)

        if user_state_record.chat_id == str(local_chat_id) and \
                        user_state_record.state == user_state.states.UNMATCH_PENDING_ID:
            self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                                   user_state_record.str())
            # Send out message
            bot.sendMessage(local_chat_id,
                            text=screen_messages.ask_target_id(),
                            reply_markup=self.back_keyboard)
        else:
            self.logger.warn("%s: No transition state for %s" % (local_chat_id, "UNMATCHING"))
            self.no_handler(bot, update)

    def yes_handler(self, bot, update):
        """
        Yes button handler
        :param bot: Callback bot
        :param update: Callback update
        """
        local_chat_id, user_state_record= self.get_user_next_state(bot, update, user_state.transitions.YES)

        if user_state_record.prev_state == user_state.states.QUERY_PENDING_CONFIRM:
            self.query_confirmed_yes_handler(bot, update, local_chat_id, user_state_record)
        elif user_state_record.prev_state == user_state.states.RESPONSE_PENDING_CONFIRM:
            self.response_confirmed_yes_handler(bot, update, local_chat_id, user_state_record)
        elif user_state_record.prev_state == user_state.states.MATCH_PENDING_CONFIRM:
            self.match_confirmed_yes_handler(bot, update, local_chat_id, user_state_record)
        elif user_state_record.prev_state == user_state.states.UNMATCH_PENDING_CONFIRM:
            self.unmatch_confirmed_yes_handler(bot, update, local_chat_id, user_state_record)
        else:
            self.no_handler(bot, update)

    def query_confirmed_yes_handler(self, bot, update, local_chat_id, user_state_record):
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
                        text=screen_messages.confirm_send_query(message_record.source_id, \
                                                                message_record.msg),
                        reply_markup=telegram.ReplyKeyboardHide())

        # Change the state of the user first
        self.start_handler(bot, update)

        # Broadcast it in the channel
        bot.sendMessage(self.channel_name,
                        text=screen_messages.broadcast_query(message_record))

    def response_confirmed_yes_handler(self, bot, update, local_chat_id, user_state_record):
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
                            text=screen_messages.inactivated_target_id(channel_record.target_id),
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
                        text=screen_messages.confirm_send_response_to_target(channel_record.target_id),
                        reply_markup=telegram.ReplyKeyboardHide())

        # Change the state of the user first
        self.start_handler(bot, update)

        # Send it back to the target id
        bot.sendMessage(channel_record.target_chat_id,
                        text=screen_messages.broadcast_response(message_record))

    def match_confirmed_yes_handler(self, bot, update, local_chat_id, user_state_record):
        pass

    def unmatch_confirmed_yes_handler(self, bot, update, local_chat_id, user_state_record):
        row = self.database_client.selectone(self.database_client.channels_table_name,
                                             "*",
                                             "channelid=%d" % user_state_record.last_channel_id)
        channel_record = channel.from_channel_record(row)

        if channel_record.target_chat_id == str(local_chat_id) and channel_record.live == 1:
            # Close a query
            channel_record.live = 0
            self.database_client.insert_or_replace(self.database_client.channels_table_name,
                                                   channel_record.str())
        elif channel_record.source_chat_id == str(local_chat_id) and channel_record.live == 1:
            # Close a conversation
            channel_record.live = 0
            self.database_client.insert_or_replace(self.database_client.channels_table_name,
                                                   channel_record.str())

            # Close the counterparty
            row = self.database_client.selectone(self.database_client.channels_table_name,
                                                 "*",
                                                 "targetid=%d and sourcechatid='%s'" \
                                                 % (channel_record.source_id, channel_record.target_chat_id))
            channel_record = channel.from_channel_record(row)
            channel_record.live = 0
            self.database_client.insert_or_replace(self.database_client.channels_table_name,
                                                   channel_record.str())
        else:
            bot.sendMessage(local_chat_id,
                            text=screen_messages.inactivated_target_id(channel_record.target_id),
                            reply_markup=telegram.ReplyKeyboardHide())
            self.no_handler(bot, update)
            return

        # Update the user state
        self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                               user_state_record.str())

        # Restarted
        bot.sendMessage(local_chat_id,
                        text=screen_messages.confirm_unmatch(channel_record.target_id),
                        reply_markup=telegram.ReplyKeyboardHide())
        self.start_handler(bot, update)

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
                        text=screen_messages.cancel_action(),
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
        :param bot: callback bot
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
            elif user_state_record.state == user_state.states.MATCH_PENDING_CONFIRM:
                self.match_confirm_set_value_handler(bot, update, user_state_record)
            elif user_state_record.state == user_state.states.UNMATCH_PENDING_CONFIRM:
                self.unmatch_confirm_set_value_handler(bot, update, user_state_record)

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
                            text=screen_messages.inactivated_target_id(channel_record.target_id),
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
                        text=screen_messages.ask_confirming_response(channel_record.target_id, msg),
                        reply_markup=self.yes_no_keyboard)

    def response_msg_set_value_handler(self, bot, update, user_state_record):
        """
        Free text on state RESPONSE_PENDING_MSG handler
        :param bot: Callback bot
        :param update: Callback update
        :param user_state_record: User state object
        """
        local_chat_id = update.message.chat_id
        target_id = update.message.text

        if target_id.isdigit():
            target_id = int(target_id)
        else:
            # Target id is not integer
            bot.sendMessage(local_chat_id,
                            text=screen_messages.inactivated_target_id(target_id),
                            reply_markup=telegram.ReplyKeyboardHide())
            self.no_handler(bot, update)
            return

        row = self.database_client.selectone(self.database_client.channels_table_name,
                                             "*",
                                             "targetid=%d and sourcechatid='%d'" % (target_id, local_chat_id))
        channel_row = channel.from_channel_record(row)

        if channel_row.target_id == target_id and channel_row.source_chat_id == str(local_chat_id):
            # Channel has been opened between the two users
            if channel_row.live == 0:
                # The communication is no longer live. Need to reject it
                bot.sendMessage(local_chat_id,
                                text=screen_messages.inactivated_target_id(target_id),
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
                                text=screen_messages.inactivated_target_id(target_id),
                                reply_markup=telegram.ReplyKeyboardHide())
                self.no_handler(bot, update)
                return

        # Update user state
        self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                               user_state_record.str())

        bot.sendMessage(update.message.chat_id,
                        text=screen_messages.ask_response(),
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

        # Update user state
        user_state_record.last_channel_id = channel_id
        self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                               user_state_record.str())

        # Acknowledge the demand
        bot.sendMessage(update.message.chat_id,
                        text=screen_messages.ask_confirming_query(question),
                        reply_markup=self.yes_no_keyboard)

    def match_confirm_set_value_handler(self, bot, update, user_state_record):
        target_id = int(update.message.text)
        row = self.database_client.selectone(self.database_client.channels_table_name,
                                             "*",
                                             "targetid=%d and sourcechatid='%s'" \
                                             % (target_id, user_state_record.chat_id))
        channel_record = channel.from_channel_record(row)

        if channel_record.target_id == target_id and \
           channel_record.source_chat_id == user_state_record.chat_id and \
           channel_record.live == 1:
            # Update the state
            user_state_record.last_channel_id = channel_record.channel_id
            self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                                   user_state_record.str())

            # Ask to confirm
            bot.sendMessage(update.message.chat_id,
                            text=screen_messages.ask_confirming_match(target_id),
                            reply_markup=self.yes_no_keyboard)
        else:
            bot.sendMessage(update.message.chat_id,
                            text=screen_messages.inactivated_target_id(target_id),
                            reply_markup=telegram.ReplyKeyboardHide())

    def unmatch_confirm_set_value_handler(self, bot, update, user_state_record):
        target_id = int(update.message.text)
        row = self.database_client.selectone(self.database_client.channels_table_name,
                                             "*",
                                             "targetid=%d and sourcechatid='%s'" \
                                             % (target_id, user_state_record.chat_id))
        channel_record = channel.from_channel_record(row)

        if channel_record.target_id == target_id and \
                        channel_record.source_chat_id == user_state_record.chat_id and \
                        channel_record.live == 1:
            # Going to close the one-to-one communication
            # Update the state
            user_state_record.last_channel_id = channel_record.channel_id
            self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                                   user_state_record.str())

            # Ask to confirm
            bot.sendMessage(update.message.chat_id,
                            text=screen_messages.ask_confirming_unmatch(target_id),
                            reply_markup=self.yes_no_keyboard)
        else:
            # Check if it is a query
            row = self.database_client.selectone(self.database_client.channels_table_name,
                                                 "*",
                                                 "targetid=%d and targetchatid='%s' and public=1 and live=1" \
                                                 % (target_id, user_state_record.chat_id))
            channel_record = channel.from_channel_record(row)

            if channel_record.target_id == target_id and channel_record.target_chat_id == user_state_record.chat_id:
                # Going to close the query
                # Update the state
                user_state_record.last_channel_id = channel_record.channel_id
                self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                                       user_state_record.str())

                # Ask to confirm
                bot.sendMessage(update.message.chat_id,
                                text=screen_messages.ask_confirming_unmatch(target_id),
                                reply_markup=self.yes_no_keyboard)
            else:
                bot.sendMessage(update.message.chat_id,
                                text=screen_messages.inactivated_target_id(target_id),
                                reply_markup=telegram.ReplyKeyboardHide())
                self.no_handler(bot, update)

