# Python program to implement client side of chat room.
import threading
import select
import sys
import grpc

import wire_pb2 as chat
import wire_pb2_grpc as rpc

MAX_MESSAGE_LENGTH = 280
MAX_RECIPIENT_LENGTH = 50

if len(sys.argv) != 3:
    print("Correct usage: script, IP address, port number")
    exit()
IP_address = str(sys.argv[1])
Port = str(sys.argv[2])
channel = grpc.insecure_channel(IP_address + ':' + Port)
conn = rpc.BidirectionalStub(channel)
# create new listening thread for when new message streams come in


def listen():
    for text in conn.ClientStream(chat.Empty()):
        print(text.sender, text.message)


# TO DO grpc parser
def process(message):
    message = message.rstrip()
    # Messages are first entered as types, and are tagged based on those types
    if message.find('Create Account') == 0:
        pass
    elif message.find('Login') == 0:
        pass
    elif message.find('Logout') == 0:
        pass
    elif message.find('Delete Account') == 0:
        pass
    elif message.find("Send") == 0:
        pass
    # TO DO this is clunky, we should dump messages when user logs in
    elif message.find("Open Undelivered Messages") == 0:
        pass
    elif message.find("List Accounts") == 0:
        pass
    else:
        print('Input not recognized. Please try again.')
        return

    bmsg = message
    return bmsg


threading.Thread(target=listen, daemon=True).start()


# Keywords that client side parses and tags to send to the server
MESSAGE_KEYS = ['Create Account: ', 'Login: ', 'Logout',
                'Delete Account', 'Send', 'List Accounts']

print("Welcome to Messenger! Login or create an account to get started!")
while True:
    message = input()
    pmessage = process(message)
    try:
        res = conn.ServerSend(pmessage)
        if res:
            print('delivered')
        else:
            print('server error')
    except:
        print('unknown error')


# To Do: limits on message and username lengths
# To Do: If we log in, and try to log in again, do we have to have a client side error, or can we just let that be a null operation (second option probably good too)
# To Do: Probably more comments about the wire protocol
# To Do: Big Endian Handling
