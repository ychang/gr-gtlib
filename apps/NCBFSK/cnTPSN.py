#!/usr/bin/env python
## @package cnPHY
#
# This is a physical layer Python module.
# @author Yong Jun Chang
#

from gnuradio import gr, gru, modulation_utils, blks2
from gnuradio import usrp
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
from IPAddr import *
from cnPHY import *
from cnCANDIMAC import *

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


#pkt header variables__________ Haejoon Jung


NULL = 0



## The packet ID for the Sync Pulse Request
SP_REQUEST =  1
## The packet ID for the Sync Pulse
SYNC_PULSE   = 2 
## The packet ID for the Acknoledgement
SYNC_ACK   = 3 




## The nodes getting the time info from this node.  (Virtual MAC for TPSN) 
# @author Haejoon Jung


# TPSN control packets ___________________________________

## Packt 1 - SyncPulseRequest (SPREQ)
# @author Haejoon Jung
class SPREQ(dict):
    ## The constructor.
    def __init__(self): 
        self['Type'] = SP_REQUEST
        self['Direction'] = 0
        self['SrcHopCount'] = 0
        self['Root1'] = 0  #ROOT1 (time info originator) node address
        self['Root2'] = 0 #ROOT2  the other end
        self['Src'] = 0 # time information source (either ROOT or a previous hop node)
        self['Dst'] = 0 # time information dst (one of the childen of Src node)
        self['LenSeq'] = 0 # the total hop-counts following the random seq
        for i in range(20):
            self[i] = 0
        


    ## Making a new SPREQ packet
    #  @return SPREQ   the created SPREQ packet
    def make_SPREQ(self): #make SPREQ packet
        Type = struct.pack('!B', SP_REQUEST)
        Direction = struct.pack('!B', self['Direction'])
        SrcHopCount = struct.pack('!H', self['SrcHopCount'])
        Root1 = struct.pack('!L', self['Root1'])
        Root2 = struct.pack('!L', self['Root2'])
        Src = struct.pack('!L', self['Src'])
        Dst = struct.pack('!L', self['Dst'])
        LenSeq = struct.pack('!L', self['LenSeq'])

        SPREQ = Type + Direction + SrcHopCount +  Root1 + Root2 + Src + Dst + LenSeq
        for i in range(20):
            tmp = struct.pack('!B', self[i])
            SPREQ = SPREQ + tmp

        return SPREQ #return the SPREQ packet


    ## Unpacking the received SPREQ packet
    #  @param payload       the received SPREQ packet
    def unmake_SPREQ(self,payload):
        (self['Type'],) = struct.unpack('!B', payload[0:1])
        (self['Direction'],) = struct.unpack('!B', payload[1:2])
        (self['SrcHopCount'],) = struct.unpack('!H', payload[2:4])
        (self['Root1'],) = struct.unpack('!L', payload[4:8])
        (self['Root2'],) = struct.unpack('!L', payload[8:12])
        (self['Src'],) = struct.unpack('!L', payload[12:16])
        (self['Dst'],) = struct.unpack('!L', payload[16:20])
        (self['LenSeq'],) = struct.unpack('!L', payload[20:24])
        for i in range(20):
            (self[i],) = struct.unpack('!B', payload[24+i:24+i+1])






## Packt 2 - SyncPulse (SYNPL)
# @author Haejoon Jung
class SYNPL(dict):
    ## The constructor.
    def __init__(self): # 9 elements (originally 8)
        self['Type'] = SYNC_PULSE
        self['Direction'] = 0
        self['DstHopCount'] = 0
        self['Root1'] = 0
        self['Root2'] = 0
        self['Src'] = 0 # time information source (either Root1 or a previous hop node)
        self['Dst'] = 0 # time information dst (one of the childen of Src node)
        self['T1'] = 0 # TX time of SyncPulse
        self['T1Frac'] = 0 # fractional parts of real T1
       

    ## Making a new SYNPL packet
    #  @return SYNPL   the created SYNPL packet
    def make_SYNPL(self): #make SYNPL packet
        Type = struct.pack('!B', SYNC_PULSE)
        Direction = struct.pack('!B', self['Direction'])
        DstHopCount = struct.pack('!H', self['DstHopCount'])
        Root1 = struct.pack('!L', self['Root1'])
        Root2 = struct.pack('!L', self['Root2'])
        Src = struct.pack('!L', self['Src'])
        Dst = struct.pack('!L', self['Dst'])
        T1 = struct.pack('!L', self['T1'])
        T1Frac = struct.pack('!L', self['T1Frac']);
        
        SYNPL = Type + Direction + DstHopCount +  Root1 + Root2 + Src + Dst + T1 + T1Frac
        return SYNPL #return the SYNPL packet


    ## Unpacking the received SYNPL packet
    #  @param payload       the received SYNPL packet
    def unmake_SYNPL(self,payload):
        (self['Type'],) = struct.unpack('!B', payload[0:1])
        (self['Direction'],) = struct.unpack('!B', payload[1:2])
        (self['DstHopCount'],) = struct.unpack('!H', payload[2:4])
        (self['Root1'],) = struct.unpack('!L', payload[4:8])
        (self['Root2'],) = struct.unpack('!L', payload[8:12])      
        (self['Src'],) = struct.unpack('!L', payload[12:16])
        (self['Dst'],) = struct.unpack('!L', payload[16:20])
        (self['T1'],) = struct.unpack('!L', payload[20:24])
        (self['T1Frac'],) = struct.unpack('!L', payload[24:28])





