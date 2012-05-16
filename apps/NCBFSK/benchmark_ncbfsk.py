#!/usr/bin/env python
## @package cnPHY
#
# This is a physical layer Python module.
# @author Yong Jun Chang
#

from gnuradio import gr, gru, blks2
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
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
from cnNodeInfo import *

from cnPHY import *
from cnPseudoMAC import *

from gtlib_usrp import usrp_utils

#import os
#print os.getpid()
#raw_input('Attach and press enter: ')

# /////////////////////////////////////////////////////////////////////////////
#   Temporal Application Layer
#   
#   Layer structure
#   PHY <-> MAC <-> APP
#
# /////////////////////////////////////////////////////////////////////////////

## Temporal Application layer class 
# @author Yong Jun Chang
class cnAPP(cnProtocol):

    def __init__(self,options, usrp):
        
        cnProtocol.__init__(self)

        self.tx_pkt_no = 0
        self.rx_pkt_no = 0
        
        self.options = options
        self.recent_tx_timetag = 0

        self.symbol_duration = 1.0 / ( float(options.bitrate) * float(options.samples_per_symbol) )
        
        print '[cnAPP] Protocol stack is created...' 
        print '[cnAPP] Symbol duration=',self.symbol_duration

        self.group_delay = {8:646.5, 16:1294.5, 32:2590.4765}

        self.tproc = 40000
        self.usrp = usrp

    def data_indication(self, payload, packet):
        
        print '[cnAPP]: P=',utils.ByteToHex(payload)

    def data_request(self, payload, txtime=None):

        packet = cnPacket()
        packet.pushPDU(cnData(payload))

        self.recent_tx_timetag = txtime

        packet.metadata.scsf_value = None        
        packet.metadata.timetag = txtime

        print '[cnAPP] Data requested @ ',txtime, payload

        self.parent.data_request(packet, self.parent.header_request(123456,765431))
        
        self.tx_pkt_no = self.tx_pkt_no + 1
        
       
# /////////////////////////////////////////////////////////////////////////////
#                                   main
# /////////////////////////////////////////////////////////////////////////////

def main():

    parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
    expert_grp = parser.add_option_group("Expert")
    channel_grp = parser.add_option_group("Channel")

    modes = ['default','loopback']
    parser.add_option("-m", "--mode", type="choice", choices=modes,
                      default=modes[0],
                      help="Select operating mode from: %s [default=%%default]"
                            % (', '.join(modes),))

    parser.add_option("","--source", action="store_true", default=False,
                      help="Set the node to source (transmitter) [default=%default]")
    
    parser.add_option("-v", "--verbose", action="store_true", default=False)

    cnPHY.add_options(parser,expert_grp,channel_grp)

    (options, args) = parser.parse_args ()

    if len(args) != 0:
        parser.print_help()
        sys.exit(1)
 
    r = gr.enable_realtime_scheduling()
    if r != gr.RT_OK:
        print "Warning: failed to enable realtime scheduling"

    nodeinfo = getNodeInfo()
    displayTitle ( nodeinfo )


    #============================================================================
    # Create a Physical layer (Open GNURadio Core)
    #============================================================================
    layer_1 = cnPHY(options)

    #============================================================================
    # Create Protocol Stacks
    #============================================================================
    usrp = usrp_utils(options)

    #============================================================================
    # Create a MAC/Link layer
    #============================================================================
    layer_2 = cnMAC('123456')

    #============================================================================
    # Create a MAC/Link layer
    #============================================================================
    layer_7 = cnAPP(options, usrp)

    #============================================================================
    # Bind the MAC/Link and network layer
    #============================================================================
    print "... Bind the PHY, MAC and APP layer"

    cnConnect(layer_1, layer_2, layer_7)


    print "... USRP Tick Period = %d (us)"%usrp.tick_period()

    time.sleep(1)

    print ""

    if options.source == True:    

    #============================================================================
    # First phase
    #============================================================================

        tproc = 0.05
        bitrate = options.bitrate
        sps = options.samples_per_symbol    
        sample_duration = (1e9)/(bitrate*sps)
        gap = long((tproc*float(bitrate*sps)))

        print '[Configuration]'
        print '  Bitrate = ',bitrate
        print '  Samples per symbol = ',sps
        print '  Sample duration = ',sample_duration
        print '  Transmission gap = ', gap

        gap = 30000

        trials = 10000
        
        while trials:
        
            layer_7.data_request('12345678')
        
            time.sleep(0.2)
            
            trials = trials - 1

    else:
        while True:
            time.sleep(1)

    layer_1.tb.wait()                       # wait for it to finish
        
    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass

        
