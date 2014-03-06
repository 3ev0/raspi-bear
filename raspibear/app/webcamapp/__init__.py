import logging
import os.path
import json
import flask

from raspibear import webcam

log = logging.getLogger()

apibp = flask.Blueprint("webcam_api", __name__)
bp = flask.Blueprint("webcam", __name__, static_folder="static", template_folder="templates")

@bp.route("/")
def show():
    return flask.render_template("webcam.html", title="Teddycam!", page_id="webcam", status_interval=5000)

@apibp.route("/")
def index():
    pass

@apibp.route("/settings/<setting>", method="GET")
def getSetting(setting):
    with webcam.applock:
        return json.dumps(webcam.config[setting])

@apibp.route("/settings/<setting>", method="PUT")
def setSetting(setting):
    value = json.loads(flask.request.form[setting])
    with webcam.applock:
        return json.dumps(webcam.set(setting=value))

@apibp.route("/switchpower/<value>", method="GET")
def switchPower(value):
    with webcam.applock:
        if value == "off":
            res = webcam.stop()        
        elif value == "on":
            res = webcam.start()
        else:
            flask.abort(404)
        return json.dumps("on" if res else "off")

@apibp.route("/status")
def status():
    with webcam.applock:
        return json.dumps(webcam.getStatus())
        