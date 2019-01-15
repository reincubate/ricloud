from __future__ import absolute_import, unicode_literals

from . import abase


class Permissions(
    abase.CreatableResource, abase.ListableResource, abase.UpdatableResource
):
    RESOURCE = "permissions"
    RESOURCE_PATH = "permissions"
