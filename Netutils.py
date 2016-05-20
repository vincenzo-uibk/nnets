'''
Created on Oct 2, 2012

@author: vlad, vincenzo
'''

import socket
import time

def getSocket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM )
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
#    s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
#    MAXSEG = s.getsockopt(socket.SOL_TCP,socket.TCP_MAXSEG)
    return s

def closeSocket(sk):
    try:
        sk.shutdown(socket.SHUT_RDWR)
    except:
        pass
    try:
        sk.close()
    except:
        pass
    
def createSocket(PORT):
    s = getSocket()
    s.settimeout(180)
    
    s.bind(('', PORT))
    s.listen(1)
    print('Listening on port %d' % PORT)
    connection = None
    try:
        connection, address = s.accept()
        #print('Inbound connection from %s:' % address[0],address[1])
    except socket.timeout as st:
        print('Timeout! Waited 3 minutes for incoming connection.')
        closeSocket(s)
        s=None
    return connection

def connectToSocket(host,PORT):
    s = getSocket()
    startTime = time.time()
    connecting=True
   
    print('Attempting to connect to %s:%d' % (host, PORT))
    while connecting and time.time()-startTime<120:
        time.sleep(1)
        try:
            s.connect((host, PORT))
            connecting=False
        except socket.error as se:
            pass
    if connecting:
        print('Timeout! Could not connect for 2 minutes.')
        closeSocket(s)
        return None
    else:
        print('Connected to %s:%d' % s.getpeername())
        return s