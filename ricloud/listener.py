from __future__ import print_function

import json
import sys

from .handlers import StreamError


class Listener(object):
    """Handle stream messagse here."""
    def __init__(self, handlers, log):
        self.log = log
        self.handlers = handlers

    def _log(self, message, *args):
        if self.log is None:
            print(message, args, file=sys.stdout)
        else:
            self.log.write(message, *args)

    def _error(self, message, *args):
        if self.log is None:
            print(message, args, file=sys.stdout)
        else:
            self.log.error(message, *args)

    def on_heartbeat(self):
        self._log('-*- Heartbeat -*-')

    def on_message(self, header, data):
        header = json.loads(header)
        handler = self.handlers.get(header['type'], self.handlers.get('__ALL__', None))

        if not handler:
            self._log('Unknown message type', header['type'])
            self._log(header)
            self._log(data)
        else:
            try:
                handler.handle(header, data)
            except StreamError as e:
                self._error(e.message)
