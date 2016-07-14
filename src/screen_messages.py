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
        return "Target ID (%s) is closed or no longer valid." % str(target_id)

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
        return "Do you confirm to match target ID %d?" % target_id

    @staticmethod
    def ask_confirming_unmatch(target_id):
        return "Do you confirm to unmatch target ID %d?" % target_id
