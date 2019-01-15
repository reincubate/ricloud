from __future__ import absolute_import, unicode_literals

from collections import OrderedDict

import ricloud
from ricloud.compat import MutableMapping, MutableSequence
from ricloud.requests import RequestHandler
from ricloud.utils import encode_json, join_url


class ABResource(MutableMapping):

    request_handler = RequestHandler()

    def __init__(self, id=None, attrs=None):
        # Need to setup using object method to avoid circular deps on init.
        object.__setattr__(self, "attrs", attrs or OrderedDict())

        if id:
            self.attrs["id"] = id

    def __repr__(self):
        return "{name}(id='{id}', json_attrs={json_attrs})".format(
            name=self.__class__.__name__,
            id=self.attrs.get("id"),
            json_attrs=encode_json(self.attrs, indent=2),
        )

    def __getitem__(self, key):
        return self.attrs[key]

    def __setitem__(self, key, value):
        self.attrs[key] = value

    def __delitem__(self, key):
        del self.attrs[key]

    def __iter__(self):
        return iter(self.attrs)

    def __len__(self):
        return len(self.attrs)

    def __getattr__(self, name):
        try:
            return self.__dict__["attrs"][name]
        except KeyError:
            raise AttributeError("Unknown attribute: %s" % name)

    def __setattr__(self, name, value):
        if name in self.__dict__:
            return super(ABResource, self).__setattr__(name, value)

        self.attrs[name] = value

    def __delattr__(self, name):
        if name in self.__dict__:
            return super(ABResource, self).__delattr__(name)

        del self.attrs[name]


class Resource(ABResource):

    RESOURCE = ""
    RESOURCE_PATH = ""

    @classmethod
    def resource_url(cls):
        resource_path = cls.RESOURCE_PATH
        return join_url(ricloud.url, resource_path)

    @property
    def instance_url(self):
        return "{}/{}".format(self.resource_url(), self.attrs["id"])

    @classmethod
    def retrieve(cls, id):
        resource = cls(id)
        resource.refresh()
        return resource

    def refresh(self):
        response, _ = self.request_handler.get(self.instance_url)
        self.attrs = response


class CreatableResource(Resource):
    @classmethod
    def create(cls, **data):
        """"Create a new resource instance on the API."""
        response, _ = cls.request_handler.post(cls.resource_url(), data=data)
        return cls(attrs=response)


class ResourceList(MutableSequence):
    def __init__(self, data, response):
        self.data = data or []
        self.has_more = response.get("has_more")

    def __repr__(self):
        return "{name}(data={data}, has_more={has_more})".format(
            name=self.__class__.__name__, data=self.data, has_more=self.has_more
        )

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        self.data[index] = value

    def __delitem__(self, index):
        del self.data[index]

    def __len__(self):
        return len(self.data)

    def insert(self, index, value):
        self.data.insert(index, value)


class ListableResource(Resource):
    @classmethod
    def list(cls, **params):
        """Retrieve a list of resources matching the provided filters."""
        response, _ = cls.request_handler.get(cls.resource_url(), params=params)
        return ResourceList(
            data=[cls(attrs=attrs) for attrs in response.pop("data", [])],
            response=response,
        )


class UpdatableResource(Resource):
    @classmethod
    def update_with_id(cls, id, **data):
        """Update a resource without retrieving it first.

        NOTE: can't name this 'update' due to the use of MutableMapping base.
        """
        resource = cls(id=id)
        resource.update(**data)
        return resource

    def update(self, **data):
        """Update a retrieved resource on the API.

        TODO: check if the resource has been modified.
        """
        response, _ = self.request_handler.post(self.instance_url, data=data)
        self.attrs.update(response)


class DeletableResource(Resource):
    @classmethod
    def delete_with_id(cls, id):
        resource = cls(id=id)
        resource.delete()
        return resource

    def delete(self):
        response, _ = self.request_handler.delete(self.instance_url)
        self.attrs.update(response)
