# Test for grpc double create account fails

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

create_account = chat.Account(type=3, username='m', connection=str(channel))
conn.ChangeAccountState(create_account)
logout = chat.Account(type=1, username='m', connection=str(channel))
conn.ChangeAccountState(logout)

evil_create_account = chat.Account(
    type=3, username='m', connection=str(channel))
evil = conn.ChangeAccountState(evil_create_account)
if evil.status == 2:
    print('TEST003 PASSED')
    delete_account = chat.Account(
        type=2, username='m', connection=str(channel))
    conn.ChangeAccountState(delete_account)

else:
    print('TEST003 FAILED')
