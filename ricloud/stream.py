import time
import logging
import requests

from requests.packages import urllib3


class Stream(object):
    def __init__(self, host, url, listener, stream, token, protocol='https'):
        self.protocol = protocol
        self.host = host
        self.url = url
        self.stream = stream
        self.token = token
        self.listener = listener

        self.streaming = False
        self.retry_count = 0

    def go(self):
        url = '%s://%s%s' % (self.protocol, self.host, self.url)

        while True:
            try:
                self._go(url)
            except (requests.exceptions.ConnectionError, urllib3.exceptions.ProtocolError):
                logging.error('Connection failed unexpectedly with error.', exc_info=True)

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

        logging.warn('Connection closed, final message: %s', buf.read())

    def _process_initial_response(self, response):
        response.raise_for_status()

        logging.debug('Stream connection established.')
        self.streaming = True
        self.retry_count = 0

    def _retry_wait(self):
        self.retry_count += 1
        retry_wait = min(max((self.retry_count - 2), 0) ** 2, 60)  # Increase quadratically to a maximum of 60s.

        logging.warning('Attempting reconnect number %d in %d seconds.', self.retry_count, retry_wait)

        time.sleep(retry_wait)
