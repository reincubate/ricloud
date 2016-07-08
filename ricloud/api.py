import requests

from ricloud.conf import settings
from ricloud.backup import BackupClient
from ricloud.acc_management import AccManagementClient
from ricloud.exceptions import TwoFactorAuthenticationRequired


class RiCloud(object):
    """Primary objects for dealing with the API."""
    _backup_client_class = BackupClient
    _accmanagement_client_class = AccManagementClient

    headers = {
        'Accept': 'application/vnd.icloud-api.v%s' % settings.get('DEFAULT', 'api_version'),
        }

    def __init__(self, user=None, key=None):
        """Initialize our client API instance

        Keyword Arguments:
        user        -- User ID to authenticate against
        key         -- Corresponding authentication KEY supplied by Reincubate
        """
        self.user = user if user else settings.get('auth', 'user')
        self.key = key if key else settings.get('auth', 'key')
        self.auth = (self.user, self.key)

        # These are only ever stored between 2FA requests to prevent
        # having to ask the user's details again.
        self.apple_id = None
        self.password = None

        self.session_key = None
        self.devices = {}

        # If 2FA is active on this account, then the trusted device list
        # will be populated once a login is attempted
        self.trusted_devices = []

        # Data from iCloud, populated once logged in and request_data
        # has been called.
        self.data = {}

        self.backup_client = RiCloud._backup_client_class(self)
        self.acc_management_client = RiCloud._accmanagement_client_class(self)

    def login(self, apple_id, password):
        """Log into the iCloud

        Keyword Arguments:
        apple_id    -- User's apple ID
        password    -- User's apple password
        """
        data = {
            "email": apple_id,
            "password": password,
        }

        if self.session_key:
            data['key'] = self.session_key

        response = requests.post(settings.get('endpoints', 'login'),
                                 auth=self.auth, data=data,
                                 headers=self.headers)

        if response.ok:
            # We've logged in successfully
            data = response.json()
            self.session_key = data['key']
            self.devices = data['devices']

            # Clear memory cache of apple credentials
            # These may or may not be set, but better to be on the safe side.
            self.apple_id = None
            self.password = None

        elif response.status_code == 409:
            data = response.json()
            error = data['error']

            if error == '2fa-required':
                # 2fa has been activated on this account
                self.trusted_devices = data['data']['trustedDevices']
                self.session_key = data['data']['key']
                self.apple_id = apple_id
                self.password = password

                raise TwoFactorAuthenticationRequired(
                    'This user has 2FA enabled, please select a device '
                    'and request a challenge.'
                    )
        else:
            # Unhandled response
            response.raise_for_status()

    def request_2fa_challenge(self, challenge_device):
        """Request a 2FA challenge to the supplied trusted device"""
        data = {
            'challenge': challenge_device,
            'key': self.session_key,
        }

        response = requests.post(settings.get('endpoints', 'challenge_2fa'), auth=self.auth,
                                 data=data, headers=self.headers)

        if response.ok:
            # The challenge has been processed, we now need to wait
            # for the user's submission
            pass
        else:
            # Unhandled respnose
            response.raise_for_status()

    def submit_2fa_challenge(self, code):
        """Submit a user supplied 2FA challenge code"""
        data = {
            'code': code,
            'key': self.session_key,
        }

        response = requests.post(settings.get('endpoints', 'submit_2fa'), auth=self.auth,
                                 data=data, headers=self.headers)

        if response.ok:
            # Retry login
            return self.login(apple_id=self.apple_id, password=self.password)
        else:
            # Unhandled respnose
            response.raise_for_status()
