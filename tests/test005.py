# Test for grpc list accounts
import threading
import select
import sys
import grpc

import wire_pb2 as chat
import wire_pb2_grpc as rpc

if len(sys.argv) != 3:
    print("Correct usage: script, IP address, port number")
    exit()
IP_address = str(sys.argv[1])
Port = sys.argv[2]
channel = grpc.insecure_channel(IP_address + ':' + Port)
conn = rpc.BidirectionalStub(channel)

accounts = ['m', 'mi', 'mike']

for a in accounts:
    create = conn.ChangeAccountState(chat.Account(
        type=3, username=a, connection=str(channel)))

list = conn.ListAccounts(chat.Query(match='m.*', number=5))
if list.list == "m mi mike ":
    print('TEST005 PASSED')
    for a in accounts:
        delete = conn.ChangeAccountState(chat.Account(
            type=2, username=a, connection=str(channel)))
else:
    print(list.list)
    print('TEST 005 FAILED')
    for a in accounts:
        delete = conn.ChangeAccountState(chat.Account(
            type=2, username=a, connection=str(channel)))
