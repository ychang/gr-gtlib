
#/bin/env python
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

from math import pi,sqrt

import random
import copy
import sys
import math
import time
import random

class channel_emulator(gr.hier_block2): 

    def __init__(self, options, samples_per_packet):

	gr.hier_block2.__init__(self, "channel_emulator_path",
                                gr.io_signature(1, 1, gr.sizeof_gr_complex), # Input signature
                                gr.io_signature(1, 1, gr.sizeof_gr_complex)) # Output signature

        
        if not options.channel_off:

            SNR = 10.0**(options.snr/10.0)
            power_in_signal = abs(options.tx_amplitude)**2.0
            noise_power_in_channel = power_in_signal/SNR
            noise_voltage = math.sqrt(noise_power_in_channel/2.0)
            print "Noise voltage: ", noise_voltage

            frequency_offset = options.frequency_offset# / options.fft_length
            clock_ratio = options.clock_ratio
            print "Frequency offset: ", frequency_offset

            if options.multipath_on:
                taps = [1.0, .2, 0.0, .1, .08, -.4, .12, -.2, 0, 0, 0, .3]
            else:
                taps = [1.0, 0.0]

        else:
            noise_voltage = 0.0
            frequency_offset = 0.0
            clock_ratio = 1.0
            taps = [1.0, 0.0]

        self.samples_per_packet = samples_per_packet
        self.length_of_silence = options.silence_length
        
        self.channel = gr.channel_model(noise_voltage, frequency_offset, clock_ratio,taps)
       
        self.scale = gr.multiply_const_cc(1)          # (Note that on the RFX cards this is a nop.)
        self.scale.set_k(options.scale)


        print "Channel : Samples per Packet ",int(self.samples_per_packet)
        # Stream Mux        
        if options.discontinuous:
            stream_size = [self.length_of_silence, int(self.samples_per_packet)]
        else:
            stream_size = [1, 100000]

        z = [0,]
        self.zeros = gr.vector_source_c(z, True)

        self.mux = gtlib.channel_mux(gr.sizeof_gr_complex, stream_size)
        #self.throttle = gr.throttle(gr.sizeof_gr_complex, options.sample_rate)

        """
        
        self.connect(self.zeros, (self.mux,0))
        self.connect(self, (self.mux,1))
        # Connect
        if options.fractional_delay:
            self.lagrange_filter=gr.fir_filter_ccf(1, [0.2734, 1.0938, -0.5469, 0.2188])                
            self.connect(self.mux, self.channel, self.lagrange_filter, self.scale)
        else:
            self.connect(self.mux, self.channel, self.scale)

        """
        #self.trimmer = gtlib.usrp_timetag_insert()     
        """
        
        self.connect(self.scale,self.trimmer,self)
        """
        self.connect( self, self.scale, self)
        
    def set_snr(self,snr):

        noise_voltage = 0

        if snr < 100:
            SNR = 10.0**(float(snr)/10.0)
            noise_power = self.power_in_signal/SNR
            noise_voltage = math.sqrt(noise_power)

        self.channel.set_noise_voltage(noise_voltage)                    
            
            
    def set_samples_per_packet(self,samples_per_packet):
    
        self.samples_per_packet = samples_per_packet    
        
    def set_length_of_silence(self,length_of_silence):

        self.length_of_silence = length_of_silence

    def add_options(normal, channel_grp):
        
        channel_grp.add_option("", "--scale", type="eng_float", default=1,
                           help="set the scale of the received signal [default=%default]")

        channel_grp.add_option("", "--snr", type="eng_float", default=100,
                           help="set the SNR of the channel in dB [default=%default]")

        channel_grp.add_option("", "--frequency-offset", type="eng_float", default=0,
                           help="set frequency offset introduced by channel [default=%default]")

        channel_grp.add_option("", "--clock-ratio", type="eng_float", default=1.0,
                           help="set sampling clock offset introduced by channel [default=%default]")

        channel_grp.add_option("", "--seed", action="store_true", default=False,
                           help="use a random seed for AWGN noise [default=%default]")

        channel_grp.add_option("", "--clockrate-ratio", type="eng_float", default=1.0,
                      help="set clock rate ratio (sample rate difference) between two systems [default=%default]")

        channel_grp.add_option("","--discontinuous", type="int", default=0,
                      help="enable discontinous transmission, burst of N packets [Default is continuous]")

        channel_grp.add_option("","--channel-off", action="store_true", default=False,
                          help="Turns AWGN, freq offset channel off")

        channel_grp.add_option("","--multipath-on", action="store_true", default=False,
                          help="enable multipath")

        channel_grp.add_option("","--fractional-delay", action="store_true", default=False,
                          help="enable fractional delay")

        channel_grp.add_option("","--silence-length", type="int", default=100,
                          help="sample length of silence period")


    # Make a static method to call before instantiation
    add_options = staticmethod(add_options)




