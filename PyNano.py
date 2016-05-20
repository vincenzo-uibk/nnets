'''
Python wrapper over libpynano.so for easy nanosleep in Python

Created on Sep 26, 2012

@author: vlad
'''
import os
from ctypes import c_int, cdll
import time
import sys

LIBNAME='libpynano.so.1.0.1'
LIBDIR='lib'


class PyNano(object):

    def __init__(self, dirpath=None):
        '''
        Loads libpynano.so from given path or from the current directory if no path is given.
        In:
            dirpath    string representing the relative path to the library (excluding the file name)
        Out:
            the loaded library
        '''
        self.correction_factor = 0
        # load the c library
        if dirpath==None:
            path=''.join((os.getcwd(),'/', LIBNAME));
        else:
            path=''.join((dirpath,'/', LIBNAME));
    
        self.lib=None
        try:
            self.lib=cdll.LoadLibrary(path)
        except Exception as ex:
            print("Could not load library. [%s] Exception: %s" % (path, str(ex)))
            
        self.correction_factor = self.calibrate()
        print("Loaded library: %s" %(str(self.lib)))
    
    def nanosleep(self, nanos):
        '''
        Sleeps for the given amount of nanoseconds... more or less.
        
        In:
            nanos - an int specifing the number of nanoseconds to sleep
        '''
        # prepare params
        nanoseconds = (nanos-self.correction_factor)
        # call lib
        try:
            self.lib.nano(nanoseconds)
        except Exception as ex:
            print('Failed nanosleep(%d) call. Exception: %s' % (nanoseconds,ex))
        # return success
        return True

    def calibrate(self):
#        print('calibrating ... ')
        st=time.time()
        for i in range(10000):
            self.nanosleep(100000)
        end=time.time()
#        realns=(end-st)*100000.0
#        print('\tEach cycle: {0} ns.'.format([realns]))
#        print('\tEach cycle: {0} ms.'.format([realns*0.1]))
#        print(int((end-st) * 1000000000.0 / 10000.0 - 100000.0))
        return int((end-st) * 1000000000.0 / 10000.0 - 100000.0)
        
    def get_correction_factor(self):
        return self.correction_factor

# ------------ TESTING ---------------    
if __name__ == '__main__':
    
    print('Loading library...')
    lib=PyNano('lib')
    
    print('[1] Sleeping 100ns ...')
    if lib.nanosleep(100):
        print("OK")
    else:
        print("Failed")
#        exit(1)
        
    print('[2] Sleeping 10,000 x 100,000ns')
    st=time.time()
    for i in range(5000):
        lib.nanosleep(200000)
    end=time.time()
    realns=(end-st) * 1000000000.0 / 5000.0
    print('\tEach cycle: {0} ns.'.format([realns]))
    print('\tEach cycle: {0} ms.'.format([realns*0.000001]))
    print('\tCorrection factor: {0} ns.'.format(lib.get_correction_factor()))
    
    
