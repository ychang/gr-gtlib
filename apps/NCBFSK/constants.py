#!/usr/bin/env python

# Georgia Institute of Technology
# Smart Antenna Research Laboratory 
# 
# DoD Project # H98230-08-C-0336 Cooperative Communication Networks
# 
# Yong Jun Chang Georgia Tech, 2010

#
# IP Address

from IPAddr import *



FLOODING_IP_ADDR    = IPAddr('0.255.255.255')
#OLAFLOODING_IP_ADDR = IPAddr('1.255.255.255')
TMP_IP_ADDR         = IPAddr('192.168.1.102') 
#TMP_IP_ADDR         = IPAddr('192.168.1.116') #cott20
#TMP_IP_ADDR         = IPAddr('143.215.148.54') #cott15
BROADCAST_IP_ADDR   = IPAddr('255.255.255.255')

BROADCAST_MAC_ADDR  = MACAddr('FFFFFFFF')

CNMAC_PKT_TYPE_QUEUED       = 0
CNMAC_PKT_TYPE_IMMEDIATE    = 1

CNMAC_INTER_PKT_DELAY       = (0.14) # 0.14 is default
CNMAC_TPROC                 = 0.025 # 0.03 is default

CNNET_DEF_TIME_TO_LIVE      = 10
CNNET_DEF_PKT_TYPE          = 0    

CNRP_DATA_PACKET            = 0
CNRP_ROUTING_PACKET         = 1

#Routing Type
ROUTING_AODV                = 0
ROUTING_OLAROAD             = 1

#Flooding Type
FLOODING_BLIND              = 0
FLOODING_OLA                = 1

#Return values for lookup
ROUTE_RESOLVE_REQUESTED     = 0
ROUTE_DROP_REQUESTED        = None

#Transmission Type for MetaData
TX_TYPE_SEND_WITH_INTERVAL  = 0 << 0    # Tproc will be ignored!!!
TX_TYPE_SEND_IMMEDIATELY     = 1 << 0

TX_TYPE_TPROC               = 0 << 1
TX_TYPE_CSMA                = 1 << 1

#Added by Haejoon 2011/12/05 Monday Random Seq Generation for TPSN
Tproc = (51200)

# NOTE : if node ID = 0X  -> just write X without 0 instead 0X
# If not using Fixed membership for CANDI, you can just put
# Node_Topology= [[Root1ID], [Root2ID]]

#Node_Topology= [[26], [19], [3], [10],[11],[12],[20],[14],[17]]
#Node_Topology= [[26],[10],[20]]
Node_Topology= [[26],[20]]

# For co-located topology, it uses two-dimensional list. For example if 
#Node_Topology= [ [1], [2, 3], [4, 5], [6] ] 
# it means that  "Root1 (0th cluster)" =1, 1st cluster = [2, 3], which are co-located , 2nd cluster = [4, 5], which are co-located, and "Root2 (last cluster)"=6

#Node_Topology= [ [1], [2, 3], [4, 5], [6], [7, 10, 9], [25] ] 
hop_range = 1 # this is the maximum number of clusters to hop over

Two_Phase_Time_Gap = 6 * Tproc
# The time gap between first phase (the tx time for 1st pahse packet (RT) ) and the second phase (the tx time for 2nd phase packet (TSD))
Tproc = (51200)


