import json


def sync(func):
    """Decorator to make a task synchronous."""
    sync_timeout = 3600  # Match standard synchronous timeout.

    def wraps(*args, **kwargs):
        task = func(*args, **kwargs)
        task.wait_for_result(timeout=sync_timeout)
        result = json.loads(task.result)
        return result

    return wraps


class BaseClient(object):

    def __init__(self, ricloud_client):
        self.ricloud = ricloud_client

    def register_account(self, account):
        return self.ricloud.api.register_account(
            username=account,
            service=self.service)

    def wait_for_pending_tasks(self):
        self.ricloud.api.wait_for_results()
