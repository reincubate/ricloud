import os
import json
import getpass

from clint.textui import indent

from .. import utils
from ..conf import settings
from ..clients.icloud import iCloudClient


class SampleICloudApplication(object):
    display_name = 'Sample iCloud Application'
    client_name = iCloudClient

    def __init__(self, ricloud_client, payload):
        self.client = self.client_name(ricloud_client)
        self.account = payload.get('account')
        self.password = payload.get('password')
        self.timeout = payload.get('timeout')

    def run(self):
        # Register the account for the iCloud service.
        self.client.register_account(self.account)
        # Attempt to login to the account.
        self.log_in()
        # Get the accounts device list.
        self.get_devices()
        # Choose a device to retrieve data from.
        self.prompt_devices_list()
        # Choose a data type and retrieve it.
        data = self.fetch_data()
        # Grab all photos and/or attachments to download
        files = self.get_file_ids_to_download(data)
        # Send all the the resquests to download the files
        if files:
            self.download_files(files)
        # Wait for any pending tasks to complete
        self.client.wait_for_pending_tasks()
        utils.info_message('All tasks completed')

    @utils.profile('Login completed in')
    def log_in(self):
        """Perform the `log_in` task to setup the API session for future data requests."""
        if not self.password:
            # Password wasn't give, ask for it now
            self.password = getpass.getpass('Password: ')

        utils.pending_message('Performing login...')

        login_result = self.client.login(
            account=self.account,
            password=self.password
        )

        if 'error' in login_result:
            self.handle_failed_login(login_result)

        utils.info_message('Login successful')

    def handle_failed_login(self, login_result):
        """If Two Factor Authentication (2FA/2SV) is enabled, the initial
        login will fail with a predictable error. Catching this error allows us
        to begin the authentication process.

        Other types of errors can be treated in a similar way.
        """
        error_code = login_result.get('error')
        if '2fa-required' in error_code:
            utils.error_message('Login Failed: 2FA or 2SV is active!')
            self.trigger_two_step_login(login_result)
            self.finish_two_step_login()
        else:
            utils.error_message_and_exit('\nLogin Failed', login_result)

    def trigger_two_step_login(self, login_result):
        utils.info_message('Starting 2FA/2SV authentication process.')

        devices = login_result['data']['trustedDevices']

        selected_trusted_device = utils.select_item(
            devices,
            prompt_instruction='Please select a device index:',
            prompt_title='This account has 2FA/2SV enabled.\nAn authorization '
                         'code will be sent to the selected devices.',
            output_type=str
        )

        start_two_fa_result = self.client.start_2fa_auth(
            account=self.account,
            challenge=selected_trusted_device
        )

        if 'error' in start_two_fa_result:
            utils.error_message_and_exit('2FA Failed', start_two_fa_result)

    def finish_two_step_login(self):
        utils.info_message('Challenge has been submitted.')

        submit_code = utils.prompt_for_input('\nPlease enter the received code:')

        utils.pending_message('Sending code...')

        finish_two_fa_result = self.client.finish_2fa_auth(
            account=self.account,
            code=submit_code
        )

        if 'error' in finish_two_fa_result:
            utils.error_message_and_exit('2FA Failed! Wrong code?', finish_two_fa_result)

    @utils.profile('Devices retrieved in')
    def get_devices(self):
        """Execute the `get_devices` task and store the results in `self.devices`."""
        utils.pending_message('Fetching device list...')

        get_devices_task = self.client.devices(
            account=self.account
        )

        # We wait for device list info as this sample relies on it next.
        get_devices_task.wait_for_result(timeout=self.timeout)

        get_devices_result = json.loads(get_devices_task.result)
        self.devices = get_devices_result['devices']

        utils.info_message('Get devices successful')

    def prompt_devices_list(self):
        utils.prompt_message('Available devices:')

        for index, (device_id, device_info) in enumerate(self.devices.iteritems()):
            line = u"{index:2d}: {device_name} ({colour} {name} running iOS {ios_version})"
            line = line.format(index=index, **device_info)
            with indent(3):
                utils.print_message(line)

        self.device_id = utils.prompt_for_choice(
            self.devices.keys(),
            message='Please select a device index:'
        )

    @utils.profile('Fetch data completed in')
    def fetch_data(self):
        """Prompt for a data type choice and execute the `fetch_data` task.
        The results are saved to a file in json format.
        """
        choices = list(self.client.available_data)
        choices.insert(0, 'All')

        selected_data_type = utils.select_item(
            choices,
            'Please select what data to fetch:',
            'Available data:',
        )

        if selected_data_type == 'All':
            selected_data_type = ','.join(self.client.available_data)

        utils.pending_message('Performing fetch data task...')

        fetch_data_task = self.client.data(
            account=self.account,
            device=self.device_id,
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

    def download_files(self, files):
        """This method uses the `download_file` task to retrieve binary files
        such as attachments, images and videos.

        Notice that this method does not wait for the tasks it creates to return
        a result synchronously.
        """
        utils.pending_message(
            "Downloading {nfiles} file{plural}...".format(
                nfiles=len(files),
                plural='s' if len(files) > 1 else ''
            ))

        for file in files:
            if 'file_id' not in file:
                continue

            def build_callback(file):
                """Callback to save a download file result to a file on disk."""
                def file_callback(task):
                    device_name = self.devices[self.device_id]['device_name']
                    path_chunks = file['file_path'].split('/')

                    directory = os.path.join('files', device_name, *path_chunks[:-1])

                    filepath = utils.get_or_create_filepath(file['filename'], directory)

                    with open(filepath, 'wb') as out:
                        out.write(task.result)

                    if settings.getboolean('logging', 'time_profile'):
                        filepath = utils.append_profile_info(filepath, task.timer)

                    with indent(4):
                        utils.print_message(filepath)

                return file_callback

            self.client.download_file(
                account=self.account,
                device=self.device_id,
                file=file['file_id'],
                callback=build_callback(file)
            )

    @staticmethod
    def get_file_ids_to_download(data):
        files = []
        for data_type, feed in data.iteritems():
            if data_type == 'photos':
                files += feed
            else:
                for feed_entry in feed:
                    if 'attachments' in feed_entry:
                        files += feed_entry['attachments'] or []
        return files
