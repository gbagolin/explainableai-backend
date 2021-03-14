from fastapi import APIRouter

router = APIRouter()

from src.problem_attributes.tiger import *
from src.problem_attributes.velocity_regulation import *


@router.post('/api/get_actions_from_problem')
def get_attributes_from_problem(problem: str):
    '''
    Return a json object based on the problem requested.
    :param problem: Requested problem
    :return: a json object containing problems attributes
    '''
    if problem.lower() == "tiger":
        return tiger
    elif problem.lower() == "velocity regulation":
        return velocity_regulation
