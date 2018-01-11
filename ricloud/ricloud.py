"""Base module for `ricloud`."""
from __future__ import absolute_import, unicode_literals

import logging
import threading
from cached_property import cached_property

from .conf import settings
from .api import Api
from .stream import Stream
from .object_store import ObjectStore
from .listener import Listener
from .handlers import RiCloudHandler
from .helpers import LogHelper


logger = logging.getLogger(__name__)


class RiCloud(object):
    """Primary class for dealing with the ricloud API/"""

    def __init__(self, api=None, listener=None):
        self.api = api or Api()
        self.api.setup()

        self.listener = listener or Listener({'__ALL__': RiCloudHandler(api=self.api)})

        self.services = self.api.allowed_services()

        if self.api.retrieval_protocol == "asstore":
            self.object_store_thread.start()
        else:
            self.stream_thread.start()

    _stream_thread = None

    @property
    def stream_thread(self):
        if not self._stream_thread:
            self._stream_thread = self._start_stream_thread()
        return self._stream_thread

    def _start_stream_thread(self):
        logger.info(LogHelper.get_message('stream_start'))
        stream = settings.get('stream', 'stream_endpoint')
        token = settings.get('auth', 'token')

        def _start():
            s = Stream(
                endpoint=self.api.stream_endpoints[0],
                listener=self.listener,
                stream=stream,
                token=token
            )
            s.go()

        stream_thread = threading.Thread(target=_start)
        stream_thread.daemon = True

        return stream_thread

    def _restart_stream_thread(self):
        logger.warn(LogHelper.get_message('stream_restart'))
        self._stream_thread = None
        self.stream_thread.start()

    def _check_stream_thread(self):
        if not self.stream_thread.is_alive():
            logger.warn(LogHelper.get_message('stream_failed_check'))
            self._restart_stream_thread()

    @cached_property
    def object_store_thread(self):

        def _start():
            s = ObjectStore(
                api=self.api
            )
            s.go()
        object_store_thread = threading.Thread(target=_start)
        object_store_thread.daemon = True
        return object_store_thread
