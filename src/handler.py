#!/bin/python
from src.channel import channel
from src.user_state import user_state
from src.message import message
from src.screen_messages import screen_messages
from src.contact import contact
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
        self.yes_contact_no_keyboard = telegram.ReplyKeyboardMarkup(
            [[telegram.KeyboardButton(text='/' + handler.yes_handler_name(),request_contact=True), '/' + handler.no_handler_name()]])

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

    def get_last_channel(self, user_state_record):
        """
        Get the last channel record by the last_channel_id in object user_state
        :param user_state_record: The object of user_state
        :return: The object of channel if succeeded; otherwise None
        """
        row = self.database_client.selectone(self.database_client.channels_table_name,
                                             "*",
                                             "channelid=%d" % user_state_record.last_channel_id)
        channel_record = channel.from_channel_record(row)

        if channel_record.channel_id != user_state_record.last_channel_id:
            # Error case of missing record in Channels
            self.logger.warn("Cannot find channel.\nChannel id = %d\nChat id=%s" \
                             % (user_state_record.last_channel_id, user_state_record.chat_id))
            return None
        else:
            return channel_record

    def get_last_message(self, last_msg_id):
        """
        Get the last message record by the last_msg_id in object channel
        :param channel_record: The object of channel
        :return: The object of message if succeeded; otherwise None
        """
        row = self.database_client.selectone(self.database_client.messages_table_name,
                                             "*",
                                             "msgid=%d" % last_msg_id)
        message_record = message.from_message_record(row)

        if message_record.msg_id != last_msg_id:
            # Error case of missing record in Messages
            self.logger.warn("Cannot find message.\nMessage id = %d" % last_msg_id)
            return None
        else:
            return message_record

    def handler_by_replying(self, bot, update, \
                            trans=user_state.transitions.UNDEF, \
                            expected_state=user_state.states.UNDEF, \
                            reply_msg=''):
        """

        :param bot: Callback bot
        :param update: Callback update
        :param trans: Transition in user_state
        :param expected_state: Expected state in user_state
        :param reply_msg: String, the reply message
        """
        local_chat_id, user_state_record = self.get_user_next_state(bot, update, trans)

        if user_state_record.chat_id == str(local_chat_id) and \
                        user_state_record.state == expected_state:
            self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                                   user_state_record.str())
            # Send out message
            bot.sendMessage(local_chat_id,
                            text=reply_msg,
                            reply_markup=self.back_keyboard)
        else:
            self.logger.debug("%s: No transition of %d from %d to %d" \
                              % (local_chat_id, trans, user_state_record.prev_state, expected_state))
            self.no_handler(bot, update)

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
        self.handler_by_replying(bot, update,
                                 user_state.transitions.QUERYING,
                                 user_state.states.QUERY_PENDING_MSG,
                                 screen_messages.ask_query())

    def response_handler(self, bot, update):
        """
        Response handler
        :param bot: Callback bot
        :param update: Callback update
        """
        self.handler_by_replying(bot, update,
                                 user_state.transitions.RESPONSING,
                                 user_state.states.RESPONSE_PENDING_ID,
                                 screen_messages.ask_target_id())

    def match_handler(self, bot, update):
        """
        Match button handler
        :param bot: Callback bot
        :param update: Callback update
        """
        self.handler_by_replying(bot, update,
                                 user_state.transitions.MATCHING,
                                 user_state.states.MATCH_PENDING_ID,
                                 screen_messages.ask_target_id())

    def unmatch_handler(self, bot, update):
        """
        NoMatch button handler
        :param bot: Callback bot
        :param update: Callback update
        """
        self.handler_by_replying(bot, update,
                                 user_state.transitions.UNMATCHING,
                                 user_state.states.UNMATCH_PENDING_ID,
                                 screen_messages.ask_target_id())

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
        """
        :param bot: Callback bot
        :param update: Callback update
        :param local_chat_id: Local chat id, in data type of Telegram chat id
        :param user_state_record: The object user_state
        """
        message_record = self.get_last_message(user_state_record.last_msg_id)

        if not message_record:
            # Error case of missing record in Messages
            self.no_handler(bot, update)
            return

        # Update user state
        self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                               user_state_record.str())

        # Insert channel
        channel_record = channel(channel_id=self.get_next_channel_id(),
                                 target_id=user_state_record.last_target_id,
                                 target_chat_id=user_state_record.chat_id,
                                 public=1,
                                 live=1,
                                 match=0)
        self.database_client.insert_or_replace(self.database_client.channels_table_name,
                                               channel_record.str())

        # Acknowledge the user
        bot.sendMessage(local_chat_id,
                        text=screen_messages.confirm_send_query(message_record.source_id,
                                                                message_record.msg),
                        reply_markup=telegram.ReplyKeyboardHide())

        # Change the state of the user first
        self.start_handler(bot, update)

        # Broadcast it in the channel
        bot.sendMessage(self.channel_name,
                        text=screen_messages.broadcast_query(message_record))

    def response_confirmed_yes_handler(self, bot, update, local_chat_id, user_state_record):
        message_record = self.get_last_message(user_state_record.last_msg_id)

        if not message_record:
            # Error case of not finding source id in message
            self.no_handler(bot, update)
            return

        # Create channel
        row = self.database_client.selectone(self.database_client.channels_table_name,
                                             "*",
                                             "targetid=%d and sourcechatid='%s'" \
                                             % (user_state_record.last_target_id, user_state_record.chat_id))
        channel_record = channel.from_channel_record(row)

        if channel_record.target_id == user_state_record.last_target_id and \
           channel_record.source_chat_id == user_state_record.chat_id and \
           channel_record.live == 1:
            # Continue the opened channel
            target_chat_id=int(channel_record.target_chat_id)
            message_record.source_id=channel_record.source_id
            message_record.channel_id=channel_record.channel_id
        else:
            row = self.database_client.selectone(self.database_client.channels_table_name,
                                                 "*",
                                                 "targetid=%d and sourcechatid='' and public=1 and live=1" \
                                                 % user_state_record.last_target_id)
            channel_record = channel.from_channel_record(row)
            if channel_record.target_id == user_state_record.last_target_id and \
               channel_record.public == 1 and \
               channel_record.live == 1:
                # The target id is a query. Create a two way channel
                channel_src2tar = channel(channel_id=self.get_next_channel_id(),
                                          source_id=self.get_next_source_id(),
                                          source_chat_id=user_state_record.chat_id,
                                          target_id=channel_record.target_id,
                                          target_chat_id=channel_record.target_chat_id,
                                          public=0,
                                          live=1,
                                          match=0)
                channel_tar2src = channel(channel_id=self.get_next_channel_id(),
                                          source_id=channel_record.target_id,
                                          source_chat_id=channel_record.target_chat_id,
                                          target_id=channel_src2tar.source_id,
                                          target_chat_id=user_state_record.chat_id,
                                          public=0,
                                          live=1,
                                          match=0)
                target_chat_id=int(channel_src2tar.target_chat_id)
                message_record.source_id=channel_src2tar.source_id
                message_record.channel_id=channel_src2tar.channel_id
                self.database_client.insert_or_replace(self.database_client.channels_table_name,
                                                       channel_src2tar.str())
                self.database_client.insert_or_replace(self.database_client.channels_table_name,
                                                       channel_tar2src.str())
            else:
                bot.sendMessage(local_chat_id,
                                text=screen_messages.inactivated_target_id(user_state_record.last_target_id),
                                reply_markup=telegram.ReplyKeyboardHide())
                self.start_handler(bot,update)
                return

        # Update message
        self.database_client.insert_or_replace(self.database_client.messages_table_name,
                                               message_record.str())

        # Update user state
        self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                               user_state_record.str())

        # Acknowledge the user
        bot.sendMessage(local_chat_id,
                        text=screen_messages.confirm_send_response_to_target(user_state_record.last_target_id),
                        reply_markup=telegram.ReplyKeyboardHide())

        # Change the state of the user first
        self.start_handler(bot, update)

        # Send it back to the target id
        bot.sendMessage(int(target_chat_id),
                        text=screen_messages.broadcast_response(message_record))

    def match_confirmed_yes_handler(self, bot, update, local_chat_id, user_state_record):
        channel_record = self.get_last_channel(user_state_record)

        if not channel_record:
            # Error case for not finding channel id
            self.no_handler(bot, update)
            return

        row = self.database_client.selectone(self.database_client.channels_table_name,
                                             "*",
                                             "targetid=%d and sourcechatid='%s'" \
                                             % (channel_record.source_id, channel_record.target_chat_id))
        channel_record_counterparty = channel.from_channel_record(row)

        if channel_record_counterparty.target_id != channel_record.source_id and \
           channel_record_counterparty.source_chat_id != channel_record.target_chat_id:
            # Error case for not finding channel id
            self.logger.warn("Channel id %d / Src id %d is not found." \
                             % (user_state_record.last_channel_id, channel_record_counterparty.source_chat_id))
            self.no_handler(bot, update)
            return

        # Update the contact
        contact_record = contact(chat_id=local_chat_id,
                                 phone_number=update.message.contact.phone_number,
                                 first_name=update.message.contact.first_name,
                                 last_name=update.message.contact.last_name)
        self.database_client.insert_or_replace(self.database_client.contacts_table_name,
                                               contact_record.str())

        if channel_record_counterparty.match == 1:
            row = self.database_client.selectone(self.database_client.contacts_table_name,
                                                 "*",
                                                 "chatid='%s'" % channel_record_counterparty.source_chat_id)
            contact_record_counterparty = contact.from_contact_record(row)

            if contact_record_counterparty.chat_id != channel_record_counterparty.source_chat_id:
                self.logger.warn("Cannot find contact by chatid = %s" % channel_record_counterparty.source_chat_id)
                self.no_handler(bot, update)
                return

            bot.sendMessage(local_chat_id,
                            text=screen_messages.match_send_contact(channel_record.target_id),
                            reply_markup=telegram.ReplyKeyboardHide())
            bot.sendContact(local_chat_id,
                            phone_number=contact_record_counterparty.phone_number,
                            first_name=contact_record_counterparty.first_name,
                            last_name=contact_record_counterparty.last_name)

            bot.sendMessage(int(contact_record_counterparty.chat_id),
                            text=screen_messages.match_send_contact(channel_record.source_id),
                            reply_markup=telegram.ReplyKeyboardHide())
            bot.sendContact(int(contact_record_counterparty.chat_id),
                            phone_number=contact_record.phone_number,
                            first_name=contact_record.first_name,
                            last_name=contact_record.last_name)

        else:
            bot.sendMessage(local_chat_id,
                            text=screen_messages.confirm_match(channel_record.target_id),
                            reply_markup=telegram.ReplyKeyboardHide())
            bot.sendMessage(local_chat_id,
                            text=screen_messages.match_and_wait_counterparty(channel_record.target_id),
                            reply_markup=telegram.ReplyKeyboardHide())

        # Update the status of field match
        channel_record.match = 1
        self.database_client.insert_or_replace(self.database_client.channels_table_name,
                                               channel_record.str())

        # Update user state
        self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                               user_state_record.str())
        self.start_handler(bot, update)

    def unmatch_confirmed_yes_handler(self, bot, update, local_chat_id, user_state_record):
        channel_record = self.get_last_channel(user_state_record)
        target_id = channel_record.target_id

        if not channel_record:
            self.no_handler(bot, update)
            return

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
                        text=screen_messages.confirm_unmatch(target_id),
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
        # Update message first
        msg = update.message.text
        message_id = self.get_next_message_id()
        message_record = message(msg_id=message_id,
                                 source_chat_id=user_state_record.chat_id,
                                 msg=msg)
        self.database_client.insert_or_replace(self.database_client.messages_table_name,
                                               message_record.str())

        # Update user state
        user_state_record.last_msg_id = message_id
        self.database_client.insert_or_replace(self.database_client.user_states_table_name,
                                               user_state_record.str())

        bot.sendMessage(int(user_state_record.chat_id),
                        text=screen_messages.ask_confirming_response(user_state_record.last_target_id, msg),
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

        if target_id <= 0:
            # Target id is not integer
            bot.sendMessage(local_chat_id,
                            text=screen_messages.inactivated_target_id(target_id),
                            reply_markup=telegram.ReplyKeyboardHide())
            self.no_handler(bot, update)
            return

        # Update user state
        user_state_record.last_target_id = target_id
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
        message_id = self.get_next_message_id()

        # Insert the message into database
        message_record = message(msg_id=message_id,
                                 source_id=source_id,
                                 source_chat_id=local_chat_id,
                                 msg=question)
        self.database_client.insert_or_replace(self.database_client.messages_table_name,
                                               message_record.str())

        # Update user state
        user_state_record.last_target_id=source_id
        user_state_record.last_msg_id=message_id
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
                            reply_markup=self.yes_contact_no_keyboard)
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
