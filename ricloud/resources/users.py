from __future__ import absolute_import, unicode_literals

from . import abase


class User(abase.CreatableResource, abase.ListableResource, abase.UpdatableResource):
    RESOURCE = "user"
    RESOURCE_PATH = "users"
