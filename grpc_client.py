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
Port = sys.argv[2]
channel = grpc.insecure_channel(IP_address + ':' + Port)
print(channel)
conn = rpc.BidirectionalStub(channel)
print(conn)
# create new listening thread for when new message streams come in
# could be an issue here with concurrency, check this and may have to switch to class objects

username = ''
listen_thread = None


def listen():
    this_acc = chat.Account(type=0, username=username,
                            connection=str(channel))
    try:
        for text in conn.ClientStream(this_acc):
            print(text.sender, text.message)
    except Exception as e:
        print(e)


# TO DO grpc parser
def process(message):
    global username
    global listen_thread
    message = message.rstrip()
    # Messages are first entered as types, and are tagged based on those types
    if message.find('Create Account') == 0:
        pmessage = input('username:')
        acct = chat.Account(type=3, username=pmessage, connection=str(channel))
        res = conn.ChangeAccountState(acct)
        if res:
            username = pmessage
            listen_thread = threading.Thread(
                target=listen, daemon=True)
            listen_thread.start()
    elif message.find('Login') == 0:
        pmessage = input("username:")
        acct = chat.Account(type=0, username=pmessage, connection=str(channel))
        res = conn.ChangeAccountState(acct)
        if res:
            username = pmessage
            listen_thread = threading.Thread(
                target=listen, daemon=True)
            listen_thread.start()
    elif message.find('Logout') == 0:
        acct = chat.Account(type=1, username=username, connection=str(channel))
        res = conn.ChangeAccountState(acct)
        if res:
            username = ''
            # listen_thread.join()
    elif message.find('Delete Account') == 0:
        acct = chat.Account(type=2, username=pmessage, connection=str(channel))
        res = conn.ChangeAccountState(acct)
    elif message.find("Send") == 0:
        receiver = input('to: ')
        text = input('begin message: ')
        conn.ServerSend(chat.Text(sender=username,
                        receiver=receiver, message=text))
    # TO DO this is clunky, we should dump messages when user logs in
    elif message.find("Open Undelivered Messages") == 0:
        pass
    elif message.find("List Accounts") == 0:
        query = input('search users: ')
        number = int(input('number of matches: '))
        res = conn.ListAccounts(chat.Query(match=query, number=number))
        print(res.list)
    else:
        print('Input not recognized. Please try again.')
        return
    return res


# Keywords that client side parses and tags to send to the server
MESSAGE_KEYS = ['Create Account: ', 'Login: ', 'Logout',
                'Delete Account', 'Send', 'List Accounts']

print("Welcome to Messenger! Login or create an account to get started!")
while True:
    message = input()
    try:
        res = process(message)
        print(res.status)
        if res:
            print('delivered')
        else:
            print('server error')
    except Exception as e:
        print(e)


# To Do: limits on message and username lengths
# To Do: If we log in, and try to log in again, do we have to have a client side error, or can we just let that be a null operation (second option probably good too)
# To Do: Probably more comments about the wire protocol
# To Do: Big Endian Handling
