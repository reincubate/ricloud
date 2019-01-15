from __future__ import absolute_import, unicode_literals

from . import abase


class Session(abase.CreatableResource, abase.ListableResource, abase.DeletableResource):
    RESOURCE = "session"
    RESOURCE_PATH = "sessions"
