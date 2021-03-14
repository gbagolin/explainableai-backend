from pydantic import BaseModel


class Problem(BaseModel):
    '''
    Class used as schema for typing validation
    '''
    name: str
