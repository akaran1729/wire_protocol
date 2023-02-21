# grpc load/synchronization test
import threading
import select
import sys
import grpc
import time
import random
import string


import wire_pb2 as chat
import wire_pb2_grpc as rpc

NUMBOTS = 4

if len(sys.argv) != 3:
    print("Correct usage: script, IP address, port number")
    exit()
IP_address = str(sys.argv[1])
Port = sys.argv[2]

channel_array = [grpc.insecure_channel(
    IP_address + ':' + Port) for _ in range(NUMBOTS)]
conn_array = [rpc.BidirectionalStub(channel_array[i]) for i in range(NUMBOTS)]
bot_conversations = [[] for i in range(NUMBOTS)]

messages = ['Want to get a meal sometime?',
            'What are you studying?', 'Not much, just grinding', "Where are you from?",
            "What classes are you taking?", "What's the move?", "What's your concentration?", "What are your summer plans?"]

convo_lock = threading.Lock()


def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))


def generate_random_string_array(n, min_length=5, max_length=10):
    return [generate_random_string(random.randint(min_length, max_length)) for _ in range(n)]


bot_array = generate_random_string_array(NUMBOTS)


for i in range(NUMBOTS):
    res = conn_array[i].ChangeAccountState(chat.Account(
        type=3, username=bot_array[i], connection=str(channel_array[i])))


def listen(bot_id):
    global bot_conversations
    global conn_array
    global bot_array
    global channel_array
    for text in conn_array[bot_id].ClientStream(chat.Account(
            type=0, username=bot_array[bot_id], connection=str(channel_array[bot_id]))):
        convo_lock.acquire()
        bot_conversations[bot_id].append("<" +
                                         text.sender+">: " + text.message + '\n')
        convo_lock.release()


for i in range(NUMBOTS):
    threading.Thread(target=listen, args=(i,), daemon=True).start()


time.sleep(1)

for i in range(2000):
    chosen_bot = random.randint(0, NUMBOTS-1)
    conn_array[chosen_bot].ServerSend(
        chat.Text(sender=bot_array[chosen_bot], receiver=bot_array[random.randint(0, NUMBOTS-1)], message=messages[random.randint(0, len(messages)-1)]))


time.sleep(1)

while len(bot_conversations) > 0:
    convo_lock.acquire()
    if len(bot_conversations[0]) == 0:
        bot_conversations.pop(0)
        if len(bot_conversations) == 0:
            break
    print(bot_conversations[0].pop())
    convo_lock.release()
    time.sleep(0.2)

for i in range(NUMBOTS):
    conn_array[i].ChangeAccountState(chat.Account(
        type=2, username=bot_array[i], connection=str(channel_array[i])))
