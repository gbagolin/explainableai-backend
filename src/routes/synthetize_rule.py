from fastapi import APIRouter, Request
from typing import List

from ..types.Data import Data

from ..utility.map import *
from src.xpomcp.Tiger_Problem import *
from src.xpomcp.Velocity_Regulation_Problem import *
from src.xpomcp.AtomicRule import AtomicRule
from src.xpomcp.RuleTemplate import RuleTemplate


router = APIRouter()


@router.post('/api/send_rule')
def synthetize_rule(request: Data):
    data = request

    map_variable_string_to_object = dict()
    map_belief_to_rule_sintax = dict()

    problem = None
    rule = None
    trace = data.ruleTemplate[0].trace
    if data.ruleTemplate[0].problem == "tiger":
        ''' Initialization of Tiger problem '''
        problem = Tiger_Problem(xes_log=f'src/xpomcp/tracce/{MAP_TRACES[trace]}',
                                num_traces_to_analyze=100,
                                states=[TIGER_LEFT, TIGER_RIGHT])
        map_belief_to_rule_sintax = {
            "tiger left": TIGER_LEFT.get_probability(),
            "tiger right": TIGER_RIGHT.get_probability()
        }
        states = ["tiger left", "tiger right"]
    elif data.ruleTemplate[0].problem == "velocity regulation":
        ''' Initialization of Velocity regulation problem '''
        problem = Velocity_Regulation_Problem(xes_log=f'src/xpomcp/tracce/{MAP_TRACES[trace]}',
                                              states=[
                                                  EASY, INTERMEDIATE, DIFFICULT],
                                              num_traces_to_analyze=None)
        map_belief_to_rule_sintax = {
            "easy": EASY.get_probability(),
            "intermediate": INTERMEDIATE.get_probability(),
            "difficult": DIFFICULT.get_probability()
        }

        states = ["easy", "intermediate", "difficult"]

    # TODO: create the list of actions out.
    rule_list = []
    actions = []
    for atomic_rule in data.ruleTemplate:
        rule = AtomicRule(
            actions=[MAP_ACTIONS_TO_BACKEND[atomic_rule.action.name]],
            problem=problem
        )
        actions.append({"id": atomic_rule.action.id,
                        "name": atomic_rule.action.name})

        for variable in atomic_rule.variables:
            variable_name = variable
            map_variable_string_to_object[variable_name] = rule.declareVariable(
                variable_name)

        for constraints in atomic_rule.constraints:
            '''constraints in "and" here'''
            constraint = []
            for single_constraint in constraints:
                '''
                for each constraint in "AND",
                the constraint gets created following the template:
                "variable" "operator" "belief"
                '''
                el = eval(
                    single_constraint.variable +
                    single_constraint.operator +
                    str(map_belief_to_rule_sintax[single_constraint.state]),
                    {}, dict(**map_variable_string_to_object,
                             **map_belief_to_rule_sintax,
                             **{"single_constraint": single_constraint,
                                "map_belief_to_rule_sintax": map_belief_to_rule_sintax}))
                constraint.append(el)
            rule.addConstraint(constraint)
        hard_constraints = []

        for hard_constraint in atomic_rule.hard_constraint:
            el = eval(
                hard_constraint.variable +
                hard_constraint.operator +
                str(hard_constraint.probability),
                {}, dict(**map_variable_string_to_object))
            hard_constraints.append(el)

        rule.addHardConstraint(hard_constraints)
        rule_list.append(rule)

    rule_template = RuleTemplate(rule_list, problem, threshold=0.10)

    hard_constraints = []
    for hard_constraint in data.hardConstraint:
        el = eval(
            hard_constraint.variable +
            hard_constraint.operator +
            str(hard_constraint.term),
            {}, dict(**map_variable_string_to_object))
        hard_constraints.append(el)
    rule_template.add_constraint(hard_constraints)
    rule_template.solve()
    #
    constraints_synthetized = rule_template.result.get_constraint_synthetized(
        MAP_STATES_TO_FRONTEND)
    for ruleIndex in range(len(constraints_synthetized)):
        constraints_synthetized[ruleIndex]['action'] = actions[ruleIndex]

    all_actions = []
    for rule in rule_template.rule_list:
        all_actions.append(rule.actions)

    all_actions = [action for actions in all_actions for action in actions]

    # actions = list(map(lambda x: MAP_ACTIONS_TO_FRONTEND[x], all_actions))
    anomalies_same_action = []
    for indexRule in range(len(rule_template.rule_list)):
        rule = rule_template.rule_list[indexRule]
        anomalies = {
            "actions": actions[indexRule],
            "anomalies": list(
                rule.result.get_all_rule_unsat_same_action(MAP_ACTIONS_TO_FRONTEND,
                                                           MAP_STATES_TO_FRONTEND)
            )
        }
        anomalies_same_action.append(anomalies)

    anomalies_different_action = []
    for indexRule in range(len(rule_template.rule_list)):
        rule = rule_template.rule_list[indexRule]
        anomalies = {
            "actions": actions[indexRule],
            "anomalies": list(
                rule.result.get_all_rule_unsat_different_action(MAP_ACTIONS_TO_FRONTEND,
                                                                MAP_STATES_TO_FRONTEND)
            )
        }
        anomalies_different_action.append(anomalies)

    steps_counter_anomalies_same_action = dict()
    steps_counter_anomalies_different_action = dict()

    # print(anomalies_same_action)

    for anomaliesObject in anomalies_same_action:
        for anomaly in anomaliesObject['anomalies']:
            if anomaly['step'] in steps_counter_anomalies_same_action.keys():
                steps_counter_anomalies_same_action[anomaly['step']] += 1
            else:
                steps_counter_anomalies_same_action[anomaly['step']] = 1

    for anomaliesObject in anomalies_different_action:
        for anomaly in anomaliesObject['anomalies']:
            if anomaly['step'] in steps_counter_anomalies_different_action.keys():
                steps_counter_anomalies_different_action[anomaly['step']] += 1
            else:
                steps_counter_anomalies_different_action[anomaly['step']] = 1

    return ({
        "rule": constraints_synthetized,
        "anomalies_same_action": anomalies_same_action,
        "anomalies_different_action": anomalies_different_action,
        "states": states,
        "actions": actions,
        "steps_counter_anomalies_same_action": steps_counter_anomalies_same_action,
        "steps_counter_anomalies_different_action": steps_counter_anomalies_different_action,
    })
