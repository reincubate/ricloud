from __future__ import absolute_import, unicode_literals

from . import abase


class Organisation(abase.UpdatableResource):
    RESOURCE = "organisation"
    RESOURCE_PATH = "organisation"

    @property
    def instance_url(self):
        return self.resource_url()

    @classmethod
    def retrieve(cls):
        resource = cls()
        resource.refresh()
        return resource
