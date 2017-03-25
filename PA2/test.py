#!/usr/bin/python

from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.link import TCLink
from CustomTopo import *

setLogLevel('info')

linkopts1 = {'bw':50, 'delay':'5ms'}
linkopts2 = {'bw':30, 'delay':'10ms'}
linkopts3 = {'bw':10, 'delay':'15ms'}

topo = CustomTopo(linkopts1, linkopts2, linkopts3, fanout=3)
net = Mininet(topo=topo, link=TCLink)
net.start()

#put in your tests here
net.pingAll()
dumpNodeConnections(net.hosts)

#stop
net.stop()