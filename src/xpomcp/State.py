class State: 
    def __init__(self,state_name): 
        self.state_name = state_name
        self.id = None

    def get_probability(self):
        return self.id