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
'''
MAP BETWEEN ACTION AND STRING. 
'''

MAP_STATES_TO_FRONTEND = {
    0 : "low",
    1 : "medium",
    2 : "high"
}

MAP_ACTIONS_TO_FRONTEND = {
    0 : "slow",
    1 : "medium",
    2 : "fast",
}

MAP_ACTIONS_TO_BACKEND = {
    "slow" : 0,
    "medium": 1,
    "fast": 2, 
    "open left": "open left",
    "open right": "open right",
    "listen": "listen",
}

MAP_TRACES = {
    "Tiger correct": "tiger_correct.xes",
    "Tiger 40": "dataset_tiger_40.xes",
    "Tiger 60": "dataset_tiger_60.xes",
    "Tiger 80": "dataset_tiger_80.xes",
    "Velocity regulation 10": "obstacle_avoidance_10.xes",
    "Velocity regulation 100": "obstacle_avoidance_100.xes",
}

app = Flask(__name__)
CORS(app)

@app.route('/api/send_rule', methods=['POST'])
def synthetize_rule():
    # test()
    data = request.get_json()
    map_variable_string_to_object = dict()
    map_belief_to_rule_sintax = dict()

    problem = None
    rule = None
    trace = data['atomic_rule']['trace']
    if data['atomic_rule']['problem'] == "Tiger":
        ''' Initialization of Tiger problem '''
        problem = Tiger_Problem(xes_log=f'./src/xpomcp/tracce/{MAP_TRACES[trace]}',
                                num_traces_to_analyze=100,
                                states=[TIGER_LEFT, TIGER_RIGHT])
        map_belief_to_rule_sintax = {
            "tiger left": TIGER_LEFT.get_probability(),
            "tiger right": TIGER_RIGHT.get_probability()
        }
        states = ["tiger left", "tiger right"]
    else:
        ''' Initialization of Velocity regulation problem '''
        problem = Velocity_Regulation_Problem(xes_log=f'./src/xpomcp/tracce/{MAP_TRACES[trace]}',
                                              states=[EASY, INTERMEDIATE, DIFFICULT],
                                            )
        map_belief_to_rule_sintax = {
            "low": EASY.get_probability(),
            "medium": INTERMEDIATE.get_probability(),
            "high": DIFFICULT.get_probability()
        }

        states = ["low", "medium","high"]
    #TODO: create the list of actions out. 
    rule = AtomicRule(actions=[MAP_ACTIONS_TO_BACKEND[data["atomic_rule"]["action"]]], problem=problem)

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
    hard_constraints = []
    

    for hard_constraint in data['atomic_rule']['hard_constraint']:
        el = eval(
            hard_constraint['variable'] +
            hard_constraint['operator'] +
            str(hard_constraint['probability']),
            {}, dict(**map_variable_string_to_object))
        hard_constraints.append(el)

    rule.addHardConstraint(hard_constraints)
    rule.solve()

    constraints_synthetized = rule.result.get_constraint_synthetized(MAP_STATES_TO_FRONTEND)
    actions = rule.result.rule_obj.actions
    actions = list(map(lambda x: MAP_ACTIONS_TO_FRONTEND[x],actions))
    anomalies = list(map(
                        lambda x: x.to_dict(MAP_STATES_TO_FRONTEND), 
                        rule.result.all_rules_unsatisfied
                         ))
    return jsonify({
        "rule": constraints_synthetized,
        "anomalies": anomalies,
        "states": states,
        "actions": actions
    })

@app.route("/api/traces", methods=['GET'])
def get_traces():
    return jsonify(
        traces=['Tiger correct',
                'Tiger 40',
                'Tiger 60',
                'Tiger 80',
                'Velocity regulation 10',
                'Velocity regulation 100',
                ]
    )


if __name__ == '__main__':
    app.run(debug=True)
