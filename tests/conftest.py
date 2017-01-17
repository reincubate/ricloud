import pytest


@pytest.fixture
def mock_Api(mocker, stream_endpoints):
    mock_api = mocker.patch('ricloud.ricloud.Api')

    mock_api.return_value.stream_endpoints = stream_endpoints

    return mock_api


@pytest.fixture
def mock_Api_object_store(mocker):

    mock_api = mocker.patch('ricloud.ricloud.Api')

    mock_api.return_value.retrieval_protocol = "asstore"

    return mock_api


@pytest.fixture
def mock_Listener(mocker):
    return mocker.patch('ricloud.ricloud.Listener')


@pytest.fixture
def mock_Stream(mocker):
    return mocker.patch('ricloud.ricloud.Stream')


@pytest.fixture
def mock_object_store(mocker):
    return mocker.patch('ricloud.ricloud.ObjectStore')


@pytest.fixture
def mock_Thread(mocker):
    mock_threading = mocker.patch('ricloud.ricloud.threading')

    mock_thread = mocker.MagicMock()

    def _init(target):
        mock_thread.target = target
        return mock_thread

    def _run():
        mock_thread.target()

    mock_threading.Thread.side_effect = _init

    mock_thread.start.side_effect = _run

    return mock_thread
