from fastapi import APIRouter

router = APIRouter()

@router.get('/')
def home():
    return {"It works"}