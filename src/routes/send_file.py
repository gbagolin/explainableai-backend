import numpy
import numpy as np
import matplotlib.pyplot as plt
from fastapi import APIRouter, Request, Response
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from os import path
from PIL import Image
import base64
import io
import weasyprint
from time import gmtime, strftime
from typing import List
from . import var

path_str = path.dirname(path.realpath(__file__))
print(path_str)

router = APIRouter()
templates = Jinja2Templates(directory="src/template")


def extract_statistics(anomalies_same_action: List) -> List:
    '''

    :param anomalies_same_action: List, of all anomalies whose action is equal to the action analyzed.
    :return: numpy.array[10]

    arr[i] contains the number of anomalies whose (i / 10) <= severity (i / 10) + 0.1
    This function is used as support function to plot the graph.
    '''
    # get the list of severities for each severity in the list of anomalies same action.
    severities = [anom['hellinger_distance'] for anom in anomalies_same_action]
    arr = numpy.asarray(severities)
    # num_seve_per_dec[i] contains the number of anomalies whose i <= severity < i + 0.1
    num_seve_per_dec = np.zeros(10)
    left = 0
    pos = 0
    space = np.arange(0.0, 1.0, 0.1)
    for dec in space:
        right = dec + 0.1
        cond = numpy.logical_and(arr >= left, arr < right)
        num_seve_per_dec[pos] = len(arr[cond])
        left = right
        pos += 1

    return num_seve_per_dec

def plot_distribution(distr: List) -> None:
    for pos, elem in enumerate(distr):
        plt.bar(pos,height=elem, width=1, align='edge')

    plt.xticks(np.arange(10),labels=np.arange(0,1,0.10).round(1))
    plt.xlabel("severity")
    plt.ylabel("#anomalies")
    plt.title("Anomalies distribution for severity")
    plt.savefig('distribution.jpg')
    plt.close()

@router.get('/api/send_file')
async def main():
    # headers = {"Content-Disposition": "attachment;",
    #            "filename": "google.pdf;"}
    headers = {}
    pdf = weasyprint.HTML('http://localhost:8001/create_report').write_pdf()
    open('report.pdf', 'wb').write(pdf)
    distr = extract_statistics(var.anomalies_sa)
    plot_distribution(distr)
    return FileResponse("report.pdf", headers=headers)


@router.get("/create_report", response_class=HTMLResponse)
async def read_item(request: Request):
    now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    google_logo = Image.open("distribution.jpg")
    # google_logo.show()
    data = io.BytesIO()
    google_logo.save(data, "JPEG")
    encoded_img_data = base64.b64encode(data.getvalue())
    return templates.TemplateResponse("report.html", {"request": request,
                                                      "now": now,
                                                      "anomalies_sa": var.anomalies_sa,
                                                      "anomalies_da": var.anomalies_sa,
                                                      "img_data": encoded_img_data.decode('utf-8')})
