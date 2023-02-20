# Test for grpc list accounts edge cases
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

nulllist = (conn.ListAccounts(chat.Query(match='mhla', number=5)).list == '')
if not nulllist:
    print('TEST006 FAILED')
    exit()

accounts = ['m', 'mi', 'mike']

for a in accounts:
    create = conn.ChangeAccountState(chat.Account(
        type=3, username=a, connection=str(channel)))

list1 = (conn.ListAccounts(chat.Query(match='', number=5)).list == '')
list2 = (conn.ListAccounts(chat.Query(
    match='         ', number=5)).list == '')
list3 = (conn.ListAccounts(chat.Query(
    match='$', number=5)).list == '')
list4 = (conn.ListAccounts(chat.Query(
    match='*', number=5)).list == 'Regex Error')


if list1 and list2 and list3 and list4:
    print('TEST 006 PASSED')
    for a in accounts:
        delete = conn.ChangeAccountState(chat.Account(
            type=2, username=a, connection=str(channel)))

else:
    print('TEST 006 FAILED')
    print(list1, list2, list3, list4)
    for a in accounts:
        delete = conn.ChangeAccountState(chat.Account(
            type=2, username=a, connection=str(channel)))
