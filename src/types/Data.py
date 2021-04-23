from typing import Dict, Any, List
from pydantic import BaseModel


class Constraint(BaseModel):
    operator: str
    state: str
    variable: str


class Hard_Constraint(BaseModel):
    variable: str
    operator: str
    term: str


class Action(BaseModel):
    id: int
    name: str


class Atomic_Rule(BaseModel):
    action: Action
    variables: List[str]
    constraints: List[List[Constraint]]
    hard_constraint: List[int] = []
    trace: str
    problem: str


class Data(BaseModel):
    hardConstraint: List[Hard_Constraint]
    ruleTemplate: List[Atomic_Rule]
