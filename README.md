# TeleX
An unofficial Telegram message exchange rebot

![alt tag](https://github.com/gavincyi/TeleX/blob/master/doc/flow.jpg)

## Objective

Telex provides annoymous communication channel to exchange queries and responses in Telegram. 

1. A person (we call him "Customer") sends out a query to a robot. 
2. The rebot passes the query to the channel with a key (the query key)
3. Subscribers in the channel (we call them "Agents") can all see the query
4. Agents can response the query and send it to the rebot by the query key
5. The rebot passes the response back to the customer with another key (the response key)
6. The customer and agent can communicate under the query and response key

## Functionality

The following commands are supported in the rebot
* Query (/r)
* Response (/q \<id\>)


