from __future__ import absolute_import

from ricloud.utils import encode_json, decode_json


class RicloudError(Exception):
    def __init__(self, status, content):
        self.status = status
        self.content = content

    def __repr__(self):
        return "RequestError(status={s.status}, content='{s.content}')".format(s=self)

    def __str__(self):
        return "status:{s.status}, content:{s.content}".format(s=self)


class RequestError(RicloudError):
    """Error response returned from the API."""

    def __init__(self, status, content):
        super(RequestError, self).__init__(status, content)

        self.error, self.message, self.params = self.parse_content(content)

    @staticmethod
    def parse_content(content):
        data = decode_json(content)
        error = data.get("error")
        message = data.get("message")
        params = data.get("params")
        return error, message, params

    def __str__(self):
        format_str = "status:{s.status}, error:{s.error}, message:'{s.message}'".format(
            s=self
        )

        if self.params:
            format_str += ", params:{params}".format(params=encode_json(self.params))

        return format_str


class ServerError(RicloudError):
    """A server error was returned from the API."""
