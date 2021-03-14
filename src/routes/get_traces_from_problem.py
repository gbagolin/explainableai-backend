from fastapi import APIRouter

router = APIRouter()

from src.schemas.Problem import Problem


@router.post("/api/get_traces_from_problem")
def get_traces_from_problem(problem: Problem):
    '''

    :param problem: Requested problem
    :return: List of traces available of the requested problem.
    '''
    if problem.name.lower() == "tiger":
        return [
            "tiger correct",
            "tiger 40",
            "tiger 60",
            "tiger 80",
        ]
    elif problem.name.lower() == "velocity regulation":
        return [
            "velocity regulation 10",
            "velocity regulation 100",
            "velocity regulation arms"
        ]
    else:
        return {
            "problem"
        }
