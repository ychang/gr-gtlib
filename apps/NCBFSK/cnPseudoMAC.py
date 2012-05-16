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

import utils

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

        print '[MAC] Protocol stack is created...' 
        
        pass

    def SetInterval(self,interval):
        self.interval = interval

    def queue_empty(self):
        return (len(self.queue)==0)

    def kill(self):
        self.stop = True

    def set_parent(self,parent):
        
        self.parent = parent
        #self.parent.set_rx_callback(self.data_indication)

    def data_indication(self, payload, packet):

        (l2header,l2payload) = cnMACHeader().construct(payload)

        print '[MAC:Rx] H=',utils.ByteToHex(l2header.serialize()),'| P=',utils.ByteToHex(l2payload)
        
        packet.popPDU(l2header)
        
        for ch in self.child:
            ch.data_indication(l2payload,packet)

    def header_request(self,peer_macaddr,self_macaddr=None):

        if self_macaddr == None:
            h = cnMACHeader(self.macaddr,peer_macaddr)
        else:
            h = cnMACHeader(self_macaddr,peer_macaddr)
        return h     

    def data_request(self,packet, l2header=None):
        
        print '[MAC:Tx] H=',utils.ByteToHex(l2header.serialize()),'| P=',utils.ByteToHex(packet.serialize())

        # Insert a UDP packet to the Packet class
        packet.pushPDU(l2header)
        
        self.parent.data_request(packet, self.parent.header_request())
        
    def data_request2(self, data):

        print '[MAC:Tx] Data requested : Length=',len(data)
        metadata = cnMetaData()
        metadata.timetag = None
        metadata.freq_offset = 0

        self.parent.data_request(data,metadata)


