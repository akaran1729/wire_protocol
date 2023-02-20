import subprocess
import threading
import sys
import time


# Run a shell command and get its output
def listen():
    # Start the process
    process = subprocess.Popen(
        ['python', '/Users/michaelh40/Code/wire_protocol/grpc/grpc_server.py', 'localhost', '8081'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Read output as it is produced
    while True:
        output = process.stdout.readline().decode().strip()
        if output == '' and process.poll() is not None:
            break

        error = process.stderr.readline().decode().strip()
        if error == '' and process.poll() is not None:
            break
        if error:
            print(error)

    # Get the return code
    return_code = process.poll()

    if return_code != 0:
        print(f"Process returned non-zero exit status {return_code}")


try:
    server_thread = threading.Thread(target=listen)
except:
    print('TEST 001 FAILED')

# Run a shell command and get its exit status


def run_client():
    # Start the process
    process = subprocess.Popen(
        ['python', '/Users/michaelh40/Code/wire_protocol/grpc/grpc_client.py', 'localhost', '8081'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Read output as it is produced
    while True:
        output = process.stdout.readline().decode().strip()
        if output == '' and process.poll() is not None:
            break

        error = process.stderr.readline().decode().strip()
        if error == '' and process.poll() is not None:
            break
        if error:
            print(error)

    # Get the return code
    return_code = process.poll()

    if return_code != 0:
        print(f"Process returned non-zero exit status {return_code}")
        return


try:
    client_thread = threading.Thread(target=run_client)
    print('TEST 001 PASSED')
except:
    print('TEST001 FAILED')
