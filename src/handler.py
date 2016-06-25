#!/bin/python
from src.db_client import txn

class handler:
    def __init__(self, logger, conf):
        self.logger = logger
        self.conf = conf
        self.session = 0
        self.channel_name = conf.channel_name
        self.id = 0

    @staticmethod
    def query_handler_name():
        return 'q'

    @staticmethod
    def response_handler_name():
        return 'r'

    @staticmethod
    def help_handler_name():
        return 'help'

    def init_db(self, database_client):
        self.database_client = database_client

        # Get the latest id
        row = self.database_client.selectone(self.database_client.txn_table_name,
                                             "inid",
                                             "session = %d" % self.session,
                                             "session desc, inid desc")
        if row is None or not row[0]:
            self.id = 0
        else:
            self.id = row[0]

        self.logger.info("Current Id = %d" % self.id)

    def start_handler(self, bot, update):
        """
        Start handler
        :param bot: Callback bot
        :param update: Callback update
        """

        # Welcome message
        print_out = 'Welcome to TeleX, %s!\n'%update.message.from_user.first_name
        print_out += "TeleX is a community to connect demand and provider.\n"
        print_out += "The identity is not revealed until the request and response are matched.\n"
        # Send out message
        bot.sendMessage(update.message.chat_id,
                        text=print_out)

        print_out = "Basic commands:\n"
        print_out += "/%s : Query for service. Please follow with a question or details\n"%handler.query_handler_name()
        print_out += (" " * 4) + \
                      "Usage = /%s <Question>\n" % handler.query_handler_name()
        print_out += (" " * 4) + \
                     "Example = /%s I need a babysitter tonight. Anyone help?\n" % handler.query_handler_name()
        print_out += "/%s : Response demand. Please answer the query in details\n"%handler.response_handler_name()
        print_out += (" " * 4) + \
                     "Usage = /%s <QueryId> <Response>\n" % handler.response_handler_name()
        print_out += (" " * 4) + \
                     "Example = /%s 18348 $100/hr. Available on every Monday.\n" % handler.response_handler_name()
        print_out += "/%s : Show detailed commands.\n"%handler.help_handler_name()
        print_out += (" " * 4) + \
                     "Usage = /%s\n" % handler.help_handler_name()
        print_out += (" " * 4) + \
                     "Usage = /%s <Command name>\n" % handler.help_handler_name()

        # Send out message
        bot.sendMessage(update.message.chat_id,
                        text=print_out)

    def query_handler(self, bot, update):
        """
        Query handler
        :param bot: Callback bot
        :param update: Callback update
        """

        # Increment id to provide an unique id
        self.id += 1

        # Insert the transaction into database
        txn_record = txn(self.session, self.id, update.message.chat_id)
        self.database_client.insert(self.database_client.txn_table_name,
                                    txn_record.str())

        # print out
        print_out = ["Query <%d>"%self.id,
                     "ChatId: %s"%update.message.chat_id,
                     update.message.text.replace("/%s"%handler.query_handler_name(), '').strip()]
        self.logger.info("\n" + ("\n".join(print_out)))

        # Acknowledge the demand
        bot.sendMessage(update.message.chat_id,
                        text="\n".join(print_out))

        # Broadcast it in the channel
        bot.sendMessage(self.channel_name,
                        text="%s\n%s"%(print_out[0], print_out[2]))

    def response_handler(self, bot, update):
        """
        Response handler
        :param bot: Callback bot
        :param update: Callback update
        """
        text = update.message.text.replace("/%s"%handler.response_handler_name(), '').strip()
        first_space = text.find(" ")

        # Query id validation
        if first_space == -1:
            bot.sendMessage(update.message.chat_id,
                            "Please provide a query id and an answer. Please send \"/%s %s\" for detailed usage."%
                            (handler.help_handler_name(), handler.response_handler_name()))
            return

        # Query id validation in database
        query_id = int(text[:first_space])
        row = self.database_client.selectone(self.database_client.txn_table_name,
                                             "*",
                                             "inid = %d" % query_id)

        if not row[0]:
            bot.sendMessage(update.message.chat_id,
                            "Query id (%s) cannot be found. Please send \"/%s %s\" for detailed usage."%
                            (query_id, handler.help_handler_name(), handler.response_handler_name()))
            return

        response = text[first_space+1:]

        # Insert the transaction into db
        self.id += 1
        txn_record = txn(self.session, self.id, update.message.chat_id)
        txn_record.outid = row[txn.inid_index()]
        txn_record.outchatid = row[txn.inchatid_index()]
        self.database_client.insert_or_replace(self.database_client.txn_table_name,
                                               txn_record.str())

        bot.sendMessage(txn_record.outchatid,
                        text="Response <%d> - Reply for query <%d>:\n%s" % (self.id, query_id, response))
        bot.sendMessage(update.message.chat_id,
                        text="Response <%d> is sent." % self.id)

    def help_handler(self, bot, update):
        """
        Help handler
        :param bot: Callback bot
        :param update: Callback update
        """
        self.logger.info("Not yet implemented")