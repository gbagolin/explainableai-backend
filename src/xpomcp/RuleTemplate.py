import z3
import copy
from numba import jit
from time import process_time

from .Problem import Problem
from .DummyVar import DummyVar
from .Constraint import Constraint
from .exceptions.OperandError import OperandError
from .utilities.util import *
from .Result import Result
from .Run import Run


class RuleTemplate:
    def __init__(self, rule_list, problem, threshold):
        self.rule_list = rule_list
        self.solver = z3.Optimize()
        self._set_attributes()
        self.problem = problem
        self.soft_constr = []
        self.threshold = threshold

    def _set_attributes(self):
        self.variables = {}
        self.variable_sign = {}
        self.variable_state = {}
        self.variable_constraint_set = []
        self.constraints = []
        self.hard_constraint = []
        self.actions = []

        for rule in self.rule_list:
            self.variables.update(rule.variables)
            self.variable_sign.update(rule.variable_sign)
            self.variable_state.update(rule.variable_state)
            self.variable_constraint_set += rule.variable_constraint_set
            self.constraints.append(rule.constraints)
            self.hard_constraint += rule.hard_constraint

        for variable in self.variables:
            self.solver.add(self.variables[variable] >= 0.0)
            self.solver.add(self.variables[variable] <= 1.0)

        for hard_constraint in self.hard_constraint:
            self.solver.add(hard_constraint)

    def add_constraint(self, formula):
        for constraint in formula:
            self.solver.add(constraint)
            self.hard_constraint.append(constraint)

    def find_max_smt_in_rules(self):
        print("Solving MAX-SMT problem")
        formula = None
        print(f"Num of steps: {len(self.problem.belief_in_runs[1])}"
              )

        for rule_num, rule in enumerate(self.rule_list):
            for run in range(len(self.problem.belief_in_runs)):
                for bel, belief in enumerate(self.problem.belief_in_runs[run]):
                    # generate boolean var for soft constraints
                    soft = z3.Bool('b_{}_{}_{}'.format(run, bel, rule_num))
                    self.soft_constr.append(
                        DummyVar(soft, run, bel, rule_num))
                    subrules = []

                    for constraints_in_and in rule.constraints:
                        subrule = []
                        for i, constraint in enumerate(constraints_in_and):
                            constraint.belief = belief[self.problem.states[constraint.state].state_name]
                            subrule.append(
                                eval(constraint.__str__(), {}, self.variables))

                        subrules.append(z3.And(subrule))
                    formula = z3.Or(subrules)

                    if self.problem.actions_in_runs[run][bel] not in rule.actions:
                        formula = z3.Not(formula)

                    self.solver.add(z3.Or(soft, formula))
        # solve MAX-SMT problem
        low_threshold = 0
        total_soft_constr = len(self.soft_constr)
        high_threshold = len(self.soft_constr)
        final_threshold = -1
        best_model = []

        # uso una ricerca binaria per risolvere l'or gigante definito sopra!
        while low_threshold <= high_threshold:
            # risolutore incrementale, consente di evitare di rifare calcoli creando un ambiente virtuale
            self.solver.push()
            threshold = (low_threshold + high_threshold) // 2
            # Pble pseudo boolean less equal
            self.solver.add(z3.PbLe([(soft.literal, 1) for soft in self.soft_constr],
                                    threshold))  # l'add viene fatto sull'ambiente virtuale appena creato.
            result = self.solver.check()
            if result == z3.sat:
                final_threshold = threshold
                best_model = self.solver.model()
                high_threshold = threshold - 1
            else:
                low_threshold = threshold + 1
            self.solver.pop()

        print('fail to satisfy {} steps out of {}'.format(
            final_threshold, total_soft_constr))
        # return a model that satisfy all the hard clauses and the maximum number of soft clauses
        # print(best_model)
        return best_model

    def synthetize_rule(self, model):
        """
        Synthetize a rule as close as possible to the trace.
        Print all the unstatisfiable steps and highlight anomalies.
        """
        self.solver.push()

        # fix dummy variables
        for soft in self.soft_constr:
            if model[soft.literal] == True:
                self.solver.add(soft.literal)
            elif model[soft.literal] == False:
                self.solver.add(z3.Not(soft.literal))

        # try to optimize intervals
        # cerco di trovare i numeri più grandi che soddisfano la regola.
        interval_cost = z3.Real('interval_cost')
        cost = []

        negative_sign = ['<', '<=']
        for variable_set in self.variable_constraint_set:
            for variable in variable_set:
                if self.variable_sign[variable] in negative_sign:
                    cost.append(-variable)
                else:
                    cost.append(variable)

        total_cost = z3.Sum(cost)
        self.solver.add(interval_cost == total_cost)
        self.solver.minimize(interval_cost)

        # check if SAT or UNSAT
        print('Check Formulas')
        # print(self.solver)
        result = self.solver.check()
        # print(result)

        m = self.solver.model()
        self.model = m
        # remove intervall optimization requirements
        self.solver.pop()

        # exit if unsat
        # in teoria non potrebbe mai essere unsat perchè l'abbiamo già risolto prima, ora abbiamo spostato solo le threshold.
        # se è unsat mi dovrebbe dare delle prove. (NON guardare i log)
        if result != z3.sat:
            print("IMPOSSIBLE TO SATISFY, ):")
            return

        # print results
        self.result = Result(rule_obj=copy.copy(
            self), model=m, type="final_rule")
        print(self.result)

        for rule in self.rule_list:
            # generate 1000 random points inside the rule
            rule_points = []
            generated_points = 0
            # crei dei punti perchè potrei non aver visto tutti i casi strani dalle traccie.
            attempts = 0
            while generated_points < 1000 and attempts < 10000:
                attempts += 1
                point = self.problem.generate_points()

                satisfy_a_constraint = False
                for i, and_constraint in enumerate(rule.constraints):
                    is_ok = True
                    for constraint in and_constraint:
                        threshold = to_real(m[constraint.variable])
                        if constraint.operator == '<':
                            if point[constraint.state] > threshold:
                                is_ok = False
                                break
                        elif constraint.operator == '>':
                            if point[constraint.state] < threshold:
                                is_ok = False
                                break
                        elif constraint.operator == '<=':
                            if point[constraint.state] >= threshold:
                                is_ok = False
                                break

                        elif constraint.operator == '>=':
                            if point[constraint.state] <= threshold:
                                is_ok = False
                                break
                        elif constraint.operator == '==':
                            if point[constraint.state] == threshold:
                                is_ok = False
                                break
                        else:
                            raise OperandError(constraint.operator)

                    if not is_ok:
                        continue

                    satisfy_a_constraint = True
                    break

                if satisfy_a_constraint:
                    rule_points.append(point)
                    generated_points += 1

            rule.result = Result()

            # Hellinger distance of unsatisfiable steps
            failed_rules_diff_action = []
            Hellinger_min = []
            failed_step_counter = 0
            for num, soft in enumerate(self.soft_constr):
                if m[soft.literal] == False or not (self.problem.actions_in_runs[soft.run][soft.step] in rule.actions):
                    continue
                failed_rules_diff_action.append(num)
                P = [self.problem.belief_in_runs[soft.run][soft.step][state] for state in
                     map(lambda state: state.state_name, self.problem.states, )]
                hel_dst = [Hellinger_distance(P, Q) for Q in rule_points]
                if len(hel_dst) == 0:
                    hel_dst = [1.0]
                Hellinger_min.append(min(hel_dst))

            # print unsatisfiable steps in decreasing order of hellinger distancEe
            for soft, hel in [[self.soft_constr[x], h] for h, x in zip(Hellinger_min, failed_rules_diff_action)]:
                is_anomaly = False
                if hel > self.threshold:
                    is_anomaly = True

                state_beliefs = []
                for state in map(lambda state: state.state_name, self.problem.states):
                    state_beliefs.append(({
                        "state": state,
                        "belief": self.problem.belief_in_runs[soft.run][soft.step][state]
                    }))

                run = Run(run=self.problem.run_folders[soft.run], step=soft.step,
                          action=self.problem.actions_in_runs[soft.run][soft.step], beliefs=state_beliefs,
                          hellinger_distance=hel, is_anomaly=is_anomaly)
                rule.result.add_run(run)
                failed_step_counter += 1

            failed_steps_same_action = []
            for num, soft in enumerate(self.soft_constr):
                if m[soft.literal] == False or (self.problem.actions_in_runs[soft.run][soft.step] in rule.actions):
                    continue
                failed_steps_same_action.append(soft)

            for soft in failed_steps_same_action:
                state_beliefs = []
                for state in map(lambda state: state.state_name, self.problem.states):
                    state_beliefs.append(({
                        "state": state,
                        "belief": self.problem.belief_in_runs[soft.run][soft.step][state]
                    }))

                run = Run(run=self.problem.run_folders[soft.run], step=soft.step,
                          action=self.problem.actions_in_runs[soft.run][soft.step], beliefs=state_beliefs,
                          hellinger_distance=None, is_anomaly=False)
                rule.result.add_run_different_action(run)

                failed_step_counter += 1

            rule.result.print_unsat_steps(rule.actions)
            rule.result.print_unsat_steps_different_action()
            rule.result.reset_rule_unsatisfied()

    def solve(self):
        """
        synthetize each rule
        """
        self.solver.push()
        model = self.find_max_smt_in_rules()
        t_start = process_time()
        self.synthetize_rule(model)
        t_stop = process_time()
        print(f"Elapsed time: {t_stop - t_start}")
        # self.print_rule_result(model)
        self.solver.pop()
        print()
