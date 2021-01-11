from sanic import Sanic
from sanic.response import json
from sanic import response
from sanic_cors import CORS, cross_origin

app = Sanic("server")
CORS(app)

@app.route("/api", methods=["POST"])
def post_json(request):
    return json({ "received": "true", "message": request.json})

# @app.route('/api')
# def handle_request(request):
#     return response.text('Hello world!')

if __name__ == "__main__":
    app.run(host="localhost", port=8000)
