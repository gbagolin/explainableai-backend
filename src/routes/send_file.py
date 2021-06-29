from fastapi import APIRouter, Request, Response
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from os import path
import weasyprint
from time import gmtime, strftime

path_str = path.dirname(path.realpath(__file__))
print(path_str)

router = APIRouter()
templates = Jinja2Templates(directory="src/template")

# list of anomalies same action
anomalies_sa = [
    {
        "action": "listen",
        "beliefs": [
            {
                "belief": 0.9694691535150646,
                "state": "tiger left"
            },
            {
                "belief": 0.030530846484935436,
                "state": "tiger right"
            }
        ],
        "hellinger_distance": 0.15927953822858362,
        "is_anomaly": "true",
        "run": "run 48",
        "step": 4
    },
    {
        "action": "listen",
        "beliefs": [
            {
                "belief": 0.9694691535150646,
                "state": "tiger left"
            },
            {
                "belief": 0.030530846484935436,
                "state": "tiger right"
            }
        ],
        "hellinger_distance": 0.15927953822858362,
        "is_anomaly": "true",
        "run": "run 48",
        "step": 4
    },

]

anomalies_da = [
    {
        "action": "listen",
        "beliefs": [
            {
                "belief": 0.9694691535150646,
                "state": "tiger left"
            },
            {
                "belief": 0.030530846484935436,
                "state": "tiger right"
            }
        ],
        "hellinger_distance": 0.15927953822858362,
        "is_anomaly": "true",
        "run": "run 48",
        "step": 4
    },
    {
        "action": "listen",
        "beliefs": [
            {
                "belief": 0.9694691535150646,
                "state": "tiger left"
            },
            {
                "belief": 0.030530846484935436,
                "state": "tiger right"
            }
        ],
        "hellinger_distance": 0.15927953822858362,
        "is_anomaly": "true",
        "run": "run 48",
        "step": 4
    },

]


@router.get('/api/send_file')
async def main():
    headers = {"Content-Disposition": "attachment;",
               "filename": "google.pdf;"}
    pdf = weasyprint.HTML('http://localhost:8001/create_report').write_pdf()
    open('google.pdf', 'wb').write(pdf)
    return FileResponse("google.pdf", headers=headers)


@router.get("/create_report", response_class=HTMLResponse)
async def read_item(request: Request):
    now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    return templates.TemplateResponse("report.html", {"request": request,
                                                      "now": now,
                                                      "anomalies_sa": anomalies_sa,
                                                      "anomalies_da": anomalies_da})
