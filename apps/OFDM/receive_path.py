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
import math
import copy
import sys

import gnuradio.gr.gr_threading as _threading
import ofdm_packet_utils
import psk, qam
import gtlib

from ofdm_receiver import ofdm_receiver
from ofdm_known_symbols import known_symbols_4512_3


# /////////////////////////////////////////////////////////////////////////////
#                              receive path
# /////////////////////////////////////////////////////////////////////////////

class receive_path(gr.hier_block2):
    def __init__(self, rx_callback, options):

	gr.hier_block2.__init__(self, "receive_path",
				gr.io_signature(1, 1, gr.sizeof_gr_complex),
				gr.io_signature(0, 0, 0))


        options = copy.copy(options)    # make a copy so we can destructively modify

        self._verbose     = options.verbose
        self._log         = options.log
        self._rx_callback = rx_callback      # this callback is fired when there's a packet available

        self._rcvd_pktq = gr.msg_queue()          # holds packets from the PHY

        self._modulation = options.modulation
        self._fft_length = options.fft_length
        self._occupied_tones = options.occupied_tones
        self._cp_length = options.cp_length
        self._snr = options.snr


        # Use freq domain to get doubled-up known symbol for correlation in time domain
        zeros_on_left = int(math.ceil((self._fft_length - self._occupied_tones)/2.0))

        preamble_sequence = known_symbols_4512_3[0:self._occupied_tones]
        training_sequence = ( known_symbols_4512_3[self._occupied_tones:self._occupied_tones*2], \
                            known_symbols_4512_3[self._occupied_tones*2:self._occupied_tones*3] )

        for i in range(len(preamble_sequence)):
            if((zeros_on_left + i) & 1):
                preamble_sequence[i] = 0

        # hard-coded known symbols
        preambles = (preamble_sequence,)

        symbol_length = self._fft_length + self._cp_length
        self.ofdm_recv = ofdm_receiver(self._fft_length,
                                       self._cp_length,
                                       self._occupied_tones,
                                       self._snr, 
                                       preambles,
                                       training_sequence,
                                       options.log)

        mods = {"bpsk": 2, "qpsk": 4, "8psk": 8, "qam8": 8, "qam16": 16, "qam64": 64, "qam256": 256}
        arity = mods[self._modulation]
        
        rot = 1
        if self._modulation == "qpsk":
            rot = (0.707+0.707j)

        # FIXME: pass the constellation objects instead of just the points
        if(self._modulation.find("psk") >= 0):
            constel = psk.psk_constellation(arity)
            rotated_const = map(lambda pt: pt * rot, constel.points())
        elif(self._modulation.find("qam") >= 0):
            constel = qam.qam_constellation(arity)
            rotated_const = map(lambda pt: pt * rot, constel.points())
        #print rotated_const

        phgain = 0.25
        frgain = phgain*phgain / 4.0
        self.ofdm_demod = gtlib.ofdm_frame_sink(rotated_const, range(arity),
                                                       self._rcvd_pktq,
                                                       self._occupied_tones,
                                                       phgain, frgain)


        """
        # receiver
        self.ofdm_rx = ofdm.ofdm_demod(options,
                                          callback=self._rx_callback)
        """

        # Carrier Sensing Blocks
        alpha = 0.001
        thresh = 30   # in dB, will have to adjust
        self.probe = gr.probe_avg_mag_sqrd_c(thresh,alpha)


        self.connect(self, self.ofdm_recv)
        self.connect((self.ofdm_recv, 0), (self.ofdm_demod, 0))
        self.connect((self.ofdm_recv, 1), (self.ofdm_demod, 1))

        # added output signature to work around bug, though it might not be a bad
        # thing to export, anyway
        self.connect(self.ofdm_recv.chan_filt, self.probe)

        if options.log:
            self.connect(self.ofdm_demod,
                         gr.file_sink(gr.sizeof_gr_complex*self._occupied_tones,
                                      "ofdm_frame_sink_c.dat"))
        else:
            self.connect(self.ofdm_demod,
                         gr.null_sink(gr.sizeof_gr_complex*self._occupied_tones))


        # Display some information about the setup
        if self._verbose:
            self._print_verbage()

        self._watcher = _queue_watcher_thread(self._rcvd_pktq, self._rx_callback)
        
    def carrier_sensed(self):
        """
        Return True if we think carrier is present.
        """
        #return self.probe.level() > X
        return self.probe.unmuted()

    def carrier_threshold(self):
        """
        Return current setting in dB.
        """
        return self.probe.threshold()

    def set_carrier_threshold(self, threshold_in_db):
        """
        Set carrier threshold.

        @param threshold_in_db: set detection threshold
        @type threshold_in_db:  float (dB)
        """
        self.probe.set_threshold(threshold_in_db)
    
        
    def add_options(normal, expert):
        """
        Adds receiver-specific options to the Options Parser
        """
        normal.add_option("-W", "--bandwidth", type="eng_float",
                          default=500e3,
                          help="set symbol bandwidth [default=%default]")
        normal.add_option("-v", "--verbose", action="store_true", default=False)
        expert.add_option("", "--log", action="store_true", default=False,
                          help="Log all parts of flow graph to files (CAUTION: lots of data)")

        """
        Adds OFDM-specific options to the Options Parser
        """
        normal.add_option("-m", "--modulation", type="string", default="bpsk",
                          help="set modulation type (bpsk or qpsk) [default=%default]")
        expert.add_option("", "--fft-length", type="intx", default=512,
                          help="set the number of FFT bins [default=%default]")
        expert.add_option("", "--occupied-tones", type="intx", default=200,
                          help="set the number of occupied FFT bins [default=%default]")
        expert.add_option("", "--cp-length", type="intx", default=128,
                          help="set the number of bits in the cyclic prefix [default=%default]")
        expert.add_option("", "--snr", type="float", default=30.0,
                          help="SNR estimate [default=%default]")


    # Make a static method to call before instantiation
    add_options = staticmethod(add_options)


    def _print_verbage(self):
        """
        Prints information about the receive path
        """
        """
        Prints information about the OFDM demodulator
        """
        print "\nOFDM Demodulator:"
        print "Modulation Type: %s"    % (self._modulation)
        print "FFT length:      %3d"   % (self._fft_length)
        print "Occupied Tones:  %3d"   % (self._occupied_tones)
        print "CP length:       %3d"   % (self._cp_length)

        pass
        
        
class _queue_watcher_thread(_threading.Thread):
    def __init__(self, rcvd_pktq, callback):
        _threading.Thread.__init__(self)
        self.setDaemon(1)
        self.rcvd_pktq = rcvd_pktq
        self.callback = callback
        self.keep_running = True
        self.start()


    def run(self):
        while self.keep_running:
            msg = self.rcvd_pktq.delete_head()
            ok, payload = ofdm_packet_utils.unmake_packet(msg.to_string())
            if self.callback:
                self.callback(ok, payload)        
