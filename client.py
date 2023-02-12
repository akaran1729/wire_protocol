# Python program to implement client side of chat room.
import socket
import select
import sys

MAX_MESSAGE_LENGTH = 280
MAX_RECIPIENT_LENGTH = 50

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if len(sys.argv) != 3:
    print("Correct usage: script, IP address, port number")
    exit()
IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
server.connect((IP_address, Port))



# Keywords that client side parses and tags to send to the server
MESSAGE_KEYS = ['Create Account: ', 'Login: ', 'Logout', 'Delete Account', 'Send']



#To Do: limits on message and username lengths

# always returns encoded message
def process(message):
    message.rstrip()
    # Messages are first entered as types, and are tagged based on those types
    if message.find('Create Account') == 0:
        name = ""
        name_max = False
        # Ensures created accounts are no more than the max alotted length
        while name_max == False:
            name = sys.stdin.readline()
            if len(name) <= MAX_RECIPIENT_LENGTH:
                name_max = True
            else:
                print("All usernames must be at most " + str(MAX_RECIPIENT_LENGTH) + " characters. Please try again.")
        message = name
        message = message.encode()
        tag = (0).to_bytes(1, "big")
    elif message.find('Login') == 0:
        message = sys.stdin.readline()
        message = message.encode()
        tag = (1).to_bytes(1, "big")
    elif message.find('Logout') == 0:
        message = ""
        message = message.encode()
        tag = (2).to_bytes(1, "big")
    elif message.find('Delete Account') == 0:
        message = ""
        message = message.encode()
        tag = (3).to_bytes(1, "big")
    elif message.find("Send") == 0:
        print("To: ")
        recipient = ""
        rec_max = False
        # Ensures recipient is in the length limit, for wire protocol tagging
        while rec_max == False:
            recipient = sys.stdin.readline()
            if len(recipient) <= MAX_RECIPIENT_LENGTH:
                rec_max = True
            else:
                print("All usernames are at most " + str(MAX_RECIPIENT_LENGTH) + " characters. Please try again.")
        len_r = len(recipient)
        recep_tag = (len_r).to_bytes(1, "big")
        recipient = recipient.encode()
        print("Message: ")
        mes_len = False
        message = ""
        # Ensures message is in the length limit
        while mes_len == False:
            message = sys.stdin.readline()
            if len(message) <= MAX_MESSAGE_LENGTH:
                mes_len = True
            else:
                print("Message must be at most " + str(MAX_MESSAGE_LENGTH) + " characters. Please try again.")
        message = message.encode()
        type_tag = (4).to_bytes(1, "big")
        # Wire protocol tags with type, then length of receiving username for metadata parsing, and the receiving username
        tag = type_tag + recep_tag + recipient
    elif message.find("Open Undelivered Messages") == 0:
        message = ""
        message = message.encode()
        tag = (5).to_bytes(1, "big")
    elif message.find("List Accounts") == 0:
        # To Do
        pass
    else:
        print('Input not recognized. Please try again.')
        return

    bmsg = tag + message
    return bmsg


while True:

    # maintains a list of possible input streams
    sockets_list = [sys.stdin, server]

    """ There are two possible input situations. Either the
    user wants to give manual input to send to other people,
    or the server is sending a message to be printed on the
    screen. Select returns from sockets_list, the stream that
    is reader for input. So for example, if the server wants
    to send a message, then the if condition will hold true
    below.If the user wants to send a message, the else
    condition will evaluate as true"""
    read_sockets, write_socket, error_socket = select.select(
        sockets_list, [], [])

    for socks in read_sockets:
        if socks == server:
            message = socks.recv(2048)
            dmessage = message.decode()
            print(dmessage)
        else:
            message = sys.stdin.readline()
            bmsg = process(message)
            # if bmsg and bmsg[0] != 4: ??? To Do
            if bmsg:
                try: 
                    server.send(bmsg)
                    sys.stdout.flush()
                except: 
                    print('message could not send')
server.close()



# To Do: If we log in, and try to log in again, do we have to have a client side error, or can we just let that be a null operation (second option probably good too)
# To Do: Probably more comments about the wire protocol
# To Do: Big Endian Handling