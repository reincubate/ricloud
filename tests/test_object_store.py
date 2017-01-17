import pytest
from mock import MagicMock

from ricloud.object_store import (
    ObjectStore, ResultRetrieved, InvalidTaskStatus, MAX_PENDING
)


@pytest.fixture()
def mock_Api_task_status(mocker):

    task_status = mocker.patch('ricloud.api.Api.task_status')

    task_status.return_value = {
        "mock_uuid":
            {
                'results_retrieved': False,
                'status': 'mock',
                'retrieval_endpoint': 'mock_url'
            },
    }

    return task_status


@pytest.fixture(params=[['mock'] * 5000, ['mock'] * 15000])
def mock_tasks_uuid(request):
    return request.param


@pytest.fixture()
def results_retrieved_values():
    return {
        'status': 'mock',
        'result_retrieved': True,
    }


@pytest.fixture()
def mock_object_store_urls():
    return [("mock_uuid", "mock_url")]


@pytest.fixture(params=[{'result_retrieved': False}, {'status': 'mock'}])
def missing_values_status(request):
    return request.param


@pytest.fixture()
def response():
    mock_response = MagicMock
    mock_response.content = "mock_response"
    return mock_response


class TestObjectStoreHandler(object):

    def test_fails_on_result_retrieved(self, mock_Api_object_store, results_retrieved_values):
        # Checks if we catch if a task result was already consumed from the object store
        handler = ObjectStore(mock_Api_object_store)
        with pytest.raises(ResultRetrieved):
            handler._check_status_integrity(results_retrieved_values)

    def test_fails_on_invalid_status(self, mock_Api_object_store, missing_values_status):
        # Checks if we catch an invalid response from asapi's task status
        handler = ObjectStore(mock_Api_object_store)
        with pytest.raises(InvalidTaskStatus):
            handler._check_status_integrity(missing_values_status)

    def test_get_task_status(self, mock_Api_object_store, mock_Api_task_status, mock_tasks_uuid):
        # Checks if we limit the number of status we can ask for in one go
        mock_Api_object_store.task_status = mock_Api_task_status
        handler = ObjectStore(mock_Api_object_store)
        handler._get_task_status(mock_tasks_uuid)
        mock_Api_task_status.assert_called_once_with(
            mock_tasks_uuid[:MAX_PENDING])

    def test_get_from_object_store(self, mocker, mock_Api_object_store, mock_object_store_urls, response):

        # Checks if we respect the flow to get a response in parallel with grequests
        url = mock_object_store_urls[0][1]
        uuid = mock_object_store_urls[0][0]

        mock_get = mocker.patch('ricloud.utils.threaded_get')
        mock_get.return_value = response

        handler = ObjectStore(mock_Api_object_store)
        result = handler._retrieve_result(
            mock_object_store_urls, handler.api.token_header)
        mock_get.assert_called_once_with((url, handler.api.token_header))
        assert result == {uuid: response.content}

    def test_checks_pending(self, mock_Api_object_store):

        # Checks if we get pending tasks correctly from the dictionary _pending_tasks in the api
        handler = ObjectStore(mock_Api_object_store)
        handler.api.pending_tasks = {"pending1": "mock", "pending2": "mock"}
        assert handler._pending_tasks() == handler.api.pending_tasks.keys()
        handler.api.pending_tasks = {}
        assert handler._pending_tasks() == []

    def test_handle_pending(self, mocker, mock_Api_object_store, mock_Api_task_status, response):
        # Checks if we handle pending tasks correctly -> Get status -> Get from object store
        mock_status = mocker.patch(
            'ricloud.object_store.ObjectStore._get_task_status')
        status = mock_Api_task_status()
        status.update({'success': 'mock'})
        mock_status.return_value = status

        mock_getter = mocker.patch(
            'ricloud.object_store.ObjectStore._retrieve_result')
        mock_getter.return_value = {
            mock_Api_task_status().keys()[0]: response.content}
        handler = ObjectStore(mock_Api_object_store)
        handler._handle_pending_tasks(['mock_uuid'])
        mock_status.assert_called_once_with(['mock_uuid'])
