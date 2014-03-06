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

@apibp.route("/settings/<setting>/<value>")
def setting(setting, value):
    return json.dumps(webcam.set(setting=value))

@apibp.route("/switchpower/<value>")
def switchPower(value):
    if value == "off":
        res = webcam.stop()        
    elif value == "on":
        res = webcam.start()
    else:
        flask.abort(404)
    return json.dumps("on" if res else "off")

@apibp.route("/status")
def status():
    return json.dumps(webcam.getStatus())
        