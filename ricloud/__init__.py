from __future__ import absolute_import

__version__ = "3.0.0rc0"

from ricloud import conf

token = conf.get("api", "token")
url = conf.get("api", "url")

from ricloud.resources import *


# Set default logging handler to avoid "No handler found" warnings.
import logging
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())
