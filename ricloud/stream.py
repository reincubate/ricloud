import requests


class Stream(object):
    def __init__(self, host, url, listener, stream, token, protocol='https'):
        self.protocol = protocol
        self.host = host
        self.url = url
        self.stream = stream
        self.token = token
        self.listener = listener

        self.streaming = False

    def go(self):
        url = '%s://%s%s' % (self.protocol, self.host, self.url)

        response = requests.get(
            url,
            {'stream': self.stream},
            stream=True,
            headers={
                'Authorization': 'Token %s' % self.token
            }
        )

        if not response.ok:
            print 'Something went wrong!'
            print 'Status:', response.status_code
            print response.content
            return

        self.streaming = True
        self._consume(response)

    def _consume(self, resp):
        buf = resp.raw

        while not resp.raw.closed:
            line = buf.readline().strip()

            if not line:
                self.listener.on_heartbeat()
            elif line.isdigit():
                length = int(line)
                header = buf.read(length)
                length = int(buf.readline().strip())
                body = buf.read(length - 2)
                self.listener.on_message(header, body)

        print 'Connection closed.'
        print resp.raw.read()
