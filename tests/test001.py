import subprocess
import threading


# Run a shell command and get its output
def listen():
    server = subprocess.run(['python', '/Users/michaelh40/Code/wire_protocol/grpc/grpc_server.py',
                             'localhost', '8081'], capture_output=True, text=True)
    print(server)


server_thread = threading.Thread(target=listen)


# Run a shell command and get its exit status
def run_client():
    client = subprocess.run(['python', '/Users/michaelh40/Code/wire_protocol/grpc/grpc_server.py',
                             'localhost', '8081'], capture_output=True, text=True)
    print(client)


client_thread = threading.Thread(target=run_client)
