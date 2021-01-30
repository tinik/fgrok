from urllib.parse import urlparse

import json
import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


def uri_validator(value):
    try:
        result = urlparse(value)
        return all([result.scheme, result.netloc])
    except:
        return False


def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


def _prepare_headers():
    excludes = {'Host', 'Content-Length'}

    values = dict(request.headers)
    params = values.keys() - excludes
    return {key: values[key] for key in params}


@app.after_request
def response_processor(response):
    header = response.headers
    header['access-control-allow-origin'] = '*'

    return response


@app.route('/', methods=['GET', 'POST', 'OPTIONS'])
@app.route('/<path:link>', methods=['GET', 'POST', 'OPTIONS'])
def main(link=None):
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()

    hostname = app.config['HOSTNAME']
    headers = _prepare_headers()
    response = requests.request(request.method, f"{hostname}/{link}", headers=headers, params=request.args, data=request.data)

    data = json.loads(response.text)
    return jsonify(data)


if __name__ == '__main__':
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path, override=True)

    hostname = os.environ.get('HOSTNAME')
    if not hostname:
        raise Exception('Sorry, HOSTNAME not assign in ENV, support .env files')

    if not uri_validator(hostname):
        raise Exception('Sorry, not validate link, ex: https://example.com')

    app.config['HOSTNAME'] = hostname
    app.run(debug=True)
