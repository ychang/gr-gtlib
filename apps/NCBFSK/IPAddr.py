#!/usr/bin/env python
## @package cnIPAddr
#
# This is a IP address supporting module.
# @author Yong Jun Chang
#

import struct
import socket
import fcntl

def getIpAddress(ifname):
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      return socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,struct.pack('256s', ifname[:15]))[20:24])

def IPAddr(ip):
    return struct.unpack('!L',socket.inet_aton(ip))[0]

def IPAddrToStr(data):
    return socket.inet_ntoa(struct.pack('!L',data))

def MACAddr(mac):
    return int(mac,16)
    
def MACAddrToStr(data):
    MAC_str = str(hex(data))
    return MAC_str[2:-1]
    

