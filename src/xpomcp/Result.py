from .utilities.util import *


class Result:

    def __init__(self, model=None, rule_obj=None, type="action_rule"):
        self.rule_obj = rule_obj
        self.model = model
        self.rule_unsatisfied = []
        self.rule_unsatisfied_different_action = []
        self.all_rule_unsatisfied_different_action = []
        self.all_rules_unsatisfied = []
        self.type = type

    def reset_rule_unsatisfied(self):
        for run in self.rule_unsatisfied:
            self.all_rules_unsatisfied.append(run)

        for run in self.rule_unsatisfied_different_action:
            self.all_rule_unsatisfied_different_action.append(run)

        self.rule_unsatisfied = []
        self.rule_unsatisfied_different_action = []

    def get_constraint_synthetized(self,
                                   MAP_STATES_TO_FRONTEND=None):
        '''
        :returns a list of constraints of the form:
        [[{state, operator, value}], [...]]
        When a constraint is in and, then the list is of the form:
        [[{state, operator, value},{state, operator, value}], [...]]
        '''
        rule = []
        for rule_obj in self.rule_obj.rule_list:
            constraint = {
                "action": rule_obj.actions,
                "constraints": []
            }
            for i, variables in enumerate(rule_obj.variable_constraint_set):
                sub_rule = []
                for j, variable in enumerate(variables):
                    sub_rule.append({
                        "state": MAP_STATES_TO_FRONTEND[
                            self.rule_obj.variable_state[variable].state_name
                        ],
                        "operator": self.rule_obj.variable_sign[variable],
                        "value": to_real(self.model[variable])
                    })
                constraint['constraints'].append(sub_rule)
            rule.append(constraint)
        return rule

    def get_all_rule_unsat_same_action(self,
                                       MAP_ACTIONS_TO_FRONTEND,
                                       MAP_STATES_TO_FRONTEND):
        '''
        Returns a list of anomalies having the action equal to the one analized. 
        Hellinger distance present. 
        
        Parameter MAP_ACTIONS_TO_FRONTEND: dict, used to map actions 
        from backend to frontend for user readability 
        
        Parameter MAP_STATES_TO_FRONTEND: dict, used to map states 
        from backend to frontend for user readability 
        '''
        anomalies = []
        for anomaly in self.all_rules_unsatisfied:
            anomaly_to_frontend = {
                "action": MAP_ACTIONS_TO_FRONTEND[anomaly.action],
                "beliefs": list(map(lambda e: {
                    "belief": e['belief'],
                    "state": MAP_STATES_TO_FRONTEND[e['state']]
                },
                                    anomaly.beliefs
                                    )
                                ),
                "hellinger_distance": anomaly.hellinger_distance,
                "is_anomaly": anomaly.is_anomaly,
                "run": anomaly.run,
                "step": anomaly.step
            }
            anomalies.append(anomaly_to_frontend)
        return anomalies

    def get_all_rule_unsat_different_action(self,
                                            MAP_ACTIONS_TO_FRONTEND,
                                            MAP_STATES_TO_FRONTEND):
        '''
        Returns a list of anomalies which follows the rule, but have a different action, 
        than the one imposed. 
        Hellinger distance not present. 
        
        Parameter MAP_ACTIONS_TO_FRONTEND: dict, used to map actions 
        from backend to frontend for user readability 
        
        Parameter MAP_STATES_TO_FRONTEND: dict, used to map states 
        from backend to frontend for user readability 
        '''
        anomalies = []
        for anomaly in self.all_rule_unsatisfied_different_action:
            anomaly_to_frontend = {
                "action": MAP_ACTIONS_TO_FRONTEND[anomaly.action],
                "beliefs": list(map(lambda e: {
                    "belief": e['belief'],
                    "state": MAP_STATES_TO_FRONTEND[e['state']]
                },
                                    anomaly.beliefs)
                                ),
                "run": anomaly.run,
                "step": anomaly.step
            }
            anomalies.append(anomaly_to_frontend)
        return anomalies

    def _print_rule(self):
        """
        pretty printing of rules, give a certain model
        """
        # fare qualcosa qui.
        rule = ""
        rule += 'rule: do action {} if: '.format(
            self.rule_obj.actions[0] if len(self.rule_obj.actions) == 1 else self.rule_obj.actions)

        for i, variables in enumerate(self.rule_obj.variable_constraint_set):
            if i > 0:
                rule += " OR "

            rule += "("

            for j, variable in enumerate(variables):
                if j > 0:
                    rule += " AND "
                rule += "P_{} {} {:.3f}".format(self.rule_obj.variable_state[variable].state_name,
                                                self.rule_obj.variable_sign[variable], to_real(self.model[variable]))
            rule += ")"

        self.rule = rule

    def _print_rules(self):
        """
        pretty printing of rules, give a certain model
        """
        rule = ""
        for rule_obj in self.rule_obj.rule_list:
            rule += 'rule: do action {} if: '.format(
                rule_obj.actions[0] if len(rule_obj.actions) == 1 else rule_obj.actions)

            for i, variables in enumerate(rule_obj.variable_constraint_set):
                if i > 0:
                    rule += " OR "

                rule += "("
                for j, variable in enumerate(variables):
                    if j > 0:
                        rule += " AND "
                    rule += "P_{} {} {:.3f}".format(rule_obj.variable_state[variable].state_name,
                                                    rule_obj.variable_sign[variable], to_real(self.model[variable]))
                rule += ")"
            rule += "\n"
        self.rule = rule

    def add_run(self, run):
        self.rule_unsatisfied.append(run)

    def add_run_different_action(self, run):
        self.rule_unsatisfied_different_action.append(run)

    def print_unsat_steps(self, action=""):
        self.rule_unsatisfied = sorted(list(set(self.rule_unsatisfied)), key=lambda run: run.hellinger_distance,
                                       reverse=True)
        if len(self.rule_unsatisfied) > 0:
            print(f'Unsatisfiable steps action: {action}')

        for i, unsat_rule in enumerate(self.rule_unsatisfied):
            print(f'{i} {unsat_rule}')

    def print_unsat_steps_different_action(self):
        if len(self.rule_unsatisfied) > 0:
            print('Unsatisfiable steps different action:')

        for i, unsat_rule in enumerate(self.rule_unsatisfied_different_action):
            print(f'{i} {unsat_rule}')

    def __str__(self):
        if self.type == "action_rule":
            self._print_rule()
        elif self.type == "final_rule":
            self._print_rules()
        else:
            return "ERROR: Rule type not correct!"
        return self.rule
