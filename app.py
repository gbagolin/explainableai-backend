from fastapi import FastAPI

app = FastAPI()

from src.routes import home
from src.routes import get_traces_from_problem
from src.routes import synthetize_rule
from src.routes import get_all_problems

app.include_router(home.router)
app.include_router(get_traces_from_problem.router)
app.include_router(synthetize_rule.router)
app.include_router(get_all_problems.router)