import pytest
import time

from ricloud.conf import settings
from ricloud.ricloud import RiCloud


@pytest.fixture
def stream_endpoints():
    return ['mock-stream-protocol://mock-stream-hostmock-stream-uri']


class TestAppstream(object):

    def test_ricloud_api_property(self, mock_Api, mock_Listener, mock_Stream):
        """ Are we creating the Api properly? """
        RiCloud()

        mock_Api.assert_called_once_with()

    def test_ricloud_listener_property(self, mocker, mock_Api, mock_Listener, mock_Stream):
        """ Are we creating the Listener properly? """
        mock_RiCloudHandler = mocker.patch('ricloud.ricloud.RiCloudHandler')

        ricloud_client = RiCloud()
        # Sometimes this test fails because the other thread needs time to execute...
        time.sleep(0.1)
        mock_RiCloudHandler.assert_called_once_with(api=ricloud_client.api)
        mock_Listener.assert_called_once_with({'__ALL__': mock_RiCloudHandler.return_value})

    def test_ricloud_stream_thread_property(self, mock_Thread, mock_Api, mock_Listener, mock_Stream, stream_endpoints):
        """ Are we creating the Stream properly? """
        ricloud_client = RiCloud()

        mock_Stream.assert_called_once_with(
            endpoint=stream_endpoints[0],
            listener=ricloud_client.listener,
            stream=settings.get('stream', 'stream_endpoint'),
            token=settings.get('auth', 'token')
        )
        mock_Stream.return_value.go.assert_called_once_with()
        assert mock_Thread.daemon
        mock_Thread.start.assert_called_once_with()

    def test_ricloud_object_store_property(self, mock_Thread, mock_Api_object_store, mock_Listener, mock_object_store,
                                           stream_endpoints):
        """ Are we creating the Stream properly? """
        RiCloud()

        mock_object_store.assert_called_once_with(
            api=mock_Api_object_store.return_value,
        )
        mock_object_store.return_value.go.assert_called_once_with()
        assert mock_Thread.daemon
        mock_Thread.start.assert_called_once_with()

    def test_ricloud_init(self, mocker, mock_Api, mock_Listener, mock_Stream, mock_Thread):
        """ Are we initialising stuff in the right order? """
        manager = mocker.MagicMock()
        manager.attach_mock(mock_Api.return_value.setup, 'api_setup')
        manager.attach_mock(mock_Thread.start, 'stream_thread_start')

        RiCloud()

        manager.assert_has_calls([mocker.call.api_setup(), mocker.call.stream_thread_start()])
