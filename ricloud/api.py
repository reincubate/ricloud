"""Primary API object. This handles communication with the ASApi enpoints."""

from __future__ import absolute_import

import time
import requests

from . import utils
from .conf import settings


class Api(object):
    """Primary object that pushes requests into a distinct stream thread."""

    def __init__(self):
        self.host = settings.get('hosts', 'api_host')
        self.token = settings.get('auth', 'token')

        self.account_info_endpoint = '%s%s' % (self.host, settings.get('endpoints', 'account_information'))
        self.register_account_endpoint = '%s%s' % (self.host, settings.get('endpoints', 'register_account'))
        self.task_status_endpoint = '%s%s' % (self.host, settings.get('endpoints', 'task_status'))
        self.results_consumed_endpoint = '%s%s' % (self.host, settings.get('endpoints', 'result_consumed'))

        self._pending_tasks = {}
        self.services = {}

    @property
    def pending_tasks(self):
        return self._pending_tasks

    @property
    def token_header(self):
        return {
            'Authorization': 'Token %s' % self.token,
        }

    def _get_info(self):
        """Fetch account information from ASApi host."""
        return self._perform_get_request(self.account_info_endpoint, headers=self.token_header)

    @staticmethod
    def _parse_endpoint(endpoint):
        """Expect endpoint to be dictionary containing `protocol`, `host` and `uri` keys."""
        return "{protocol}://{host}{uri}".format(**endpoint)

    def _set_endpoints(self, info):
        self.stream_endpoints = info['stream_endpoints']

        submission = info['task_submission_endpoint']
        self.submit_endpoint = self._parse_endpoint(submission)

    def _set_allowed_services_and_actions(self, services):
        """Expect services to be a list of service dictionaries, each with `name` and `actions` keys."""
        for service in services:
            self.services[service['name']] = {}

            for action in service['actions']:
                name = action.pop('name')
                self.services[service['name']][name] = action

    def setup(self):
        info = self._get_info()
        self._set_endpoints(info)
        self.retrieval_protocol = info['retrieval_protocol']
        self._set_allowed_services_and_actions(info['services'])

    def allowed_services(self):
        return self.services.keys()

    def allowed_actions(self, service_name):
        return self.services[service_name].keys()

    def register_account(self, username, service):
        """Register an account against a service.
        The account that we're querying must be referenced during any
        future task requests - so we know which account to link the task
        too.
        """
        data = {
            'service': service,
            'username': username,
        }

        return self._perform_post_request(self.register_account_endpoint, data, self.token_header)

    def perform_task(self, service, task_name, account, payload, callback=None):
        """Submit a task to the API.
        The task is executed asyncronously, and a Task object is returned.
        """
        data = {
            'service': service,
            'action': task_name,
            'account': account,
        }
        data.update(payload)

        response = self._perform_post_request(self.submit_endpoint, data, self.token_header)

        task = Task(uuid=response['task_id'], callback=callback)
        self._pending_tasks[task.uuid] = task

        return task

    def task_status(self, task_id):
        """Find the status of a task."""
        data = {
            'task_ids': task_id,
        }
        return self._perform_post_request(self.task_status_endpoint, data, self.token_header)

    def result_consumed(self, task_id):
        """Report the result as successfully consumed."""
        data = {
            'task_ids': task_id,
        }
        return self._perform_post_request(self.results_consumed_endpoint, data, self.token_header)

    def wait_for_results(self):
        while self._pending_tasks:
            time.sleep(0.1)

    def set_task_result(self, task_id, result):
        if task_id not in self._pending_tasks:
            time.sleep(1)
        try:
            self._pending_tasks[task_id].result = result
            self._pending_tasks.pop(task_id)
            self.result_consumed(task_id)
        except KeyError:
            pass

    @staticmethod
    def _parse_response(response, post_request=False):
        """Treat the response from ASApi.

        The json is dumped before checking the status as even if the response is
        not properly formed we are in trouble.

        TODO: Streamline error checking.
        """
        data = response.json()

        if not response.ok:
            utils.error_message_and_exit('Push Api Error:', data)

        if post_request and not data['success']:
            raise Exception('Push Api Error: [%s]' % data['error'])

        return data

    @staticmethod
    def _perform_get_request(url, headers=None):
        response = requests.get(
            url,
            headers=headers
        )

        return Api._parse_response(response)

    @staticmethod
    def _perform_post_request(url, data, headers=None):
        response = requests.post(
            url,
            data=data,
            headers=headers
        )

        return Api._parse_response(response, post_request=True)


class Task(object):
    """Simple object to encapsulate the result of a task.

    Can also perform checks against the server to determine its status.
    """
    def __init__(self, uuid, callback=None, object_store=False):
        self.uuid = uuid
        self._result = None
        self._resolved = False
        self.callback = callback
        self.object_store = object_store

        self.timer = time.time()

    @property
    def result(self):
        if not self._resolved:
            raise Exception('Task has not completed, no result available.')
        return self._result

    @result.setter
    def result(self, value):
        self._result = value
        self._resolved = True

        start_time = self.timer
        self.timer = time.time() - start_time

        if self.callback:
            self.callback(self)

    def wait_for_result(self, timeout=None):
        start = time.time()

        while not self.has_resolved:
            time.sleep(0.1)
            if timeout and start + timeout < time.time():
                raise Exception('Task failed to complete within the timeout limit.')

        return self._result

    @property
    def has_resolved(self):
        return self._resolved
