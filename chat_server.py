# Python program to implement server side of chat room.
import socket
import select
import sys
'''Replace "thread" with "_thread" for python 3'''
from _thread import *
from threading import Lock

 
"""The first argument AF_INET is the address domain of the
socket. This is used when we have an Internet Domain with
any two hosts The second argument is the type of socket.
SOCK_STREAM means that data or characters are read in
a continuous flow."""
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
 
if len(sys.argv) != 3:
    print ("Correct usage: script, IP address, port number")
    exit()
 
# IP address is first argument
IP_address = str(sys.argv[1])
 
# Port number is second argument
port = int(sys.argv[2])
 
# Server initialized at input IP address and port
server.bind((IP_address, port))
 
#maintains at most N active connections
N = 10
server.listen(N)


#client username dictionary, with login status: 0 if logged off, corresponding address if logged in
client_dictionary = {}

#lock for dictionary
dict_lock = Lock()

 


def clientthread(conn, addr):

    # maintain a client_state variable as logged in or logged off
    # while logged off, client_state = False
    client_state = False
 
    # sends a message to the client whose user object is conn
    message = "Welcome to Messenger! Please login or create an account:"
    conn.send(message.encode())


    # client can only create an account or login while client state is False
    # To Do: Add locking on client dictionary
    while client_state == False:
        try:
            message = conn.recv(2048)
            # check if message is of type create account or login
            # wire protocol demands initial byte is either 0 (create) or 1 (login) here
            tag = message[0]
            
            # account creation
            if tag == 0:
                username = message[1:]
                username = username.decode()
                # If the username is in existence, server asks to retry.

                # acquire lock for client_dictionary, with timeout in case of failure
                dict_lock.acquire(timeout=10)

                if username in client_dictionary.keys():
                    message = "The account " + username + " already exists. Please try again."
                    conn.send(message.encode())
                else:
                    client_dictionary[username] = addr
                    message = "Account created. Welcome " + username + "!"
                    conn.send(message.encode())
                    client_state = True
                
                dict_lock.release()


            
            # login
            if tag == 1:
                username = message[1:]
                username = username.decode()

                # acquire lock for client_dictionary, with timeout in case of failure
                dict_lock.acquire(timeout=10)

                if username not in client_dictionary.keys():
                    message = "Username not found. Please try again."
                    conn.send(message.encode())
                else:
                    # Check if username logged in elsewhere (i.e. dictionary returns 1)
                    if client_dictionary[username] != 0:
                        message = "Username logged in elsewhere. Please try again."
                        conn.send(message.encode())
                    else:
                        client_dictionary[username] = addr
                        message = "Welcome back " + username + "!"
                        conn.send(message.encode())
                        client_state = True
                        
                dict_lock.release()
                        
        except:
            continue

 
    # now suppose that the client is logged in
    # To Do: dump queue of messages
    # allowable actions are: list accounts, send message, log off, delete account
    
    while client_state == True:
            try:
                message = conn.recv(2048)
                if message:
 
                    """prints the message and address of the
                    user who just sent the message on the server
                    terminal"""
                    print(f"<{addr[0]}> ", message.decode())
 
                    # Calls broadcast function to send message to all
                    message_to_send = f"<{addr[0]}> {message.decode()}" 
                    broadcast(message_to_send, conn)
 
                else:
                    """message may have no content if the connection
                    is broken, in this case we remove the connection"""
                    remove(conn)
 
            except:
                continue
 
"""Using the below function, we broadcast the message to all
clients who's object is not the same as the one sending
the message """
def broadcast(message, connection):
    for clients in list_of_clients:
        if clients!=connection:
            try:
                clients.send(message.encode())
            except:
                clients.close()
 
                # if the link is broken, we remove the client
                remove(clients)
 
"""The following function simply removes the object
from the list that was created at the beginning of
the program"""
def remove(connection):
    if connection in list_of_clients:
        print(f"{connection} has left")
        list_of_clients.remove(connection)
 
while True:
 
    """Accepts a connection request and stores two parameters,
    conn which is a socket object for that user, and addr
    which contains the IP address of the client that just
    connected"""
    conn, addr = server.accept()
 
    """Maintains a list of clients for ease of broadcasting
    a message to all available people in the chatroom"""
    list_of_clients.append(conn)
 
    # prints the address of the user that just connected
    print (addr[0] + " connected")
 
    # creates and individual thread for every user
    # that connects
    start_new_thread(clientthread,(conn,addr))    
 
conn.close()
server.close()