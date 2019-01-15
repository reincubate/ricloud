from __future__ import absolute_import

import sys

PY3 = sys.version_info[0] >= 3

if PY3:
    from collections.abc import MutableMapping, MutableSequence
    from configparser import RawConfigParser
    from urllib.parse import urljoin, urlsplit, quote

    def want_bytes(data):
        return data.encode("utf-8") if isinstance(data, str) else data

    def want_text(data):
        return data.decode("utf-8") if isinstance(data, bytes) else data


else:
    from collections import MutableMapping, MutableSequence
    from ConfigParser import RawConfigParser
    from urlparse import urljoin, urlsplit
    from urllib import quote

    def want_bytes(data):
        return data.encode("utf-8") if isinstance(data, unicode) else data

    def want_text(data):
        return data.decode("utf-8") if isinstance(data, str) else data
