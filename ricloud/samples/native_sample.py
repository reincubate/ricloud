import json
import os

from clint.textui import puts, colored
from ..clients.icloud import iCloudClient

from ..conf import OUTPUT_DIR

SAMPLE_ACCOUNT = "johnapplessed@apple.com"
SAMPLE_PASSWORD = "johnapple"
SAMPLE_DEVICE_ID = 'b5cc9d671f96f4443d522ac15ca8bc9f66f18cf5'

#
# Task Submission and Waiting for results:
#   By calling ricloud.api.perform_task, a task is submitted to the push api.
#   The perform_task method returns the task object.
#
#   The result of the task comes from a separate thread created upon the
#   intialization of the ricloud client. This thread is connected to the client's
#   stream and saves the task result in memory. This result can be recovered by
#   calling the task.wait_for_task_result() method.
#
#   If the task's result is already in memory, this method returns immediately.
#   If not, the method blocks until the push api returns the task result.
#   If no result comes before the the timeout, the method raises an Exception
#


class SampleICloudNativeApplication(object):
    display_name = 'Sample iCloud Native Application'
    client_name = iCloudClient
    service = 'iCloud'

    def __init__(self, ricloud_client, payload):
        self.ricloud = ricloud_client
        self.account = SAMPLE_ACCOUNT
        self.password = SAMPLE_PASSWORD
        self.device_id = SAMPLE_DEVICE_ID
        self.data_to_fetch = ','.join(self.get_available_data())
        self.timeout = payload.get('timeout')

    def run(self):
        # Register the account for the iCloud service
        self.ricloud.api.register_account(self.account, self.service)

        # Log in to the sample account
        task = self.submit_login_task()
        # Wait for the task's result
        login_result = task.wait_for_result()
        self.handle_login_response(login_result)

        # Submit a task to get all available data
        task = self.submit_fetch_data_task()
        # Wait for the task's result
        feed_result = task.wait_for_result()

        # Write feed to disk
        self.write_feed_to_disk(feed_result, task.uuid)

    def submit_login_task(self):

        task = self.ricloud.api.perform_task(
            service=self.service,
            task_name='log-in',
            account=self.account,
            payload={
                'password': self.password,
            },
        )
        return task

    def submit_fetch_data_task(self):

        # Fetch data feed
        task = self.ricloud.api.perform_task(
            service=self.service,
            task_name='fetch-data',
            account=self.account,
            payload={
                'data': self.data_to_fetch,
                'device': self.device_id
            },
        )
        return task

    @staticmethod
    def write_feed_to_disk(feed, uuid):
        filename = os.path.join(OUTPUT_DIR, '%s.json' % uuid)
        with open(filename, 'w') as out:
            json.dump(feed, out, indent=2)
        puts(colored.green(
            '\nData Fetch Successful. Output file: %s.json' % uuid)
        )
        puts(colored.green('All tasks completed.'))

    def get_available_data(self):
        if 'permissions' in self.ricloud.api.services['iCloud']['Fetch Data']:
            return self.ricloud.api.services[
                'iCloud']['Fetch Data']['permissions']['data']
        return ''

    @staticmethod
    def handle_login_response(login_result):
        is_login_success = ('error' not in login_result)
        if not is_login_success:
            raise Exception("Login to sample account failed")
