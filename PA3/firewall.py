'''
Coursera:
- Software Defined Networking (SDN) course
-- Programming Assignment: Layer-2 Firewall Application

Professor: Nick Feamster
Teaching Assistant: Arpit Gupta
'''

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr
from collections import namedtuple
import os
''' Add your imports here ... '''



log = core.getLogger()
policyFile = "%s/pox/pox/misc/firewall-policies.csv" % os.environ[ 'HOME' ]  

''' Add your global variables here ... '''



class Firewall (EventMixin):

    def __init__ (self):
        self.listenTo(core.openflow)
        log.debug("Enabling Firewall Module")

    def _handle_ConnectionUp (self, event):    
        ''' Add your logic here ... '''
	f = open("/home/mininet/pox/pox/misc/firewall-policies.csv", 'r')
	line = f.readline()
	while 1:
		line = f.readline()
		if not line: break
		mac1 = line[2:19]
		mac2 = line[20:37]
		fw_rule = of.ofp_flow_mod()
		fw_rule.match.dl_src = EthAddr(mac1)
		fw_rule.match.dl_dst = EthAddr(mac2)
		fw_rule.priority = 65535
		fw_rule.actions.append(of.ofp_action_output(port = of.OFPP_NONE))
		event.connection.send(fw_rule)
		fw_rule.match.dl_src = EthAddr(mac2)
		fw_rule.match.dl_dst = EthAddr(mac1)
		event.connection.send(fw_rule)
	f.close()

    
        log.debug("Firewall rules installed on %s", dpidToStr(event.dpid))

def launch ():
    '''
    Starting the Firewall module
    '''
    core.registerNew(Firewall)
