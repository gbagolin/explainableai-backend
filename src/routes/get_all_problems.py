from fastapi import APIRouter

router = APIRouter()


@router.get('/api/get_all_problems')
def get_all_problems():
    '''

    :return: a json array containing problems' name
    '''
    return [
        "tiger",
        "velocity regulation"
    ]
