#!/usr/bin/env python
## @package cnProtocol
#
# This is the mother class of any protocol module.
# @author Yong Jun Chang
#

import sys
import struct

from IPAddr         import *
from constants      import *

def cnConnect(*args):
    
    if len(args)<2:
        return

    for n in range(0,len(args)-1):
        parent = args[n]
        child = args[n+1]

        try:        
            child.set_parent(parent)
        except:
            print 'cnConnection error : ',parent
        
        done = parent.add_child(child)
        
## Mother class of any protocol class
# @author Yong Jun Chang
#
class cnProtocol:
    def __init__(self):
        
        # Each protocol layer can have only one parent and multiple child layers
        self.parent = None
        self.child = []
        self.DEBUG = False

    # Set lower layer stack
    def set_parent(self,parent):
        if self.parent:
            raise 
        self.parent = parent

    def add_child(self,child):
    
        if child not in self.child:
            self.child.append(child)
    
    def del_child(self,child):
        if child in self.child:
            self.child.remove(child)

    def set_debug(self,value):
        self.DEBUG = value
    
    def debug(self,*args):
        if self.DEBUG:
            for a in args:
                sys.stdout.write(a)
            sys.stdout.write('\n')

    

