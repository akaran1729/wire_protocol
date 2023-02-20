# Test for grpc basic account status functionality

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
create = conn.ChangeAccountState(create_account)
check = conn.ListAccounts(chat.Query(match='m'), 1)
if create.status != 0 or check.list != 'm ':
    print('TEST002 FAILED: creation error')
    exit()

logout_account = chat.Account(type=1, username='m', connection=str(channel))
logout = conn.ChangeAccountState(logout_account)
if logout.status != 0:
    print('TEST002 FAILED: logout error')
    exit()

login_account = chat.Account(type=0, username='m', connection=str(channel))
login = conn.ChangeAccountState(login_account)
if login.status != 0:
    print('TEST002 FAILED: login error')
    exit()

delete_account = chat.Account(type=2, username='m', connection=str(channel))
delete = conn.ChangeAccountState(delete_account)
check = conn.ListAccounts(chat.Query(match='m'), 1)

if delete.status != 0 or check.list != '':
    print('TEST002 FAILED: deletion error')
    exit()

print('TEST002 PASSED')
