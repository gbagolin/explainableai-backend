class Run:

    def __init__(self, run, step, action, beliefs, is_anomaly, hellinger_distance=None, segment=None):
        self.run = run
        self.step = step
        self.action = action
        self.beliefs = beliefs  # list((state,belief))
        self.hellinger_distance = hellinger_distance
        self.is_anomaly = is_anomaly
        self.segment = segment

    def to_dict(self,
                MAP_STATES_TO_FRONTEND,
                MAP_ACTIONS_TO_FRONTEND):
        beliefs = []
        for belief in self.beliefs:
            beliefs.append(
                {
                    "belief": belief['belief'],
                    "state": MAP_STATES_TO_FRONTEND[belief['state']]
                }
            )
        return {
            "run": self.run,
            "step": self.step,
            "action": MAP_ACTIONS_TO_FRONTEND[self.action],
            "beliefs": beliefs,
            "hellinger_distance": self.hellinger_distance,
            "is_anomaly": self.is_anomaly,
            "segment": self.segment
        }

    def __str__(self):
        to_return = ""

        if self.is_anomaly:
            to_return += "ANOMALY "

        to_return += "{} step {}: action {} with belief ".format(
            self.run, self.step, self.action)

        for bel in self.beliefs:
            state = bel['state']
            belief = bel['belief']
            to_return += 'P_{} = {:.3f} '.format(state, belief)

        if self.hellinger_distance != None:
            to_return += '--- Hellinger = {}'.format(self.hellinger_distance)

        if self.segment != None:
            to_return += f'Segment: {self.segment}'

        return to_return

    def __eq__(self, other):
        return self.__str__() == other.__str__()

    def __hash__(self):
        return hash(self.__str__())