## Packt 3 - Sync Acknoledgement (SYNAK)
# @author Haejoon Jung
class SYNAK(dict):
    ## The constructor.
    def __init__(self): # 9 elements (originally 8)
        self['Type'] = SYNC_ACK
        self['Direction'] = 0
        self['SrcHopCount'] = 0
        self['Root1'] = 0  #Root1 (time info originator) node address
        self['Root2'] = 0
        self['Src'] = 0 # time information source (either Root1 or a previous hop node)
        self['Dst'] = 0 # time information dst (one of the childen of Src node)
        self['T1'] = 0 # TX time of SyncPulse
        self['T1Frac'] = 0 # fractional parts of real T1
        self['T2'] = 0 # SOP time of the received SyncPulse from Dst
        self['T2Frac'] = 0 # fractional parts of real T2
        self['T3'] = 0 # TX time of SyncPulseAck
        self['T3Frac'] = 0 # fractional parts of real T3

    ## Making a new SYNAK packet
    #  @return SYNAK   the created SYNAK packet
    def make_SYNAK(self): #make SYNAK packet
        Type = struct.pack('!B', SYNC_ACK)
        Direction = struct.pack('!B', self['Direction'])
        SrcHopCount = struct.pack('!H', self['SrcHopCount'])
        Root1 = struct.pack('!L', self['Root1'])
        Root2 = struct.pack('!L', self['Root2'])
        Src = struct.pack('!L', self['Src'])
        Dst = struct.pack('!L', self['Dst'])
        T1 = struct.pack('!L', self['T1'])
        T1Frac = struct.pack('!L', self['T1Frac']);
        T2 = struct.pack('!L', self['T2'])
        T2Frac = struct.pack('!L', self['T2Frac']);
        T3 = struct.pack('!L', self['T3'])
        T3Frac = struct.pack('!L', self['T3Frac']);

        SYNAK = Type + Direction + SrcHopCount + Root1 + Root2 + Src + Dst + T1 + T1Frac + T2 + T2Frac + T3 + T3Frac
        return SYNAK #return the SYNAK packet


    ## Unpacking the received SYNPL packet
    #  @param payload       the received SYNPL packet
    def unmake_SYNAK(self,payload):
        (self['Type'],) = struct.unpack('!B', payload[0:1])
        (self['Direction'],) = struct.unpack('!B', payload[1:2])
        (self['SrcHopCount'],) = struct.unpack('!H', payload[2:4])
        (self['Root1'],) = struct.unpack('!L', payload[4:8])
        (self['Root2'],) = struct.unpack('!L', payload[8:12])
        (self['Src'],) = struct.unpack('!L', payload[12:16])
        (self['Dst'],) = struct.unpack('!L', payload[16:20])
        (self['T1'],) = struct.unpack('!L', payload[20:24])
        (self['T1Frac'],) = struct.unpack('!L', payload[24:28])
        (self['T2'],) = struct.unpack('!L', payload[28:32])
        (self['T2Frac'],) = struct.unpack('!L', payload[32:36])
        (self['T3'],) = struct.unpack('!L', payload[36:40])
        (self['T3Frac'],) = struct.unpack('!L', payload[40:44])

