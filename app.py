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

'''States for Tiger problem '''
TIGER_LEFT = State("tiger left")
TIGER_RIGHT = State("tiger right")
'''States for Velocity regulation problem '''
EASY = State(0)
INTERMEDIATE = State(1)
DIFFICULT = State(2)

app = Flask(__name__)
CORS(app)


@app.route('/api', methods=['POST'])
def synthetize_rule():
    # test()
    data = request.get_json()
    map_variable_string_to_object = dict()
    map_belief_to_rule_sintax = dict()

    problem = None
    rule = None

    if data['atomic_rule']['problem'] == "Tiger":
        ''' Initialization of Tiger problem '''
        problem = Tiger_Problem(xes_log='./src/xpomcp/tracce/tiger_correct.xes',
                                num_traces_to_analyze=100, states=[TIGER_LEFT, TIGER_RIGHT])
        map_belief_to_rule_sintax = {
            "tiger left": TIGER_LEFT.get_probability(),
            "tiger right": TIGER_RIGHT.get_probability()
        }
    else:
        ''' Initialization of Velocity regulation problem '''
        problem = Velocity_Regulation_Problem(xes_log='./src/xpomcp/tracce/obstacle_avoidance_10.xes', states=[
            INTERMEDIATE, DIFFICULT, EASY], num_traces_to_analyze=100)
        map_belief_to_rule_sintax = {
            "easy": EASY.get_probability(),
            "intermediate": INTERMEDIATE.get_probability(),
            "difficult": DIFFICULT.get_probability()
        }

    rule = AtomicRule(actions=[data['atomic_rule']['action']], problem=problem)

    for variable in data['atomic_rule']['variables']:
        variable_name = 'x' + variable
        map_variable_string_to_object[variable_name] = rule.declareVariable(
            variable_name)

    for constraints in data['atomic_rule']['constraints']:
        '''constraints in "and" here'''
        constraint = []
        for single_constraint in constraints:
            ''' 
            for each constraint in "AND",
            the constraint gets created following the template: 
            "variable" "operator" "belief"
            '''
            el = eval(
                single_constraint['variable'] +
                single_constraint['operator'] +
                str(map_belief_to_rule_sintax[single_constraint['state']]),
                {}, dict(**map_variable_string_to_object,
                         **map_belief_to_rule_sintax,
                         **{"single_constraint": single_constraint,
                            "map_belief_to_rule_sintax": map_belief_to_rule_sintax}))
            constraint.append(el)
        rule.addConstraint(constraint)
    rule.solve()
    return "ok"


@app.route("/", methods=['POST', 'GET'])
def helloWorld():
    return "Hello, cross-origin-world!"


if __name__ == '__main__':
    app.run(debug=True)
