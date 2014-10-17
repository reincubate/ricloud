import json
import os
import shutil
from functools import wraps

from ricloud.conf import settings, get_config
from ricloud.api import ICloudApi
from ricloud.exceptions import TwoFactorAuthenticationRequired
from ricloud.tests.responses_registration import register_valid_responses, register_2fa_responses
import responses
import pytest

WORKSPACE_ROOT = os.path.join(os.path.dirname(__file__), 'workspace')

def setup_module(module):
    try:
        shutil.rmtree(WORKSPACE_ROOT)
    except:
        pass

    os.makedirs(WORKSPACE_ROOT)


def toggle_responses(func):
    """Will default to cached responses unless env variable is set."""
    @wraps(func)
    def inner(*args, **kwargs):
        if os.environ.get('RUN_LIVE_TESTS', False):
            return func(*args, **kwargs)
        return responses.activate(func)(*args, **kwargs)
    return inner

class TestLogIn:
    @toggle_responses
    def test_log_in(self):
        """Can we log in successfull to the API?"""
        register_valid_responses()
        api = ICloudApi(user=settings.get('test', 'user'), key=settings.get('test', 'key'))
        api.login(apple_id=settings.get('test', 'apple_id'), password=settings.get('test', 'password'))

    @toggle_responses
    def test_2fa_required(self):
        """What happens when 2FA is enabled?"""
        register_2fa_responses()
        api = ICloudApi(user=settings.get('test', 'user'), key=settings.get('test', 'key'))

        try:
            api.login(apple_id=settings.get('test', 'apple_id'), password=settings.get('test', 'password'))
            raise pytest.skip('2FA is not enabled for this account.')
        except TwoFactorAuthenticationRequired:
            pass

        # The trusted devices fields should now be populated
        assert len(api.trusted_devices) > 0

class TestDataDownload():
    @toggle_responses
    def test_download_everything(self):
        """Can we download all the things?"""
        register_valid_responses()
        api = ICloudApi(user=settings.get('test', 'user'), key=settings.get('test', 'key'))
        api.login(apple_id=settings.get('test', 'apple_id'), password=settings.get('test', 'password'))

        for device_id in api.devices.keys():
            data = api.backup_client.request_data(device_id=device_id)

            assert data is not None

            # Dump the data to our workspace folder for perusal
            filename = '%s.json' % api.devices[device_id]['device_name']
            with open(os.path.join(WORKSPACE_ROOT, filename), 'wb') as out:
                json.dump(data, out, indent=4)

            if len(data['photos']) > 0 and data['photos'][0] != 'Upgrade to view this data.':
                # We have some photos, let's download them too

                for photo in data['photos']:
                    filename = photo['filename']
                    file_id = photo['file_id']

                    with open(os.path.join(WORKSPACE_ROOT, filename), 'wb') as out:
                        api.backup_client.download_file(device_id=device_id, file_id=file_id, out=out)

class TestConfig():
    @classmethod
    def setup_class(cls):
        os.environ['RICLOUD_CONF_OLD'] = os.environ.get('RICLOUD_CONF', '')
        os.environ['RICLOUD_CONF'] = os.path.join(os.path.dirname(__file__), 'test_config.ini')

    @classmethod
    def teardown_class(cls):
        if os.environ['RICLOUD_CONF_OLD']:
            os.environ['RICLOUD_CONF'] = os.environ['RICLOUD_CONF_OLD']
        else:
            del os.environ['RICLOUD_CONF']
        del os.environ['RICLOUD_CONF_OLD']

    def test_config_through_environment(self):
        """Can we set an env variable to override settings?"""
        conf = get_config()

        assert conf.get('auth', 'user') == "TEST USER"
        assert conf.get('auth', 'password') == "NOT A REAL PASSWORD"