# TPSN control packets ___________________________________
 
    
def Find_Node_Mode(node_topology): 
# it returns 
# 1, if the node is Root1
# 2, if the node is Root2
# 3, if the node is neither of the two

    print '                 {TPSN}  Indentify the role of this node...........'
    print '                 {TPSN}  Root1 =',node_topology[0][0], ' /  Root2 =', node_topology[len(node_topology)-1][0]


    if (node_topology[0][0] == getNodeInfo()['moteid']  ):
        print '                 {TPSN}  This node is Root1'
        ret = 1
    elif( node_topology[len(node_topology)-1][0] == getNodeInfo()['moteid']  ):
        print '                 {TPSN}  This node is Root2'
        ret = 2
    else :
        print '                 {TPSN}  This node is a general (intermediate) member'
        ret = 3
    return ret


#________________________________________________________________________
def Random_Sequence(direction):
    
    #Node_Topology= [ [01], [02, 03], [04, 05], [06] , [13,12,18,19], [20,11], [12] ] 
    Random_Seq = Node_Topology[0]
    # For co-located topology, it uses two-dimensional list. For example if 
    #Node_Topology= [ [01], [02, 03], [04, 05], [06] ] 
# it means that  "Root1 (0th cluster)" =01, 1st cluster = [02, 03], which are co-located , 2nd cluster = [04, 05], which are co-located, and "Root2 (last cluster)"=06


    tmp_cluster_idx  = 0
    fin_flag = 0
    Root1ID = Node_Topology[0][0]

    final_cluster_idx = len(Node_Topology)
    Root2ID = Node_Topology[final_cluster_idx-1][0]

    while (fin_flag ==0):
        tmp_range = min(tmp_cluster_idx + hop_range+1, final_cluster_idx)
        tmp_set = Node_Topology[tmp_cluster_idx+1:tmp_range]
        next_cluster = random.sample(tmp_set,1)
        next_cluster = next_cluster[0]
        tmp_cluster_idx= Node_Topology.index(next_cluster)
        
        next_node = random.sample(next_cluster,1)
        next_node = next_node[0]
        Random_Seq.append(next_node)
    
        if (next_node == Root2ID):
            fin_flag = 1
        
    if (direction == 2) : # For the Reverse direction
        Random_Seq.reverse()
    
    print '                 {TPSN}  Generating a radom sequence for experiment'
    print '                 {TPSN}  Root1 =', Root1ID, ' /  Root2 =', Root2ID
    print '                 {TPSN}  Random Seq = ', Random_Seq
                   
    return {'seq' : Random_Seq, 'Root1' : Root1ID, 'Root2': Root2ID}
    #________________________________________________________________________

