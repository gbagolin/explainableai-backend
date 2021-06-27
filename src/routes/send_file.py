from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
import weasyprint
from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates
from os import path

path_str = path.dirname(path.realpath(__file__))
print(path_str)

router = APIRouter()

templates = Jinja2Templates(directory="src/template")

names = ["giovanni", "luca"]


@router.get('/api/send_file')
async def main():
    pdf = weasyprint.HTML('http://localhost:8001/create_report').write_pdf()
    open('google.pdf', 'wb').write(pdf)
    return FileResponse("google.pdf")


@router.get("/create_report", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("report.html", {"request": request, "names": names})
