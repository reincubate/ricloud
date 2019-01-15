from __future__ import absolute_import, unicode_literals

from . import abase


class Key(abase.CreatableResource, abase.ListableResource, abase.UpdatableResource):
    RESOURCE = "key"
    RESOURCE_PATH = "keys"

    @classmethod
    def rotate_with_id(cls, id, **data):
        resource = cls(id=id)
        resource.rotate(**data)
        return resource

    def rotate(self, **data):
        url = self.instance_url + "/rotate"
        response = self.request_handler.post(url, data=data)
        self.attrs.update(response)
