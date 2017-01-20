from cStringIO import StringIO
import tempfile
import os


class StreamError(Exception):

    def __init__(self, message):
        self.message = message


class HandlerBase(object):
    """Interface for all handler objects."""

    TYPE = ''

    def handle(self, header, payload):
        raise NotImplementedError()


class SystemHandler(HandlerBase):
    TYPE = 'system'

    def handle(self, header, payload):
        print '\n-*- System Message -*-\n'
        print 'Header:  ', header
        print 'Paylaod: ', payload
        print '\n'


class ChunkedDataHandler(HandlerBase):
    """Messages can come in chunks, piece them together here."""
    tmp_handles = {}

    def handle(self, header, payload):
        if header.get('total_chunks', 1) > 1:
            # Open our tmp file and write to the location
            stream = self._get_stream(header['task_id'])
            stream.seek(header['chunk_size'] * (header['chunk'] - 1))
            stream.write(payload)
            if header['chunk'] == header['total_chunks']:
                # Message should be complete
                stream.seek(0)
                self.on_complete_message(header, stream)
                stream.close()
                # Remove the stream handle
                del self.tmp_handles[header['task_id']]

        else:
            self.on_complete_message(header, StringIO(payload))

    def _get_stream(self, id):
        if id not in self.tmp_handles:
            self.tmp_handles[id] = tempfile.TemporaryFile()
        return self.tmp_handles[id]

    def on_complete_message(self, header, payload):
        print '-*- message completed -*-'
        print header
        print payload.read()


class LogInHandler(ChunkedDataHandler):
    TYPE = 'log-in'


class DataHandler(ChunkedDataHandler):
    TYPE = 'data'


class FileDownloadHandler(ChunkedDataHandler):
    TYPE = 'download-file'

    def on_complete_message(self, header, stream):
        # Copy the contents from the tmp file to a new location
        filename = header.get('filename', header['task_id'])
        filename = os.path.join('files', filename)
        with open(filename, 'wb') as out:
            while True:
                data = stream.read(1024)
                if not data:
                    break
                out.write(data)


class RiCloudHandler(ChunkedDataHandler):
    TYPE = '__ALL__'

    def __init__(self, api=None, callback=None):
        self.api = api
        self.callback = callback

    def on_complete_message(self, header, stream):
        if header['type'] == 'system':
            message = stream.read()
            if "error" in message:
                raise StreamError(message)
        else:
            if self.callback:
                self.callback(header['task_id'], stream.read())
            elif self.api:
                self.api.set_task_result(header['task_id'], stream.read())
            else:
                raise
