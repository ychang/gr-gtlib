#!/usr/bin/env python
## @package cnPacket
#
# This is a packet structure module.
# @author Yong Jun Chang
#

import sys
import struct
import copy


from IPAddr         import *
from constants      import *

## Mother class of any Protocol Data Unit (PDU)
# @author Yong Jun Chang
#
class cnPDU:
    def __init__(self):
        pass
    
    def serialize(self):
        pass

    def construct(self,packet):
        pass

    def copy(self):
        return copy.deepcopy(self)

## Main class of data PDU
# @author Yong Jun Chang
#
class cnData:
    def __init__(self,data=None):
        self.data = data
        pass

    def serialize(self):
        return self.data

    def construct(self,data):
        self.data = data
        return self

    def layer(self):
        return 5

## Main class of data PDU
# @author Yong Jun Chang
#
class cnMetaData():
    def __init__(self):
        
        self.crc = None
        self.timetag = None
        self.rssi = None
        self.clock_ratio = 1
        self.tx_type = 0
        self.freq_offset = 0
        self.scsf_value = 0     # For SCSF

## Main class of Packet
# @author Yong Jun Chang
#
class cnPacket:
    def __init__(self, data=None):
        self.PDUs = []
        self.metadata = cnMetaData()
        self.data = data
        
    # This is for outgoing flow (=sending)
    def pushPDU(self,header):
        if header:
            self.PDUs.insert(0,header)

    # This is for incoming flow (=receiving)
    def popPDU(self,header):
        self.PDUs.append(header)
        #self.data = self.data[len(header.serialize()):]

    def peekPDU(self,layer):

        for pdu in self.PDUs:
            if pdu.layer() == layer:
                return pdu
        return None

    def serialize(self):

        buff = ''
        for pdu in self.PDUs:
            buff = buff + pdu.serialize()
        #buff = buff + self.data

        return buff

    def copy(self):
        return copy.deepcopy(self)

