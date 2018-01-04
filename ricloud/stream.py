import time
import logging
import requests

from requests.packages import urllib3


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
                logger.error('Connection failed unexpectedly with error.', exc_info=True)

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
                header = buf.read(length)
                length = int(buf.readline().strip())
                body = buf.read(length - 2)

                self.listener.on_message(header, body)

                buf.readline()  # Always have a final carriage return at the end of a message.

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
