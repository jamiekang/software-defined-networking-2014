
'''
Coursera:
- Software Defined Networking (SDN) course
-- Module 8 Programming Assignment

Professor: Nick Feamster
Teaching Assistant: Arpit Gupta
'''

##################################################################
# Author: Hyojoon Kim
# * Run
#   - pyretic.py pyretic.examples.pyretic_gardenwall
#
# * Mininet
#   - sudo mn --controller=remote,ip=127.0.0.1 --mac --arp --switch ovsk --link=tc --topo=single,5
#
# * Events
#   - python json_sender.py -n infected -l True --flow="{srcmac=00:00:00:00:00:01}" -a 127.0.0.1 -p 5000}
#   - python json_sender.py -n exempt -l True --flow="{srcmac=00:00:00:00:00:01}" -a 127.0.0.1 -p 5000}
#   - python json_sender.py -n exempt -l False --flow="{srcmac=00:00:00:00:00:01}" -a 127.0.0.1 -p 5000}
#   - python json_sender.py -n infected -l False --flow="{srcmac=00:00:00:00:00:01}" -a 127.0.0.1 -p 5000}
##################################################################


from pyretic.lib.corelib import *
from pyretic.lib.std import *

# insert the name of the module and policy you want to import
from pyretic.modules.mac_learner import mac_learner
from csv import DictReader
from collections import namedtuple
from pyretic.kinetic.drivers.json_event import JSONEvent
from gardenlib import redirectToGardenWall
import os

policy_file = "%s/pyretic/pyretic/examples/firewall-policies.csv" % os.environ[ 'HOME' ] 
Policy = namedtuple('Policy', ('mac_0', 'mac_1'))

class pyretic_gardenwall(DynamicPolicy):

    def __init__(self):
        super(pyretic_gardenwall,self).__init__()

         # JSON event listener
        json_event = JSONEvent()
        json_event.register_callback(self.event_handler)

        # flow--state map
        self.flow_state_map = {}
        self.policy = passthrough

    def event_handler(self, event):
        print 'Event arrived.'
        print '   Flow: ', event.flow
        print '   Event name: ', event.name
        print '   Value: ', event.value

        # Save to flow-state map
        self.save_flowstate_map(event.flow, event.name, event.value.title())
        print self.flow_state_map

        self.update_policy(event.flow)

    def update_policy(self, flow):
        policies = [] 

        for f in self.flow_state_map:
            srcmac_field = f.get('srcmac')
            if srcmac_field is not None:
                this_policy = None
                infected_state = self.get_flowstate_map(f, 'infected')
                exempt_state = self.get_flowstate_map(f, 'exempt')
                
                ### --- Add your logic here ---- ###
		if infected_state is None:
			infected_state = False
		if exempt_state is None:
			exempt_state = False
		print "** infected state", str(infected_state)
		print "exempt state", str(exempt_state)
		if infected_state=='True' and exempt_state=='True':
			print "- infected:True & exempt:True"
			print "-- srcmac_field", srcmac_field
			this_policy = if_(match(srcmac=EthAddr(srcmac_field)), modify(dstmac=EthAddr('00:00:00:00:00:03')) >> modify(dstip=IP('10.0.0.3')))
		elif infected_state=='True':
			print "- infected:True & exempt:False"
			print "-- srcmac_field", srcmac_field
		        this_policy = (match(srcmac=EthAddr(srcmac_field)))
			this_policy = ~this_policy
		else:
			print "- infected:False & exempt:False"
			print "-- srcmac_field", srcmac_field
		        #this_policy = (match(srcmac=EthAddr(srcmac_field)))
			this_policy = passthrough
                
                # Forward to gardenwall if both True.
                # Else if infected is True, drop.
                # Add
                policies.append(this_policy)

        if len(policies)==0:
            policies.append(passthrough)

        self.policy = union(policies)

        print self.policy


    # Copy the code you used to read firewall-policies.csv last week - ignore!!
    def read_policies (self,file):
        with open(file, 'r') as f:
            reader = DictReader(f, delimiter = ",")
            policies = {}
            for row in reader:
                policies[row['id']] = Policy(row['mac_0'], row['mac_1'])
        return policies

    def save_flowstate_map(self, flow, state, value):
        if flow is not None:
            if self.flow_state_map.has_key(flow):
                state_map = self.flow_state_map[flow]
                state_map[state] = value
            else:
                state_map = {}
                state_map[state] = value
                self.flow_state_map[flow] = state_map
        
    def get_flowstate_map(self, flow, state):
        value = None
        if flow is not None and self.flow_state_map.has_key(flow):
            state_map = self.flow_state_map[flow]
            value = state_map.get(state)
        return value

def main():
    return pyretic_gardenwall() >> mac_learner()
