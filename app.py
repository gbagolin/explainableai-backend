from src.routes import get_graph_from_trace
from src.routes import get_attributes_from_problem
from src.routes import get_all_problems
from src.routes import synthetize_rule
from src.routes import get_traces_from_problem
from src.routes import home
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(home.router)
app.include_router(get_traces_from_problem.router)
app.include_router(synthetize_rule.router)
app.include_router(get_all_problems.router)
app.include_router(get_attributes_from_problem.router)
app.include_router(get_graph_from_trace.router)
