# Test for grpc delete non existing account

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

delete_account = chat.Account(type=2, username='m', connection=str(channel))
evil = conn.ChangeAccountState(delete_account)
if evil.status == 1:
    print('TEST004 PASSED')
else:
    print('TEST004 FAILED')
