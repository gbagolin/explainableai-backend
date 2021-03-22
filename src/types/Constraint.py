from typing import Dict, Any, List
from pydantic import BaseModel


class Constraint(BaseModel):
    operator: str
    state: str
    variable: str
