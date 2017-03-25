'''
Coursera:
- Software Defined Networking (SDN) course
-- Network Virtualization

Professor: Nick Feamster
Teaching Assistant: Arpit Gupta
'''

from pox.core import core
from collections import defaultdict

import pox.openflow.libopenflow_01 as of
import pox.openflow.discovery
import pox.openflow.spanning_tree

from pox.lib.revent import *
from pox.lib.util import dpid_to_str
from pox.lib.util import dpidToStr
from pox.lib.addresses import IPAddr, EthAddr
from collections import namedtuple
import os

log = core.getLogger()


class VideoSlice (EventMixin):

    def __init__(self):
        self.listenTo(core.openflow)
        core.openflow_discovery.addListeners(self)

        # Adjacency map.  [sw1][sw2] -> port from sw1 to sw2
        self.adjacency = defaultdict(lambda:defaultdict(lambda:None))
        
        '''
        The structure of self.portmap is a four-tuple key and a string value.
        The type is:
        (dpid string, src MAC addr, dst MAC addr, port (int)) -> dpid of next switch
        '''

        self.portmap = { 
                        # for Video Traffic
                        # SW1: Video from h1 to h3 => forward to SW3
                        ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:01'),
                         EthAddr('00:00:00:00:00:03'), 80): '00-00-00-00-00-03',
                        # SW1: Video from h1 to h4 => forward to SW3
                        ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:01'),
                         EthAddr('00:00:00:00:00:04'), 80): '00-00-00-00-00-03',
                        # SW1: Video from h2 to h3 => forward to SW3
                        ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:02'),
                         EthAddr('00:00:00:00:00:03'), 80): '00-00-00-00-00-03',
                        # SW1: Video from h2 to h4 => forward to SW3
                        ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:02'),
                         EthAddr('00:00:00:00:00:04'), 80): '00-00-00-00-00-03',

                        # SW3: Video from h1 to h3 => forward to SW4
                        ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:01'),
                         EthAddr('00:00:00:00:00:03'), 80): '00-00-00-00-00-04',                        
                        # SW3: Video from h1 to h4 => forward to SW4
                        ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:01'),
                         EthAddr('00:00:00:00:00:04'), 80): '00-00-00-00-00-04',
                        # SW3: Video from h2 to h3 => forward to SW4
                        ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:02'),
                         EthAddr('00:00:00:00:00:03'), 80): '00-00-00-00-00-04',
                        # SW3: Video from h2 to h4 => forward to SW4
                        ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:02'),
                         EthAddr('00:00:00:00:00:04'), 80): '00-00-00-00-00-04',

                        # SW3: Video from h3 to h1 => forward to SW1
                        ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:03'),
                         EthAddr('00:00:00:00:00:01'), 80): '00-00-00-00-00-01',
                        # SW3: Video from h4 to h1 => forward to SW1
                        ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:04'),
                         EthAddr('00:00:00:00:00:01'), 80): '00-00-00-00-00-01',
                        # SW3: Video from h3 to h2 => forward to SW1
                        ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:03'),
                         EthAddr('00:00:00:00:00:02'), 80): '00-00-00-00-00-01',
                        # SW3: Video from h4 to h2 => forward to SW1
                        ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:04'),
                         EthAddr('00:00:00:00:00:02'), 80): '00-00-00-00-00-01',

                        # SW4: Video from h3 to h1 => forward to SW3
                        ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:03'),
                         EthAddr('00:00:00:00:00:01'), 80): '00-00-00-00-00-03',                        
                        # SW4: Video from h4 to h1 => forward to SW3
                        ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:04'),
                         EthAddr('00:00:00:00:00:01'), 80): '00-00-00-00-00-03',
                        # SW4: Video from h3 to h2 => forward to SW3
                        ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:03'),
                         EthAddr('00:00:00:00:00:02'), 80): '00-00-00-00-00-03',
                        # SW4: Video from h4 to h2 => forward to SW3
                        ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:04'),
                         EthAddr('00:00:00:00:00:02'), 80): '00-00-00-00-00-03',

                        # for Non-Video Traffic: use 81 for wildcard
                        # SW1: Non-Video from h1 to h3 => forward to SW2
                        ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:01'),
                         EthAddr('00:00:00:00:00:03'), 81): '00-00-00-00-00-02',
                        # SW1: Non-Video from h1 to h4 => forward to SW2
                        ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:01'),
                         EthAddr('00:00:00:00:00:04'), 81): '00-00-00-00-00-02',
                        # SW1: Non-Video from h2 to h3 => forward to SW2
                        ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:02'),
                         EthAddr('00:00:00:00:00:03'), 81): '00-00-00-00-00-02',
                        # SW1: Non-Video from h2 to h4 => forward to SW2
                        ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:02'),
                         EthAddr('00:00:00:00:00:04'), 81): '00-00-00-00-00-02',

                        # SW2: Non-Video from h1 to h3 => forward to SW4
                        ('00-00-00-00-00-02', EthAddr('00:00:00:00:00:01'),
                         EthAddr('00:00:00:00:00:03'), 81): '00-00-00-00-00-04',                        
                        # SW2: Non-Video from h1 to h4 => forward to SW4
                        ('00-00-00-00-00-02', EthAddr('00:00:00:00:00:01'),
                         EthAddr('00:00:00:00:00:04'), 81): '00-00-00-00-00-04',
                        # SW2: Non-Video from h2 to h3 => forward to SW4
                        ('00-00-00-00-00-02', EthAddr('00:00:00:00:00:02'),
                         EthAddr('00:00:00:00:00:03'), 81): '00-00-00-00-00-04',
                        # SW2: Non-Video from h2 to h4 => forward to SW4
                        ('00-00-00-00-00-02', EthAddr('00:00:00:00:00:02'),
                         EthAddr('00:00:00:00:00:04'), 81): '00-00-00-00-00-04',

                        # SW2: Non-Video from h3 to h1 => forward to SW1
                        ('00-00-00-00-00-02', EthAddr('00:00:00:00:00:03'),
                         EthAddr('00:00:00:00:00:01'), 81): '00-00-00-00-00-01',
                        # SW2: Non-Video from h4 to h1 => forward to SW1
                        ('00-00-00-00-00-02', EthAddr('00:00:00:00:00:04'),
                         EthAddr('00:00:00:00:00:01'), 81): '00-00-00-00-00-01',
                        # SW2: Non-Video from h3 to h2 => forward to SW1
                        ('00-00-00-00-00-02', EthAddr('00:00:00:00:00:03'),
                         EthAddr('00:00:00:00:00:02'), 81): '00-00-00-00-00-01',
                        # SW2: Non-Video from h4 to h2 => forward to SW1
                        ('00-00-00-00-00-02', EthAddr('00:00:00:00:00:04'),
                         EthAddr('00:00:00:00:00:02'), 81): '00-00-00-00-00-01',

                        # SW4: Non-Video from h3 to h1 => forward to SW2
                        ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:03'),
                         EthAddr('00:00:00:00:00:01'), 81): '00-00-00-00-00-02',                        
                        # SW4: Non-Video from h4 to h1 => forward to SW2
                        ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:04'),
                         EthAddr('00:00:00:00:00:01'), 81): '00-00-00-00-00-02',
                        # SW4: Non-Video from h3 to h2 => forward to SW2
                        ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:03'),
                         EthAddr('00:00:00:00:00:02'), 81): '00-00-00-00-00-02',
                        # SW4: Non-Video from h4 to h2 => forward to SW2
                        ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:04'),
                         EthAddr('00:00:00:00:00:02'), 81): '00-00-00-00-00-02'
                        }
        '''
        The structure of self.hostmap is a two-tuple key and an integer value.
        The type is:
        (dpid string, dst MAC addr) -> port (int)
        '''
        self.hostmap = { 
                        # SW4 to h3 => port 3
                        ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:03')): 3,
                        # SW4 to h4 => port 4
                        ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:04')): 4,
                        # SW1 to h1 => port 3
                        ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:01')): 3,
                        # SW1 to h2 => port 4
                        ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:02')): 4
                        }
    def _handle_LinkEvent (self, event):
        l = event.link
        sw1 = dpid_to_str(l.dpid1)
        sw2 = dpid_to_str(l.dpid2)

        log.debug ("link %s[%d] <-> %s[%d]",
                   sw1, l.port1,
                   sw2, l.port2)

        self.adjacency[sw1][sw2] = l.port1
        self.adjacency[sw2][sw1] = l.port2


    def _handle_PacketIn (self, event):
        """
        Handle packet in messages from the switch to implement above algorithm.
        """
        packet = event.parsed
        tcpp = event.parsed.find('tcp')

        def install_fwdrule(event,packet,outport):
            msg = of.ofp_flow_mod()
            msg.idle_timeout = 10
            msg.hard_timeout = 30
            msg.match = of.ofp_match.from_packet(packet, event.port)
            msg.actions.append(of.ofp_action_output(port = outport))
            msg.data = event.ofp
            msg.in_port = event.port
            event.connection.send(msg)

        def forward (message = None):
            this_dpid = dpid_to_str(event.dpid)

            if packet.dst.is_multicast:
                flood()
                return
            else:
                log.debug("Got unicast packet for %s at %s (input port %d):",
                          packet.dst, dpid_to_str(event.dpid), event.port)

                try:
                    """ Add your logic here"""
                    #if tcpp:
                    #    print "**** event.port: %d" % event.port
                    #    print "**** tcpp.dstport: %d" % tcpp.dstport
                    #    print "**** tcpp.srcport: %d" % tcpp.srcport
                    if tcpp and (tcpp.dstport == 80 or tcpp.srcport == 80):    # Video
                        #print "** Case 1"
                        host_tuple=(this_dpid,EthAddr(packet.dst))
                        if host_tuple in self.hostmap:
                            print "**** Case 18"
                            egress_port = self.hostmap[host_tuple]
                            install_fwdrule(event,packet,egress_port)
                            return
                        flow_tuple=(this_dpid,EthAddr(packet.src),EthAddr(packet.dst),80)
                        if flow_tuple not in self.portmap:
                            print "**** Case 10"
                            install_fwdrule(event,packet,of.OFPP_FLOOD)
                            return
                        else:
                            print "**** Case 11"
                            #msg.match = of.ofp_match.from_packet(packet, event.port)
                            next_dpid = self.portmap[flow_tuple]
                            egress_port = self.adjacency[this_dpid][next_dpid]
                            #msg.actions.append(of.ofp_action_output(egress_port)) 
                            #event.connection.send(msg)
                            install_fwdrule(event,packet,egress_port)
                    elif tcpp:                          # Non-Video
                        #print "** Case 2"
                        host_tuple=(this_dpid,EthAddr(packet.dst))
                        if host_tuple in self.hostmap:
                            print "**** Case 28"
                            egress_port = self.hostmap[host_tuple]
                            install_fwdrule(event,packet,egress_port)
                            return                        
                        flow_tuple=(this_dpid,EthAddr(packet.src),EthAddr(packet.dst),81)
                        if flow_tuple not in self.portmap:
                            print "**** Case 20"
                            install_fwdrule(event,packet,of.OFPP_FLOOD)
                            return
                        else:
                            print "**** Case 21"
                            #msg.match = of.ofp_match.from_packet(packet, event.port)
                            next_dpid = self.portmap[flow_tuple]
                            egress_port = self.adjacency[this_dpid][next_dpid]
                            #msg.actions.append(of.ofp_action_output(egress_port)) 
                            #event.connection.send(msg)
                            install_fwdrule(event,packet,egress_port)
                    else:   # flood
                        #print "** Case 3"
                        install_fwdrule(event,packet,of.OFPP_FLOOD)   

                except AttributeError:
                    log.debug("packet type has no transport ports, flooding")

                    # flood and install the flow table entry for the flood
                    install_fwdrule(event,packet,of.OFPP_FLOOD)

        # flood, but don't install the rule
        def flood (message = None):
            """ Floods the packet """
            msg = of.ofp_packet_out()
            msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
            msg.data = event.ofp
            msg.in_port = event.port
            event.connection.send(msg)

        forward()


    def _handle_ConnectionUp(self, event):
        dpid = dpidToStr(event.dpid)
        log.debug("Switch %s has come up.", dpid)
        

def launch():
    # Run spanning tree so that we can deal with topologies with loops
    pox.openflow.discovery.launch()
    pox.openflow.spanning_tree.launch()

    '''
    Starting the Video Slicing module
    '''
    core.registerNew(VideoSlice)
