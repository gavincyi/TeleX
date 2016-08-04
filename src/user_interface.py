#!/bin/python

import yaml
import telegram

class user_interface():
    def __init__(self, platform, channel_name, file_path):
        self.platform = platform            # Platform name
        self.channel_name = channel_name    # Broadcast channel name
        
        with open(file_path) as stream:
            try:
                self.console = yaml.load(stream)
                
                not_found_messages = [s for s in user_interface.mandatory_messages() \
                                      if s not in self.console.keys()]
                if len(not_found_messages) > 0:
                    s = "The following fields are missing in user interface:\n"
                    s += '\n'.join(not_found_messages)
                    raise SystemError(s)
                                                      
            except yaml.YAMLError as exc:
                raise SystemError("Error interface file path: %s" % exc)                
                
    @staticmethod
    def mandatory_messages():
        return ["QueryButton",
                "ResponseButton",
                "MatchButton",
                "UnmatchButton",
                "HelpButton",
                "YesButton",
                "NoButton",
                "BackButton",
                "WelcomeMsg",
                "AskTargetIDMsg",
                "AskQueryMsg",
                "AskResponseMsg",
                "AskHelpMsg",
                "AskConfirmQueryMsg",
                "AskConfirmResponseMsg",
                "AskConfirmMatchMsg",
                "AskConfirmUnmatchMsg",
                "AskConfirmHelpMsg",
                "ConfirmQueryMsg",
                "ConfirmResponseMsg",
                "ConfirmMatchMsg",
                "ConfirmUnmatchMsg",
                "ConfirmHelpMsg",
                "MatchAndWaitMsg",
                "MatchAndExchangeMsg",
                "BroadcastQueryMsg",
                "BroadcastResponseMsg",
                "BroadcastHelpMsg",
                "InvalidTargetIDMsg",
                "CancelMsg",
                "RejectMultiplyMatchMsg",
                "RejectMultiplyUnmatchMsg"
                ]
                
    def substitute(self, msg_type, update=None, source_id=None, 
                   target_id=None, msg=None, date_time=None, chat_id=None):
        if msg_type not in self.console.keys():
            raise SystemError("Cannot find the user interface item %s" % msg_type)
        else:
            ret = self.console[msg_type]
        
        ret = ret.replace('%PLATFORM_NAME%', self.platform)
        ret = ret.replace('%CHANNEL_NAME%', self.channel_name)
        ret = ret.replace('%QUERY_BUTTON%', self.console['QueryButton'])
        ret = ret.replace('%RESPONSE_BUTTON%', self.console['ResponseButton'])
        ret = ret.replace('%MATCH_BUTTON%', self.console['MatchButton'])
        ret = ret.replace('%UNMATCH_BUTTON%', self.console['UnmatchButton'])
        ret = ret.replace('%HELP_BUTTON%', self.console['HelpButton'])
        ret = ret.replace('%YES_BUTTON%', self.console['YesButton'])
        ret = ret.replace('%NO_BUTTON%', self.console['NoButton'])
        ret = ret.replace('%BAKC_BUTTON%', self.console['BackButton'])
        
        if update is not None:
            ret = ret.replace('%USER_FIRST_NAME%', update.message.from_user.first_name)
        
        if source_id is not None:           
            ret = ret.replace('%SOURCE_ID%', str(source_id))
        
        if target_id is not None:            
            ret = ret.replace('%TARGET_ID%', str(target_id))
        
        if msg is not None:            
            ret = ret.replace('%MESSAGE%', msg)            
            
        if date_time is not None:
            ret = ret.replace('%DATETIME%', date_time)            
            
        if chat_id is not None:
            ret = ret.replace('%CHAT_ID%', chat_id)
            
        return ret
    
    def welcome(self, update):
        return self.substitute('WelcomeMsg', update=update)

    #####################################################################
    # Processing messages
    #####################################################################
    def ask_target_id(self, update):
        return self.substitute('AskTargetIDMsg', update=update)

    def ask_query(self, update):
        return self.substitute('AskQueryMsg', update=update)

    def ask_response(self, update):
        return self.substitute('AskResponseMsg', update=update)

    def ask_help(self, update):
        return self.substitute('AskHelpMsg', update=update)

    def ask_confirm_query(self, update, msg):
        return self.substitute('AskConfirmQueryMsg', update=update, msg=msg)

    def ask_confirm_response(self, update, target_id, msg):
        return self.substitute('AskConfirmResponseMsg', update=update, target_id=target_id, msg=msg)

    def ask_confirm_match(self, update, target_id):
        return self.substitute('AskConfirmMatchMsg', update=update, target_id=target_id)

    def ask_confirm_unmatch(self, update, target_id):
        return self.substitute('AskConfirmUnmatchMsg', update=update, target_id=target_id)

    def ask_confirm_help(self, update, msg):
        return self.substitute('AskConfirmHelpMsg', update=update, msg=msg)
               
    def confirm_query(self, update, source_id, query):
        return self.substitute('ConfirmQueryMsg', 
                                update=update, 
                                source_id=source_id,
                                msg=query)

    def confirm_response(self, update, target_id, response):
        return self.substitute('ConfirmResponseMsg', 
                                update=update, 
                                target_id=target_id,
                                msg=response)

    def confirm_match(self, update, target_id):
        return self.substitute('ConfirmMatchMsg', 
                                update=update, 
                                target_id=target_id)

    def confirm_unmatch(self, update, target_id):
        return self.substitute('ConfirmUnmatchMsg', 
                                update=update, 
                                target_id=target_id)
                          
    def confirm_help(self, update, source_id, query):
        return self.substitute('ConfirmHelpMsg', 
                               update=update, 
                               source_id=source_id,
                               msg=query)

    def match_and_wait(self, update, target_id):
        return self.substitute('MatchAndWaitMsg',
                                update=update,
                                target_id=target_id)
    
    def match_and_exchange(self, update, target_id):
        return self.substitute('MatchAndExchangeMsg',
                                update=update,
                                target_id=target_id)

    #####################################################################
    # Broadcast message
    #####################################################################
    def broadcast_query(self, update, message_record):
        return self.substitute('BroadcastQueryMsg',
                                update=update, 
                                source_id=message_record.source_id,
                                msg=message_record.msg,
                                date_time="%s %s" % (message_record.date, message_record.time[0:8]))

    def broadcast_response(self, update, message_record):
        return self.substitute('BroadcastResponseMsg',
                                update=update, 
                                source_id=message_record.source_id,
                                msg=message_record.msg,
                                date_time="%s %s" % (message_record.date, message_record.time[0:8]))        

    def broadcast_help(self, update, message_record):
        return self.substitute('BroadcastHelpMsg',
                                update=update, 
                                source_id=message_record.source_id,
                                msg=message_record.msg,
                                chat_id=message_record.source_chat_id,
                                date_time="%s %s" % (message_record.date, message_record.time[0:8]))        

    #####################################################################
    # Cancel or error message
    #####################################################################
    def invalid_target_id(self, update, target_id):
        return self.substitute('InvalidTargetIDMsg',
                                update=update,  
                                target_id=target_id)

    def cancel(self, update):
        return self.substitute('CancelMsg',
                                update=update)

    def reject_multiply_match(self, update, target_id):
        return self.substitute('RejectMultiplyMatchMsg',
                                update=update,  
                                target_id=target_id)

    def reject_multiply_unmatch(self, update, target_id):
        return self.substitute('RejectMultiplyUnmatchMsg',
                                update=update,  
                                target_id=target_id)

    #####################################################################
    # Keyboard
    #####################################################################
    def query_key_name(self, with_slash=True):
        if with_slash:
            return '/' + self.console['QueryButton']
        else:
            return self.console['QueryButton']

    def response_key_name(self, with_slash=True):
        if with_slash:
            return '/' + self.console['ResponseButton']
        else:
            return self.console['ResponseButton']

    def help_key_name(self, with_slash=True):
        if with_slash:
            return '/' + self.console['HelpButton']
        else:
            return self.console['HelpButton']

    def yes_key_name(self, with_slash=True):
        if with_slash:
            return '/' + self.console['YesButton']
        else:
            return self.console['YesButton']

    def no_key_name(self, with_slash=True):
        if with_slash:
            return '/' + self.console['NoButton']
        else:
            return self.console['NoButton']
            
    def back_key_name(self, with_slash=True):
        if with_slash:
            return '/' + self.console['BackButton']
        else:
            return self.console['BackButton']

    def match_key_name(self, with_slash=True):
        if with_slash:
            return '/' + self.console['MatchButton']
        else:
            return self.console['MatchButton']

    def unmatch_key_name(self, with_slash=True):
        if with_slash:
            return '/' + self.console['UnmatchButton']
        else:
            return self.console['UnmatchButton']

    def back_key_name(self, with_slash=True):
        if with_slash:
            return '/' + self.console['BackButton']
        else:
            return self.console['BackButton']
        
    def main_keyboard(self):
        return telegram.ReplyKeyboardMarkup(
                [[self.query_key_name(), self.response_key_name()],
                 [self.match_key_name(), self.unmatch_key_name(), self.help_key_name()]
                ])        
                
    def back_keyboard(self):
        return telegram.ReplyKeyboardMarkup(
                 [[self.back_key_name()]])                
                 
    def yes_no_keyboard(self):
        return telegram.ReplyKeyboardMarkup(
                 [[self.yes_key_name(), self.no_key_name()]])                 

    def yes_contact_no_keyboard(self): 
        return telegram.ReplyKeyboardMarkup(
                 [[telegram.KeyboardButton(text=self.yes_key_name(),request_contact=True), self.no_key_name()]])                 
        