from __future__ import absolute_import, unicode_literals

from . import abase


class Poll(abase.CreatableResource, abase.ListableResource):
    RESOURCE = "poll"
    RESOURCE_PATH = "polls"
