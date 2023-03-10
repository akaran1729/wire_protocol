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
conn = rpc.BidirectionalStub(channel)

# create new listening thread for when new message streams come in
# could be an issue here with concurrency, check this and may have to switch to class objects

username = ''
listen_thread = None


def listen():
    if username != '':
        this_acc = chat.Account(type=0, username=username,
                                connection=str(channel))
        try:
            for text in conn.ClientStream(this_acc):
                print("<"+text.sender+">: " + text.message)
        except Exception as e:
            print(e)


def process(message):
    global username
    global listen_thread
    message = message.rstrip()
    # Messages are first entered as types, and are tagged based on those types
    if message.find('Create Account') == 0:
        if username == '':
            pmessage = input('username:').rstrip()
            if len(pmessage) > MAX_RECIPIENT_LENGTH:
                print('username must be under 50 characters')
                res = None
                return res
            acct = chat.Account(type=3, username=pmessage,
                                connection=str(channel))
            res = conn.ChangeAccountState(acct)
            if res.status == 0:
                username = pmessage
                listen_thread = threading.Thread(
                    target=listen, daemon=True)
                listen_thread.start()
        else:
            print(f'Currently signed in as {username}, please log out first')
            res = None
    elif message.find('Login') == 0:
        if username == '':
            pmessage = input("username:").rstrip()
            acct = chat.Account(type=0, username=pmessage,
                                connection=str(channel))
            res = conn.ChangeAccountState(acct)
            if res.status == 0:
                username = pmessage
                listen_thread = threading.Thread(
                    target=listen, daemon=True)
                listen_thread.start()
        else:
            print(f'Currently signed in as {username}, please log out first')
            res = None
    elif message.find('Logout') == 0:
        if username != '':
            acct = chat.Account(type=1, username=username,
                                connection=str(channel))
            res = conn.ChangeAccountState(acct)
            if res.status == 0:
                username = ''
        else:
            res = None
            print('Please log in first')
    elif message.find('Delete Account') == 0:
        if username != '':
            acct = chat.Account(type=2, username=username,
                                connection=str(channel))
            res = conn.ChangeAccountState(acct)
            username = ''
        else:
            res = None
            print('Please log in first')
    elif message.find("Send") == 0:
        if username != '':
            receiver = input('to: ').rstrip()
            text = input('begin message: ')
            if len(text) > MAX_MESSAGE_LENGTH:
                res = None
                print("Message must be under 250 characters")
                return res
            res = conn.ServerSend(chat.Text(sender=username,
                                            receiver=receiver, message=text))
        else:
            res = None
            print('Please log in first')
    elif message.find("List Accounts") == 0:
        query = input('search users: ').rstrip()
        number = int(input('number of matches: '))
        results = conn.ListAccounts(chat.Query(match=query, number=number))
        print(results.list)
        res = chat.Res(status=0)
        if len(results.list) == 0:
            res.status = 1

    else:
        print('Input not recognized. Please try again.')
        return
    return res


print("Welcome to Messenger! Login or create an account to get started!")
while True:
    message = input()
    try:
        res = process(message)
        if res is not None:
            if res.status == 0:
                print('success')
            elif res.status == 1:
                print('Account(s) not found')
            elif res.status == 2:
                print('Username taken, enter prompt to try again')
            else:
                print('Unknown server error')
    except Exception as e:
        print(e)


# To Do: limits on message and username lengths
# To Do: If we log in, and try to log in again, do we have to have a client side error, or can we just let that be a null operation (second option probably good too)
# To Do: Probably more comments about the wire protocol
# To Do: Big Endian Handling
