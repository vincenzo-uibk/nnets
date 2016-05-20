#! /usr/bin/python
'''
Created on Dec 14, 2010

@author: vlad
'''
import sys

def get_multival_param(arguments, name, alt_name=None):
    '''
    Gets the values of the given parameter.
    In:
        arguments - an array of strings representing the command line parameters;
        name - the name of the sought parameter.
    Out:
        a list of strings representing the values of the sought parameter, extracted from arguments,
        or None if the parameter is not present 
    '''
    values = None
    
    found = False
    for param in arguments:
        if found:
            if param.startswith("-"):
                break
            else:
                values.append(param)
        else:
            if param == name or (alt_name!=None and param == alt_name):
                values = list()
                found = True
                
    return values

def get_singleval_param(arguments, name, alt_name=None):
    '''
    Gets the value of the given parameter.
    In:
        arguments - an array of strings representing the command line parameters;
        name - the name of the sought parameter.
    Out:
        a string representing the value of the sought parameter (only the first value is returned), extracted from arguments,
        or None if the parameter is not present 
    '''
    values = get_multival_param(arguments, name, alt_name)
    if values!=None and len(values)>0:
        return values[0]
    else:
        return None

if __name__=='__main__':
    print("CommandLineOptions.py is a library. Nothing to do.")
    sys.exit(1)
