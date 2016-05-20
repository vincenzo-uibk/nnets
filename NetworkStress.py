#! /usr/bin/python2.7
'''
Created on Feb 27, 2012

@author: vincenzo
'''
import CommandLineOptions
import sys
import socket
import time
import random
import string
import os
from Netutils import closeSocket, createSocket, connectToSocket
from SendThread import SendThread
from RecvThread import RecvThread
import PyNano
from threading import Timer

class NetworkStress:

    def __init__(self):
        self.__SENDFLAG = True
        self.__PORT=50020
        self.__MAXSEG = 0	

    def getPort(self):
        return self.__PORT

    def sleepSet(self):
        self.__SLEEPTIMER=True

    def send(self,sk, dsize, psize, throttle, wait):
        if dsize == None:
            dsize = 0
        print('Sending %d MB with a packet size of %d B (throttling: %.3f s)... to %s ' % (dsize/1024/1024, psize, throttle, str(sk.getpeername())))
        PACKET = ''.join(random.choice(string.letters) for i in range(psize))
        LAST_PACKET = ''.join((PACKET[:len(PACKET)-2],'&]'))
        start = time.time()
        TIMERSET=False    
        self.__SLEEPTIMER=False
        #    outpk = open('pack_d_eth', 'a')
        #inner_start = time.time()
        bytesCount = 0
        if dsize == 0:
            t = Timer(wait,self.sleepSet)
            while self.__SENDFLAG:
            #	if throttle!=0 and time.time() - inner_start >= float(wait):
                if not TIMERSET:
                    TIMERSET=True
                    t = Timer(wait,self.sleepSet)
                    t.start()
                if self.__SLEEPTIMER:
#			    print('Calling sleep for %.3f s',%throttle);
                    time.sleep(throttle)
                    TIMERSET=False
                    self.__SLEEPTIMER=False
#			inner_start = time.time()
#			time.sleep(throttle)
                sk.send(PACKET)
                bytesCount += len(PACKET)
            
            sk.send(LAST_PACKET)
            bytesCount += len(LAST_PACKET)
	    end = time.time()
        else:
            for i in range(dsize/psize - 1 ):
                if not TIMERSET:
                    TIMERSET=True
                    t = Timer(wait,self.sleepSet)
                    t.start()
                if self.__SLEEPTIMER:
#			print('Calling sleep for %.3f s',%throttle);
                    time.sleep(throttle)
                    TIMERSET=False
                    self.__SLEEPTIMER=False
#			inner_start = time.time()
#			time.sleep(throttle)
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
#        print len(data)
#        print 'Received: ' + str(bytesCount)
        end = time.time()
    
    # compute stats
        timeS = end-start
        dataMB = bytesCount/1024./1024.
        transferMBs = dataMB/float(end-start)
    
        # desync for when running on the same machine
        time.sleep(1)
        print('Finished sending. Total time: %.5fs. Total data: %.1fMB. Total packets: %d. Transfer rate: %.2fMB/s.' % (timeS, dataMB, packetCount, transferMBs) )

    def duplex(self,peer, dsize, psize, nodelay, throttle, burst, pairnum = 1):
        BASE_PORT = 50019
        sendT = []
        recvT = []
        for i in range(pairnum):
            sendT.append(SendThread(dsize,psize, nodelay, throttle,burst,BASE_PORT + i));
            recvT.append(RecvThread(peer, psize, nodelay ,BASE_PORT + i));
    
            sendT[i].start()
            recvT[i].start()
        
        for i in range(pairnum):
            recvT[i].join()
            sendT[i].join()

    def setSendFlag(self,val = False):
        self.__SENDFLAG = val
        
    def getSendFlag(self):
        return self.__SENDFLAG

    def print_usage(self):
        print('USAGE:    %s -m <mode> -p <packet_size> ( -i <IP> ) | ( -s <data_size> [-t <throttle>] )' % sys.argv[0])
        print('')
        print('\t-m|--mode     : the mode to start in. Choose from \'send\' and \'recv\' and \'nuplex\'')
        print('\t-p|--packet   : the packet size to use for sending the data, in bytes. In mode \'recv\' this represents the receive buffer size.')
        print('\t-i|--ip       : [RECV mode] the IP to connect to')
        print('\t-s|--size     : [SEND mode] the total amount of data to send in MB')
        print('\t-t|--throttle : [SEND mode] the time to wait between successive packets in milliseconds')
        print('\t-b|--burst : [SEND mode] the size in milliseconds of active sending intervals')
        print('\t-S|--seconds : [SEND mode] sets a timer to our data transfer (in seconds)')
        print('\t-P|--pairs : [NUPLEX mode] the number of send/receive pairs')
	print('\t-N|--nodelay : Sets the TCP_NODELAY flag (disable Nagle Buffering Algorithm)')
        sys.exit(1)
    