## Temporal Application layer class 
# @author Yong Jun Chang
class cnAPP_TPSN(cnProtocol):

    def __init__(self,options):
        
        cnProtocol.__init__(self)

        self.tx_pkt_no = 0
        self.rx_pkt_no = 0
        
        self.options = options
        self.recent_tx_timetag = 0


        #modified on 11/29/2011 by Haejoon Jung

        self.localmacaddr = MACAddr(getNodeInfo()['mac'])
        self.syncflag1 = 0 # Flag for forward link time synchronization 
        self.syncflag2 = 0 # Flag for reverse link time synchronization
        # it indicates the status of synchoronization 
        # 0 : Not synchoronized 
        # 1 : synchronized to the root (source)
        # 2 : the node sent "synchronization pulse" to the time information source, which has been synchronized to the root (source)  




        self.node_mode = Find_Node_Mode(Node_Topology)
        # 1, if the node is Root1
        # 2, if the node is Root2
        # 3, if the node is neither of the two

       

        self.rootID1 = 0    # MAC address of Root1
        self.rootoffset1 = 0  # The time difference between Root1 to local clock of this node
       
        

        self.rootID2 = 0    # MAC address of Root2
        self.rootoffset2 = 0 # The time difference between Root1 to local clock of this node
       
        

        
        # clock offset to the root  = (root clock) - (my local clock )

        self.sourceID = 0
        self.sourceSeq = 0
        
        
        self.my_hopcount1 = 0
        self.my_hopcount2 = 0            

        self.next_hop1 = 0
        self.next_hop2 = 0

        self.rand_seq = []
        
        self.E2E_error = 1000;
      
        self.spreq = SPREQ()
        self.synpl = SYNPL()
        self.synak = SYNAK()

        #self.Node_Topology = Node_Topology        
        
        print '[cnAPP] TPSN Protocol stack is created...' 

    
    
            
        
    


    
        
    #________________________________________________________________________
    def data_indication(self, payload, packet):
        print '                 {TPSN}  a packet is received'
        
        if (packet.peekPDU(2).d_macaddr != self.localmacaddr):
            if (payload != NULL) :
                (pkt_type,) = struct.unpack('!B', payload[0:1])
                (direct_tmp,) = struct.unpack('!B', payload[1:2])
                print '                 {TPSN}  received msg type =', int(pkt_type),' /  direction=',direct_tmp
            pass
            print '                 {TPSN / MAC}  The dest MAC address is', (packet.peekPDU(2).d_macaddr), 'but my MAC address is ', (self.localmacaddr)
            print '                 {TPSN / MAC} Ignore this packet........'

        elif (payload != NULL) :
            (pkt_type,) = struct.unpack('!B', payload[0:1])
            (direct_tmp,) = struct.unpack('!B', payload[1:2])
            print '                 {TPSN}  received msg type =', int(pkt_type),' /  direction=',direct_tmp

            if (pkt_type == SP_REQUEST ):
                print '                 {TPSN}  received SynReq from', MACAddrToStr(packet.peekPDU(2).s_macaddr)
                #print '----[AODV]: AODV received msg : RREQ from',
                self.RecvSPREQ(payload, packet)

            elif ( pkt_type == SYNC_PULSE ):
                print '                 {TPSN}  received SyncPulse from', MACAddrToStr(packet.peekPDU(2).s_macaddr)
                self.RecvSYNPL(payload, packet)

            elif ( pkt_type == SYNC_ACK ):
                print '                 {TPSN}  received SyncACK from', MACAddrToStr(packet.peekPDU(2).s_macaddr)
                self.RecvSYNAK(payload, packet)
                      
            else :
                print '                 {TPSN}   it is an unknown packet format.'
                pass        
    #________________________________________________________________________



    #________________________________________________________________________
    def RecvSPREQ(self, payload, packet):  # it goes from SRC to DST
        print '                 {TPSN}  Inside RecvSPREQ'
        self.spreq.unmake_SPREQ(payload)

        self.rand_seq = []        
        for idx in range(self.spreq['LenSeq']):
            self.rand_seq.append(self.spreq[idx])

        
        # the DST is now making a SYNPL packt, and sending it back to SRC
        if (self.spreq['Dst'] == self.localmacaddr):

            if ( (self.spreq['Direction'] == 1) and (self.syncflag1 ==1)):
                print '                 {TPSN} Error : This node has been synchronizaed already for Forward direction'

            elif ( (self.spreq['Direction'] == 2) and (self.syncflag2 ==1)):
                print '                 {TPSN} Error : This node has been synchronizaed already for Reverse direction'
            
            else : 
                self.sourceID = self.spreq['Src']
                
                
                if (self.spreq['Direction'] == 1) :                
                    self.syncflag1 = 2
                    self.my_hopcount1 = self.spreq['SrcHopCount'] + 1
                    self.rootID1 = self.spreq['Root1']
                    
                    if (self.spreq[self.my_hopcount1+1] < 10):
                        self.next_hop1 = MACAddr('ffffff0' + str(self.spreq[self.my_hopcount1+1])) 
                    else : 
                        self.next_hop1 = MACAddr('ffffff' + str(self.spreq[self.my_hopcount1+1])) 
                    #NOTE ! : SPREQ[X] means the (X+1) hop node
                    
                elif (self.spreq['Direction'] == 2) :
                    self.syncflag2 = 2                                    
                    self.my_hopcount2 = self.spreq['SrcHopCount'] + 1
                    self.rootID2 = self.spreq['Root2']
                    
                    if (self.spreq[self.my_hopcount2+1] < 10):
                        self.next_hop2 = MACAddr('ffffff0' + str(self.spreq[self.my_hopcount2+1])) 
                    else : 
                        self.next_hop2 = MACAddr('ffffff' + str(self.spreq[self.my_hopcount2+1])) 
                    #NOTE ! : SPREQ[X] means the (X+1) hop node
                    

                self.synpl = SYNPL()
                self.synpl['Direction'] = self.spreq['Direction']
                self.synpl['DstHopCount'] = self.spreq['SrcHopCount'] + 1
                self.synpl['Root1'] = self.rootID1
                self.synpl['Root2'] = self.rootID2
                self.synpl['Src'] = self.spreq['Src']
                self.synpl['Dst'] = self.localmacaddr

                SOP_timetag = (float(packet.metadata.timetag)/256)
                # SOP time ( integer   + fractional parts) [by local clock]

                tx_timetag = int(SOP_timetag) + Tproc
                # TX time (integer of SOP + Tporc) [by local clock]
                
                self.synpl['T1'] = tx_timetag
                self.synpl['T1Frac'] = 0 # actually, this field is redundant

                SYNPL0 = self.synpl.make_SYNPL() 
                packet0 = cnPacket()
                packet0.pushPDU(cnData(SYNPL0))
                packet0.metadata.timetag = tx_timetag
        
                print '[cnAPP] Data requested : SyncPulse @ ', tx_timetag
                print '                 {TPSN} : Send Sync Pulse \n', self.synpl
                self.parent.data_request(packet0, self.parent.header_request(self.localmacaddr, self.sourceID))

                self.tx_pkt_no = self.tx_pkt_no + 1

        else:
                print '                 {TPSN} This SyncPulseRequest pkt is not for me, Dst =', self.spreq['Dst'] 
    #________________________________________________________________________           

       


    #________________________________________________________________________
    def RecvSYNPL(self, payload, packet): # it goes from DST to SRC
        print '                 {TPSN}  Inside RecvSYNPL'
        self.synpl.unmake_SYNPL(payload)

        if (self.synpl['Src'] == self.localmacaddr):
            if ((self.synpl['Direction'] == 1 and self.syncflag1 != 1)):
                print '                 {TPSN} Error : This node is not synchronizaed yet (Forward)'
            
            elif ((self.synpl['Direction'] == 2 and self.syncflag2 != 1)):
                print '                 {TPSN} Error : This node is not synchronizaed yet (Reverse)'
            
            else :
                if ( ((self.next_hop1 != self.synpl['Dst'] ) and (self.synpl['Direction'] == 1)) or ((self.next_hop2 != self.synpl['Dst'] ) and (self.synpl['Direction'] == 2))):
                    print '                 {TPSN} Error :',(self.synpl['Dst']),' is not my nexthop node'
                    print '                 {TPSN} my nexthop1=',(self.next_hop1),' / nexthop2', (self.next_hop2)

                else :
                    self.synak = SYNAK()
                    self.synak['Direction'] =  self.synpl['Direction'] 
                    
                                     
                    self.synak['Root1'] = self.rootID1
                    self.synak['Root2'] = self.rootID2
                    
                    self.synak['Src'] = self.localmacaddr
                    self.synak['Dst'] = self.synpl['Dst']
                    
                    self.synak['T1'] = self.synpl['T1']
                    self.synak['T1Frac'] = self.synpl['T1Frac']
                    
                    #TODO ~ T2
                    SOP_timetag_local = (float(packet.metadata.timetag)/256)
                    TX_timetag_local = int(SOP_timetag_local + Tproc)
                    
                    if (self.synpl['Direction'] == 1) :   
                        print '                 direction1'
                        self.synak['SrcHopCount'] = self.my_hopcount1
             
                        SOP_timetag_global = SOP_timetag_local + self.rootoffset1
                        SOP_timetag_global_int = int(SOP_timetag_global)
                        SOP_timetag_global_frac =  (SOP_timetag_global - SOP_timetag_global_int) * 256
                        TX_timetag_global = TX_timetag_local + self.rootoffset1
                        TX_timetag_global_int = int(TX_timetag_global)
                        TX_timetag_global_frac =  (TX_timetag_global - TX_timetag_global_int) * 256

                    elif (self.synpl['Direction'] == 2) :
                        print '                 direction2'
                        self.synak['SrcHopCount'] = self.my_hopcount2

                        SOP_timetag_global = SOP_timetag_local + self.rootoffset2
                        SOP_timetag_global_int = int(SOP_timetag_global)
                        SOP_timetag_global_frac =  (SOP_timetag_global - SOP_timetag_global_int) * 256
                        TX_timetag_global = TX_timetag_local + self.rootoffset2
                        TX_timetag_global_int = int(TX_timetag_global)
                        TX_timetag_global_frac =  (TX_timetag_global - TX_timetag_global_int) * 256

                     
                    
                    self.synak['T2'] = SOP_timetag_global_int
                    # SOP time (integer parts) [by "root" node clock]

                    self.synak['T2Frac'] = SOP_timetag_global_frac
                    # SOP time (fractional parts ) x 256 [by "root" node clock]

                    self.synak['T3'] = TX_timetag_global_int
                    # SOP time (integer parts) [by "root" node clock]

                    self.synak['T3Frac'] = TX_timetag_global_frac
                    # SOP time (fractional parts ) x 256 [by "root" node clock]
                                                    
                    
                    SYNAK0 = self.synak.make_SYNAK() 
                    packet0 = cnPacket()
                    packet0.pushPDU(cnData(SYNAK0))
                    packet0.metadata.timetag = TX_timetag_local
        
                    print '[cnAPP] Data requested : SyncACK @ ', TX_timetag_local
                    print '                 {TPSN} : Send Sync ACK \n', self.synak
                    self.parent.data_request(packet0, self.parent.header_request(self.localmacaddr, self.synpl['Dst']))

                    self.tx_pkt_no = self.tx_pkt_no + 1
    #________________________________________________________________________            
           

     
                    
    #________________________________________________________________________
    def RecvSYNAK(self, payload, packet): # it goes from DST to SRC
        print '                 {TPSN}  Inside RecvSYNAK'
        self.synak.unmake_SYNAK(payload)

        if (self.synak['Dst'] == self.localmacaddr):
            if ( (self.synak['Direction'] == 1) and (self.syncflag1 !=2)):
                print '                 {TPSN} Error : This node flag is NOT 2 for Forward link'

            elif ( (self.synak['Direction'] == 2) and (self.syncflag2 !=2)):
                print '                 {TPSN} Error : This node flag is NOT 2 for Revers link'

            elif (self.sourceID != self.synak['Src']):
                print '                 {TPSN} Error : This node is NOT my source node in the previous SyncPulseRequest'
            
            else :
                self.rootID1 = self.synak['Root1']
                self.rootID2 = self.synak['Root2']
                
                SOP_timetag_local = (float(packet.metadata.timetag)/256)
                TX_timetag_local = int(SOP_timetag_local + Tproc)
                
                T1=self.synak['T1'] + float(self.synak['T1Frac']/256)
                T2=self.synak['T2'] + float(self.synak['T2Frac']/256)
                T3=self.synak['T3'] + float(self.synak['T3Frac']/256)
                T4=SOP_timetag_local
                
                propagation_delay = ((T2 - T1) + (T4 - T3))/2
                clock_drift = ((T2 - T1) - (T4 - T3))/2
           
                if (self.synpl['Direction'] == 1) :             
                    self.syncflag1 = 1
                    self.rootoffset1 = clock_drift# - propagation_delay 

                    print '================================================='
                    print '{TPSN} Forward Direction Clock is SYNCHRONIZED , Offeset =', self.rootoffset1
                    print 'clock drift =', clock_drift, ' /  propagation delay =',propagation_delay
                    print '================================================='
                    SOP_timetag_global = SOP_timetag_local + self.rootoffset1
                    SOP_timetag_global_int = int(SOP_timetag_global)
                    SOP_timetag_global_frac =  (SOP_timetag_global - SOP_timetag_global_int) * 256             
                    TX_timetag_global = TX_timetag_local + self.rootoffset1
                    TX_timetag_global_int = int(TX_timetag_global)
                    TX_timetag_global_frac =  (TX_timetag_global - TX_timetag_global_int) * 256
                                                                              
     
                elif (self.synpl['Direction'] == 2) :
                    self.syncflag2 = 1
                    self.rootoffset2 = clock_drift #- propagation_delay 
                    print '================================================='
                    print '{TPSN} Reverse Direction Clock is SYNCHRONIZED , Offeset =', self.rootoffset2
                    print 'clock drift =', clock_drift, ' /  propagation delay =',propagation_delay
                    print '================================================='

                    SOP_timetag_global = SOP_timetag_local + self.rootoffset2
                    SOP_timetag_global_int = int(SOP_timetag_global)
                    SOP_timetag_global_frac =  (SOP_timetag_global - SOP_timetag_global_int) * 256

                    TX_timetag_global = TX_timetag_local + self.rootoffset2
                    TX_timetag_global_int = int(TX_timetag_global)
                    TX_timetag_global_frac =  (TX_timetag_global - TX_timetag_global_int) * 256



                # Now, it will forward the achieved global time info if needed
                if (self.node_mode==2 and self.synpl['Direction'] == 1): 
                # When it is Root2
                    self.SendSPREQ2(TX_timetag_local)
                
                elif(self.node_mode==1 and self.synpl['Direction'] == 2):
                    self.E2E_error = self.rootoffset2
                    print '================================================='
                    print '{TPSN}        Final E2E Error :   ', self.E2E_error
                    print '================================================='
                
                elif (self.node_mode==3) :
                    self.SendSPREQ3(TX_timetag_local)

                else :          
                    print '                 {TPSN} Error : It cannot happen in RecvSyncACK'
                    

    #________________________________________________________________________
                    
                    

    # this function is used only at Root1 (original time info source)________________________
    def SendSPREQ1(self):           
        if ((self.node_mode==1) and(self.syncflag1==0)and(self.syncflag2==0)) :
            tmpret = Random_Sequence(1)
            
            
            if (tmpret['Root1'] != getNodeInfo()['moteid']):
                print '                 {TPSN} Error : SendSPREQ1 is called, but this node is NOT Root1'
            
            else :
                self.rand_seq = tmpret['seq']
                self.syncflag1 = 1
                self.rootoffset1 = 0 
                

                self.rootID1 = self.localmacaddr

                if (tmpret['Root2'] < 10):
                    self.rootID2 = MACAddr('ffffff0' + str(tmpret['Root2']))
                else : 
                    self.rootID2 = MACAddr('ffffff' + str(tmpret['Root2']))
                
                
                self.sourceID = self.localmacaddr


                if (self.rand_seq[1] < 10):
                    self.next_hop1 = MACAddr('ffffff0' + str(self.rand_seq[1]))
                else : 
                    self.next_hop1 = MACAddr('ffffff' + str(self.rand_seq[1]))

                
                
                self.spreq= SPREQ()
                self.spreq['Direction'] = 1
                self.spreq['SrcHopCount'] = 0
                self.spreq['Root1'] = self.localmacaddr
                self.spreq['Root2'] = self.rootID2
                self.spreq['Src'] = self.localmacaddr
                self.spreq['Dst'] = self.next_hop1
                self.spreq['LenSeq'] = len(self.rand_seq)

                for i in range(len(self.rand_seq)):
                    self.spreq[i] = self.rand_seq[i]
                    
            
                SPREQ0 = self.spreq.make_SPREQ() 
                
                print 'SyncPulseRequest pkt =' , self.spreq
                
                packet0 = cnPacket()
                current_time = self.parent.parent.timetag_request()
                tx_time = current_time + Tproc
                packet0.pushPDU(cnData(SPREQ0))
                packet0.metadata.timetag = tx_time
                

                print '[cnAPP] Data requested : SyncPulseRequest @ ', tx_time
                print '                 {TPSN} : SendSPREQ1\n ', self.spreq
                self.parent.data_request(packet0, self.parent.header_request(self.localmacaddr,self.next_hop1))

                self.tx_pkt_no = self.tx_pkt_no + 1
              #____________________________________________________________________            


    # this function is used only at Root2 (original time info source)________________________
    def SendSPREQ2(self, tx_time_local):           
        if ((self.node_mode==2) and(self.syncflag1==1)and(self.syncflag2==0)) :
            tmpret = Random_Sequence(2)
            
            
            if (tmpret['Root2'] != getNodeInfo()['moteid']):
                print '                 {TPSN} Error : SendSPREQ2 is called, but this node is NOT Root2'
            
            else :
                self.rand_seq = tmpret['seq']
                self.syncflag2 = 1
                self.rootoffset2 = self.rootoffset1
                
                if (tmpret['Root1'] < 10):
                    self.rootID1 = MACAddr('ffffff0' + str(tmpret['Root1']))
    
                else : 
                    self.rootID1 = MACAddr('ffffff' + str(tmpret['Root1']))



                self.rootID2 = self.localmacaddr
                
                self.sourceID = self.localmacaddr


                if (self.rand_seq[1] < 10):
                    self.next_hop2 = MACAddr('ffffff0' + str(self.rand_seq[1]))
    
                else : 
                    self.next_hop2 = MACAddr('ffffff' + str(self.rand_seq[1]))


                
                self.spreq= SPREQ()
                self.spreq['Direction'] = 2
                self.spreq['SrcHopCount'] = 0
                self.spreq['Root1'] = self.rootID1
                self.spreq['Root2'] = self.localmacaddr
                self.spreq['Src'] = self.localmacaddr
                self.spreq['Dst'] = self.next_hop2
                self.spreq['LenSeq'] = len(self.rand_seq)

                for i in range(len(self.rand_seq)):
                    self.spreq[i] = self.rand_seq[i]
                    
            
                SPREQ0 = self.spreq.make_SPREQ() 
                
                packet0 = cnPacket()
                packet0.pushPDU(cnData(SPREQ0))
                packet0.metadata.timetag = tx_time_local
        
                print '[cnAPP] Data requested : SyncPulseRequest @ ', tx_time_local
                print '                 {TPSN} : SendSPREQ2 \n ', self.spreq
                self.parent.data_request(packet0, self.parent.header_request(self.localmacaddr,self.next_hop2))
                self.tx_pkt_no = self.tx_pkt_no + 1
              #____________________________________________________________________            


    # this function is used only at general member (neither Root1 nor Root2)____
    def SendSPREQ3(self, tx_time_local):           
        if (self.node_mode==3 and (self.syncflag1 == 1 or self.syncflag2 == 1 )) :
            tmpseq = self.rand_seq

            if (self.synak['Direction'] == 1):
                myhopcount = self.my_hopcount1

                if (tmpseq[myhopcount+1] < 10):
                    nexthop = MACAddr('ffffff0' + str(tmpseq[myhopcount+1])) 
    
                else : 
                    nexthop = MACAddr('ffffff' + str(tmpseq[myhopcount+1])) 

                
                print '                 {TPSN} SendSPREQ3  (Forward): nexthop node is ', nexthop
                print '                 {TPSN} SendSPREQ3  self.my_hopcount1 = ', self.my_hopcount1
                print '                 {TPSN} SendSPREQ3  self.rand_seq = ', self.rand_seq

                self.nexthop1 = nexthop

            elif (self.synak['Direction'] == 2): 
                myhopcount = self.my_hopcount2
                if (tmpseq[myhopcount+1] < 10):
                    nexthop = MACAddr('ffffff0' + str(tmpseq[myhopcount+1])) 
    
                else : 
                    nexthop = MACAddr('ffffff' + str(tmpseq[myhopcount+1])) 

                print '                 {TPSN} SendSPREQ3  (Reverse): nexthop node is ', nexthop
                print '                 {TPSN} SendSPREQ3  self.my_hopcount2 = ', self.my_hopcount2
                print '                 {TPSN} SendSPREQ3  self.rand_seq = ', self.rand_seq

                self.nexthop2 = nexthop

            else :
                print '                 {TPSN} Error : It cannot happen in SendSPREQ3'


            self.spreq= SPREQ()
            self.spreq['Direction'] = self.synak['Direction']
            self.spreq['SrcHopCount'] = myhopcount
            self.spreq['Root1'] = self.rootID1
            self.spreq['Root2'] = self.rootID2
            self.spreq['Src'] = self.localmacaddr
            self.spreq['Dst'] =nexthop
            self.spreq['LenSeq'] = len(tmpseq)

            for i in range(len(self.rand_seq)):
                self.spreq[i] = self.rand_seq[i]
                    
            
            SPREQ0 = self.spreq.make_SPREQ() 
            
            packet0 = cnPacket()
            packet0.pushPDU(cnData(SPREQ0))
            packet0.metadata.timetag = tx_time_local
        
            print '[cnAPP] Data requested : SyncPulseRequest @ ', tx_time_local
            print '                 {TPSN} : SendSPREQ3 \n ', self.spreq
            self.parent.data_request(packet0, self.parent.header_request(self.localmacaddr,nexthop))
            self.tx_pkt_no = self.tx_pkt_no + 1
              #____________________________________________________________________                                
       







        
     
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
    # Create Protocol Stacks
    #============================================================================

    #============================================================================
    # Create a Physical layer (Open GNURadio Core)
    #============================================================================
    layer_1 = cnPHY(options)

    #============================================================================
    # Create a MAC/Link layer
    #============================================================================
    localmacaddr = getNodeInfo()['mac']    
    layer_2 = cnCANDIMAC(MACAddr(localmacaddr))

    #============================================================================
    # Create a MAC/Link layer
    #============================================================================
    layer_7 = cnAPP_TPSN(options) ## modified by Haejoon (11/30)

    #============================================================================
    # Bind the MAC/Link and network layer
    #============================================================================
    print "... Bind the PHY, MAC and APP layer"

    cnConnect(layer_1, layer_2, layer_7)

    time.sleep(1)

    print ""

    #============================================================================
    # CANDI Protocol
    #============================================================================

    if layer_7.node_mode == 1: # If it is the Root1     

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


        layer_7.SendSPREQ1() 
        time.sleep(1)

    else:
        while True:
            time.sleep(1)

    layer_1.tb.wait()                       # wait for it to finish
        
    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass

