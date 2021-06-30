from fastapi import APIRouter

from src.types.Report import Report
import base64
from PIL import Image
import io

router = APIRouter()


@router.post('/api/base64')
def process_image(report: Report):
    for base64_img in report.plots:
        image = base64.b64decode(str(base64_img))
        img = Image.open(io.BytesIO(image))
    # for anomaly in report.rule.anomalies_same_action:
    #     print(f"Anomaly: {anomaly}")
    print(report.ruleString)
