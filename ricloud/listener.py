from __future__ import print_function

import json
import logging
import traceback

from .handlers import StreamError


logger = logging.getLogger(__name__)


class Listener(object):
    """Handle stream messagse here."""
    def __init__(self, handlers):
        self.handlers = handlers

    def on_heartbeat(self):
        logger.debug('-*- Heartbeat -*-')

    def on_message(self, header, data):
        header = json.loads(header)
        handler = self.handlers.get(header['type'], self.handlers.get('__ALL__', None))

        if not handler:
            logger.error('Unknown message type', header['type'])
            logger.error(header)
            logger.error(data)
        else:
            try:
                handler.handle(header, data)
            except StreamError as e:
                logger.error("StreamError: %s", e.message)
            except Exception as e:
                logger.critical("%s: %s", type(e), e.args)
                logger.critical(traceback.format_exc())
