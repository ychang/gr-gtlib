#
# Copyright 2005,2006,2011 Free Software Foundation, Inc.
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

from gnuradio import gr
from gnuradio import eng_notation
from gnuradio import digital

import copy
import sys
import math

import gtlib
import ofdm_packet_utils
import psk

from ofdm_known_symbols import known_symbols_4512_3 
# /////////////////////////////////////////////////////////////////////////////
#                              transmit path
# /////////////////////////////////////////////////////////////////////////////

class transmit_path(gr.hier_block2): 
    def __init__(self, options):
        '''
        See below for what options should hold
        '''

	gr.hier_block2.__init__(self, "transmit_path",
				gr.io_signature(0, 0, 0),
				gr.io_signature(1, 1, gr.sizeof_gr_complex))

        options = copy.copy(options)    # make a copy so we can destructively modify

        self._verbose      = options.verbose      # turn verbose mode on/off
        self._tx_amplitude = options.tx_amplitude # digital amp sent to radio
        self._pad_for_usrp = False
        self._modulation = options.modulation
        self._fft_length = options.fft_length
        self._occupied_tones = options.occupied_tones
        self._cp_length = options.cp_length

        msgq_limit = 4

        win = [] #[1 for i in range(self._fft_length)]

        # Use freq domain to get doubled-up known symbol for correlation in time domain
        zeros_on_left = int(math.ceil((self._fft_length - self._occupied_tones)/2.0))


        # STBC Initialization
        self._block_length = 2
        
        print "Length of predetermined known symbols =",len(known_symbols_4512_3)

        # Preamble Sequence
        preamble_sequence = known_symbols_4512_3[0:self._occupied_tones]
        training_sequence = ( known_symbols_4512_3[self._occupied_tones:self._occupied_tones*2], \
                            known_symbols_4512_3[self._occupied_tones*2:self._occupied_tones*3] )
               
        # Generating consecutive two symbols in time domain
        for i in range(len(preamble_sequence)):
            if((zeros_on_left + i) & 1):
                preamble_sequence[i] = 0

        
        for i in range(len(training_sequence[0])):
                #training_sequence[0][i] = 0
                training_sequence[1][i] = 0

        # hard-coded known symbols
        # preambles = (preamble_sequence,)
        preambles = (preamble_sequence, training_sequence[0], training_sequence[1])
                
        padded_preambles = list()
        for pre in preambles:
            padded = self._fft_length*[0,]
            padded[zeros_on_left : zeros_on_left + self._occupied_tones] = pre
            padded_preambles.append(padded)
            
        symbol_length = options.fft_length + options.cp_length
        
        mods = {"bpsk": 2, "qpsk": 4, "8psk": 8, "qam8": 8, "qam16": 16, "qam64": 64, "qam256": 256}
        self.arity = mods[self._modulation]
        
        rot = 1
        if self._modulation == "qpsk":
            rot = (0.707+0.707j)

        print "Padded Preambles (l=%d,%d):"%(len(padded_preambles),len(padded_preambles[0])), padded_preambles
            
        # FIXME: pass the constellation objects instead of just the points
        if(self._modulation.find("psk") >= 0):
            constel = psk.psk_constellation(self.arity)
            rotated_const = map(lambda pt: pt * rot, constel.points())
        elif(self._modulation.find("qam") >= 0):
            constel = qam.qam_constellation(self.arity)
            rotated_const = map(lambda pt: pt * rot, constel.points())
        #print rotated_const
        self._pkt_input = gtlib.ofdm_mapper_bcv(rotated_const,
                                                       msgq_limit,
                                                       options.occupied_tones,
                                                       options.fft_length)
        
        self.preambles = gtlib.ofdm_insert_preamble(self._fft_length,
                                                           padded_preambles)
        self.ifft = gr.fft_vcc(self._fft_length, False, win, True)
        self.cp_adder = gtlib.ofdm_cyclic_prefixer(self._fft_length,
                                                          symbol_length)
        self.scale = gr.multiply_const_cc(1.0 / math.sqrt(self._fft_length))

        self.amp = gr.multiply_const_cc(1)
        self.set_tx_amplitude(self._tx_amplitude)

        """        
        Transformation Matrix
        
        Alamouti
        
         1  0  0  0
         0  1  0  0
         0  0  0  1
         0  0 -1  0
        
        """ 
        
        code_matrix = [ [1,0,0,0], [0,1,0,0], [0,0,0,-1], [0,0,1,0] ];
        
        self.stbc_encoder = gtlib.ofdm_stbc_encoder(options.fft_length,code_matrix, 1.0)
        
        # Create and setup transmit path flow graph
        
        self.subcarrier_size = self._pkt_input.subcarrier_size() 
        symbols_per_packet = math.ceil(((4+1+options.size+4) * 8) / math.log(self.arity,2) / self.subcarrier_size)
        samples_per_packet = (symbols_per_packet + 3 + 0) * (options.fft_length+options.cp_length)

        stream_size = [int(options.discontinuous*samples_per_packet), 0]

        z = [0.000001,]
        self.zeros = gr.vector_source_c(z, True)
        self.mux = gr.stream_mux(gr.sizeof_gr_complex, stream_size)
        
        
        #self.connect((self._pkt_input, 0), (self.preambles, 0))
        #self.connect((self._pkt_input, 1), (self.preambles, 1))
        
        self.connect((self._pkt_input, 0), (self.stbc_encoder, 0))
        self.connect((self._pkt_input, 1), (self.stbc_encoder, 1))
        
        self.connect( (self.stbc_encoder,0) , (self.preambles, 0))
        self.connect( (self.stbc_encoder,1), gr.null_sink ( 8*self._fft_length) )

        self.connect((self._pkt_input, 1), (self.preambles, 1))
        
        if options.dummy_zero:
            self.connect(self.preambles, self.ifft, self.cp_adder, self.scale, self.amp, (self.mux,0))
            self.connect(self.zeros , (self.mux,1))
            self.connect(self.mux, self)
        else:        
            self.connect(self.preambles, self.ifft, self.cp_adder, self.scale, self.amp, self)
        
        
     
        if options.verbose:
            self._print_verbage()

        if options.log:
            self.connect(self._pkt_input, gr.file_sink(gr.sizeof_gr_complex*options.fft_length,
                                                       "ofdm_mapper_c.dat"))
            self.connect((self.stbc_encoder,0), gr.file_sink(gr.sizeof_gr_complex*options.fft_length,
                                                       "ofdm_stbc_encoder_c.dat"))
            self.connect(self.preambles, gr.file_sink(gr.sizeof_gr_complex*options.fft_length,
                                                      "ofdm_preambles.dat"))
            self.connect(self.ifft, gr.file_sink(gr.sizeof_gr_complex*options.fft_length,
                                                 "ofdm_ifft_c.dat"))
            self.connect(self.cp_adder, gr.file_sink(gr.sizeof_gr_complex,
                                                     "ofdm_cp_adder_c.dat"))





    def set_tx_amplitude(self, ampl):
        """
        Sets the transmit amplitude sent to the USRP
        @param: ampl 0 <= ampl < 1.0.  Try 0.10
        """
        self._tx_amplitude = max(0.0, min(ampl, 1))
        self.amp.set_k(self._tx_amplitude)
        
    def send_pkt(self, payload='', eof=False):
        """
        Send the payload.

        @param payload: data to send
        @type payload: string
        """
        if eof:
            msg = gr.message(1) # tell self._pkt_input we're not sending any more packets
        else:
            # print "original_payload =", string_to_hex_list(payload)
            pkt = ofdm_packet_utils.make_packet(payload, 1, 1,
                                                self._pad_for_usrp,
                                                whitening=True)
            
            #print "pkt =", string_to_hex_list(pkt)
            msg = gr.message_from_string(pkt)
        self._pkt_input.msgq().insert_tail(msg)
                
    def add_options(normal, expert):
        """
        Adds OFDM-specific options to the Options Parser
        """
        normal.add_option("-m", "--modulation", type="string", default="bpsk",
                          help="set modulation type (bpsk, qpsk, 8psk, qam{16,64}) [default=%default]")
        expert.add_option("", "--fft-length", type="intx", default=512,
                          help="set the number of FFT bins [default=%default]")
        expert.add_option("", "--occupied-tones", type="intx", default=200,
                          help="set the number of occupied FFT bins [default=%default]")
        expert.add_option("", "--cp-length", type="intx", default=128,
                          help="set the number of bits in the cyclic prefix [default=%default]")
                          
        """
        Adds transmitter-specific options to the Options Parser
        """
        normal.add_option("", "--tx-amplitude", type="eng_float",
                          default=0.1, metavar="AMPL",
                          help="set transmitter digital amplitude: 0 <= AMPL < 1.0 [default=%default]")
        normal.add_option("-W", "--bandwidth", type="eng_float",
                          default=500e3,
                          help="set symbol bandwidth [default=%default]")
        normal.add_option("-v", "--verbose", action="store_true",
                          default=False)
        
        normal.add_option("", "--dummy-zero", action="store_true",
                          default=False)
        
        expert.add_option("", "--log", action="store_true",
                          default=False,
                          help="Log all parts of flow graph to file (CAUTION: lots of data)")

    # Make a static method to call before instantiation
    add_options = staticmethod(add_options)

    def _print_verbage(self):
        """
        Prints information about the OFDM modulator
        """
        print "\nOFDM Modulator:"
        print "Modulation Type: %s"    % (self._modulation)
        print "FFT length:      %3d"   % (self._fft_length)
        print "Occupied Tones:  %3d"   % (self._occupied_tones)
        print "CP length:       %3d"   % (self._cp_length)
        print "Tx amplitude     %s" % (self._tx_amplitude)

