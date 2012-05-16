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


# For Compensating SOP Detection Time ( Average Samples from the start of the packet to the preamble detection )
SOP_detection_delay = {4: 300.0, 8:646.5, 16:1294.5, 32:2590.0}
default_ola_spade_code = '\xAC\xDD\xA5\x5A\xA5\x5A\x5A\x55'

def dBm_to_TSSI(dBm):
    return dBm+73
                          
# /////////////////////////////////////////////////////////////////////////////
#                              receive path
# /////////////////////////////////////////////////////////////////////////////

class receive_path(gr.hier_block2):

    def __init__(self, rx_callback, packet, options):


        gr.hier_block2.__init__(self, "receive_path",
                                gr.io_signature(1, 1, gr.sizeof_gr_complex), # Input signature
                                gr.io_signature(0, 0, 0)) # Output signature

        self.options = copy.copy(options)    # make a copy so we can destructively modify

        self._verbose            = self.options.verbose
        self._samples_per_symbol = self.options.samples_per_symbol  # desired samples/symbol
        self._order_of_subchannels= self.options.order_of_subchannels
                
        self._rx_callback       = rx_callback             # this callback is fired when there's a packet available
        self._packet            = packet

        # Options for Transmit Time Synchronization
        self._sfo               = self.options.sfo             # Sampling Frequency Offset Compensation
        self._bpf               = self.options.bpf             # Bandpass Filtering
        self._gamma             = self.options.gamma
        self._access_code       = packet_utils.conv_packed_binary_string_to_1_0_string(default_ola_spade_code)
        self._threshold         = 2

        self._down_sample_rate  = self.options.down_sample_rate
        self.n_filter_taps = int (self._samples_per_symbol / self._down_sample_rate)
        
        #self._cs_upper_db       = -11
        #self._cs_lower_db       = -11

        # Display some information about the setup
        if self._verbose:
            self._print_verbage()

        self._rcvd_pktq     = gr.msg_queue()          # holds packets from the PHY
        self.framer_sink    = gtlib.framer_sink_2(self._sfo,self._rcvd_pktq,False)
        self.ncbfsk_demod   = gtlib.ncbfsk_freq_diversity(self.n_filter_taps, self._gamma,self._access_code,self._threshold)
                          
        #self.timetag_extractor = gtlib.usrp_timetag_extract(self._cs_upper_db,self._cs_lower_db, 8*self._samples_per_symbol, self._down_sample_rate)

        self._bitrate = 256000
        #self.timetag_extractor.config_clock(self._bitrate*256, self._bitrate)
        self.ncbfsk_demod.config_timestamp(0)
        
        unlock_func = self.ncbfsk_demod.unlock()

        phase_1 = phase_2 = phase_3 = phase_4 = 0

        self.amp = gr.multiply_const_cc(10)


        sensitivity_1 = (2 *pi * 1) / self.n_filter_taps
        sensitivity_2 = (2 *pi * 2) / self.n_filter_taps
        sensitivity_3 = (2 *pi * 3) / self.n_filter_taps
        sensitivity_4 = (2 *pi * 4) / self.n_filter_taps

        #Matched Filter Taps for diversity channel #1
        self.taps_1_a = [1,] * self.n_filter_taps
        self.taps_1_b = [1,] * self.n_filter_taps

        #Matched Filter Taps for diversity channel #2
        self.taps_2_a = [1,] * self.n_filter_taps
        self.taps_2_b = [1,] * self.n_filter_taps

        #Matched Filter Taps for diversity channel #3
        self.taps_3_a = [1,] * self.n_filter_taps
        self.taps_3_b = [1,] * self.n_filter_taps

        #Matched Filter Taps for diversity channel #4
        self.taps_4_a = [1,] * self.n_filter_taps
        self.taps_4_b = [1,] * self.n_filter_taps


        #Magnitude
        self.abs_1_a = gr.complex_to_mag()
        self.abs_1_b = gr.complex_to_mag()
        self.abs_2_a = gr.complex_to_mag()
        self.abs_2_b = gr.complex_to_mag()
        self.abs_3_a = gr.complex_to_mag()
        self.abs_3_b = gr.complex_to_mag()
        self.abs_4_a = gr.complex_to_mag()
        self.abs_4_b = gr.complex_to_mag()
        
        for i in range(0,self.n_filter_taps):   

            self.taps_1_a[i] =  (math.cos(phase_1) + 1j* (math.sin(phase_1))) / self.n_filter_taps
            self.taps_1_b[i] =  (math.cos(phase_1) - 1j* (math.sin(phase_1))) / self.n_filter_taps

            self.taps_2_a[i] =  (math.cos(phase_2) + 1j* (math.sin(phase_2))) / self.n_filter_taps
            self.taps_2_b[i] =  (math.cos(phase_2) - 1j* (math.sin(phase_2))) / self.n_filter_taps

            self.taps_3_a[i] =  (math.cos(phase_3) + 1j* (math.sin(phase_3))) / self.n_filter_taps
            self.taps_3_b[i] =  (math.cos(phase_3) - 1j* (math.sin(phase_3))) / self.n_filter_taps

            self.taps_4_a[i] =  (math.cos(phase_4) + 1j* (math.sin(phase_4))) / self.n_filter_taps
            self.taps_4_b[i] =  (math.cos(phase_4) - 1j* (math.sin(phase_4))) / self.n_filter_taps
            
            phase_1 = phase_1 + sensitivity_1
            phase_2 = phase_2 + sensitivity_2

            phase_3 = phase_3 + sensitivity_3
            phase_4 = phase_4 + sensitivity_4

        self.match_filter_1_a = gr.fir_filter_ccc(1,self.taps_1_a)
        self.match_filter_1_b = gr.fir_filter_ccc(1,self.taps_1_b)

        self.match_filter_2_a = gr.fir_filter_ccc(1,self.taps_2_a)
        self.match_filter_2_b = gr.fir_filter_ccc(1,self.taps_2_b)

        self.match_filter_3_a = gr.fir_filter_ccc(1,self.taps_3_a)
        self.match_filter_3_b = gr.fir_filter_ccc(1,self.taps_3_b)

        self.match_filter_4_a = gr.fir_filter_ccc(1,self.taps_4_a)
        self.match_filter_4_b = gr.fir_filter_ccc(1,self.taps_4_b)

        self.sub = gr.sub_ff()
        self.adder_a = gr.add_ff()
        self.adder_b = gr.add_ff()
        
        fs = gr.null_sink(gr.sizeof_float)

        self.connect(self,self.amp)

        # Data Stream

        print '>>> [Receive Path] Order of Subchannels=', self._order_of_subchannels

        if self._order_of_subchannels > 0:
            print '>>> [Receive Path] Setup first subchannel'
            self.connect(self.amp,self.match_filter_1_a,self.abs_1_a,(self.adder_a,0))
            self.connect(self.amp,self.match_filter_1_b,self.abs_1_b,(self.adder_b,0))
        
        if self._order_of_subchannels > 1:
            print '>>> [Receive Path] Setup second subchannel'
            self.connect(self.amp,self.match_filter_2_a,self.abs_2_a,(self.adder_a,1))
            self.connect(self.amp,self.match_filter_2_b,self.abs_2_b,(self.adder_b,1))
        
        if self._order_of_subchannels > 2:
            print '>>> [Receive Path] Setup third subchannel'
            self.connect(self.amp,self.match_filter_3_a,self.abs_3_a,(self.adder_a,2))
            self.connect(self.amp,self.match_filter_3_b,self.abs_3_b,(self.adder_b,2))
        
        if self._order_of_subchannels > 3:
            print '>>> [Receive Path] Setup fourth subchannel'
            self.connect(self.amp,self.match_filter_4_a,self.abs_4_a,(self.adder_a,3))
            self.connect(self.amp,self.match_filter_4_b,self.abs_4_b,(self.adder_b,3))
        
        self.connect(self.adder_a,(self.sub,0))
        self.connect(self.adder_b,(self.sub,1))

        self.connect(self.sub,self.ncbfsk_demod)

        self.connect(self.ncbfsk_demod,self.framer_sink)

        # Time-tag Stream
        #self.connect((self.timetag_extractor,0),(self.ncbfsk_demod,0),(self.framer_sink,0))
        #self.connect((self.timetag_extractor,0),gr.null_sink(8))

        self._watcher = _queue_watcher_thread_demod_pkts_ncbfsk(self._rcvd_pktq, rx_callback, self._packet, self.ncbfsk_demod, self.framer_sink, self)

    def set_gain(self, gain):
        """
        Sets the analog gain in the USRP
        """
        if gain is None:
            r = self.subdev.gain_range()
            gain = (r[0] + r[1])/2               # set gain to midpoint
        self.gain = gain
        return self.subdev.set_gain(gain)

    def bitrate(self):
        return self._bitrate

    def samples_per_symbol(self):
        return self._samples_per_symbol

    def decim(self):
        return self._decim

    def add_options(normal, expert):
        """
        Adds receiver-specific options to the Options Parser
        """
        expert.add_option("", "--sfo", type="intx", default=True,
                          help="Sampling Frequency Offset Compensation")

        expert.add_option("", "--bpf", type="intx", default=False,
                          help="Bandpass Filtering")

        expert.add_option("", "--gamma", type="float", default=0.0,
                          help="SPADE threshold")

        expert.add_option("","--order-of-subchannels", type="intx", default=4,
                          help="Select the order of diversity sub-channels [default=%default]")


    # Make a static method to call before instantiation
    add_options = staticmethod(add_options)

    def _print_verbage(self):
        """
        Prints information about the receive path
        """
        print ""
        print "\nReceive Path:"
        print "samples/symbol:  %3d"   % (self._samples_per_symbol)
        #print "number of filter taps:  %3d"   % (self.n_filter_taps)
        # print "Rx Frequency:    %f"    % (self._rx_freq)

