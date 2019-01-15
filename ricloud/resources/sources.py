from __future__ import absolute_import, unicode_literals

from . import abase


class Source(abase.CreatableResource, abase.ListableResource, abase.UpdatableResource):
    RESOURCE = "source"
    RESOURCE_PATH = "sources"
