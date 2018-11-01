import time
import logging
import tempfile

from collections import OrderedDict

from datetime import datetime

from . import conf


logger = logging.getLogger(__name__)


class LogHelper(object):

    LOG_MESSAGES = {
        'stream_heartbeat': '-*- Heartbeat -*-',
        'stream_start': 'Starting ricloud listener stream thread.',
        'stream_restart': 'Restarting ricloud listener stream thread.',
        'stream_failed_check': 'Uptime check failed on ricloud listener stream thread.',
        'stream_error': 'Error occurred in listener stream thread.',
        'listener_worker_start': 'Starting ricloud listener worker thread.',
        'listener_worker_error': 'Error occurred in listener worker thread.',
    }

    @classmethod
    def get_message(cls, message):
        return cls.LOG_MESSAGES.get(message)

    @classmethod
    def get_status(cls):
        return {
            'last_messages': dict((key, cls._get_latest_message(key)) for key in cls.LOG_MESSAGES),
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f'),
        }

    @classmethod
    def _get_latest_message(cls, message):
        message_content = cls.get_message(message)

        with open(conf.LOG_FILE, 'r') as log_file:
            latest_message_line = ''

            for line in log_file:
                if message_content in line:
                    latest_message_line = line

        latest_message = latest_message_line[1:].split(': ', 1)[0]

        return latest_message or 'No occurrence in log file or log level is too high.'


class TemporaryFileHandler(object):
    TIMEOUT = conf.TEMPFILE_TIMEOUT
    CHECK_INTERVAL = conf.TEMPFILE_TIMEOUT_CHECK_INTERVAL

    def __init__(self):
        self.handles = OrderedDict()

        self._last_check = time.time()

    def get(self, handle_id):
        if handle_id not in self.handles:
            self.handles[handle_id] = {
                'handle': tempfile.NamedTemporaryFile(),
                'timestamp': time.time(),
            }
        return self.handles[handle_id]['handle']

    def delete(self, handle_id):
        del self.handles[handle_id]  # Delete the reference but don't close here.

    def check_expiries(self):
        time_now = time.time()

        if (self._last_check + self.CHECK_INTERVAL) > time_now:
            return

        logger.info('Checking temporary file expiries.')

        self._last_check = time_now

        to_delete = []
        for handle_id, handle in self.handles.iteritems():  # These are ordered by time of insertion.
            if self._is_expired(handle['timestamp']):
                to_delete.append(handle_id)
            else:
                break  # Iterate until the first handle that is not expired.

        logger.info('Found %d expired files to remove.', len(to_delete))

        for handle_id in to_delete:
            self.handles[handle_id]['handle'].close()  # Nothing should be expecting this, so close it.
            del self.handles[handle_id]

    def _is_expired(self, timestamp):
        return (timestamp + self.TIMEOUT) < time.time()
