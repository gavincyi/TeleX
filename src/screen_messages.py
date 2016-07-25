#!/bin/python


class screen_messages():
    @staticmethod
    def welcome(first_name=''):
        print_out = 'Welcome to TeleX, %s!\n'%first_name
        print_out += "TeleX is a community to connect demand and provider.\n"
        print_out += "The identity is not revealed until the request and response are matched.\n"
        return print_out

    @staticmethod
    def ask_target_id():
        return "What is the target ID?"

    @staticmethod
    def ask_query():
        return "What is your query?"

    @staticmethod
    def ask_response():
        return "What is your response?"

    @staticmethod
    def confirm_send_query(source_id, query):
        return "Query has been sent.\nSource ID: %d\nQuery: %s" % (source_id, query)

    @staticmethod
    def confirm_send_response_to_target(target_id):
        return "Response has been sent to target %d" % target_id

    @staticmethod
    def confirm_match(target_id):
        return ("Matching target ID %d has been sent.\n" % target_id) + \
                "When the other side also sends out matching, the contact will be exchanged"

    @staticmethod
    def confirm_unmatch(target_id):
        return ("Unmatching target ID %d has been sent.\n" % target_id) + \
                "If it is a query, its responses will no longer be received.\n" + \
                "If it is a private communication, the counterparty will not send message to you."

    @staticmethod
    def broadcast_query(message_record):
        return "Time: %s %s\nSource ID: %d\nQuery: %s" \
               % (message_record.date, message_record.time[0:8], message_record.source_id, message_record.msg)

    @staticmethod
    def broadcast_response(message_record):
        return "Time: %s %s\nSource ID: %d\nResponse: %s" \
               % (message_record.date, message_record.time[0:8], message_record.source_id, message_record.msg)

    @staticmethod
    def inactivated_target_id(target_id):
        try:
            return "Target ID (%d) is closed or no longer valid." % target_id
        except:
            return "Target ID (%s) is closed or no longer valid." % target_id

    @staticmethod
    def cancel_action():
        return "Action has been cancelled"

    @staticmethod
    def ask_confirming_query(msg):
        return "Please confirm to send out the following query:\n%s" % msg

    @staticmethod
    def ask_confirming_response(target_id, msg):
        return ("Please confirm to send out the following response:\n" + \
                ("Target ID: %d\nResponse: %s" % (target_id, msg)))

    @staticmethod
    def ask_confirming_match(target_id):
        try:
            return "Do you confirm to match target ID %d?" % target_id
        except:
            return "Do you confirm to match target ID %s?" % target_id

    @staticmethod
    def ask_confirming_unmatch(target_id):
        return "Do you confirm to unmatch target ID %d?" % target_id

    @staticmethod
    def match_and_wait_counterparty(target_id):
        return ("The counterparty %d has not yet agreed to match.\n" % target_id) + \
               "Your contact has not yet been forwarded.\n" + \
               "Once the counterparty agrees as well we will exchange the two contacts."
               
    @staticmethod
    def match_send_contact(target_id):
        return ("The following is the contact of target id %d" % target_id)

    @staticmethod
    def reject_multiply_match(target_id):
        return ("Action matching target ID %d has been sent." % target_id) + \
               "Please wait for the opponent to send matching if you haven't received his/her contact."

    @staticmethod
    def reject_multiply_unmatch(target_id):
        return ("Target ID %d has been blocked." % target_id) + \
               "If you still can receive the opponent's response. Please send /help to report it"
