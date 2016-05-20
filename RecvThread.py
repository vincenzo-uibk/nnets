'''
Created on Sep 30, 2012

@author: vincenzo
'''
from Netutils import connectToSocket, closeSocket
import socket
import time
import threading
from ctypes import *

DEFAULT_PORT = 50020

class RecvThread(threading.Thread):
    '''
    classdocs
    '''


    def __init__(self,ip,psize,nodelay,port = DEFAULT_PORT):
        '''
        Constructor
        '''
        threading.Thread.__init__(self)
        self.__ip = ip
        self.__psize = psize
	self.__nodelay
        self.__port = port
    
    def connect(self):
        sk = connectToSocket(self.__ip,self.__port)
        if sk!=None:
                if self.__psize == 0:
                    self.__psize = sk.getsockopt(socket.SOL_TCP,socket.TCP_MAXSEG)
                sk.setsockopt(socket.SOL_TCP,socket.TCP_MAXSEG,self.__psize)
		if self.__nodelay:
	                sk.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
                return sk
    
    def recv(self,sk, psize):
        print('Receiving with a buffer size of %d B...' % psize)
    
        packetCount = 0
        bytesCount = 0.0
        start = time.time()
        data='00'
        while data!=None and len(data)>1 and data[len(data)-2:]!='&]':
            #    for i in range(dsize/psize):
            data = sk.recv(psize)
            bytesCount += len(data)
            packetCount += 1
#            print 'Received: ' + str(len(data)) + ' from ' + str(sk.getpeername()) + ' at ' + str(sk.getsockname())
#        print len(data)
#        print 'Received: ' + str(bytesCount) + ' from ' + str(sk.getpeername())
        end = time.time()
    
        # compute stats
        timeS = end-start
        dataMB = bytesCount/1024./1024.
        transferMBs = dataMB/float(end-start)
    
        # desync for when running on the same machine
        time.sleep(1)
        print('Finished receiving. Total time: %.5fs. Total data: %.1fMB. Total packets: %d. Transfer rate: %.2fMB/s.' % (timeS, dataMB, packetCount, transferMBs) )

    def run(self):
        recvsock = self.connect()
        self.recv(recvsock,self.__psize)
        closeSocket(recvsock)
        
