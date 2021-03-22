from typing import Dict, Any, List
from pydantic import BaseModel
from .Constraint import Constraint


class Atomic_Rule(BaseModel):
    action: str
    variables: List[str]
    constraints: List[List[Constraint]]
    hard_constraint: List[int] = []
    trace: str
    problem: str
