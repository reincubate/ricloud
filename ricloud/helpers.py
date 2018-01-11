import logging
import MySQLdb

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


class DatabaseHandler(object):

    def __init__(self, db_name=conf.LISTENER_DB_NAME):
        logger.debug('Setting up DatabaseHandler for database `%s`.', db_name)
        self.db_name = db_name

    _db_con = None

    @property
    def db_con(self):
        if not self._db_con:
            logger.debug('Establishing new database connection to database `%s`.', self.db_name)
            self._db_con = MySQLdb.connect(
                host=conf.LISTENER_DB_HOST,
                port=int(conf.LISTENER_DB_PORT),
                user=conf.LISTENER_DB_USER,
                passwd=conf.LISTENER_DB_PASSWORD,
                db=self.db_name
            )
        return self._db_con

    def handle_query(self, query, args=None, retry=2):
        try:
            cursor = self.db_con.cursor()
            cursor.execute(query, args=args)
            self.db_con.commit()
        except (AttributeError, MySQLdb.OperationalError):
            if not retry:
                logger.error('Query failed, no retries remaining.', exc_info=True)
                raise

            logger.warn('Query failed, attempting to refresh connection (%d retries remaining)', retry)
            self._db_con = None
            self.handle_query(query, args=args, retry=retry - 1)
