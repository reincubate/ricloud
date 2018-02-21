import os
import logging

from cStringIO import StringIO

from .helpers import TemporaryFileHandler


logger = logging.getLogger(__name__)


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
        logger.info('-*- System Message -*-')
        logger.info('Header:  %s', header)
        logger.info('Paylaod: %s', payload)


class ChunkedDataHandler(HandlerBase):
    """Messages can come in chunks, piece them together here."""
    temporary_files = TemporaryFileHandler()

    def handle(self, header, payload):
        if header.get('total_chunks', 1) > 1:
            stream = self.temporary_files.get(header['task_id'])  # Get a tmp handle.
            stream.seek(header['chunk_size'] * (header['chunk'] - 1))  # Write to chunk's position.
            stream.write(payload)

            if header['chunk'] == header['total_chunks']:  # Message should be complete.
                stream.seek(0)
                self.on_complete_message(header, stream)
                stream.close()

                self.temporary_files.delete(header['task_id'])  # Remove the stream handle.

        else:
            self.on_complete_message(header, StringIO(payload))

    def on_complete_message(self, header, stream):
        logger.info('-*- message completed -*-')
        logger.info(header)
        logger.info(stream.read())


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
