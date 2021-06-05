from pydantic import BaseModel


class Trace(BaseModel):
    name: str