if __name__=='__main__':
    
    NetStress = NetworkStress()
    
    mode = CommandLineOptions.get_singleval_param(sys.argv, '-m', '--mode')
    if mode!=None:
        mode=mode.lower()
    
    
    size = CommandLineOptions.get_singleval_param(sys.argv, '-s', '--size')
    if size != None:
        size = int(size) * 1024 * 1024
    ip  = CommandLineOptions.get_singleval_param(sys.argv, '-i', '--ip')
    burst = CommandLineOptions.get_singleval_param(sys.argv, '-b', '--burst')
    seconds = CommandLineOptions.get_singleval_param(sys.argv, '-S', '--seconds')
    pairs = CommandLineOptions.get_singleval_param(sys.argv, '-P', '--pairs')
    nodelay = CommandLineOptions.get_singleval_param(sys.argv,'-N','--nodelay')
    if nodelay == None:
	nodelay = False
    if pairs == None:
        pairs = 1
    if seconds != None:
        seconds = float(seconds)
    if burst == None:
        burst = 0.001
    else:
        burst = float(burst)/1000.0
    if mode==None or (mode!='send' and mode!='recv' and mode!='duplex'):
        print('Invalid mode or no mode specified.')
        NetStress.print_usage()
    elif mode=='send' or mode == 'nuplex':
        #size = CommandLineOptions.get_singleval_param(sys.argv, '-s', '--size')
        throttle = CommandLineOptions.get_singleval_param(sys.argv, '-t', '--throttle')
        if throttle == None:
            throttle = 0
        if size==None and seconds == None:
            print('No size and no timer specified.')
            NetStress.print_usage()
        elif throttle != None:
            throttle = float(throttle)/1000.0    
       
    elif mode=='recv' or mode == 'duplex':
        
        if ip==None:
            print('The IP of the peer to connect to was not specified.')
            NetStress.print_usage()
    
    packet = CommandLineOptions.get_singleval_param(sys.argv, '-p', '--packet')
    if packet==None:
        packet = 0
    else:
        packet = int(packet)
    if mode=='send':
            sendTimer = None
            if seconds != None and seconds > 0:
                sendTimer = Timer(seconds,NetStress.setSendFlag)
            sk = createSocket(NetStress.getPort())
            if sk!=None:
                if packet == 0:
                        packet = sk.getsockopt(socket.IPPROTO_TCP,socket.TCP_MAXSEG)
                sk.setsockopt(socket.IPPROTO_TCP,socket.TCP_MAXSEG,packet)
		if nodelay:
			sk.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                if sendTimer != None:
                    sendTimer.start()
                NetStress.send(sk, size, packet, throttle, burst)
                closeSocket(sk)
            else:
                print('Fatal! Did not receive any connection from peer.')
                sys.exit(1)
    elif mode=='recv':
        sk = connectToSocket(ip,NetStress.getPort())
        if sk!=None:
                if packet == 0:
                    packet = sk.getsockopt(socket.IPPROTO_TCP,socket.TCP_MAXSEG)
                sk.setsockopt(socket.IPPROTO_TCP,socket.TCP_MAXSEG,packet)
		if nodelay:
			sk.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
#               sk.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,packet)
                NetStress.recv(sk, packet)
#                send(size, packet, throttle)
                closeSocket(sk)
        else:
            print('Fatal! Could not connect to peer.')
            sys.exit(2)
    elif mode=='duplex':
        NetStress.duplex(ip, size, packet, nodelay, throttle, burst,int(pairs))
    else:
            print('Fatal! Could not connect to peer.')
            sys.exit(2)
