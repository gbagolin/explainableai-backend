#from pm4py.objects.log.importer.xes import importer as xes_importer
import xml.etree.ElementTree as ET

import random
from .utilities.util import *
from .Problem import *

#######
# XES #
#######


class Velocity_Regulation_Problem(Problem):

    def __init__(self, xes_log=None, states=[0, 1, 2], actions=[0, 1, 2], beliefs=None, num_traces_to_analyze=None):
        super().__init__(xes_log, states, actions)
        self.segments_in_runs = []
        self.sub_segments_in_runs = []
        self.parse_xes(
            xes=xes_log, num_traces_to_analyze=num_traces_to_analyze)

    def get_current_segment(self, event):
        '''
        Return current segment in the parsing function. 
        '''
        return int(node_from_key(event, 'segment').attrib['value'])

    def get_next_segment(self, event):
        '''
        Return next segment in the parsing function 
        '''
        segment = int(node_from_key(event, 'segment').attrib['value'])
        if(segment == 8):
            return segment
        else:
            return segment + 1

    def get_current_difficulty(self, state, segment):
        '''
        Return the difficulty of the current segment
        '''
        return (int(state) // (3 ** (7 - segment))) % 3

    def get_current_action(self, event):
        '''
        Return the current action used  
        '''
        return int(node_from_key(event, 'action').attrib['value'])

    def avoid_one_segment(self, event, segment_to_avoid):
        '''
        Return False if the the segment in the run needs to be avoided. 
        Return the segment otherwise. 
        '''
        segment = self.get_current_segment(event)
        if segment == segment_to_avoid:
            return False

        return segment

    def consider_only_one_segment(self, event, segment_to_consider):
        '''
        Return False if the current segment is not the one that needs to be considered. 
        Return the current segment otherwise. 
        '''
        segment = self.get_current_segment(event)
        if segment == segment_to_consider:
            return segment

        return False

    def get_current_sub_seg(self, event):
        return int(node_from_key(event, 'subsegment').attrib['value'])

    def parse_run(self, event):
        # attributes
        segment = self.get_current_segment(event)
        sub_segment = self.get_current_sub_seg(event)

        segment_and_subsegment_to_add = str(segment) + str(sub_segment)

        if segment == False:
            # in case the function above returns False, we don't need to parse this run
            return

        self.segments_in_runs[-1].append(segment)
        self.sub_segments_in_runs[-1].append(segment_and_subsegment_to_add)
        action = self.get_current_action(event)
        self.actions_in_runs[-1].append(action)

        # belief
        belief_dict = {}
        for state in range(len(self.states)):
            belief_dict[state] = 0

        self.belief_in_runs[-1].append(belief_dict)

        for i in node_from_key(event, 'belief'):
            state = i.attrib['key']
            particles = int(i.attrib['value'])
            local_difficulty = self.get_current_difficulty(state, segment)
            self.belief_in_runs[-1][-1][local_difficulty] += particles

        total = 0
        for state in range(len(self.states)):
            total += self.belief_in_runs[-1][-1][state]

        for state in range(len(self.states)):
            self.belief_in_runs[-1][-1][state] /= total

        # REFERENCE HERE THE SUBSEGMENT.

    def parse_xes(self, xes, num_traces_to_analyze):
        """
        Parse xes log and build data from traces
        """
        log = self.xes_tree.getroot()
        count = 0
        for trace in log.findall('xes:trace', XES_NES):
            if num_traces_to_analyze != None and count > num_traces_to_analyze:
                return
            count += 1
            # FIXME: this is probably redundant in xes
            self.run_folders.append('run {}'.format(
                int(node_from_key(trace, 'run').attrib['value'])))
            # each xes trace is a POMCP's run
            self.segments_in_runs.append([])
            self.sub_segments_in_runs.append([])
            self.actions_in_runs.append([])
            self.belief_in_runs.append([])
            
            print(len(trace.findall('xes:event', XES_NES)))

            for event in trace.findall('xes:event', XES_NES):
                self.parse_run(event)
