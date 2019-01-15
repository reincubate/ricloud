from __future__ import absolute_import, unicode_literals

import os
import csv
import json
import time
import uuid
import base64
import decimal
import hashlib
import logging
import datetime

from collections import OrderedDict

import ricloud
from ricloud import compat
from ricloud import conf


logger = logging.getLogger('ricloud')
log_level = logging.getLevelName(conf.get("logging", "log_level"))
logger.setLevel(log_level)


def log_debug(message, *args, **kwargs):
    logger.debug(message, *args, **kwargs)


def log_info(message, *args, **kwargs):
    logger.info(message, *args, **kwargs)


def generate_timestamp():
    return int(time.time())


def _encode(data):
    """Adapted from Django source:
    https://github.com/django/django/blob/master/django/core/serializers/json.py
    """
    if isinstance(data, datetime.datetime):
        r = data.isoformat()
        if data.microsecond:
            r = r[:23] + r[26:]
        if r.endswith("+00:00"):
            r = r[:-6] + "Z"
        return r
    elif isinstance(data, datetime.date):
        return data.isoformat()
    elif isinstance(data, datetime.time):
        r = data.isoformat()
        if data.microsecond:
            r = r[:12]
        return r
    elif isinstance(data, datetime.timedelta):
        return data.total_seconds()
    elif isinstance(data, (decimal.Decimal, uuid.UUID)):
        return str(data)
    elif isinstance(data, ricloud.resources.abase.ABResource):
        return data.id


class DataEncoder(json.JSONEncoder):
    def default(self, data):
        encoded_data = _encode(data)

        if encoded_data is None:
            return super(DataEncoder, self).default(data)

        return encoded_data


def encode_json(data, indent=None):
    return json.dumps(data, indent=indent, cls=DataEncoder, ensure_ascii=False)


def decode_json(data):
    return json.loads(data, object_pairs_hook=OrderedDict)


def encode_b64(data):
    return base64.b64encode(data)


def decode_b64(data):
    return base64.b64decode(data)


def transform_csv_file_to_json(file_object):
    """Transforms a one line CSV to a JSON dictionary."""
    csv_dictionary = list(csv.DictReader(file_object))[0]
    return dict(
        (key.lower().replace(" ", "_"), value) for key, value in csv_dictionary.items()
    )


def join_url(base, url, allow_fragments=True):
    return compat.urljoin(base, url, allow_fragments=allow_fragments)


def get_url_path(url):
    return compat.urlsplit(url).path


def escape(string):
    return compat.quote(string, safe="")


def get_md5_hash(data, hex_encode=True):
    md5_hash = hashlib.md5(compat.want_bytes(data))

    return md5_hash.hexdigest() if hex_encode else md5_hash.digest()


def get_path_extension(path):
    _, extension = os.path.splitext(path)
    return extension


def get_directory_from_path(path):
    return os.path.split(path)[0]


def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def ensure_path_exists(path):
    directory = get_directory_from_path(path)
    ensure_directory_exists(directory)


def get_filename(*args):
    output_directory = conf.get("samples", "output_directory")

    if not os.path.isabs(output_directory):
        output_directory = os.path.join(os.getcwd(), output_directory)

    path = os.path.join(output_directory, *args)

    ensure_path_exists(path)

    return path
