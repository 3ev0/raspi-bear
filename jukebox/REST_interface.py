import logging
import os.path
import json

from . import globals

log = logging.getLogger(__name__)

audioplayer = None
    
def form_response():
    bottle.response.set_header('Access-Control-Allow-Origin', '*')
    return
    
@bottle.error(code=404)
def handle_error404(error):
    log.error("Page not found by Bottle")
    form_response()
    return "Page not found by Bottle"

@bottle.error(code=500)
def handle_error(error):
    log.error("Bottle caught exception: %s", str(error.exception))
    form_response()
    return str(error.exception)

@bottle.get("/status")
@bottle.get("/")
def handle_status():
    log.info("Received 'status' command")
    form_response()
    return json.dumps(audioplayer.get_status())

@bottle.get("/mute")
def handle_mute():
    log.info("Received 'mute' command")
    form_response()
    return json.dumps(audioplayer.mute_toggle())
    
@bottle.get("/skip2end")
def handle_skip2end():
    log.info("Received 'skip2end' command")
    form_response()
    return json.dumps(audioplayer.skip2end())

@bottle.get("/skip2start")
def handle_skip2start():
    log.info("Received 'skip2start' command")
    form_response()
    return json.dumps(audioplayer.skip2start())

@bottle.get("/stop")
def handle_stop():
    log.info("Received 'stop' command")
    form_response()
    return json.dumps(audioplayer.stop())
    
@bottle.get("/volup")
def handle_volup():
    log.info("Received 'volup' command")
    form_response()
    return json.dumps(audioplayer.increase_volume())

@bottle.get("/voldown")
def handle_voldown():
    log.info("Received 'voldown' command")
    form_response()
    return json.dumps(audioplayer.decrease_volume())

@bottle.get("/setvol/<value:int>")
def handle_setvol(value):
    log.info("Received 'setvol' command with value %s", value)
    form_response()
    return json.dumps(audioplayer.set_volume(value))
        
@bottle.get("/pause")
def handle_pause():
    log.info("Received 'pause' command")
    form_response()
    return json.dumps(audioplayer.pause_toggle())
    
@bottle.get("/play")    
def handle_play():
    log.info("Received 'play' command")
    form_response()
    return json.dumps(audioplayer.play())
    
@bottle.get("/play/<value:path>")    
def handle_play(value):
    form_response()
    if os.path.isfile(value):
        log.info("Received 'play' command with file path %s", value)
        return json.dumps(audioplayer.play([value]))
    elif os.path.isdir(value):
        log.info("Received 'play' command with dir path %s", value)
        fpaths = [os.path.join(value, fp) for fp in os.listdir(value) if (os.path.splitext(fp)[1][1:] in globals.supp_exts)]
        return json.dumps(audioplayer.play(fpaths))
    else:
        raise Exception("{} is not a valid path".format(value))
    
        