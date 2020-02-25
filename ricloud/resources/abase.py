from __future__ import absolute_import, unicode_literals

from collections import OrderedDict

import ricloud
from ricloud.compat import Mapping, MutableMapping, MutableSequence
from ricloud.requests import RequestHandler
from ricloud.utils import pretty_print, join_url


class ABResource(MutableMapping):

    request_handler = RequestHandler()

    def __init__(self, **attrs):
        attrs = self.parse_attrs(attrs)
        # Need to setup using object method to avoid circular deps on init.
        object.__setattr__(self, "attrs", attrs or OrderedDict())

    def __repr__(self):
        return "{name}({attrs})".format(
            name=self.__class__.__name__, attrs=pretty_print(self.attrs),
        )

    def __getitem__(self, key):
        return self.attrs[key]

    def __setitem__(self, key, value):
        self.attrs[key] = self.parse_value(value)

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
            if name == "attrs" and value:
                value = self.parse_attrs(value)

            return super(ABResource, self).__setattr__(name, value)

        self.attrs[name] = self.parse_value(value)

    def __delattr__(self, name):
        if name in self.__dict__:
            return super(ABResource, self).__delattr__(name)

        del self.attrs[name]

    def __eq__(self, other):
        ignore = ["resource"]
        attrs_self = {key: value for key, value in self.items() if key not in ignore}
        attrs_other = {key: value for key, value in other.items() if key not in ignore}
        return attrs_self == attrs_other

    @classmethod
    def get_resources(cls):
        for subclass in cls.__subclasses__():
            if getattr(subclass, "RESOURCE", None):
                yield subclass.RESOURCE, subclass

            for item in subclass.get_resources():
                yield item

    _resources = None

    @classmethod
    def get_resource(cls, resource_type):
        if ABResource._resources is None:
            ABResource._resources = dict(ABResource.get_resources())
        return ABResource._resources.get(resource_type)

    @classmethod
    def parse_value(cls, value):
        if isinstance(value, Mapping) and not isinstance(value, ABResource):
            resource_type = value.get("resource")
            if resource_type:
                resource = cls.get_resource(resource_type)
                return resource(**value)
        return value

    @classmethod
    def parse_attrs(cls, attrs):
        return dict([(attr, cls.parse_value(value)) for attr, value in attrs.items()])


class Resource(ABResource):
    RESOURCE = ""
    RESOURCE_PATH = ""

    def __init__(self, *args, **attrs):
        if args:
            attrs["id"] = args[0]
        super(Resource, self).__init__(**attrs)

    @classmethod
    def resource_url(cls, resource_path=None):
        resource_path = resource_path or cls.RESOURCE_PATH
        return join_url(ricloud.url, resource_path)

    @property
    def instance_url(self):
        return "{}/{}".format(self.resource_url(), self.id)

    @classmethod
    def retrieve(cls, id):
        resource = cls(id=id)
        resource.refresh()
        return resource

    def refresh(self):
        response, _ = self.request_handler.get(self.instance_url)
        self.attrs = response


class ABList(MutableSequence, ABResource):
    def __init__(self, **attrs):
        data = attrs.get("data")
        if data:
            attrs["data"] = self.parse_list_data(data)
        super(ABList, self).__init__(**attrs)

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

    @classmethod
    def parse_list_data(cls, data):
        resource_type = data[0]["resource"]
        resource = cls.get_resource(resource_type)
        return [resource(**attrs) for attrs in data]


class List(ABList):
    RESOURCE = "list"

    @property
    def instance_url(self):
        return self.url


class CreatableResource(Resource):
    @classmethod
    def create(cls, **data):
        """"Create a new resource instance on the API."""
        response, _ = cls.request_handler.post(cls.resource_url(), data=data)
        return cls(**response)


class ListableResource(Resource):
    @classmethod
    def list(cls, **params):
        """Retrieve a list of resources matching the provided filters."""
        response, _ = cls.request_handler.get(cls.resource_url(), params=params)
        return List(**response)


class UpdatableResource(Resource):
    @classmethod
    def update_with_id(cls, id, **data):
        """Update a resource without retrieving it first."""
        resource = cls(id=id)
        resource.update(**data)
        return resource

    def update(self, **data):
        """Update a retrieved resource on the API."""
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
