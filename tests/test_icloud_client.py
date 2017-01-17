import pytest

from ricloud.clients.icloud import iCloudClient


@pytest.fixture
def mock_iCloud_permissions():
    return [
        'photos',
        'sms'
    ]


@pytest.fixture
def mock_RiCloud(mocker, mock_iCloud_permissions):
    mock = mocker.MagicMock()

    mock.api.services = {
        'iCloud': {
            'Fetch Data': {
                'permissions': {
                    'data': mock_iCloud_permissions
                }
            }
        }
    }

    return mock


class TestsICloudClient(object):

    def test_service_ok(self, mock_RiCloud):
        client = iCloudClient(ricloud_client=mock_RiCloud)

        assert 'iCloud' == client.service

    @pytest.mark.parametrize(
        'method,task_name,payload',
        [
            ('devices', 'list-devices', {}),
            ('data', 'fetch-data', {'device': 'mock-device', 'data': 'sms'}),
            ('download_file', 'download-file', {'device': 'mock-device', 'file': 'mock-file-id'}),
        ])
    def test_async_task_names_are_ok(self, mocker, mock_RiCloud, method, task_name, payload):

        client = iCloudClient(ricloud_client=mock_RiCloud)

        client.devices(account='mock-account')

        getattr(client, method)(account='mock-account', **payload)

        mock_RiCloud.api.perform_task.assert_called_with(
            service='iCloud',
            task_name=task_name,
            account='mock-account',
            payload=payload,
            callback=None)

    def test_available_data_is_ok(self, mock_RiCloud, mock_iCloud_permissions):
        client = iCloudClient(ricloud_client=mock_RiCloud)

        assert client.available_data == mock_iCloud_permissions
