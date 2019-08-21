# Name: Benjamin Fawcett
import sys
import socket
import time

port = int(sys.argv[1])
global text

def receiveMessage(socket):
    global text
    msg = socket.recv(4096).decode()

    text = text + str(msg)
    if (len(msg) == 4096):
        receiveMessage(socket)
    return text


def connect(port):
    cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cs.connect(('comp431sp19.cs.unc.edu',port))
    return cs

def reconnect(port):
    connected = True
    try:
        client = connect(port)
    except OSError:
        connected = False
    finally:
        if (connected):
            return client
    return None

reconnected = False
num_tries = 0
for line in sys.stdin:
    sys.stdout.write(line)
    try:
        client_socket = connect(port)
        
        client_socket.send(line.encode())
        text = ""
        receiveMessage(client_socket)
        sys.stdout.write(text)
        reconnected = False
        num_tries = 0
    except OSError as e:
        print("Connection Error")
        for i in range (1,11):
            client_socket = reconnect(port)
            if not (client_socket == None):
                break
        if (client_socket == None):
            break
        else:
            client_socket.close()
    finally:
        client_socket.close()
