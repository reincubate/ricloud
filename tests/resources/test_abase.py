from __future__ import absolute_import

import pytest

import ricloud
from ricloud.resources.abase import Resource, List


class ResourceFixture(Resource):
    RESOURCE = "test_resource"
    RESOURCE_PATH = "test/resource"


@pytest.fixture
def resource_obj():
    return ResourceFixture("abcd1234", **{"attr1": "value1",})


@pytest.fixture
def nested_obj():
    return ResourceFixture(
        "abcd1234", **{"nested": {"id": "abcd123", "resource": "test_resource"}}
    )


class TestResource(object):
    def test_ok(self, resource_obj):
        assert resource_obj.id == "abcd1234"
        assert resource_obj.attr1 == "value1"

        assert resource_obj["id"] == "abcd1234"
        assert resource_obj["attr1"] == "value1"

    def test_nested(self, nested_obj):
        assert nested_obj.id == "abcd1234"
        assert isinstance(nested_obj.nested, ResourceFixture)
        assert nested_obj.nested.id == "abcd123"

    def test_resource_url(self):
        assert ResourceFixture.resource_url() == ricloud.url + "/test/resource"

    def test_instance_url(self, resource_obj):
        assert resource_obj.instance_url == ricloud.url + "/test/resource/abcd1234"


@pytest.fixture
def list_obj():
    return List(
        **{
            "resource": "list",
            "data": [{"id": "abcd1234", "resource": "test_resource"}],
            "has_more": False,
            "total_count": 1,
            "url": "/users",
        }
    )


class TestList(object):
    def test_ok(self, list_obj):
        assert list_obj.data == [ResourceFixture(id="abcd1234")]
        assert not list_obj.has_more
        assert list_obj.total_count == 1
        assert list_obj.instance_url == "/users"

    def test_iterable(self, list_obj):
        item = next(iter(list_obj))
        assert item == ResourceFixture(id="abcd1234")

    def test_indexable(self, list_obj):
        item = list_obj[0]
        assert item == ResourceFixture(id="abcd1234")

    def test_length(self, list_obj):
        assert len(list_obj) == 1
