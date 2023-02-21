# Test for grpc message sending to nonexistent user
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

conn1.ChangeAccountState(chat.Account(
    type=3, username=accounts[0], connection=str(channel1)))

res = conn1.ServerSend(
    chat.Text(sender=accounts[0], receiver=accounts[1], message='yo'))

if res.status == 1:
    print("TEST008 PASSED")
    conn1.ChangeAccountState(chat.Account(
        type=2, username='yush', connection=str(channel1)))
    conn2.ChangeAccountState(chat.Account(
        type=2, username='mike', connection=str(channel2)))
else:
    print("TEST008 FAILED")
    conn1.ChangeAccountState(chat.Account(
        type=2, username='yush', connection=str(channel1)))
    conn2.ChangeAccountState(chat.Account(
        type=2, username='mike', connection=str(channel2)))
