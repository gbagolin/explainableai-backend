import z3
import math
import re
import random
import copy
import pdb

from .Problem import Problem
from .DummyVar import DummyVar
from .Constraint import Constraint
from .exceptions.OperandError import OperandError
from .utilities.util import *
from .Result import Result
from .Run import Run


class AtomicRule:

    def __init__(self, problem=None, ruleNum=0, id=None, actions=None, formula=None, threshold=0.10):
        self.id = id
        self.actions = actions
        self.formula = formula
        self.solver = z3.Optimize()
        self.problem = problem
        self.soft_constr = []
        self.constraints = []
        self.rule_num = ruleNum
        self.variables = {}
        self.variable_sign = {}
        self.variable_state = {}
        self.threshold = threshold
        self.variable_constraint_set = []
        self.hard_constraint = []
        self.result = None
        self.model = None

    def declareVariable(self, variableName):
        '''
        Return a z3 variable, which stands for a free variable, with probability constraint.
        '''
        x = z3.Real(variableName)
        self.solver.add(0.0 < x)
        self.solver.add(x <= 1.0)
        newVariable = {variableName: x}
        self.variables.update(newVariable)
        return x

    def addConstraint(self, formula):
        '''
        Create a z3 formula representing a constraint given a formula.
        eg: Rule.addConstraint(x1 == 1, x2 == 2, x3 == 3)
        output: z3.And(x1 == 1,x2 == 2, x3 == 3)
        '''
        variablesInFormula = set()
        and_constraint_list = []
        # set probabilities limits for free variables in args
        # a formula could be of the form: x1 == 1, x2 == 2, x3 == 3
        # we want to put these constraints in z3.And only if they are passed all together like this: 
        # Rule.addConstraint(x1 == 1, x2 == 2, x3 == 3)
        for constraint in formula:
            constr = Constraint(constraint)
            variablesInFormula.add(constr.variable)
            self.variable_sign[constr.variable] = constr.operator
            self.variable_state[constr.variable] = self.problem.states[constr.state]
            and_constraint_list.append(constr)

        self.variable_constraint_set.append(variablesInFormula)
        self.constraints.append(and_constraint_list)

    def addHardConstraint(self, constraints):
        '''
        Add hard constraints 
        '''
        for constraint in constraints:
            self.solver.add(constraint)
            self.hard_constraint.append(constraint)

    def findMaxSmtInRule(self):
        print("Solving MAX-SMT problem")
        formula = None

        for run in range(len(self.problem.belief_in_runs)):
            for bel, belief in enumerate(self.problem.belief_in_runs[run]):
                # generate boolean var for soft constraints
                soft = z3.Bool('b_{}_{}'.format(run, bel))
                self.soft_constr.append(DummyVar(soft, run, bel))
                subrules = []

                for constraints_in_and in self.constraints:
                    subrule = []
                    for i, constraint in enumerate(constraints_in_and):
                        constraint.belief = belief[self.problem.states[constraint.state].state_name]
                        subrule.append(eval(constraint.__str__(), {}, self.variables))

                    subrules.append(z3.And(subrule))
                formula = z3.Or(subrules)
                # la mia regola deve spiegare se ha fatto l'azione, altrimenti non deve spiegarla.
                if self.problem.actions_in_runs[run][
                    bel] not in self.actions:  # vedo se l'azione scelta viene rispettata dal bielef
                    formula = z3.Not(formula)
                # può essere risolto dall cheat (soft) oppure dalla formula
                self.solver.add(z3.Or(soft, formula))

                # solve MAX-SMT problem
        low_threshold = 0
        total_soft_constr = len(self.soft_constr)
        high_threshold = len(self.soft_constr)
        final_threshold = -1
        best_model = []

        # uso una ricerca binaria per risolvere l'or gigante definito sopra!
        while low_threshold <= high_threshold:
            self.solver.push()  # risolutore incrementale, consente di evitare di rifare calcoli creando un ambiente virtuale
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

        print('fail to satisfy {} steps out of {}'.format(final_threshold, total_soft_constr))
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
        self.result = Result(rule_obj=copy.copy(self), model=m)
        print(self.result)

        # generate 1000 random points inside the rule
        rule_points = []
        generated_points = 0
        # crei dei punti perchè potrei non aver visto tutti i casi strani dalle traccie.
        attempts = 0
        while generated_points < 1000 and attempts < 10000:
            attempts += 1
            point = self.problem.generate_points()

            satisfy_a_constraint = False
            for i, and_constraint in enumerate(self.constraints):
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

        # Hellinger distance of unsatisfiable steps
        failed_rules_diff_action = []
        Hellinger_min = []
        failed_step_counter = 0
        for num, soft in enumerate(self.soft_constr):
            if m[soft.literal] == False or not (self.problem.actions_in_runs[soft.run][soft.step] in self.actions):
                continue
            failed_rules_diff_action.append(num)
            P = [self.problem.belief_in_runs[soft.run][soft.step][state] for state in
                 map(lambda state: state.state_name, self.problem.states)]

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
                state_beliefs.append(
                    ({
                        "state": state,
                        "belief": self.problem.belief_in_runs[soft.run][soft.step][state]
                    }))

            run = Run(run=self.problem.run_folders[soft.run], 
                      step=soft.step,
                      action=self.problem.actions_in_runs[soft.run][soft.step], 
                      beliefs=state_beliefs,
                      hellinger_distance=hel, is_anomaly=is_anomaly)
            self.result.add_run(run)
            failed_step_counter += 1
        failed_steps_same_action = []
        for num, soft in enumerate(self.soft_constr):
            if m[soft.literal] == False or (self.problem.actions_in_runs[soft.run][soft.step] in self.actions):
                continue
            failed_steps_same_action.append(soft)

        for soft in failed_steps_same_action:
            state_beliefs = []
            for state in map(lambda state: state.state_name, self.problem.states):
                state_beliefs.append(
                    ({
                        "state": state,
                        "belief": self.problem.belief_in_runs[soft.run][soft.step][state]
                    }
                    ))

            run = Run(run=self.problem.run_folders[soft.run], step=soft.step,
                      action=self.problem.actions_in_runs[soft.run][soft.step], beliefs=state_beliefs,
                      hellinger_distance=None, is_anomaly=False)
            self.result.add_run_different_action(run)

            failed_step_counter += 1

        self.result.print_unsat_steps(self.actions)
        self.result.print_unsat_steps_different_action()
        self.result.reset_rule_unsatisfied()

    def solve(self):
        """
        synthetize each rule
        """
        self.solver.push()
        model = self.findMaxSmtInRule()
        self.synthetize_rule(model)
        # self.print_rule_result(model)
        self.solver.pop()
        print()
