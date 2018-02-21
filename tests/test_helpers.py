import time
import mock

from ricloud.helpers import TemporaryFileHandler


class TestTemporaryFileHandler(object):

    def test_get(self):
        tfh = TemporaryFileHandler()

        handle_id = '1'
        handle = tfh.get(handle_id)

        assert hasattr(handle, 'read')
        assert handle_id in tfh.handles
        assert handle == tfh.handles[handle_id]['handle']
        assert tfh.handles[handle_id]['timestamp'] > 0

    def test_delete(self):
        tfh = TemporaryFileHandler()

        handle_id = '1'
        handle = tfh.get(handle_id)

        assert handle_id in tfh.handles

        tfh.delete(handle_id)

        assert handle_id not in tfh.handles
        assert not handle.closed

    def test_check_expiries(self):
        tfh = TemporaryFileHandler()
        tfh.CHECK_INTERVAL = 0  # Make sure we run full check.

        handle_id_1 = '1'
        handle_1 = tfh.get(handle_id_1)

        handle_id_2 = '2'
        handle_2 = tfh.get(handle_id_2)

        handle_id_3 = '3'
        handle_3 = tfh.get(handle_id_3)

        assert handle_id_1 in tfh.handles
        assert handle_id_2 in tfh.handles
        assert handle_id_3 in tfh.handles

        tfh.handles[handle_id_1]['timestamp'] = 0  # Make sure this one is expired.

        def tfh_is_expired(timestamp):  # Mock to check calls.
            return (timestamp + tfh.TIMEOUT) < time.time()

        tfh._is_expired = mock.MagicMock()
        tfh._is_expired.side_effect = tfh_is_expired

        tfh.check_expiries()

        assert handle_id_1 not in tfh.handles
        assert handle_id_2 in tfh.handles
        assert handle_id_3 in tfh.handles

        assert handle_1.closed
        assert not handle_2.closed
        assert not handle_3.closed

        assert tfh._is_expired.call_count == 2, 'Loop did not break on finding first non-expired item.'
