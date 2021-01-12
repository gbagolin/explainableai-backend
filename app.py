from flask import Flask
from flask import request, jsonify
from flask_cors import CORS

from src.xpomcp.RuleTemplate import RuleTemplate
from src.xpomcp.AtomicRule import AtomicRule
from src.xpomcp.Velocity_Regulation_Problem import Velocity_Regulation_Problem
from src.xpomcp.Tiger_Problem import Tiger_Problem
from src.xpomcp.State import State

from src.xpomcp.main import * 

import sys
import z3
import pdb

app = Flask(__name__)
CORS(app)

@app.route('/api',methods = ['POST'])
def synthetize_rule():
    # test()
    data = request.get_json()
    problem = data['atomic_rule']['problem']
    action_to_analyze = data['atomic_rule']['action']
    constraints = data['atomic_rule']['constraints']
    map_object_to_variable = dict()
    
    for constraint in constraints:
        '''constraints in "and" here'''
        if(type(constraint) == list):
            constraint_and = []
            for single_constraint in constraint: 
                el = eval("single_constraint['variable'] + single_constraint['operator'] + single_constraint['state']")
                constraint_and.append(el)
            #add rule here
        #constrain
        else:
            '''constraints in "or" here'''
            el = eval("constraint['variable'] + constraint['operator'] + constraint['state']")
            print(el)
            #add the element to z3
            
    # variables_to_declare = ['x' + str(var) for var in data['atomic_rule']['variables']]
    # print(problem, action_to_analyze, variables_to_declare)  
    return "ok"

@app.route("/", methods = ['POST'])
def helloWorld():
  return "Hello, cross-origin-world!"

if __name__ == '__main__':
    app.run(debug=True)