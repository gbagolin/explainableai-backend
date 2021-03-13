import uvicorn
from fastapi import FastAPI

app = FastAPI()

from src.routes import home
from src.routes import get_traces
from src.routes import synthetize_rule

app.include_router(home.router)
app.include_router(get_traces.router)
app.include_router(synthetize_rule.router)