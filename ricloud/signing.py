from __future__ import absolute_import, unicode_literals

import hmac
import hashlib

from ricloud import compat
from ricloud.utils import encode_b64, decode_b64, generate_timestamp


DEFAULT_ALGORITHM = hashlib.sha256


def hmac_sign(message, key, algorithm=None):
    """Get a hmac signature of a message using the give key."""
    algorithm = algorithm or DEFAULT_ALGORITHM

    return hmac.new(
        compat.want_bytes(key), compat.want_bytes(message), digestmod=algorithm
    ).digest()


def hmac_verify(digest, message, key, algorithm=None):
    """Check a hmac signature is valid for a given message and key."""
    algorithm = algorithm or DEFAULT_ALGORITHM

    return hmac.compare_digest(hmac_sign(message, key), digest)


class Signature:
    """Helper for handling hmac signatures."""

    class SignatureError(Exception):
        """Generic signature error."""

    class InvalidSignatureHeader(SignatureError):
        """Signature header did not conform to the expected format."""

    class InvalidSignature(SignatureError):
        """Signature did not match the expected signature given the payload and secret."""

    class InvalidSignatureTimestamp(SignatureError):
        """Timestamp too old, not accepting signature as relevant."""

    def __init__(self, signature, timestamp):
        self.signature = signature
        self.timestamp = timestamp

    _header_format = "t={timestamp},s={signature}"

    def to_header(self):
        """Dump the signature to a header format."""
        signature = compat.want_text(encode_b64(self.signature))

        return Signature._header_format.format(
            timestamp=self.timestamp, signature=signature
        )

    @classmethod
    def from_header(cls, header):
        """Load a signature from a header string."""
        try:
            timestamp, signature = header.split(",", 1)

            timestamp = timestamp[2:]
            signature = signature[2:]

            signature = decode_b64(compat.want_bytes(signature))
        except Exception:
            raise Signature.InvalidSignatureHeader

        return Signature(signature, timestamp)

    @classmethod
    def sign(cls, data, secret):
        """Sign a bit of data with the given secret."""
        timestamp = compat.want_text(generate_timestamp())

        payload = cls._get_payload(data, timestamp)

        signature = hmac_sign(payload, secret)

        return Signature(signature, timestamp)

    def verify(self, data, secret, delta=None):
        """Verify a signature is valid for a given payload and secret."""
        payload = self._get_payload(data, self.timestamp)

        if not hmac_verify(self.signature, payload, secret):
            raise Signature.InvalidSignature

        if delta and (generate_timestamp() - self.timestamp) > delta:
            raise Signature.InvalidSignatureTimestamp

    @staticmethod
    def _get_payload(data, timestamp):
        return ".".join([timestamp, compat.want_text(data)])
