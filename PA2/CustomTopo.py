#!/usr/bin/python
'''
Coursera:
- Software Defined Networking (SDN) course
-- Programming Assignment 2

Professor: Nick Feamster
Teaching Assistant: Arpit Gupta, Muhammad Shahbaz
Student: Jiyang Kang (jiyang71@yahoo.co.kr)
'''

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import irange,dumpNodeConnections
from mininet.log import setLogLevel

class CustomTopo(Topo):
    "Simple Data Center Topology"

    "linkopts - (1:core, 2:aggregation, 3: edge) parameters"
    "fanout - number of child switch per parent switch"
    def __init__(self, linkopts1, linkopts2, linkopts3, fanout=2, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        
        # Add your logic here ...
        #
        c_sw = self.addSwitch('c1')	# Core
        for i in irange(1, fanout):
        	#host = self.addHost('h')
        	a_sw = self.addSwitch('a%s' % i)	# Aggregation
        	self.addLink(c_sw, a_sw, **linkopts1)
        	for j in irange(1, fanout):
        		j0 = j+fanout*(i-1)	
        		e_sw = self.addSwitch('e%s' % j0)	# Edge
           		self.addLink(a_sw, e_sw, **linkopts2)
           		for k in irange(1, fanout):
           			k0 = k+fanout*(j0-1)
           			host = self.addHost('h%s' % k0)	# Host
           			self.addLink(host, e_sw, **linkopts3)
    		# e.g. fanout=2                    
    		#i : 1       2
    		#j : 1   2   1   2
    		#j0: 1   2   3   4	: fanout*(i-1)
    		#k : 1 2 1 2 1 2 1 2
    		#k0: 1 2 3 4 5 6 7 8	: k+fanout(j0-1)

        topos = { 'custom': ( lambda: CustomTopo() ) }
