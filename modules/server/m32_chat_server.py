#!/usr/bin/env python3
"""
original idea from
https://github.com/sp9wpn/m32_chat_server
"""

__author__ = "F3L Team"
__version__ = "0.1.0"
__license__ = "MIT"

import socket
import time
 

SERVER_IP = "0.0.0.0"
UDP_PORT = 7373
CLIENT_TIMEOUT = 300
MAX_CLIENTS = 10
KEEPALIVE = 10
RX_BUFFER_SIZE = 128
DEBUG = True
 
receivers = {}


def debug(str):
    if DEBUG:
        print(str)


def broadcast(data, client):
    for c in receivers.keys():
        if c == client:
              continue
        debug("Sending to {}".format(c))
        serversock.sendto(data, c)


def welcome(client):
    serversock.sendto(b'D\x7a\xa5\x45\x51\x70', client)  # this is ":hi" at 30wpm
    receivers[client] = time.time()
    debug("New client: {}".format(client))


def handle_new_client(data_body, client):
    if data_body[0:2] == b'T\\':
        if (len(receivers) < MAX_CLIENTS):
            receivers[client] = time.time()
            welcome(client)
        else:
            debug("ERR: maximum clients reached")
    else:
        debug("-unknown client, ignoring-")


def client_timeout_cleanup():
    for client, last_heared in receivers.items():
        if last_heared + CLIENT_TIMEOUT < time.time():
            serversock.sendto(b'D\x7a\xa5\x49\x52\x68\x70', client)  # this is ":bye" at 30wpm
            del receivers[client]
            debug ("Removing expired client {}".format(client))

 
def setup():
    global serversock
    serversock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    serversock.bind((SERVER_IP, UDP_PORT))
    serversock.settimeout(KEEPALIVE)


def receive_loop():
    while KeyboardInterrupt:
        # anti flood
        time.sleep(0.2)

        try:
            data, client = serversock.recvfrom(RX_BUFFER_SIZE)
            debug("Received {} from {}".format(data, client))
            data_header = data[0:2]
            data_body = data[2:]
            
            #debug ("\nReceived %s from %s" % (":".join("{:02x}".format(ord(c)) for c in data),client))

            if client in receivers:
                broadcast(data, client)
                receivers[client] = time.time()
            else:
                handle_new_client(data_body, client)

        except socket.timeout:
            # Send UDP keepalives
            for client in receivers.keys():
                serversock.sendto(b'', client)

        except (KeyboardInterrupt, SystemExit):
            serversock.close()
            break

        client_timeout_cleanup()
     

if __name__ == "__main__":
    setup()
    receive_loop()

