import datetime
from StringIO import StringIO

from ricloud.conf import settings
import requests

class BackupClient(object):
    DATA_SMS = 1
    DATA_PHOTOS = 2
    DATA_BROWSER_HISTORY = 4
    DATA_CALL_HISTORY = 8
    DATA_CONTACTS = 16
    DATA_INSTALLED_APPS = 32
    DATA_WHATSAPP_MESSAGES = 512
    DATA_SKYPE_MESSAGES = 1024
    DATA_APPOINTMENTS = 2048
    DATA_LINE_MESSAGES = 4096
    DATA_KIK_MESSAGES = 8192
    DATA_VIBER_MESSAGES = 16384

    DATA_WEB_CONTACTS = 64
    DATA_WEB_LOCATION = 256

    AVAILABLE_DATA = (
            (DATA_SMS,              'Messages'),
            (DATA_PHOTOS,           'Photos and Videos'),
            (DATA_BROWSER_HISTORY,  'Browser History'),
            (DATA_CALL_HISTORY,     'Call History'),
            (DATA_CONTACTS,         'Contacts'),
            (DATA_INSTALLED_APPS,   'Installed Apps'),
            (DATA_WHATSAPP_MESSAGES,   'WhatsApp Messages'),
            (DATA_SKYPE_MESSAGES,   'Skype Messages'),
            (DATA_APPOINTMENTS,   'Appointments'),
            (DATA_LINE_MESSAGES,   'Line Messages'),
            (DATA_KIK_MESSAGES,   'Kik Messages'),
            (DATA_VIBER_MESSAGES,   'Viber Messages'),


            (DATA_WEB_CONTACTS,     'Contacts (live)'),
            (DATA_WEB_LOCATION,     'Location (live)'),
        )

    MIN_REQUEST_DATE = datetime.datetime(year=1900, month=1, day=1)

    def __init__(self, api):
        self.api = api

    def request_data(self, device_id, data_mask=None, since=None):
        """Pull data from iCloud from a given point in time.

        Arguments:
        device_id   -- Device ID to pull data for

        Keyword Arguments:
        data_mask   -- Bit Mask representing what data to download
        since       -- Datetime to retrieve data from (i.e. SMS received
                       after this point)
        """
        assert self.api.session_key is not None, 'Session key is required, please log in.'

        if not data_mask:
            # No mask has been set, so use everything
            data_mask = 0
            for mask, _ in BackupClient.AVAILABLE_DATA:
                data_mask |= mask

        if not since:
            since = BackupClient.MIN_REQUEST_DATE

        # The start date cannot be below the min request date, may as
        # well check it now (server will just send an error anyway)
        assert since >= BackupClient.MIN_REQUEST_DATE

        post_data = {
            'key': self.api.session_key,
            'mask': data_mask,
            'since': since.strftime('%Y-%m-%d %H:%M:%S.%f'),
            'device': device_id,
        }

        response = requests.post(settings.get('endpoints', 'download_data'),
                                    auth=self.api.auth, data=post_data,
                                    headers=self.api.headers)

        if not response.ok:
            # Unhandled respnose
            response.raise_for_status()
        return response.json()

    def download_file(self, device_id, file_id, out=None):
        """Download an individual file from the iCloud Backup


        Arguments:
        device_id   -- Device ID to pull file from
        file_id     -- File ID representing the file we want to download

        Keyword Arguments:
        out         -- File like object to write response to. If not
                       provided we will write the object to memory.
        """
        if not out:
            out = StringIO()

        post_data = {
            'key': self.api.session_key,
            'device': device_id,
            'file': file_id,
        }

        response = requests.post(settings.get('endpoints', 'download_file'),
                                    auth=self.api.auth, data=post_data,
                                    stream=True, headers=self.api.headers)

        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                out.write(chunk)
        out.flush()

        return out
