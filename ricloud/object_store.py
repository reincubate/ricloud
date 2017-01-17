import time

from .utils import concurrent_get

MAX_PENDING = 10000


class ResultRetrieved(Exception):
    pass


class InvalidTaskStatus(Exception):
    pass


class ObjectStore(object):
    def __init__(self, api):
        self.api = api

    def go(self):
        while True:
            time.sleep(1)
            pending = self._pending_tasks()
            if pending:
                self._handle_pending_tasks(pending)
                time.sleep(5)

    def _pending_tasks(self):
        return self.api.pending_tasks.keys() if self.api.pending_tasks else []

    @staticmethod
    def _check_status_integrity(status):
        # Check if everything is ok with the status
        if 'result_retrieved' not in status or 'status' not in status:
            raise InvalidTaskStatus
        if status['result_retrieved']:
            raise ResultRetrieved

    def _get_task_status(self, pending):
        return self.api.task_status(pending[:MAX_PENDING])

    def _set_result_in_memory(self, uuid, result):
        # Make the result accessible to the other thread
        self.api.set_task_result(uuid, result)

    def _handle_pending_tasks(self, pending):
        task_status_response = self._get_task_status(pending)
        task_status_response.pop('success')

        retrieval_urls = []
        for task_id, task_status in task_status_response.iteritems():
            if 'retrieval_endpoint' in task_status:
                url = (task_id, task_status['retrieval_endpoint'])
                retrieval_urls.append(url)

        if retrieval_urls:
            results = self._retrieve_result(retrieval_urls, self.api.token_header)
            for task_id, task_result in results.iteritems():
                self._set_result_in_memory(task_id, task_result)

    @staticmethod
    def _retrieve_result(endpoints, token_header):
        """Prepare the request list and execute them concurrently."""
        request_list = [
            (url, token_header)
            for (task_id, url) in endpoints
        ]

        responses = concurrent_get(request_list)

        # Quick sanity check
        assert len(endpoints) == len(responses)

        responses_dic = {
            task_id: r.content
            for (task_id, _), r in zip(endpoints, responses)
        }
        return responses_dic
