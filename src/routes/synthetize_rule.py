from fastapi import APIRouter, Request
from typing import Dict, Any, List
from pydantic import BaseModel

from ..types.Atomic_Rule import Atomic_Rule

from ..utility.map import *
from src.xpomcp.Tiger_Problem import *
from src.xpomcp.Velocity_Regulation_Problem import *
from src.xpomcp.AtomicRule import AtomicRule
from src.xpomcp.RuleTemplate import RuleTemplate

router = APIRouter()


@router.post('/api/send_rule')
def synthetize_rule(request: List[Atomic_Rule]):
    data = request

    map_variable_string_to_object = dict()
    map_belief_to_rule_sintax = dict()

    problem = None
    rule = None
    trace = data[0].trace
    if data[0].problem == "tiger":
        ''' Initialization of Tiger problem '''
        problem = Tiger_Problem(xes_log=f'src/xpomcp/tracce/{MAP_TRACES[trace]}',
                                num_traces_to_analyze=100,
                                states=[TIGER_LEFT, TIGER_RIGHT])
        map_belief_to_rule_sintax = {
            "tiger left": TIGER_LEFT.get_probability(),
            "tiger right": TIGER_RIGHT.get_probability()
        }
        states = ["tiger left", "tiger right"]
    elif data[0].problem == "velocity regulation":
        ''' Initialization of Velocity regulation problem '''
        problem = Velocity_Regulation_Problem(xes_log=f'src/xpomcp/tracce/{MAP_TRACES[trace]}',
                                              states=[
                                                  EASY, INTERMEDIATE, DIFFICULT],
                                              num_traces_to_analyze=100)
        map_belief_to_rule_sintax = {
            "easy": EASY.get_probability(),
            "intermediate": INTERMEDIATE.get_probability(),
            "difficult": DIFFICULT.get_probability()
        }

        states = ["easy", "intermediate", "difficult"]

    # TODO: create the list of actions out.
    rule_list = []
    for atomic_rule in data:
        print(atomic_rule)
        rule = AtomicRule(
            actions=[MAP_ACTIONS_TO_BACKEND[atomic_rule.action]],
            problem=problem
        )

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
    rule_template.solve()
    #
    constraints_synthetized = rule_template.result.get_constraint_synthetized(MAP_STATES_TO_FRONTEND
                                                                              )
    actions = rule_template.result.rule_obj.actions
    actions = list(map(lambda x: MAP_ACTIONS_TO_FRONTEND[x], actions))
    anomalies_same_action = list(
        rule_template.result.get_all_rule_unsat_same_action(MAP_ACTIONS_TO_FRONTEND,
                                                            MAP_STATES_TO_FRONTEND)
    )
    anomalies_different_action = list(
        rule_template.result.get_all_rule_unsat_different_action(MAP_ACTIONS_TO_FRONTEND,
                                                                 MAP_STATES_TO_FRONTEND)
    )
    #
    return ({
        "rule": constraints_synthetized,
        "anomalies_same_action": anomalies_same_action,
        "anomalies_different_action": anomalies_different_action,
        "states": states,
        "actions": actions
    })
