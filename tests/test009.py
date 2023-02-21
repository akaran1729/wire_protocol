# Test for delivering messages once person logs in
import threading
import select
import sys
import grpc
import time

import wire_pb2 as chat
import wire_pb2_grpc as rpc

if len(sys.argv) != 3:
    print("Correct usage: script, IP address, port number")
    exit()
IP_address = str(sys.argv[1])
Port = sys.argv[2]
channel1 = grpc.insecure_channel(IP_address + ':' + Port)
channel2 = grpc.insecure_channel(IP_address + ':' + Port)
conn1 = rpc.BidirectionalStub(channel1)
conn2 = rpc.BidirectionalStub(channel2)


accounts = ['yush', 'mike']
output1 = ''

conn1.ChangeAccountState(chat.Account(
    type=3, username=accounts[0], connection=str(channel1)))
conn2.ChangeAccountState(chat.Account(
    type=3, username=accounts[1], connection=str(channel2)))

conn2.ChangeAccountState(chat.Account(
    type=1, username=accounts[1], connection=str(channel2)))


def listen():
    global output1
    for text in conn2.ClientStream(chat.Account(
            type=0, username=accounts[1], connection=str(channel2))):
        output1 = "<"+text.sender+">: " + text.message
        return


conn1.ServerSend(
    chat.Text(sender=accounts[0], receiver=accounts[1], message='yo'))
conn1.ServerSend(
    chat.Text(sender=accounts[0], receiver=accounts[1], message='mike'))

time.sleep(1)

conn2.ChangeAccountState(chat.Account(
    type=0, username=accounts[1], connection=str(channel2)))


listen_thread = threading.Thread(target=listen, daemon=True)
listen_thread.start()

time.sleep(1)

if output1 == "<yush>: yo":
    print("TEST009 PASSED")
    conn1.ChangeAccountState(chat.Account(
        type=2, username='yush', connection=str(channel1)))
    conn2.ChangeAccountState(chat.Account(
        type=2, username='mike', connection=str(channel2)))
else:
    print(output1)
    print("TEST009 FAILED")
    conn1.ChangeAccountState(chat.Account(
        type=2, username='yush', connection=str(channel1)))
    conn2.ChangeAccountState(chat.Account(
        type=2, username='mike', connection=str(channel2)))
