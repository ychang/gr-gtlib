#!/usr/bin/env python
## @package cnMAC
#
# This is a MAC layer Python module.
# @author Yong Jun Chang
#

import sys
import struct
import time
from datetime import datetime 
from threading import Thread

from cnProtocol     import *
from constants      import *
from cnPacket       import *

# Transmission Interval
SEND_WITH_INTERVAL  = 0
SEND_IMMEDIATELY    = 1

# Medium Access Type
CSMA                = 0
TPROC               = 1

## Header class of a MAC layer
# @author Yong Jun Chang
#
class cnMACHeader(cnPDU):

    def __init__(self,s_macaddr=None,d_macaddr=None):
      
        self.s_macaddr = s_macaddr
        self.d_macaddr = d_macaddr
                    
    def serialize(self):
        h_s_addr = struct.pack('!L', self.s_macaddr)
        h_d_addr = struct.pack('!L', self.d_macaddr)
        return h_s_addr+h_d_addr

    def construct(self,frame):
        (self.s_macaddr,) = struct.unpack('!L', frame[0:4])
        (self.d_macaddr,) = struct.unpack('!L', frame[4:8])
        return (self,frame[8:])

    def layer(self):
        return 2

## Thread class of a MAC layer
# @author Yong Jun Chang
#
class cnMACThread(Thread):
    def __init__(self, queue, send_func, interval, debug):
        
        Thread.__init__(self)
        self.queue = queue
        self.send_func = send_func
        self.interval = interval
        self.debug = debug

    def run(self):
        while len(self.queue) > 0:
            packet = self.queue.pop()
            self.debug ( '[MAC] Send with interval : Time=',str(datetime.now() ))
            self.send_func(packet)
            time.sleep(self.interval)

## Main class of a MAC layer
# @author Yong Jun Chang
#
class cnMAC(cnProtocol, Thread):
    
    def __init__(self, macaddr):

        cnProtocol.__init__(self)
        Thread.__init__(self)
        
        self.macaddr = long(macaddr)
        self.queue = []
        self.mac_thread = None
        self.interval = CNMAC_INTER_PKT_DELAY
        #self.start()
        pass

    def SetInterval(self,interval):
        self.interval = interval

        if self.debug: print 'Interval = ',self.interval,' sec'

    def queue_empty(self):
        return (len(self.queue)==0)

    def kill(self):
        self.stop = True

    def set_parent(self,parent):
        
        self.parent = parent
        self.parent.set_rx_callback(self.data_indication)

    def data_indication(self,data,timetag,rssi):
        
        # Create a Packet class
        packet = cnPacket()
        
        # Set metadata
        packet.metadata.timetag = timetag
        packet.metadata.rssi = rssi
        
        (l2header,l2payload) = cnMACHeader().construct(data)
        packet.popPDU(l2header)
        
        if l2header.d_macaddr == BROADCAST_MAC_ADDR or l2header.d_macaddr == self.macaddr:
            self.debug( '[MAC] Packet is received. Src Addr = %s,Dest Addr = %s'%(MACAddrToStr(l2header.s_macaddr),MACAddrToStr(l2header.d_macaddr)) )
            for ch in self.child:
                ch.data_indication(l2payload,packet)
                    
        else:
            self.debug ( '[MAC] Packet is dropped. Src Addr = %s,Dest Addr = %s'%(MACAddrToStr(l2header.s_macaddr),MACAddrToStr(l2header.d_macaddr)) )
        
    def header_request(self,peer_macaddr,self_macaddr=None):

        if self_macaddr == None:
            h = cnMACHeader(self.macaddr,peer_macaddr)
        else:
            h = cnMACHeader(self_macaddr,peer_macaddr)
        return h     

    def data_request(self,packet, l2header=None):
        
        # Insert a UDP packet to the Packet class
        packet.pushPDU(l2header)
        
        if (packet.metadata.tx_type&0x01) == TX_TYPE_SEND_WITH_INTERVAL:
            self.debug ( '[MAC] METADATA = SEND_WITH_INTERVAL') 
            tx_type = TX_TYPE_SEND_WITH_INTERVAL
            
        else:
            self.debug ( '[MAC] METADATA = SEND_IMMEDIATELY') 
            tx_type = TX_TYPE_SEND_IMMEDIATELY
        
        if tx_type == TX_TYPE_SEND_IMMEDIATELY:

            self.debug ( '[MAC] Send immediately : Time=',str(datetime.now() )) 
            self.send_immediate(packet)

        else:

            self.queue.insert(0,packet.copy())

            if self.mac_thread:
                if not self.mac_thread.isAlive():
                    del self.mac_thread
                    self.mac_thread = None        

            if not self.mac_thread:
                self.mac_thread = cnMACThread(self.queue,self.send_immediate,self.interval, self.debug)
                self.mac_thread.start()

        #if not self.isAlive():
        #    self.start()

    def send_immediate(self,packet):
        
        #self.parent.send(packet.serialize(),packet.metadata)
        self.parent.send(packet)

    def run(self):

        while True:        
            if len(self.queue) > 0:
                self.debug ( '[MAC] Send with interval : Time=',datetime.now() )
                time.sleep(self.interval)
                self.send_immediate(self.queue.pop())
            else:
                time.sleep(self.interval)
        #self.join()


