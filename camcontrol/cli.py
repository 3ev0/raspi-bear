#!/usr/bin/env python
'''
Created on Oct 6, 2013

@author: ivo
'''
import argparse
import logging
import traceback
import signal
import sys

from camcontrol import config
from camcontrol import vlc_streaming

streamer = None
log = logging.getLogger()

def parse_args():
    argparser = argparse.ArgumentParser(description=config.program_descr)
    argparser.add_argument("--debug", "-d", action="store_true", help="enable debug output.")
    
    subparsers = argparser.add_subparsers(help="subcommand help", dest="subcmd")
    
    start_parser = subparsers.add_parser("start", help="start stream.")
    start_parser.add_argument("stream", help="which stream to control.")
    
    stop_parser = subparsers.add_parser("stop", help="stop stream.")
    stop_parser.add_argument("stream", help="which stream to control.")
        
    status_parser = subparsers.add_parser("status", help="Show stream status.")
    status_parser.add_argument("stream", help="which stream to control.")
    
    list_parser = subparsers.add_parser("list", help="Show available streams.")
    
    return argparser.parse_args()

def signal_handler(signum = None, frame = None):
    log.critical('Signal handler called with signal %s', signum)
    global streamer
    streamer.stop()
    log.critical("Cleanup done, bye!")
    sys.exit(0)

def init_logger(debug):
    logging.basicConfig(datefmt="%d%m%Y %H:%m:%S", format="%(asctime)s|%(name)s|%(levelname)s|%(message)s", level=logging.DEBUG if debug else logging.INFO)
    return

def main():
    args = parse_args()
    init_logger(args.debug)
    
    for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
        signal.signal(sig, signal_handler)
        
    log.info("CLI subcommand: {}".format(args.subcmd))
    try:        
        if args.subcmd == "start":            
            vlc_streaming.start(args.stream)
        elif args.subcmd == "stop":
            vlc_streaming.stop(args.stream)
        elif args.subcmd == "status":
            print(vlc_streaming.status(args.stream))
        elif args.subcmd == "list":
            streams = vlc_streaming.list()
            for stream in streams:
                print(stream)
        else:
            log.error("Unknown subcommand")
    except Exception as e:
        log.error(traceback.format_exc())
        
if __name__ == '__main__':
    main()