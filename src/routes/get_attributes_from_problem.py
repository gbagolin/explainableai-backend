from fastapi import APIRouter

router = APIRouter()

from src.problem_attributes import tiger
from src.problem_attributes import velocity_regulation

from src.schemas.Problem import Problem


@router.post('/api/get_attributes_from_problem')
def get_attributes_from_problem(problem: Problem):
    '''
    Return a json object based on the problem requested.
    :param problem: Requested problem
    :return: a json object containing problems attributes
    '''
    if problem.name.lower() == "tiger":
        return tiger.tiger
    elif problem.name.lower() == "velocity regulation":
        return velocity_regulation.velocity_regulation
