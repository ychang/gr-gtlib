#!/usr/bin/env python
#
# Copyright 2005,2006,2007 Free Software Foundation, Inc.
# 
# This file is part of GNU Radio
# 
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from gnuradio import gr, gru, blks2
from gnuradio import eng_notation
from gnuradio import gr

import gnuradio.gr.gr_threading as _threading
import gtlib
import packet_utils

from math import pi,sqrt

import copy
import sys
import math
import struct

# from current dir

default_ola_spade_code = '\xAC\xDD\xA5\x5A\xA5\x5A\x5A\x55'

def dBm_to_TSSI(dBm):
    return dBm+73

# /////////////////////////////////////////////////////////////////////////////
#                              transmit path
# /////////////////////////////////////////////////////////////////////////////

class transmit_path(gr.hier_block2): 
    def __init__(self, options, parent):
        '''
        See below for what options should hold
        '''
        gr.hier_block2.__init__(self, "transmit_path",
                                gr.io_signature(0, 0, 0), # Input signature
                				gr.io_signature(1, 1, gr.sizeof_gr_complex)) # Output signature

        options = copy.copy(options)    # make a copy so we can destructively modify

        self._bitrate            = options.bitrate         # desired bit rate
        #self._inter              = options.inter           # Decimating rate for the USRP (prelim)
        self._samples_per_symbol  = options.samples_per_symbol  # desired samples/symbol
        self._down_sample_rate    = options.down_sample_rate


        self._verbose            = options.verbose
        self._tx_amplitude       = options.tx_amplitude    # digital amplitude sent to USRP
        
        self._use_whitener_offset = options.use_whitener_offset # increment start of whitener XOR data
        self._access_code        = packet_utils.conv_packed_binary_string_to_1_0_string(default_ola_spade_code)
        self._subchannel          = options.subchannel
        self._msgq_limit         = 4
        
        self.parent = parent

        # Turn it into NRZ data.
        self.nrz = gr.bytes_to_syms()
        self.sqwave = (1,) * self._samples_per_symbol       # rectangular window
        self.gaussian_filter = gr.interp_fir_filter_fff(self._samples_per_symbol, self.sqwave)

        #Sensitivity will be seletected by set_sensitivity function in main loop
        self.sensitivity_a = (2 *pi * self._subchannel) / self._samples_per_symbol	# phase change per bit = pi / 2 (for BFSK)
        self.sensitivity_b = (2 *pi * (self._subchannel)) / self._samples_per_symbol	# phase change per bit = pi / 2 (for BFSK)

        self._pad_for_usrp = True
        self._use_whitener_offset = False
        self._whitener_offset = 0
 
        # TODO 
        # BUG : Improve or Implement Stream Selector!!!! (Check the new GNU Radio blocks!!!)
               
        # =============================================================================
        # The first flowgraph for Digital Only Modulation
        # =============================================================================
        self._pkt_input = gr.message_source(gr.sizeof_char, self._msgq_limit)   # accepts messages from the outside world
        self.fmmod = gtlib.bfsk_modulator_fc(self.sensitivity_a,self.sensitivity_b)          # BFSK modulation
       
        self.amp = gr.multiply_const_cc(1)          # (Note that on the RFX cards this is a nop.)
        self.amp_2 = gr.multiply_const_cc(1)        # (Sub channel correction)

        if self._subchannel >= 1 and self._subchannel <= 4:
            self.amp_2.set_k(pow(1.2,(float(self._subchannel)-1)))

        #self.timetag_inserter = gtlib.usrp_timetag_insert()     

        if self._verbose:
            self._print_verbage()   # Display some information about the setup
        
       
                               
        # =============================================================================
        # Flowgraph connection
        # =============================================================================

        self.connect(self._pkt_input, self.nrz, self.gaussian_filter,self.fmmod,self.amp, self.amp_2, self)
       
        self.set_tx_amplitude(self._tx_amplitude)


    def set_tx_amplitude(self, ampl):
        """
        Sets the transmit amplitude sent to the USRP
        @param: ampl 0 <= ampl < 32768.  Try 8000
        """
        self._tx_amplitude = max(0.0, min(ampl, 1.0))
        
        # TODO
        self.amp.set_k(self._tx_amplitude)
        
    def send_pkt(self, payload='', timetag=None, eof=False):
        """
        Send the payload.

        @param payload: data to send
        @type payload: string
        """
        if eof:
            msg = gr.message(1) # tell self._pkt_input we're not sending any more packets
        else:
        
            # Digital Only Packet
                
            # TODO
            pkt = packet_utils.make_packet(payload,self._samples_per_symbol,2,self._access_code,self._pad_for_usrp)
            msg = gr.message_from_string(pkt)

            if timetag != None:                    

                timetag_int = int(math.floor(timetag))
                timetag_frac = timetag - float(timetag_int)

                samples = len(pkt)*8*self._samples_per_symbol
                
                #print '[TransmitPath] Digital Packet Length =',len(pkt)
                #print '[TransmitPath] Digital Packet Sample Length=',samples
                
                #self.timetag_inserter.put_timestamp(int(timetag_int), samples)
                #self.delay.set_delay (timetag_frac, samples)

            else:
                samples = len(pkt)*8*self._samples_per_symbol

                #print '[TransmitPath] Digital Packet Length =',len(pkt)
                #print '[TransmitPath] Digital Packet Sample Length=',samples

               
            self._pkt_input.msgq().insert_tail( msg )


    def send_pkt2(self, payload='', eof=False):
        """
        Send the payload.

        @param payload: data to send
        @type payload: string
        """
        if eof:
            msg = gr.message(1) # tell self._pkt_input we're not sending any more packets
        else:
        
            #print '[TxPath] Data Requested'
            pkt = scsf_packet_utils.make_packet(payload,
                                           self._samples_per_symbol,
                                           2,
                                           self._access_code,
                                           self._pad_for_usrp,
                                           1)

            msg = gr.message_from_string(pkt)

        scsf_msg = gr.message_from_string(struct.pack('!b', 0))
        self.scsf_encoder.msgq().insert_tail(scsf_msg)
        scsf_msg = gr.message_from_string(struct.pack('!b', 0))
        self.scsf_encoder.msgq().insert_tail(scsf_msg)
                
        self._pkt_input_scsf.msgq().insert_tail(msg)
        

    def set_sub_freq(self,sub_ch):

        self._subchannel = sub_ch
        
        #Sensitivity will be seletected by set_sensitivity function in main loop
        self.sensitivity_a = (2 *pi * self._subchannel) / self._samples_per_symbol	# phase change per bit = pi / 2 (for BFSK)
        self.sensitivity_b = (2 *pi * (self._subchannel)) / self._samples_per_symbol	# phase change per bit = pi / 2 (for BFSK)

        self.fmmod.set_sensitivity(self.sensitivity_a,self.sensitivity_b)

        if self._subchannel >= 1 and self._subchannel <= 4:
            self.amp_2.set_k(pow(1.2,(float(self._subchannel)-1)))

        
    def bitrate(self):
        return self._bitrate

    def samples_per_symbol(self):
        return self._samples_per_symbol

    def interp(self):
        return self._interp

    def add_options(normal, expert):
        """
        Adds transmitter-specific options to the Options Parser
        """
        normal.add_option("", "--tx-amplitude", type="eng_float", default=0.5, metavar="AMPL",
                          help="set transmitter digital amplitude: 0 <= AMPL < 32768 [default=%default]")
        normal.add_option("", "--tx-power", type="eng_float", default=None, metavar="TXPOWER",
                          help="set transmitter power : -73 <= TX_POWER < 17 (dBm)[default=%default]")
        normal.add_option("-l", "--subchannel", type="intx", default=1,
                          help="Select diversity sub-channel [default=%default]")
        
    # Make a static method to call before instantiation
    add_options = staticmethod(add_options)

    def _print_verbage(self):
        """
        Prints information about the transmit path
        """
        print ""
        print "Tx amplitude     %s"    % (self._tx_amplitude)
        print "samples/symbol:  %3d"   % (self._samples_per_symbol)
        

