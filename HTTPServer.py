# Name: Benjamin Fawcett
import sys
import os
import socket
import time

global initial

parseerror1 = "ERROR -- Invalid Method token.\n"
parseerror2 = "ERROR -- Invalid Absolute-Path token.\n"
parseerror3 = "ERROR -- Invalid HTTP-Version token.\n"
parseerror4 = "ERROR -- Spurious token before CRLF.\n"

def checkLines(url):
    checkfile = open(cd + url, 'r')
    numlines = 0
    for line in checkfile:
        numlines += 1
    return numlines

def printreaderror(x, y):
    if (x == 1):
        return str("501 Not Implemented: " + y + '\n')
    if (x == 2):
        return str("404 Not Found: " + y + '\n')
    if (x == 3):
        return str("ERROR: " + str(y) + '\n')

def validurlchar(y):
    charlist = list(range(46, 58))
    for x in list(range(65, 91)):
        charlist.append(x)
    charlist.append(95)
    for x in list(range(97, 123)):
        charlist.append(x)

    if (ord(y[0]) != 47):
        return False

    for z in y:
        if not (ord(z) in charlist):
            return False
    return True

def validhttptoken(x):
    after = x[5:]

    numlist = list(range(48,58))

    if (x[:5] != "HTTP/"):
        return False
    elif not (len(x) == 8):
        return False
    elif not ("." == after[1]):
        return False
    elif not (ord(after[0]) in numlist):
        return False
    elif not (ord(after[-1]) in numlist):
        return False
    elif not (len(after) == 3):
        return False
    else:
        return True

def sendMessage(socket, message, typeMsg):
    message = str(message)
    sendIt = message
    socket.send(sendIt.encode())

def connect(port):
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ss.bind(('comp431sp19.cs.unc.edu', port))
    ss.listen(1) # Allow only one connection at a time
    
    return ss

def reconnect(port):
    try:
        return connect(port)
    except OSError:
        return None, None



port = int(sys.argv[1])
reconnected = False
num_tries = 0

server_socket = connect(port)

while True:
    try:
        connection_socket, addr = server_socket.accept()

        line = connection_socket.recv(4096).decode()
        initial = line
        wl = line.split()
        if (line == ""):
            sendMessage(connection_socket, parseerror1, 2)
            connection_socket.close()
            continue
        if not (line[0] == "G"):
            sendMessage(connection_socket, parseerror1, 2)
            connection_socket.close()
            continue
        elif (len(wl) == 1):
            if not (wl[0] == ("GET" or "GET\r" or "GET\n" or "GET\r\n")):
                sendMessage(connection_socket, parseerror1, 2)
            else:
                sendMessage(connection_socket, parseerror2, 2)
            connection_socket.close()
            continue
        elif (len(wl) == 0):
            sendMessage(connection_socket, parseerror1, 2)
            connection_socket.close()
            continue
        elif (len(wl) == 2):
            if (wl[0] != "GET"):
                sendMessage(connection_socket, parseerror1, 2)
            else:
                tmp = wl[1]
                if "\r\n" in tmp:
                    tmp = tmp[:-2]
                elif "\r" in tmp:
                    tmp = tmp[:-1]
                elif "\n" in tmp:
                    tmp = tmp[:-1]

                if (validurlchar(tmp)):
                    sendMessage(connection_socket, parseerror3, 2)
                else:
                    sendMessage(connection_socket, parseerror2, 2)
            connection_socket.close()
            continue
        elif (len(wl) > 3):
            if not (wl[0] == ("GET" or "GET\r" or "GET\n" or "GET\r\n")):
                sendMessage(connection_socket, parseerror1, 2)
            elif not (validurlchar(wl[1])):
                sendMessage(connection_socket, parseerror2, 2)
            elif not (validhttptoken(wl[2])):
                sendMessage(connection_socket, parseerror3, 2)
            else:
                sendMessage(connection_socket, parseerror4, 2)
            connection_socket.close()
            continue
        else:
            method = wl[0]
            url = wl[1]
            version = wl[2]
        if (method != "GET"):
            sendMessage(connection_socket, parseerror1, 2)
            connection_socket.close()
            continue

        if not validurlchar(url):
            sendMessage(connection_socket, parseerror2, 2)
            connection_socket.close()
            continue

        if not (validhttptoken(version)):
            sendMessage(connection_socket, parseerror3, 2)
            connection_socket.close()
            continue
        

        x = ""
        x = x + str("Method = " + method + '\n')
        x = x + str("Request-URL = " + url + '\n')

        if "\r\n" in version:
            version = version[:-2]
        elif "\r" in version:
            version = version[:-1]
        elif "\n" in version:
            version = version[:-1]
        x = x + str("HTTP-Version = " + version + '\n')

        fileextension = list(url.split("."))[-1]

        fileextension = fileextension.lower()

        if not (fileextension == "htm" or fileextension == "html" or fileextension == "txt"):
            message = x + printreaderror(1,url)
            sendMessage(connection_socket, message, 2)
            connection_socket.close()
            continue

        cd = os.getcwd()

        try:
            checkfile = open(cd + url, 'r')
        except FileNotFoundError as e:
            message = x + printreaderror(2, url)
            sendMessage(connection_socket, message, 2)
            connection_socket.close()
            continue
        except IOError as e:
            message = x + printreaderror(3,str(e))
            sendMessage(connection_socket, message, 2)
            connection_socket.close()
            continue
        

        for line in checkfile:
            x = x + str(line)
        
        sendMessage(connection_socket, x, 1)


        reconnected = False
        message = "done"
        num_tries = 0
        connection_socket.close()

    except (KeyboardInterrupt):
        try:
            connection_socket.close()
        except:
            this = "error"
        break

    except OSError as e:
        print("Connection Error")
        try:
            connection_socket.close()
        except:
            this = "error"
        break

try:
    server_socket.close()
except:
    this = "error"
try:
    connection_socket.close()
except:
    this = "error"
