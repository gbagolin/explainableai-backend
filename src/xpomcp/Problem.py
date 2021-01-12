#from pm4py.objects.log.importer.xes import importer as xes_importer
import xml.etree.ElementTree as ET
import random
from abc import ABC, abstractmethod

from .utilities.util import * 


class Problem:

    def __init__(self,xes_log = None,states = None,actions = None,beliefs = None):
        self.states = states
        
        for i in range(len(states)): 
            states[i].id = i 
            
        self.actions = actions
        self.beliefs = beliefs

        self.actions_in_runs = []
        self.belief_in_runs = []
        self.run_folders = []

        self.xes_log = xes_log
        self.xes_tree = ET.parse(xes_log)

    @abstractmethod
    def parse_xes(self, xes):
        pass     
    
    def generate_points(self): 
        point = [ 0.0 for _ in range(len(self.states))]
        
        for i in range(len(self.states) - 1):
            prev_points = 1.0
            for pos in range(i):
                prev_points -= point[pos]
            point[i] = random.uniform(0.0, prev_points)
                
        prev_points = 1.0
        for i in range(len(self.states)): 
            prev_points -= point[i]
        point[len(self.states) - 1] = prev_points
        
        return point
    
        

