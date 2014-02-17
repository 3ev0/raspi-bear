import argparse
import logging
import traceback
import signal
import sys

from . import audioplay_pygame
from . import globals
from . import REST_interface

log = logging.getLogger(__name__)
audioplayer = None

def main():    
    global audioplayer
    args = parse_args()
    
    globals.init_config()
    globals.init_logging(args.debug)
    
    audioplayer = audioplay_pygame.AudioPlayer()
    for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
        signal.signal(sig, signal_handler)
    
    try:
        start_REST_player()
    except Exception as e:
        log.error(traceback.format_exc())
        

def parse_args():
    argparser = argparse.ArgumentParser(description="Jukebox! The python REST-based audio player")
    argparser.add_argument("--debug", "-d", action="store_true", help="enable debug output.")
    return argparser.parse_args()

def start_REST_player():
    REST_interface.run(audioplayer)

def signal_handler(signum = None, frame = None):
    log.critical('Signal handler called with signal %s', signum)
    audioplayer.stop()
    log.critical("Cleanup done, bye!")
    sys.exit(0)

if __name__ == '__main__':
    main()
    