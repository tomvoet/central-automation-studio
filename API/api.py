# API Proxy v1.2
# Updated: 2022/03/20
# Aaron Scott (WiFi Downunder) 2022
# ------------------------------------------------------------------------------------------
# Convert JS based API calls into Python calls (to work around CORS) and return the results
# ------------------------------------------------------------------------------------------


from flask import Flask, jsonify, request, json, render_template, g
from flask_cors import CORS, cross_origin
from datetime import datetime
import flask
import logging
import requests
import binascii
import os

from logging.handlers import RotatingFileHandler

app = Flask(__name__)

# cors = CORS(app, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], supports_credentials=True,
#          expose_headers='Authorization', allow_headers=['Accept', 'Authorization', 'Cache-Control', 'Content-Type', 'DNT', 'If-Modified-Since', 'Keep-Alive', 'Origin', 'User-Agent', 'X-Requested-With'])

# allow all
cors = CORS(app, resources={r"/*": {"origins": "*"}})


def create_timed_rotating_log(path):
    app.logger = logging.getLogger('werkzeug')
    # creates handler for the log file
    handler = RotatingFileHandler(path, maxBytes=1024, backupCount=5)
    # controls the priority of the messages that are logged
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)  # adds handler to the logger


# creates this file at the specified path
log_file = "/central/API/timed_test.log"
create_timed_rotating_log(log_file)


