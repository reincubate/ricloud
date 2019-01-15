from __future__ import absolute_import, unicode_literals

from . import abase


class Result(abase.ListableResource):
    RESOURCE = "result"
    RESOURCE_PATH = "results"

    @classmethod
    def acknowledge_with_id(cls, id):
        resource = cls(id=id)
        resource.acknowledge()
        return resource

    def acknowledge(self):
        url = self.instance_url + "/ack"
        response = self.request_handler.get(url)
        self.attrs.update(response)
