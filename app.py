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
tiger_left = State("tiger left")
tiger_right = State("tiger right")
'''States for Velocity regulation problem '''
easy = State(0)
intermediate = State(1)
difficult = State(2)

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
                                num_traces_to_analyze=100, states=[tiger_left, tiger_right])
        map_belief_to_rule_sintax = {
            "tiger_left": tiger_left.get_probability(),
            "tiger_right": tiger_right.get_probability()
        }
    else:
        ''' Initialization of Velocity regulation problem '''
        problem = Velocity_Regulation_Problem(xes_log='./src/xpomcp/tracce/tiger_correct.xes', states=[
                                              intermediate, difficult, easy], num_traces_to_analyze=100)
        map_belief_to_rule_sintax = {
            "easy": easy.get_probability(),
            "intermediate": intermediate.get_probability(),
            "difficult": difficult.get_probability()
        }

    rule = AtomicRule(actions=[data['atomic_rule']['action']], problem=problem)

    for variable in data['atomic_rule']['variables']:
        map_variable_string_to_object[variable] = rule.declareVariable(
            variable)

    for constraint in data['atomic_rule']['constraints']:
        if(type(constraint) == list):
            '''constraints in "and" here'''
            constraint_and = []
            for single_constraint in constraint:
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
                constraint_and.append(el)
            print(constraint_and)
            rule.addConstraint(constraint_and)
        else:
            '''constraints in "or" here'''
            el = eval(
                constraint['variable'] +
                constraint['operator'] +
                str(map_belief_to_rule_sintax[constraint['state']]),
                {}, dict(**map_variable_string_to_object,
                         **map_belief_to_rule_sintax,
                         **{"single_constraint": single_constraint,
                            "map_belief_to_rule_sintax": map_belief_to_rule_sintax}))
            print(el)
            rule.addConstraint(el)
    rule.solve()
    return "ok"


@app.route("/", methods=['POST'])
def helloWorld():
    return "Hello, cross-origin-world!"

if __name__ == '__main__':
    app.run(debug=True)
