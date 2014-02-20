'''
Created on Oct 6, 2013

@author: ivo
'''

import logging
import os.path
import json

import globals

log = logging.getLogger()

@bottle.get("/status")
@bottle.get("/")
def handle_status():
    log.info("Received 'status' command")
    form_response()
    return json.dumps(audioplayer.get_status())

@bottle.get("/start")
def handle_start():
    log.info("Received 'start' command")
    form_response()
    return json.dumps(audioplayer.start())

@bottle.get("/stop")
def handle_stop():
    log.info("Received 'stop' command")
    form_response()
    return json.dumps(audioplayer.stop())

        