import time
import logging
import requests

from requests.packages import urllib3

from .helpers import LogHelper


logger = logging.getLogger(__name__)


class Stream(object):
    def __init__(self, endpoint, listener, stream, token):
        self.endpoint = endpoint
        self.stream = stream
        self.token = token
        self.listener = listener

        self.streaming = False
        self.retry_count = 0

    def go(self):
        while True:
            try:
                self._go(self.endpoint)
            except (requests.exceptions.ConnectionError, urllib3.exceptions.ProtocolError):
                logger.error(LogHelper.get_message('stream_error'), exc_info=True)
            except:  # noqa: E722 want to log any error that occurs properly.
                logger.error(LogHelper.get_message('stream_error'), exc_info=True)
                break

            self._retry_wait()

    def _go(self, url):
        response = requests.get(
            url,
            {'stream': self.stream},
            stream=True,
            headers={
                'Authorization': 'Token %s' % self.token
            }
        )

        self._process_initial_response(response)
        self._consume(response)

    def _consume(self, response):
        buf = response.raw

        while not buf.closed:
            line = buf.readline().strip()

            if not line:
                self.listener.on_heartbeat()
            elif line.isdigit():
                length = int(line)
                header = buf.read(length).strip()  # Header is always json formatted, safe to strip.

                length = int(buf.readline().strip())
                body = buf.read(length - 2)  # Read body until the `\r\n` end marker.

                self.listener.on_message(header, body)

                buf.read(2)  # Discard the `\r\n` end marker here

        logger.warn('Connection closed, final message: %s', buf.read())

    def _process_initial_response(self, response):
        response.raise_for_status()

        logger.debug('Stream connection established.')
        self.streaming = True
        self.retry_count = 0

    def _retry_wait(self):
        self.retry_count += 1
        retry_wait = min(max((self.retry_count - 2), 0) ** 2, 60)  # Increase quadratically to a maximum of 60s.

        logger.warn('Attempting reconnect number %d in %d seconds.', self.retry_count, retry_wait)

        time.sleep(retry_wait)
