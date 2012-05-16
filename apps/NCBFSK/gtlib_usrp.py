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
from gnuradio import digital

import gnuradio.gr.gr_threading as _threading
from math import pi,sqrt

import copy
import sys
import math
import os


# /////////////////////////////////////////////////////////////////////////////
#                              USRP General
# /////////////////////////////////////////////////////////////////////////////
class usrp_options():
    def add_options(normal, expert):
        """
        Adds transmitter-specific options to the Options Parser
        """
        mods = digital.modulation_utils.type_1_mods()

        normal.add_option("-m", "--modulation", type="choice", choices=mods.keys(),
                      default='psk',
                      help="Select modulation from: %s [default=%%default]"
                            % (', '.join(mods.keys()),))

        normal.add_option("-r", "--bitrate", type="eng_float", default='62.5k',
                          help="specify bitrate [default=%default]")
        normal.add_option("", "--tx-freq", type="eng_float", default=None,
                          help="set transmit frequency to FREQ [default=%default]", metavar="FREQ")
        normal.add_option("", "--rx-freq", type="eng_float", default=None,
                          help="set Rx frequency to FREQ [default=%default]", metavar="FREQ")
        normal.add_option("", "--freq", type="eng_float", default=None,
                          help="set Tx/Rx frequency to FREQ [default=%default]", metavar="FREQ")

        expert.add_option("-w", "--which", type="int", default=0,
                          help="select USRP board [default=%default]")
        expert.add_option("-T", "--tx-subdev-spec", type="subdev", default=None,
                          help="select USRP Tx side A or B")
        expert.add_option("-R", "--rx-subdev-spec", type="subdev", default=None,
                          help="select USRP Rx side A or B")


        # TX Amplitude / Gain / Power

        normal.add_option("", "--tx-gain", type="eng_float", default=None, metavar="TXGAIN",
                          help="set transmitter digital amplitude: 0 <= TX_GAIN < 90 [default=%default]")

        # RX Gain

        normal.add_option("", "--rx-gain", type="eng_float", default=45, metavar="GAIN",
                          help="set receiver gain in dB [default=midpoint].  See also --show-rx-gain-range")
        normal.add_option("", "--show-rx-gain-range", action="store_true", default=False, 
                          help="print min and max Rx gain available on selected daughterboard")


        normal.add_option("-s", "--samples-per-symbol", type="int", default=16,
                          help="set samples/symbol [default=%default]")
        
        expert.add_option("-i", "--interp", type="intx", default=None,
                          help="set fpga interpolation rate to INTERP [default=%default]")
        expert.add_option("-d", "--decim", type="intx", default=None,
                          help="set fpga decimation rate to DECIM [default=%default]")

        expert.add_option("", "--log", action="store_true", default=False,
                          help="Log all parts of flow graph to file (CAUTION: lots of data)")


    # Make a static method to call before instantiation
    add_options = staticmethod(add_options)


# /////////////////////////////////////////////////////////////////////////////
#                              USRP Utils
# /////////////////////////////////////////////////////////////////////////////
    
class usrp_utils():
    def __init__(self, options):

        self.options = copy.copy(options)
        
        self._bitrate            = options.bitrate         # desired bit rate
        self._interp             = options.interp          # interpolating rate for the USRP (prelim)
        self._samples_per_symbol = options.samples_per_symbol  # desired samples/baud
        self._tick_period        = 1000000.0 / ( float(self._bitrate) * float(self._samples_per_symbol) ) # Unit us

        self._usrp_delay = { 1000000 : 14.158 }

    def tick_period(self):
        return self._tick_period

    def tick2time(self, tick):
        
        return float(tick) * self._tick_period

    def usrp_roundtrip_delay(self):
        
        try:
            return self._usrp_delay[( float(self._bitrate) * float(self._samples_per_symbol) )] 
        except:
            print 'Exception Error: USRP Hardware Delay Data is missing on sampling rate=%f'%( float(self._bitrate) * float(self._samples_per_symbol) )
            return 0.0
    
