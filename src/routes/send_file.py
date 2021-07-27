import numpy as np
import matplotlib.pyplot as plt
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from PIL import Image
import base64
import io
import weasyprint
from time import gmtime, strftime
from typing import List

from src.types.Report import Report

# path_str = path.dirname(path.realpath(__file__))
# print(path_str)

router = APIRouter()
templates = Jinja2Templates(directory="src/template")

PATH_TO_DISTR_DIR = "src/distributions"


def extract_statistics(anomalies_same_action: List) -> List:
    '''

    :param anomalies_same_action: List, of all anomalies whose action is equal to the action analyzed.
    :return: numpy.array[10]

    arr[i] contains the number of anomalies whose (i / 10) <= severity (i / 10) + 0.1
    This function is used as support function to plot the graph.
    '''
    # get the list of severities for each severity in the list of anomalies same action.
    severities = [anom['hellinger_distance'] for anom in anomalies_same_action]
    arr = np.asarray(severities)
    # num_seve_per_dec[i] contains the number of anomalies whose i <= severity < i + 0.1
    num_seve_per_dec = np.zeros(10)
    left = 0
    pos = 0
    space = np.arange(0.0, 1.0, 0.1)
    for dec in space:
        right = dec + 0.1
        cond = np.logical_and(arr >= left, arr < right)
        num_seve_per_dec[pos] = len(arr[cond])
        left = right
        pos += 1

    return num_seve_per_dec


def plot_distribution(distr: List, file_name: str, path: str) -> None:
    for pos, elem in enumerate(distr):
        plt.bar(pos, height=elem, width=1, align='edge')

    plt.xticks(np.arange(10), labels=np.arange(0, 1, 0.10).round(1))
    plt.xlabel("severity")
    plt.ylabel("#anomalies")
    plt.title("Anomalies distribution for severity")
    plt.savefig(f"{path}/{file_name}.jpg")
    plt.close()


def preprocess_rule_synthetized(rules: List) -> List[str]:
    '''
    example of usage:
    rules = preprocess_rule_synthethzied(report.rule.rule)
    :param rules:
    :return:
    '''
    # element 'i' correspondes to the rule synthetized of action 'i'
    rules_synthetetized = []
    # rule for action i
    print(rules)
    for rule in rules:
        rules_in_or = []
        for constraint in rule['constraints']:
            rule_str = ""
            for sub_rule_count, sub_rule in enumerate(constraint):
                if sub_rule_count > 0:
                    rule_str += " and "
                rule_str += sub_rule['state'] \
                            + " " + sub_rule['operator'] \
                            + " " + str(round(sub_rule['value'], 2))
            rules_in_or.append(rule_str)
        rules_synthetetized.append(rules_in_or)
    return rules_synthetetized


@router.post('/api/send_file')
async def main(request: Request, report: Report):
    # headers = {"Content-Disposition": "attachment;",
    #            "filename": "report.pdf;"}
    headers = {}
    # print(report)
    now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    rules_synthetized = preprocess_rule_synthetized(report.rule.rule)
    # plot and save the anomaly distribution per action
    for i in range(len(report.rule.actions)):
        distribution = extract_statistics(report.rule.anomalies_same_action[i]['anomalies'])
        plot_distribution(distribution, f"distribution_{i}", PATH_TO_DISTR_DIR)

    # list of base64 strings of the distributions images.
    distributions_images_encoded = []
    # list of Image ready to pass to the Jinja2 template
    distributions_images_decoded = []
    # add to the list the distribution image for each action.
    for i in range(len(report.rule.actions)):
        img = Image.open(f"{PATH_TO_DISTR_DIR}/distribution_{i}.jpg")
        data = io.BytesIO()
        img.save(data, "JPEG")
        distributions_images_encoded.append(base64.b64encode(data.getvalue()))
        distributions_images_decoded.append(distributions_images_encoded[i].decode('utf-8'))

    # list of base64 strings of the scatter bar plot coming with the request.
    anomalies_scatter_bar_plots_images_encoded = []
    # list of Image ready to be passed to the Jinja2 template
    anomalies_scatter_bar_plots_images_decoded = []
    for base64_img in report.plots:
        image = base64.b64decode(str(base64_img))
        anomalies_scatter_bar_plots_images_encoded.append(image)
        img = Image.open(io.BytesIO(image))

    template = templates.get_template("report.html")

    output = template.render(
        context={
            "request": request,
            "now": now,
            "actions": report.rule.actions,
            "rule_string": report.ruleString,
            "rules_synthetized": rules_synthetized,
            "anomalies_same_action": report.rule.anomalies_same_action,
            "anomalies_different_action": report.rule.anomalies_different_action,
            "distribution_plot": distributions_images_decoded,
            "anomalies_plot": anomalies_scatter_bar_plots_images_encoded
        })

    print(f"Output: {output}")
    pdf = weasyprint.HTML(string=output).write_pdf()
    open('report.pdf', 'wb').write(pdf)

    return FileResponse('report.pdf', media_type='application/pdf', filename="report.pdf", headers=headers)
