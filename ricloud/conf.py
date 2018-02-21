import os
import logging
import ConfigParser


def get_config(config_name='ricloud.ini'):
    config = ConfigParser.RawConfigParser()

    path_to_config = os.path.join(os.path.dirname(__file__), config_name)  # Read defaults.

    home_path = os.path.expanduser(os.path.join('~', '.%s' % config_name))  # Read user config.

    paths = [path_to_config, home_path]

    if 'RICLOUD_CONF' in os.environ:
        paths.append(os.environ['RICLOUD_CONF'])

    config.read(paths)

    return config


settings = get_config()

BASE_DIR = os.getcwd()

OUTPUT_DIR = os.path.join(BASE_DIR, settings.get('output', 'output_directory'))

LOG_DIRECTORY = os.path.join(BASE_DIR, settings.get('logging', 'logs_directory'))
LOG_FILE = os.path.join(LOG_DIRECTORY, 'ricloud.log')
LOG_LEVEL = settings.get('logging', 'level')

if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)

logging.basicConfig(
    filename=LOG_FILE,
    filemode='a',
    format='[%(asctime)s: %(levelname)s/%(processName)s/%(thread)d] [%(name)s:%(lineno)s] %(message)s',
    level=LOG_LEVEL
)

LISTENER_DB_HOST = settings.get('mysql', 'host')
LISTENER_DB_PORT = settings.get('mysql', 'port')
LISTENER_DB_NAME = settings.get('mysql', 'database')
LISTENER_DB_USER = settings.get('mysql', 'username')
LISTENER_DB_PASSWORD = settings.get('mysql', 'password')

TEMPFILE_TIMEOUT = settings.getint('tempfiles', 'timeout')
TEMPFILE_TIMEOUT_CHECK_INTERVAL = settings.getint('tempfiles', 'timeout_check_interval')
