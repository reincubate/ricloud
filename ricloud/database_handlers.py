import logging
import MySQLdb

from . import conf


logger = logging.getLogger(__name__)


class DatabaseHandler(object):

    def __init__(self, db_name=conf.LISTENER_DB_NAME):
        logger.debug('Setting up DatabaseHandler for database `%s`.', db_name)
        self.db_name = db_name

    _db_con = None

    @property
    def db_con(self):
        if not self._db_con:
            logger.debug('Establishing new database connection to database `%s`.', self.db_name)
            import MySQLdb
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
