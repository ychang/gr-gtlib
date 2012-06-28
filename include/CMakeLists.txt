# Copyright 2011 Free Software Foundation, Inc.
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

########################################################################
# Install public header files
########################################################################
install(FILES
    gtlib_api.h
    gtlib_bfsk_modulator_fc.h
    gtlib_ncbfsk_freq_diversity.h
    gtlib_framer_sink_2.h
    gtlib_receiver_monitor.h
    gtlib_channel_mux.h
    gtlib_ofdm_mapper_bcv.h
    gtlib_ofdm_insert_preamble.h
    gtlib_ofdm_cyclic_prefixer.h
    gtlib_ofdm_sampler.h
    gtlib_ofdm_frame_acquisition.h
    gtlib_ofdm_frame_sink.h
    gtlib_ofdm_stbc_encoder.h
    gtlib_ofdm_stbc_decoder.h DESTINATION include/gtlib
)
