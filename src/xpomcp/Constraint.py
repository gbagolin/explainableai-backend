import z3

class Constraint: 
    def __init__(self,formula):
        
        self.belief = None
        self.operator = formula.decl().name()
        self.formula = formula
        
        for variable in formula.children():
            if z3.is_const(variable) and variable.decl().kind() == z3.Z3_OP_UNINTERPRETED:
                self.variable = variable
            else: 
                self.state = variable.as_long()
                
    def __str__(self):
        if self.belief != None: 
            return "{} {} {}".format(self.belief,self.operator,self.variable)
        else: 
            return "{} {} {}".format(self.state,self.operator,self.variable)

    def get_constraint(self):
        return "{} {} {}".format(self.state, self.operator, self.variable)
        
    
    
    
    
                


            