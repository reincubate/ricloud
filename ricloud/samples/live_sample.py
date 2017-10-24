import json

from .icloud_sample import SampleICloudApplication

from .. import utils


class SampleLiveICloudApplication(SampleICloudApplication):
    display_name = 'Sample Live Data Application'

    def run(self):
        # Register the account for the iCloud service.
        self.client.register_account(self.account)
        # Attempt to login to the account.
        self.log_in()
        # Choose a data type and retrieve it.
        self.fetch_data()
        # Wait for any pending tasks to complete
        self.client.wait_for_pending_tasks()
        utils.info_message('All tasks completed')

    def fetch_data(self):
        """Prompt for a data type choice and execute the `fetch_data` task.
        The results are saved to a file in json format.
        """
        choices = self.available_data
        choices.insert(0, 'All')

        selected_data_type = utils.select_item(
            choices,
            'Please select what data to fetch:',
            'Available data:',
        )

        if selected_data_type == 'All':
            selected_data_type = ','.join(self.available_data)

        utils.pending_message('Performing fetch data task...')

        fetch_data_task = self.client.data(
            account=self.account,
            data=selected_data_type,
        )

        # Wait here for result as rest of sample app relies on it.
        fetch_data_task.wait_for_result(timeout=self.timeout)
        fetch_data_result = json.loads(fetch_data_task.result)

        # Write the result to file.
        task_id = fetch_data_task.uuid
        filepath = utils.get_or_create_filepath('%s.json' % task_id)

        with open(filepath, 'w') as out:
            json.dump(fetch_data_result, out, indent=2)

        utils.info_message('Fetch data successful. Output file: %s.json' % task_id)

        return fetch_data_result

    @property
    def available_data(self):
        live_feeds = [
            'location',
            'mobileme_contacts',
            'web_browser_history',
            'live_call_history',
            'live_photos',
        ]
        return [c for c in self.client.available_data
                if c in live_feeds]