class _queue_watcher_thread_demod_pkts_ncbfsk(_threading.Thread):
    def __init__(self, rcvd_pktq, callback,packet,ncbfsk_demod,framer_sink, parent):
        _threading.Thread.__init__(self)
        self.setDaemon(1)
        self.rcvd_pktq = rcvd_pktq
        self.callback = callback
        self.packet = packet
        self.keep_running = True
        self.start()
        self.ncbfsk_demod = ncbfsk_demod
        self.framer_sink = framer_sink
        self.parent = parent

    def run(self):
        while self.keep_running:
            msg = self.rcvd_pktq.delete_head()
            ok, payload = packet_utils.unmake_packet(msg.to_string(), 0)
            self.ncbfsk_demod.unlock()
            # Avoid tiny bug on MSG_QUEUE (Yong, 09/01/09)

            if self.callback:
            
                meta_idx = msg.type()
                
                packet_copy = copy.deepcopy(self.packet)
                
                packet_copy.metadata.crc = ok

                # SCSF Packet Check!!!
                if ( (self.framer_sink.meta_header(meta_idx) >> 12)&0xF == 1 ):
                    packet_copy.metadata.scsf_value = self.parent.scsf_decoder.read_scsf_value() - self.parent.scsf_decoder.read_scsf_ref()
                else:
                    packet_copy.metadata.scsf_value = None

                try:
                    time_tag_correction = math.floor(SOP_detection_delay[self.parent.options.samples_per_symbol]*256.0)
                except:
                    print 'Exception Error: Samples per symbol %d does not support'%self.parent.options.samples_per_symbol



                packet_copy.metadata.timetag = self.framer_sink.meta_rtg(meta_idx) - time_tag_correction
                packet_copy.metadata.rssi = self.framer_sink.meta_rssi(meta_idx)
                packet_copy.metadata.clock_ratio = self.framer_sink.meta_sps(meta_idx)

                self.callback(payload, packet_copy)
                
