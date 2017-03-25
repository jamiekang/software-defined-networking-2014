#!/usr/bin/python
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.node import Controller
from mininet.topo import SingleSwitchTopo
from mininet.log import setLogLevel
import os

#setLoglevel('info')

class POXBridge( Controller ):                                                                         
  "Custom Controller class to invoke POX"                                     
  def start( self ):                                                                                 
    "Start POX learning switch"                                                                    
    self.pox = '%s/pox/pox.py' % os.environ[ 'HOME' ]  
    self.cmd( self.pox, 'forwarding.l2_learning misc.firewall &' )                                               
  def stop( self ):                                                                                  
    "Stop POX"                                                                                     
    self.cmd( 'kill %' + self.pox )                      
          

net = Mininet( topo=SingleSwitchTopo( 8 ), controller=POXBridge, autoSetMacs=True )                                  
net.start()   
net.pingAll()
dumpNodeConnections(net.hosts)

net.stop()
