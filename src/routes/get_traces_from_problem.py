from fastapi import APIRouter

router = APIRouter()


@router.post("/api/get_traces_from_problem")
def get_traces_from_problem(problem: str):
    '''

    :param problem: Requested problem
    :return: List of traces available of the requested problem.
    '''
    if problem.lower() == "tiger":
        return [
            "tiger correct",
            "tiger 40",
            "tiger 60",
            "tiger 80",
        ]
    elif problem.lower() == "velocity regulation":
        return [
            "velocity regulation 10",
            "velocity regulation 100",
            "velocity regulation arms"
        ]
    else:
        return {
            "problem"
        }
