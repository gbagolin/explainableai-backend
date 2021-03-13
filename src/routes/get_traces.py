from fastapi import APIRouter

router = APIRouter()

@router.get("/api/traces")
def get_traces():
    return (
        {
            "traces": [
                'Tiger correct',
                'Tiger 40',
                'Tiger 60',
                'Tiger 80',
                'Velocity regulation 10',
                'Velocity regulation 100',
                "Velocity regulation ARMS"
            ]
        }
    )