'''
Created on Sep 30, 2012

@author: vincenzo
'''

import sys
import socket
import time
import random
import string
import os
import threading
from Netutils import closeSocket, createSocket
from threading import Timer,Thread

DEFAULT_PORT = 50020
class SendThread(Thread):
    '''
    classdocs
    '''


    def __init__(self,dsize,psize, nodelay ,throttle,burst, port = DEFAULT_PORT):
        '''
        Constructor
        '''
        threading.Thread.__init__(self)
        self.__dsize = dsize
        self.__psize = psize
        self.__throttle = throttle
        self.__burst = wait
        self.__SENDFLAG = True
        self.__port = port
        self.__SLEEPTIMER = False
	self.__nodelay = nodelay
    
    def sleepSet(self):
        self.__SLEEPTIMER=True
       
    def connect(self):
        sendsock = createSocket(self.__port)
        if sendsock!=None:
            if self.__psize == 0:
                self.__psize = sendsock.getsockopt(socket.SOL_TCP,socket.TCP_MAXSEG)
            #print self.__psize
            sendsock.setsockopt(socket.SOL_TCP,socket.TCP_MAXSEG,self.__psize)
            if self.__nodelay:
	            sendsock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            return sendsock
                    
    def send(self,sk, dsize, psize, throttle, burst):
        if dsize == None:
            dsize = 0
        print('Sending %d MB with a packet size of %d B (throttling: %.3f s)... to %s ' % (dsize/1024/1024, psize, throttle, str(sk.getpeername())))
        PACKET = ''.join(random.choice(string.letters) for i in range(psize))
        LAST_PACKET = ''.join((PACKET[:len(PACKET)-2],'&]'))
        start = time.time()
        TIMERSET=False    
               
        bytesCount = 0
        if dsize == 0:
            t = Timer(burst,self.sleepSet)
            while self.__SENDFLAG:
            
                if not TIMERSET:
                    TIMERSET=True
                    t = Timer(burst,self.sleepSet)
                    t.start()
                if self.__SLEEPTIMER:
#                print('Calling sleep for %.3f s',%throttle);
                    time.sleep(throttle)
                    TIMERSET=False
                    self.__SLEEPTIMER=False
#            inner_start = time.time()
#            time.sleep(throttle)
                sk.send(PACKET)
                bytesCount += len(PACKET)
            
            sk.send(LAST_PACKET)
            bytesCount += len(LAST_PACKET)
	    end = time.time()
        else:
            for i in range(dsize/psize - 1 ):
                if not TIMERSET:
                    TIMERSET=True
                    t = Timer(burst,self.sleepUnset)
                    t.start()
                if self.__SLEEPTIMER:
#            print('Calling sleep for %.3f s',%throttle);
                    time.sleep(throttle)
                    TIMERSET=False
                    self.__SLEEPTIMER=False
#            inner_start = time.time()
#            time.sleep(throttle)
                sk.send(PACKET)
                bytesCount += len(PACKET)
        
            sk.send(LAST_PACKET)
            bytesCount += len(PACKET)
            end = time.time()
    
    # compute stats
        timeS = end-start
        dataMB = bytesCount/1024./1024.
        transferMBs = dataMB/float(end-start)
    
        print('Finished sending. Total time: %.5fs. Total data: %.1fMB. Total packets: %d. Transfer rate: %.2fMB/s.' % ( timeS, dataMB, bytesCount/psize, transferMBs) )
        
          
    def run(self):
        sk = self.connect()
        self.send(sk,self.__dsize,self.__psize,self.__throttle,self.__wait)
        closeSocket(sk)
        
    def setflag(self):
        self.__flag = False
        
    def getTimeOffset(self):
        return self.__time_offset
    
    def setTimeOffset(self,offset):
        self.__time_offset = offset
        