@app.route('/auth/refresh', methods=["POST"])
def tokenRefresh():
    data = request.get_json()
    url = data['base_url'] + "/oauth2/token"
    payload = json.dumps({
        "client_id": data['client_id'],
        "client_secret": data['client_secret'],
        "grant_type": "refresh_token",
        "refresh_token": data['refresh_token']
    })
    headers = {
        'Authorization': 'Bearer ' + data['access_token'],
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    try:
        result = jsonify(json.loads(response.text))
        # ...
    except ValueError:
        # no JSON returned
        result = jsonify(status=str(response.status_code),
                         reason=response.reason)
    return result


@app.route('/auth/refreshwHeaders', methods=["POST"])
def tokenRefreshwHeaders():
    data = request.get_json()
    url = data['base_url'] + "/oauth2/token"
    payload = json.dumps({
        "client_id": data['client_id'],
        "client_secret": data['client_secret'],
        "grant_type": "refresh_token",
        "refresh_token": data['refresh_token']
    })
    headers = {
        'Authorization': 'Bearer ' + data['access_token'],
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    headers_json = json.dumps(dict(response.headers))
    try:
        result = jsonify(responseBody=str(response.text), status=str(
            response.status_code), headers=headers_json)
    except ValueError:
        # no JSON returned
        result = jsonify(status=str(response.status_code),
                         reason=response.reason)
    return result


@app.route('/tools/getCommand', methods=["POST"])
def getCommand():
    data = request.get_json()
    url = data['url']
    if 'tenantID' in data:
        headers = {
            'cache-control': "no-cache",
            'Authorization': 'Bearer ' + data['access_token'],
            'Content-Type': 'application/json',
            'TenantID': data['tenantID']
        }
    else:
        headers = {
            'cache-control': "no-cache",
            'Authorization': 'Bearer ' + data['access_token'],
            'Content-Type': 'application/json'
        }

    response = requests.request("GET", url, headers=headers)
    # print(response.text)
    # print(response);
    try:
        result = jsonify(json.loads(response.text))
        # ...
    except ValueError:
        # no JSON returned
        result = jsonify(status=str(response.status_code),
                         reason=response.reason, responseBody=str(response.text))
    return result


@app.route('/tools/getCommandwHeaders', methods=["POST"])
def getCommandwHeaders():
    data = request.get_json()
    url = data['url']
    if 'tenantID' in data:
        headers = {
            'cache-control': "no-cache",
            'Authorization': 'Bearer ' + data['access_token'],
            'Content-Type': 'application/json',
            'TenantID': data['tenantID']
        }
    else:
        headers = {
            'cache-control': "no-cache",
            'Authorization': 'Bearer ' + data['access_token'],
            'Content-Type': 'application/json'
        }

    response = requests.request("GET", url, headers=headers)
    headers_json = json.dumps(dict(response.headers))
    try:
        result = jsonify(responseBody=str(response.text), status=str(
            response.status_code), headers=headers_json)
        # ...
    except ValueError:
        # no JSON returned
        result = jsonify(responseBody=str(response.text), status=str(
            response.status_code), reason=response.reason)
    return result


@app.route('/tools/postCommand', methods=["POST"])
def postCommand():
    data = request.get_json()
    url = data['url']

    if 'tenantID' in data:
        headers = {
            'cache-control': "no-cache",
            'Authorization': 'Bearer ' + data['access_token'],
            'Content-Type': 'application/json',
            'TenantID': data['tenantID']
        }
    else:
        headers = {
            'cache-control': "no-cache",
            'Authorization': 'Bearer ' + data['access_token'],
            'Content-Type': 'application/json'
        }

    if 'data' in data:
        payload = data['data']
        response = requests.request("POST", url, headers=headers, data=payload)
    else:
        response = requests.request("POST", url, headers=headers)

    # app.logger.debug(response.text)

    try:
        result = jsonify(json.loads(response.text))
        # ...
    except ValueError:
        # no JSON returned
        app.logger.debug("No JSON")
        result = jsonify(status=str(response.status_code),
                         reason=response.reason)
    return result


@app.route('/tools/postFormDataCommand', methods=["POST"])
def postFormDataCommand():
    data = request.get_json()
    url = data['url']

    if 'tenantID' in data:
        headers = {
            'cache-control': "no-cache",
            'Authorization': 'Bearer ' + data['access_token'],
            "Accept": "*/*",
            'TenantID': data['tenantID']
        }
    else:
        headers = {
            'cache-control': "no-cache",
            'Authorization': 'Bearer ' + data['access_token'],
            "Accept": "*/*"
        }

    if 'template' in data:
        payload = data['template']
        files = {'template': ('template.txt', payload)}
        response = requests.request("POST", url, headers=headers, files=files)
    elif 'variables' in data:
        payload = data['variables']
        files = {'variables': ('variables.txt', payload)}
        response = requests.request("POST", url, headers=headers, files=files)
    else:
        response = requests.request("POST", url, headers=headers)

    # app.logger.debug(response.text)

    try:
        result = jsonify(json.loads(response.text))
        # ...
    except ValueError:
        # no JSON returned
        app.logger.debug("No JSON")
        result = jsonify(status=str(response.status_code),
                         reason=response.reason)
    return result


@app.route('/tools/putCommand', methods=["POST"])
def putCommand():
    data = request.get_json()
    url = data['url']
    payload = data['data']

    if 'tenantID' in data:
        headers = {
            'cache-control': "no-cache",
            'Authorization': 'Bearer ' + data['access_token'],
            'Content-Type': 'application/json',
            'TenantID': data['tenantID']
        }
    else:
        headers = {
            'cache-control': "no-cache",
            'Authorization': 'Bearer ' + data['access_token'],
            'Content-Type': 'application/json'
        }

    response = requests.request("PUT", url, data=payload, headers=headers)

    app.logger.debug(response.text)
    try:
        result = jsonify(json.loads(response.text))
        # ...
    except ValueError:
        # no JSON returned
        result = jsonify(status=str(response.status_code),
                         reason=response.reason)
    return result


@app.route('/tools/patchFormDataCommand', methods=["POST"])
def patchFormDataCommand():
    data = request.get_json()
    url = data['url']

    if 'tenantID' in data:
        headers = {
            'cache-control': "no-cache",
            'Authorization': 'Bearer ' + data['access_token'],
            "Accept": "*/*",
            'TenantID': data['tenantID']
        }
    else:
        headers = {
            'cache-control': "no-cache",
            'Authorization': 'Bearer ' + data['access_token'],
            "Accept": "*/*"
        }

    if 'template' in data:
        payload = data['template']
        files = {'template': ('template.txt', payload)}
        response = requests.request("PATCH", url, headers=headers, files=files)
    elif 'variables' in data:
        payload = data['variables']
        files = {'variables': ('variables.txt', payload)}
        response = requests.request("PATCH", url, headers=headers, files=files)
    else:
        response = requests.request("PATCH", url, headers=headers)

    # app.logger.debug(response.text)

    try:
        result = jsonify(json.loads(response.text))
        # ...
    except ValueError:
        # no JSON returned
        app.logger.debug("No JSON")
        result = jsonify(status=str(response.status_code),
                         reason=response.reason)
    return result


@app.route('/tools/patchCommand', methods=["POST"])
def patchCommand():
    data = request.get_json()
    url = data['url']
    payload = data['data']

    if 'tenantID' in data:
        headers = {
            'cache-control': "no-cache",
            'Authorization': 'Bearer ' + data['access_token'],
            'Content-Type': 'application/json',
            'TenantID': data['tenantID']
        }
    else:
        headers = {
            'cache-control': "no-cache",
            'Authorization': 'Bearer ' + data['access_token'],
            'Content-Type': 'application/json'
        }

    response = requests.request("PATCH", url, data=payload, headers=headers)

    app.logger.debug(response.text)
    try:
        result = jsonify(json.loads(response.text))
        # ...
    except ValueError:
        # no JSON returned
        result = jsonify(status=str(response.status_code),
                         reason=response.reason)
    return result


@app.route('/tools/deleteCommand', methods=["POST"])
def deleteCommand():
    data = request.get_json()
    url = data['url']

    if 'tenantID' in data:
        headers = {
            'cache-control': "no-cache",
            'Authorization': 'Bearer ' + data['access_token'],
            'Content-Type': 'application/json',
            'TenantID': data['tenantID']
        }
    else:
        headers = {
            'cache-control': "no-cache",
            'Authorization': 'Bearer ' + data['access_token'],
            'Content-Type': 'application/json'
        }

    if "data" in data:
        payload = data['data']
        response = requests.request(
            "DELETE", url, data=payload, headers=headers)
    else:
        response = requests.request("DELETE", url, headers=headers)

    app.logger.debug(response.status_code)
    try:
        result = jsonify(json.loads(response.text)), response.status_code
    except ValueError:
        # no JSON returned
        result = jsonify(status=str(response.status_code),
                         reason=response.reason), response.status_code
    return result


def change_vlan(client_mac, vlan, api_base, access_token):
    print(client_mac)

    response = requests.patch(api_base + "/api/endpoint/mac-address/" + client_mac, headers={
        "Authorization": "Bearer " + access_token, "Content-Type": "application/json"}, json={"attributes": {"vlan": vlan}})

    if response.status_code < 300:
        print("VLAN changed")
        return True
    else:
        print("VLAN change failed: " +
              str(response.status_code) + " " + response.text)
        Exception("VLAN change failed")
        return False


def get_session_id(client_mac, api_base, access_token):
    request = requests.get(api_base + "/api/session", headers={
        'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'})
    if request.status_code < 300:
        sessionData = request.json()

        sessions = sessionData['_embedded']['items']

        for session in sessions:
            if session['callingstationid'] == client_mac and session['acctstoptime'] is None:
                return session['id']
        return None
    else:
        print("Error getting session ID: " + str(request.status_code))
        return None


def reauthorize_session(session_id, api_base, access_token):
    request = requests.post(api_base + "/api/session/" + session_id + "/reauthorize",
                            headers={
                                'Authorization': 'Bearer ' + access_token,
                                'Content-Type': 'application/json'
                            },
                            json={
                                "confirm_reauthorize": True,
                                "reauthorize_profile": "[AOS-CX - Bounce Switch Port]"
                            }
                            )

    if request.status_code < 300:
        return True
    else:
        print("Error reauthorizing session: " +
              str(request.status_code) + " " + request.text)
        return False


@app.route("/set_vlan", methods=["POST"])
def set_vlan():
    data = request.get_json()
    api_base = data['api_base']
    access_token = data['access_token']
    client_mac = data['client_mac']
    vlan = data['vlan']

    try:
        vlan_success = change_vlan(client_mac, vlan, api_base, access_token)
        if vlan_success:
            session_id = get_session_id(client_mac, api_base, access_token)
            if session_id is not None:
                reauth_success = reauthorize_session(
                    session_id, api_base, access_token)
                if reauth_success:
                    return "VLAN changed and session reauthorized"
                else:
                    return "VLAN changed, but session reauthorization failed"
            else:
                return "VLAN changed, but session could not be found"
        else:
            return "VLAN change failed"
    except Exception as e:
        return "Error: " + str(e)


@app.route("/")
def hello():
    return render_template('index.html')


@app.route("/reachable")
def reachable():
    return flask.request.url_root


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
