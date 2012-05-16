#!/usr/bin/env python
## @package cnNodeInfo
#
# This is a library module for gathering node information
# @author Yong Jun Chang
#

import sys
import os
import pwd
import string
import subprocess

YEAR = '2011'
MONTH = 'Nov'
DAY = '16'


# Decide local IP address from user IP of Linux system
# CottXX : XX = 01~20
# 192.168.1.101 ~ 192.168.1.120

def getNodeInfo():
    s=pwd.getpwall()
    
    for entry in s:
        if 'cott' in entry.pw_name:
            user_id = entry.pw_name
            local_ip = string.replace(user_id,'cott','192.168.1.1')
            local_mac = string.replace(user_id,'cott','ffffff')
            mote_id = int(string.replace(user_id,'cott',''))
            return {'id':user_id,'ip':local_ip,'mac':local_mac,'moteid':mote_id}

    user_id = 'cott99'
    local_ip = string.replace(user_id,'cott','192.168.1.1')
    local_mac = string.replace(user_id,'cott','ffffff')
    mote_id = int(string.replace(user_id,'cott',''))
    return {'id':user_id,'ip':local_ip,'mac':local_mac,'moteid':mote_id}


def displayTitle(node_info):
    
    """
    Black       0;30     Dark Gray     1;30
    Blue        0;34     Light Blue    1;34
    Green       0;32     Light Green   1;32
    Cyan        0;36     Light Cyan    1;36
    Red         0;31     Light Red     1;31
    Purple      0;35     Light Purple  1;35
    Brown       0;33     Yellow        1;33
    Light Gray  0;37     White         1;37
    """

    print "============================================================================="
    print " OLA Cooperative Communication "
    print "============================================================================="
    print " Smart Antenna Research Lab   %s %s, %s"%(MONTH,DAY,YEAR)
    print " Georgia Institute of Technology"
    print "============================================================================="
    print ""
    print "Node ID  :\033[1;31m",node_info['id'],"\033[0m"
    print "Local IP :\033[1;31m",node_info['ip'],"\033[0m"
    print "Local MAC:\033[1;31m",node_info['mac'],"\033[0m"
    print ""

    filename = sys.argv[0][2:]

    # Kill previous processors
    cmd = 'kill -9 `ps -ef | grep %s | grep -v grep | grep -v %d | awk \'{print $2}\'`'%(filename,os.getpid())
    fout = os.popen4(cmd)


