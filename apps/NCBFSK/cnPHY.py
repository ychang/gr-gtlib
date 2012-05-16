#!/usr/bin/env python
## @package cnPHY
#
# This is a physical layer Python module.
# @author Yong Jun Chang
#
# Revision May 15, 2012 : Support UHD
#
from gnuradio import gr, gru
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from gnuradio import digital
from optparse import OptionParser
from threading import Thread
from math import pi,sqrt,floor

import random
import struct
import sys
import time
import Queue
import math
import os
import copy
import utils

from cnProtocol     import *
from constants      import *

# Including sub Python files
from transmit_path import transmit_path
from receive_path import receive_path
from gtlib_usrp import usrp_options
from uhd_interface import uhd_transmitter, uhd_receiver
from channel import channel_emulator

from cnProtocol     import *
from cnPacket       import *

RSSI_THRESHOLD = 0

#__________________________________
#import os
#print os.getpid()
#raw_input('Attach and press enter: ')


class my_top_block(gr.top_block):
    def __init__(self, rx_callback, options):
        gr.top_block.__init__(self)

        # Setting up 'Transmit Path'
        self.txpath = transmit_path(options, self)

        # Setting up 'Receive Path'
        packet = cnPacket()
        self.rxpath = receive_path(rx_callback, packet, options) 

        # Channel
        samples_per_packet = options.samples_per_symbol * 8 * 36
 
        if options.mode == 'default':
            print 'Operating mode : Default'
            
            mods = digital.modulation_utils.type_1_mods()
            modulator = mods[options.modulation]
            
            args = modulator.extract_kwargs_from_options(options)
            symbol_rate = options.bitrate / modulator(**args).bits_per_symbol()

            self.usrp_sink = uhd_transmitter(options.args, symbol_rate,
                                        options.samples_per_symbol,
                                        options.tx_freq, options.tx_gain,
                                        options.spec, options.antenna,
                                        options.verbose)

            self.usrp_source = uhd_receiver(options.args, symbol_rate,
                                       options.samples_per_symbol,
                                       options.rx_freq, options.rx_gain,
                                       options.spec, options.antenna,
                                       options.verbose)

            options.samples_per_symbol = self.usrp_sink._sps
            
            
            #self.usrp_sink = usrp_sink(options)
            #self.usrp_source = usrp_source(options)
            self.connect(self.txpath, self.usrp_sink)
            self.connect(self.usrp_source, self.rxpath)

            
        elif options.mode == 'loopback':
            print 'Operating mode : Loopback'
      
            self.channel = channel_emulator(options,samples_per_packet)
            self.connect(self.txpath, self.channel, self.rxpath)
            #self.connect(self.txpath,self.rxpath)

class cnPHYHeader(cnPDU):

    def __init__(self, index=None):
      
        self.index = index
                    
    def serialize(self):
        h_index = struct.pack('!L', self.index)
        return h_index

    def construct(self,frame):
        
        if len(frame)<4:
            return  (self,'')
            
        (self.index,) = struct.unpack('!L', frame[0:4])
        return (self,frame[4:])

    def layer(self):
        return 1

## Main class of GNU Radio top_block
# @author Yong Jun Chang
#
class cnPHY(cnProtocol):

    def __init__(self,options):
        
        
        cnProtocol.__init__(self)

        self.options = copy.copy(options)
        self.index = 0
        self.prev_tx_freq=None
        self.prev_tx_freq=None
        
        self.open()        

        print '>>> [cnPHY] Protocol stack is created...' 

    def open(self):
        self.tb = my_top_block(self.data_indication, self.options)
        self.tb.start()            
        
        amp = self.tb.txpath._tx_amplitude
        self.tb.txpath.set_tx_amplitude(0)
        #self.tb.txpath.send_pkt('',scsf_value = None, timetag=None, eof=False)
        time.sleep(0.1)
        self.tb.txpath.set_tx_amplitude(amp)
        

    def close(self):
        self.tb.stop()
        self.tb.wait()
        del self.tb

    def data_indication(self, payload, packet):
    #def rx_callback(self,ok, payload, timetag, power,measured_sps ):

        # added by Haejoon 2011 12 18
        if packet.metadata.crc ==False:
            print ' ###########################################'
            print ' ##### CRC Check Error in data_indication of cnPHY #####_____ Drop this packet'
            print ' ###########################################'
            print ' [PHY] =',utils.ByteToHex(payload)
            return 

        (l1header,l1payload) = cnPHYHeader().construct(payload)

        print '[cnPHY] RX: H=',utils.ByteToHex(l1header.serialize()),'| P=',utils.ByteToHex(l1payload)

        packet.popPDU(l1header)
        
        for ch in self.child:
            ch.data_indication(l1payload,packet)
                    
    def header_request(self):

        h = cnPHYHeader(self.index)
        self.index = (self.index + 1) % 65536        
        return h     


    #def data_request(self, payload='', header=None, metadata=None):
    def data_request(self, packet, l1header=None):
        
        print '[cnPHY] TX: H=',utils.ByteToHex(l1header.serialize()),'| P=',utils.ByteToHex(packet.serialize())
        
        # Insert a UDP packet to the Packet class
        packet.pushPDU(l1header)

        tx_timetag = None
        
        if self.options.mode != 'loopback':

            if packet.metadata.timetag != None:
                tx_timetag = float(packet.metadata.timetag) / 256.0
                    
        payload = packet.serialize()
        
        self.tb.txpath.send_pkt(payload,timetag = tx_timetag, eof=False)

   
    def setTemporalSubFreq(self,tx_freq_offset,rx_freq_offset):

        print '[PHY] Set Temporal Frequency : Tx Offset=%dHz, Rx Offset=%dHz'%(tx_freq_offset,rx_freq_offset)

        # Store Current TX and RX freqeuncy
        self.prev_tx_freq = self.tb.usrp_sink._tx_freq
        self.prev_rx_freq = self.tb.usrp_source._rx_freq

        # Set new frequencies with offsets
        self.tb.usrp_sink.set_freq ( self.prev_tx_freq + tx_freq_offset )
        self.tb.usrp_source.set_freq ( self.prev_rx_freq + rx_freq_offset )

    def restoreTemporalSubFreq(self):
        print '[PHY] Restore Frequency : Tx %dHz, Rx =%dHz'%(self.prev_tx_freq,self.prev_tx_freq)
        # Set new frequencies with offsets
        if self.prev_tx_freq!=None: self.tb.usrp_sink.set_freq ( self.prev_tx_freq )
        if self.prev_rx_freq!=None: self.tb.usrp_source.set_freq ( self.prev_rx_freq )

    def add_options(normal, expert_grp, channel_grp):
        
        mods = digital.modulation_utils.type_1_mods()
        for mod in mods.values():
                mod.add_options(expert_grp)        
                
        usrp_options.add_options(normal,expert_grp)
        uhd_transmitter.add_options(expert_grp)
        uhd_receiver.add_options(expert_grp)
        
        transmit_path.add_options(normal,expert_grp)        
        receive_path.add_options(normal,expert_grp)        
        channel_emulator.add_options(normal,channel_grp)

        expert_grp.add_option("","--use-whitener-offset", action="store_true", default=False,
                          help="make sequential packets use different whitening")

        expert_grp.add_option("","--down-sample-rate", type="intx", default=1,
                          help="Select the software down-sampling rate [default=%default]")
        
    # Make a static method to call before instantiation
    add_options = staticmethod(add_options)

        
