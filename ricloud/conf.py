from __future__ import absolute_import

import os

from ricloud.compat import RawConfigParser


def get_config(config_name="ricloud.ini"):
    config = RawConfigParser()

    # Read defaults.
    default_conf = os.path.join(os.path.dirname(__file__), config_name)

    # Read user config. We look for these in the user's root directory.
    user_root_conf = os.path.expanduser(os.path.join("~", ".%s" % config_name))

    paths = [default_conf, user_root_conf]

    if "RICLOUD_CONF" in os.environ:
        paths.append(os.environ["RICLOUD_CONF"])

    config.read(paths)

    return config


settings = get_config()


def get(setting_section, setting_name):
    """Retrieves configuration from either the local env or conf files."""
    env_name = "RICLOUD_{}".format(setting_name.upper())

    if env_name in os.environ:
        return os.environ.get(env_name)

    return settings.get(setting_section, setting_name)


def getint(setting_section, setting_name):
    setting = get(setting_section, setting_name)

    try:
        return int(setting)
    except ValueError:
        return 0


def getboolean(setting_section, setting_name):
    setting = get(setting_section, setting_name)

    if not setting:
        return None

    return setting.lower() == "true"
