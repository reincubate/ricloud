from __future__ import absolute_import, unicode_literals, print_function

import pytest

import ricloud
from ricloud.resources.abase import ABResource, Resource


def assert_attrs(resource, expected_attrs):
    print(ricloud.utils.encode_json(resource.attrs, indent=4))

    assert resource == expected_attrs


class TestABResource(object):

    def test_attrs_ok(self):
        ab_resource = ABResource(
            id='test-id',
            attrs={
                'attr_a': 'value_a',
                'attr_b': ['value_b1', 'value_b2']
            }
        )

        assert ab_resource.id == 'test-id'
        assert ab_resource.attr_a == 'value_a'
        assert ab_resource.attr_b == ['value_b1', 'value_b2']

    def test_setattrs_ok(self):
        ab_resource = ABResource(attrs={'attr_a': 'value_a1'})

        ab_resource.attr_a = 'value_a2'

        assert ab_resource.attr_a == 'value_a2'

        ab_resource = ABResource()

        ab_resource.attr_a = 'value_a1'

        assert ab_resource.attr_a == 'value_a1'

    def test_delattrs_ok(self):
        ab_resource = ABResource(attrs={'attr_a': 'value_a1'})

        del ab_resource.attr_a

        assert not hasattr(ab_resource, 'attr_a')


class ResourceFixture(Resource):
    RESOURCE = 'test_resource'
    RESOURCE_PATH = 'test/resource'


@pytest.fixture
def test_resource():
    return ResourceFixture(id='test-id', attrs={
        'attr_a': 'value_a',
        'attr_b': ['value_b1', 'value_b2']
    })


class TestResource(object):

    def test_ok(self, test_resource):
        expected_resource_url = '{}/{}'.format(
            ricloud.url, ResourceFixture.RESOURCE_PATH
        )

        assert ResourceFixture.resource_url() == expected_resource_url
        assert test_resource.resource_url() == expected_resource_url

        expected_instance_url = expected_resource_url + '/test-id'

        assert test_resource.instance_url == expected_instance_url


@pytest.mark.skip('Waiting for safer test fixtures to generate responses.')
class TestOrganisation(object):

    def test_retrieve_ok(self):
        org = ricloud.Organisation.retrieve()

        expected_attrs = {
            "id": 1,
            "resource": "organisation",
            "name": "Super Org",
            "slug": "super-org",
            "permissions": {},
            "storage_configs": [
                {
                    "id": 1,
                    "resource": "storage_config",
                    "type": "local",
                    "url": "gs://nonce",
                    "credentials": None,
                    "state": "valid",
                    "date_created": "2018-10-01T17:04:34.154530Z"
                },
                {
                    "id": 3,
                    "resource": "storage_config",
                    "type": "gs",
                    "url": "gs://nonce",
                    "credentials": None,
                    "state": "new",
                    "date_created": "2018-10-31T11:20:27.528691Z"
                }
            ],
            "storage_config_default": 1,
            "webhook_configs": [
                {
                    "id": 1,
                    "resource": "webhook_config",
                    "url": "http://127.0.0.1:8001/webhooks/",
                    "secret": "123",
                    "state": "valid",
                    "date_created": "2018-10-01T17:04:34.155917Z"
                },
                {
                    "id": 3,
                    "resource": "webhook_config",
                    "url": "http://localhost:8001/webhooks/",
                    "secret": "nonce",
                    "state": "invalid",
                    "date_created": "2018-10-31T16:14:46.645148Z"
                }
            ],
            "webhook_config_default": 1,
            "state": "active",
            "date_created": "2018-10-01T17:04:34.116738Z"
        }

        assert_attrs(org, expected_attrs)


@pytest.mark.skip('Waiting for safer test fixtures to generate responses.')
class TestKey(object):

    def test_retrieve_ok(self):
        key = ricloud.Key.retrieve(1)

        expected_attrs = {
            "id": 1,
            "resource": "key",
            "organisation": 1,
            "type": "standard",
            "storage_config": 1,
            "webhook_config": 1,
            "token": "nonce",
            "state": "active",
            "date_created": "2018-10-01T17:04:34.160171Z",
            "date_expires": None
        }

        assert_attrs(key, expected_attrs)

    def test_retrieve_not_found(self):
        with pytest.raises(ricloud.exceptions.RequestError):
            ricloud.Key.retrieve(999999)
