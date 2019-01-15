from __future__ import absolute_import, unicode_literals

from . import abase


class Event(abase.ListableResource):
    RESOURCE = "event"
    RESOURCE_PATH = "events"
