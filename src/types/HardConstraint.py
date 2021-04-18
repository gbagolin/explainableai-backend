from pydantic import BaseModel

class HardConstraint(BaseModel):
    variable: str
    operator: str
    term: str
