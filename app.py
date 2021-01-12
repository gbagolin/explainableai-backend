from flask import Flask
from flask import request, jsonify
from flask_cors import CORS

from src.xpomcp.RuleTemplate import RuleTemplate
from src.xpomcp.AtomicRule import AtomicRule
from src.xpomcp.Velocity_Regulation_Problem import Velocity_Regulation_Problem
from src.xpomcp.Tiger_Problem import Tiger_Problem
from src.xpomcp.State import State

import sys
import z3
import pdb

app = Flask(__name__)
CORS(app)

@app.route('/api',methods = ['POST'])
def synthetize_rule():
    data = request.json
    print(data)
    for atomic_rule in data:
        print(f'{var} : {data[var]}')
        
    return "ok"

@app.route("/", methods = ['POST'])
def helloWorld():
  return "Hello, cross-origin-world!"

if __name__ == '__main__':
    app.run(debug=True)