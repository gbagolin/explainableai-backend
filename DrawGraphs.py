import plotly.graph_objects as go
from plotly.subplots import make_subplots


class DrawGraphs:
    def __init__(self, rule):
        self.rule = rule

    def draw(self):
        constraints_synthetized = self.rule.result.get_constraint_synthetized()
        num_sub_plots = len(constraints_synthetized)
        print(f"Num sublplots: {num_sub_plots}")
        fig = make_subplots(rows=1, cols=1)
        print(constraints_synthetized)
        y = [0.5, 1]
        fig.add_bar(
            name=constraints_synthetized[0][0]['state'],
            x=[constraints_synthetized[0][0]['state']],
            y=y
        )
        #     for unsat_step in list_unsat_rule:
        #         for i, constraints_in_and in enumerate(constraints_synthetized):
        #             for constraint in constraints_in_and:
        #                 # if unsat_step.is_anomaly:
        #                 print(unsat_step.beliefs)
        #                 fig.add_bar(name=constraint['state'],
        #                             x=[constraint['state']],
        #                             y=[constraint['value']],
        #                             row=1,
        #                             col=i + 1
        #                             )
        # fig.update_layout(
        #     autosize=False,
        #     width=500,
        #     height=500
        # )
        fig.show()
