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
    return flask.render_template("webcam.html", title="Teddycam!", page_id="webcam", status_interval=30000, server=flask.request.host)

@apibp.route("/")
def index():
    pass

@apibp.route("/settings/<setting>", methods=["GET"])
def getSetting(setting):
    with webcam.applock:
        return json.dumps(webcam.config[setting])

@apibp.route("/settings/<setting>", methods=["PUT"])
def configure(setting):
    value = flask.request.form[setting]
    with webcam.applock:
        retval = json.dumps(webcam.configure(**{setting:value}))
        webcam.restart()
        return retval

@apibp.route("/switchpower/<value>", methods=["GET"])
def switchPower(value):
    with webcam.applock:
        if value == "false":    
            return json.dumps(webcam.stop())        
        elif value == "true":
            return json.dumps(webcam.start())
        else:
            flask.abort(404)
            
@apibp.route("/status")
def status():
    with webcam.applock:
        return json.dumps(webcam.getStatus())
        