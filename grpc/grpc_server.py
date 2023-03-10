from concurrent import futures

import grpc
import time
import sys

import wire_pb2 as chat
import wire_pb2_grpc as rpc

from _thread import *
from threading import Lock
import re

account_dict = {}
msg_dict = {}
msg_lock = Lock()
account_lock = Lock()


class ChatServer(rpc.BidirectionalServicer):

    def __init__(self):
        self.obj = []

    # The stream which will be used to send new messages to clients
    def ClientStream(self, request, context):
        """
        This is a response-stream type call. This means the server can keep sending messages
        Every client opens this connection and waits for server to send new messages
        Every stream is unique since we instantiate a class object for each connection
        """
        if len(request.username) > 50:
            return
        try:
            # For every client a infinite loop starts (in gRPC's own managed thread)
            while context.is_active():
                # Check if there are any new messages
                account_lock.acquire(timeout=3)
                if request.username in account_dict.keys():
                    if account_dict[request.username] != 0:
                        msg_lock.acquire()
                        while len(msg_dict[request.username]) > 0:
                            text = msg_dict[request.username].pop(0)
                            yield text
                            print(text)
                        msg_lock.release()
                account_lock.release()

                # check if logged out or deleted account
                account_lock.acquire(timeout=3)
                if request.username not in account_dict.keys():
                    account_lock.release()
                    print("username not found, account was deleted: ",
                          request.username)
                    return
                else:
                    if account_dict[request.username] == 0:
                        account_lock.release()
                        print(request.username + " logged out.")
                        return
                account_lock.release()

            # In case of broken connection
            if context.is_active() == False:
                print(request.username + " disconnected.")
                account_lock.acquire(timeout=3)
                if request.username in account_dict.keys():
                    if account_dict[request.username] != 0:
                        account_dict[request.username] = 0
                account_lock.release()
                return

        # Any other interruption will automatically disconnect
        except Exception as e:
            print(e)
            print(request.username + " disconnected.")
            account_lock.acquire(timeout=3)
            if request.username in account_dict.keys():
                if account_dict[request.username] != 0:
                    account_dict[request.username] = 0
            account_lock.release()
            return

    def ServerSend(self, request: chat.Text, context):
        """
        This method is called when a clients sends a message to the server.
        :param request:
        :param context:
        :return:
        """
        res = chat.Res(status=0)
        if len(request.message) > 250 or len(request.receiver) > 50 or len(request.sender) > 50:
            res.status = -1
            return res
        msg_lock.acquire(timeout=10)
        try:
            # this is only for the server console
            print("[{}] {}".format(request.sender, request.message))
            # Add it to the chat history
            if request.receiver in msg_dict.keys():
                msg_dict[request.receiver].append(request)
            else:
                res.status = 1
                print(request.receiver + " not found")
        except Exception as e:
            print(e)
            res.status = -1
        msg_lock.release()
        return res

    def ChangeAccountState(self, request: chat.Account, context):
        res = chat.Res(status=-1)
        account_lock.acquire(timeout=10)
        if len(request.username) <= 50:
            # login
            if request.type == 0:
                if request.username in account_dict.keys():
                    if account_dict[request.username] == 0:
                        account_dict[request.username] = request.connection
                        res.status = 0
                else:
                    res.status = 1
            # logout
            elif request.type == 1:
                if request.username in account_dict.keys():
                    if account_dict[request.username] != 0:
                        account_dict[request.username] = 0
                        res.status = 0
                else:
                    res.status = 1
            # delete account
            elif request.type == 2:
                if request.username in account_dict.keys() and request.username in msg_dict.keys():
                    account_dict.pop(request.username)
                    msg_lock.acquire(timeout=10)
                    msg_dict.pop(request.username)
                    msg_lock.release()
                    res.status = 0
                else:
                    res.status = 1
            # create account
            elif request.type == 3:
                if request.username not in account_dict.keys():
                    account_dict[request.username] = request.connection
                    msg_lock.acquire(timeout=10)
                    msg_dict[request.username] = []
                    msg_lock.release()
                    res.status = 0
                else:
                    res.status = 2
        account_lock.release()
        print(account_dict)
        return res

    def ListAccounts(self, request, context):
        query = request.match
        if len(query) > 50:
            return chat.List(list='query too long, must be under 50 chars')
        # query = query.replace('*', ".*")
        res = ''
        counter = 0
        account_lock.acquire(timeout=10)
        try:
            for key in account_dict.keys():
                match = re.search(query, key)
                if match is not None and match.group() == key:
                    res += key + " "
                    counter += 1
                if counter >= request.number:
                    break
            print(res)
        except Exception as e:
            print(e)
            res = 'Regex Error'
            account_lock.release()
            return chat.List(list=res)
        account_lock.release()
        return chat.List(list=res)


if __name__ == '__main__':
    port = sys.argv[2]  # a random port for the server to run on
    IP_addr = str(sys.argv[1])
    # the workers is like the amount of threads that can be opened at the same time, when there are 10 clients connected
    # then no more clients able to connect to the server.
    server = grpc.server(futures.ThreadPoolExecutor())  # create a gRPC server
    rpc.add_BidirectionalServicer_to_server(
        ChatServer(), server)  # register the server to gRPC
    # gRPC basically manages all the threading and server responding logic, which is perfect!
    print(f'Starting server on {IP_addr}. Listening...')
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    # Server starts in background (in another thread) so keep waiting
    # if we don't wait here the main thread will end, which will end all the child threads, and thus the threads
    # from the server won't continue to work and stop the server
    while True:
        time.sleep(64 * 64 * 100)
