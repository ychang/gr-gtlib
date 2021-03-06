# Copyright 2011 Free Software Foundation, Inc.
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
# Setup library
########################################################################
include(GrPlatform) #define LIB_SUFFIX
add_library(gnuradio-gtlib SHARED gtlib_bfsk_modulator_fc.cc gtlib_ncbfsk_freq_diversity.cc gtlib_framer_sink_2.cc gtlib_receiver_monitor.cc gtlib_channel_mux.cc gtlib_ofdm_mapper_bcv.cc gtlib_ofdm_insert_preamble.cc gtlib_ofdm_cyclic_prefixer.cc gtlib_ofdm_sampler.cc gtlib_ofdm_frame_acquisition.cc gtlib_ofdm_frame_sink.cc gtlib_ofdm_stbc_encoder.cc gtlib_ofdm_stbc_decoder.cc gtlib_ofdm_stbc_frame_acquisition.cc )
target_link_libraries(gnuradio-gtlib ${Boost_LIBRARIES} ${GRUEL_LIBRARIES} ${GNURADIO_CORE_LIBRARIES})
set_target_properties(gnuradio-gtlib PROPERTIES DEFINE_SYMBOL "gnuradio_gtlib_EXPORTS")

########################################################################
# Install built library files
########################################################################
install(TARGETS gnuradio-gtlib
    LIBRARY DESTINATION lib${LIB_SUFFIX} # .so/.dylib file
    ARCHIVE DESTINATION lib${LIB_SUFFIX} # .lib file
    RUNTIME DESTINATION bin              # .dll file
)

########################################################################
# Build and register unit test
########################################################################
find_package(Boost COMPONENTS unit_test_framework)

include(GrTest)
set(GR_TEST_TARGET_DEPS gnuradio-gtlib)
#turn each test cpp file into an executable with an int main() function
add_definitions(-DBOOST_TEST_DYN_LINK -DBOOST_TEST_MAIN)

