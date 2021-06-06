class DummyVar:
    """
    Class that represent a dummy variable introduced by the MAX-SMT step.
    It contains the literal (a Boolean variable) that identify the dummy
    variable inside the SMT problem and the the information related to wich
    rule, run and step is codified by the variable.
    """

    def __init__(self, literal, run, step, rule_num=None):
        self.literal = literal
        self.run = run
        self.step = step
        self.rule_num = rule_num
