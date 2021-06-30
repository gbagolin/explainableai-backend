from pydantic import BaseModel
from typing import List


class Action(BaseModel):
    id: int
    name: str


class Rule(BaseModel):
    rule: List
    states: List
    actions: List
    anomalies_same_action: List
    anomalies_different_action: List


class Report(BaseModel):
    rule: Rule
    plots: List[str]
    ruleString: List
