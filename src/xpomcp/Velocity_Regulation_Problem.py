#from pm4py.objects.log.importer.xes import importer as xes_importer
import xml.etree.ElementTree as ET

import random
from utilities.util import *
from Problem import Problem

#######
# XES #
#######

class Velocity_Regulation_Problem(Problem):

    def __init__(self, xes_log = None,states = [0,1,2],actions = [0,1,2],beliefs = None):
        super().__init__(xes_log,states,actions)
        self.segments_in_runs = []
        self.parse_xes(xes = xes_log)

    def parse_xes(self, xes):
        """
        Parse xes log and build data from traces
        """
        log = self.xes_tree.getroot()

        for trace in log.findall('xes:trace', XES_NES):
            # FIXME: this is probably redundant in xes
            self.run_folders.append('run {}'.format(
                int(node_from_key(trace, 'run').attrib['value'])))

            # each xes trace is a POMCP's run
            self.segments_in_runs.append([])
            self.actions_in_runs.append([])
            self.belief_in_runs.append([])

            for event in trace.findall('xes:event', XES_NES):
                # attributes
                segment = int(node_from_key(event,'segment').attrib['value'])
                self.segments_in_runs[-1].append(segment)
                action = int(node_from_key(event,'action').attrib['value'])
                self.actions_in_runs[-1].append(action)

                # belief
                belief_dict = {}
                for state in range(len(self.states)):
                    belief_dict[state] = 0
                    
                self.belief_in_runs[-1].append(belief_dict)
                    
                for i in node_from_key(event, 'belief'):
                    state = i.attrib['key']
                    particles = int(i.attrib['value'])
                    # TODO 5 (far future): generalizzare anche questo, che sono i rs.p0()...
                    local_difficulty = (int(state) // (3 ** (7 - segment))) % 3
                    self.belief_in_runs[-1][-1][local_difficulty] += particles
                
                total = 0
                for state in range(len(self.states)): 
                    total += self.belief_in_runs[-1][-1][state]
                    
                for state in range(len(self.states)): 
                    self.belief_in_runs[-1][-1][state] /= total