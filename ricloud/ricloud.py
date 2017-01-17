"""Base module for `ricloud`."""
from __future__ import absolute_import, unicode_literals

import threading
from cached_property import cached_property

from .conf import settings
from .api import Api
from .stream import Stream
from .object_store import ObjectStore
from .listener import Listener
from .handlers import RiCloudHandler


class RiCloud(object):
    """Primary class for dealing with the ricloud API/"""

    def __init__(self, log=None):
        self.log = log
        self.api.setup()
        self.services = self.api.allowed_services()
        if self.api.retrieval_protocol == "asstore":
            self.object_store_thread.start()
        else:
            self.stream_thread.start()

    @cached_property
    def api(self):
        api_client = Api()
        return api_client

    @cached_property
    def listener(self):
        listener = Listener(
            {'__ALL__': RiCloudHandler(api=self.api)},
            log=self.log
        )
        return listener

    @cached_property
    def stream_thread(self):
        stream = settings.get('stream', 'stream_endpoint')
        token = settings.get('auth', 'token')

        def _start():
            s = Stream(
                host=self.api.stream_endpoints[0]['host'],
                url=self.api.stream_endpoints[0]['uri'],
                listener=self.listener,
                stream=stream,
                token=token,
                protocol=self.api.stream_endpoints[0]['protocol']
            )
            s.go()

        stream_thread = threading.Thread(target=_start)
        stream_thread.daemon = True
        return stream_thread

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
