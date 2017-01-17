import os
import mock

from ricloud.conf import get_config, settings


class TestsConfig(object):

    @mock.patch('ricloud.conf.ConfigParser')
    def test_gets_right_paths(self, mock_ConfigParser, monkeypatch):
        env_path = '../path/on/env/ricloud.ini'
        monkeypatch.setenv('RICLOUD_CONF', env_path)

        config_name = 'ricloud.ini'
        get_config(config_name=config_name)

        expected_paths = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ricloud', config_name),
            os.path.expanduser(os.path.join('~', '.%s' % config_name)),
            env_path
        ]

        mock_ConfigParser.RawConfigParser.return_value.read.assert_called_once_with(expected_paths)

    def test_ensure_all_sections_are_present(self):
        sections = [
            ('auth', ['token']),
            ('stream', ['stream_endpoint']),
            ('endpoints', ['account_information', 'register_account', 'task_status']),
            ('hosts', ['api_host', 'stream_host']),
        ]

        for section, options in sections:
            assert settings.has_section(section)
            for option in options:
                assert settings.has_option(section, option)

    @mock.patch.object(os.path, 'expanduser')
    def test_ensure_default_credentials_are_set(self, mock_os_path_expanduser):
        mock_os_path_expanduser.return_value = ''

        settings = get_config()

        assert 'your-ricloud-api-access-token-here' == settings.get('auth', 'token')
        assert 'your-aschannel-stream-name-here' == settings.get('stream', 'stream_endpoint')
