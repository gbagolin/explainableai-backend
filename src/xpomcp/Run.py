class Run: 
    
    def __init__(self,run,step,action,beliefs,is_anomaly,hellinger_distance=None):
        self.run = run 
        self.step = step
        self.action = action
        self.beliefs = beliefs # list((state,belief))
        self.hellinger_distance = hellinger_distance
        self.is_anomaly = is_anomaly
    
    def __str__(self): 
        to_return = ""
        
        if self.is_anomaly: 
            to_return += "ANOMALY "
            
        to_return += "{} step {}: action {} with belief ".format(self.run,self.step,self.action)
        
        for bel in self.beliefs: 
            state, belief = bel
            to_return += 'P_{} = {:.3f} '.format(state,belief)
        
        if self.hellinger_distance != None:
            to_return += '--- Hellinger = {}'.format(self.hellinger_distance)
        
        return to_return
    
    def __eq__(self, other):
        return self.__str__() == other.__str__() 

    def __hash__(self):
        return hash(self.__str__())