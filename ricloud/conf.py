import ConfigParser
import os


def get_config(config_name='ricloud.ini'):
    """Loop through all paths and find the config, starting here.

    :Note: We check the user's home directory for the config file as
    well as the `RICLOUD_CONF` environment variable.
    """
    config = ConfigParser.RawConfigParser()
    path_to_config = os.path.join(os.path.dirname(__file__), config_name)

    home_path = os.path.expanduser(os.path.join('~', '.%s' % config_name))
    paths = [path_to_config, home_path]

    if 'RICLOUD_CONF' in os.environ:
        paths.append(os.environ['RICLOUD_CONF'])

    config.read(paths)

    # Push paths into the config (if they don't already exist)
    if config.has_section('endpoints'):
        host = config.get('endpoints', 'host')
        endpoints = {
            'login': "%s/c/sign-in/",
            'challenge_2fa': "%s/c/perform-2fa-challenge/",
            'submit_2fa': "%s/c/submit-2fa-challenge/",
            'download_data': "%s/c/download-data/",
            'download_file': "%s/c/download-file/",
            'deactivation': "%s/c/client-management/deactivation/",
            'activation': "%s/c/client-management/activation/",
            }

        for key, uri in endpoints.iteritems():
            if not config.get('endpoints', key):
                config.set('endpoints', key, uri % host)

    return config

settings = get_config()
