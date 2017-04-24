from __future__ import print_function

import sys
import json
import logging
import traceback

from .handlers import StreamError


class Listener(object):
    """Handle stream messagse here."""
    def __init__(self, handlers):
        self.handlers = handlers

    def on_heartbeat(self):
        logging.debug('-*- Heartbeat -*-')

    def on_message(self, header, data):
        header = json.loads(header)
        handler = self.handlers.get(header['type'], self.handlers.get('__ALL__', None))

        if not handler:
            logging.error('Unknown message type', header['type'])
            logging.error(header)
            logging.error(data)
        else:
            try:
                handler.handle(header, data)
            except StreamError as e:
                logging.error("StreamError: %s", e.message)
            except Exception as e:
                logging.critical("%s: %s", type(e), e.args)
                logging.critical(traceback.format_exc())
