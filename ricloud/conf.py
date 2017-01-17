import os
import ConfigParser


def get_config(config_name='ricloud.ini'):

    config = ConfigParser.RawConfigParser()
    path_to_config = os.path.join(os.path.dirname(__file__), config_name)

    home_path = os.path.expanduser(os.path.join('~', '.%s' % config_name))
    paths = [path_to_config, home_path]

    if 'RICLOUD_CONF' in os.environ:
        paths.append(os.environ['RICLOUD_CONF'])

    config.read(paths)

    return config


settings = get_config()

BASE_DIR = os.getcwd()

OUTPUT_DIR = os.path.join(BASE_DIR, settings.get('output', 'output_directory'))

LOG_DIRECTORY = os.path.join(BASE_DIR, settings.get('logging', 'logs_directory'))

DEFAULT_LOG = os.path.join(LOG_DIRECTORY, 'ricloud.log')
