from __future__ import absolute_import

__version__ = "3.2.0"

from ricloud import conf

token = conf.get("api", "token")
url = conf.get("api", "url")

from ricloud.resources import *  # NOQA

# Set default logging handler to avoid "No handler found" warnings.
import logging  # NOQA
from logging import NullHandler  # NOQA

logging.getLogger(__name__).addHandler(NullHandler())
