import os
import re
import json
import shutil
import logging
import hashlib
import MySQLdb

from .ricloud import RiCloud
from .listener import Listener
from .handlers import RiCloudHandler, StreamError
from . import conf


class AsmasterListener(RiCloud):
    def __init__(self, timeout):
        self.timeout = timeout
        super(AsmasterListener, self).__init__(
            listener=Listener({'__ALL__': DatabaseWrtingHandler()}),
        )

    @property
    def stream_thread_is_daemon(self):
        return False


class DatabaseWrtingHandler(RiCloudHandler):
    def __init__(self, api=None, callback=None, db=conf.LISTENER_DB_NAME, file_location=conf.OUTPUT_DIR):
        self.db = db
        self.file_location = file_location
        super(DatabaseWrtingHandler, self).__init__(api, callback)

    _db_con = None

    @property
    def db_con(self):
        if not self._db_con:
            self._db_con = MySQLdb.connect(
                host=conf.LISTENER_DB_HOST,
                port=int(conf.LISTENER_DB_PORT),
                user=conf.LISTENER_DB_USER,
                passwd=conf.LISTENER_DB_PASSWORD,
                db=self.db
            )
        return self._db_con

    def handle_query(self, query, args=None, retry=2):
        try:
            cursor = self.db_con.cursor()
            cursor.execute(query, args=args)
            self.db_con.commit()
        except (AttributeError, MySQLdb.OperationalError):
            if not retry:
                raise

            logging.warn('asmaster listener handler query failed, attempting to refresh database connection.')
            self._db_con = None
            self.handle_query(query, args=args, retry=retry - 1)

    def on_complete_message(self, header, stream):
        if header['type'] == 'system':
            body = stream.read()
            json_body = json.loads(body)

            try:
                code = json_body['code'][:200]
            except KeyError:
                code = None

            query = """
                INSERT INTO system (`received`, `headers`, `body`, `message`, `code`)
                VALUES (NOW(), %(headers)s, %(body)s, %(message)s, %(code)s)
            """

            args = {
                "headers": json.dumps(header),
                "body": body,
                "message": json_body['message'][:200],
                "code": code,
            }

            self.handle_query(query, args)

            if "error" in body:
                raise StreamError(body)

        elif header['type'] in {'fetch-data', 'message'}:
            if header['type'] == 'fetch-data':
                table = 'feed'
            else:
                table = header['type']

            query = """
                INSERT INTO {table} (`service`, `received`, `account_id`, `device_id`, `device_tag`, `headers`, `body`)
                VALUES (%(service)s, NOW(), %(account_id)s, %(device_id)s, %(device_tag)s, %(headers)s, %(body)s)
            """.format(table=table)  # noqa

            args = {
                "table": table,
                "service": header['service'],
                "account_id": header.get('account_id', None),
                "device_id": header.get('device_id', None),
                "device_tag": header.get('device_tag', None),
                "headers": json.dumps(header),
                "body": json.dumps(stream.read()),
            }

            self.handle_query(query, args)

        elif header['type'] == 'download-file':
            try:
                file_id = header['file_id']
            except KeyError:
                raise StreamError("Invalid download file request, no file_id")
            if len(file_id) > 4096:
                raise StreamError("Invalid download file request, file_id is too long")

            file_path = self.save_stream_to_file(header, stream, self.file_location)

            query = """
                INSERT INTO file (`service`, `received`, `account_id`, `device_id`, `device_tag`, `headers`, `location`, `file_id`)
                VALUES (%(service)s, NOW(), %(account_id)s, %(device_id)s, %(device_tag)s, %(headers)s, %(location)s, %(file_id)s)
            """  # noqa

            args = {
                "service": header['service'],
                "account_id": header.get('account_id', None),
                "device_id": header.get('device_id', None),
                "device_tag": header.get('device_tag', None),
                "headers": json.dumps(header),
                "location": file_path,
                "file_id": file_id,
            }

            self.handle_query(query, args)

        else:
            raise StreamError("Unrecognised header type {}".format(header['type']))

    @classmethod
    def save_stream_to_file(cls, header, stream, file_location):
        filename = cls.file_id_to_file_name(header['file_id'])
        path = os.path.join(
            file_location,
            header['service'],
            "{}".format(header.get('account_id', "None")),
            str(header.get('device_id', "None")),
            filename,
        )

        if len(path) > 250:
            raise StreamError("File path too long, unable to save stream.")

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        if os.path.isfile(path):
            os.remove(path)

        with open(path, 'w') as f:
            shutil.copyfileobj(stream, f)

        return path

    @staticmethod
    def file_id_to_file_name(file_id):
        """
        Sometimes file ids are not the file names on the device, but are instead generated
        by the API. These are not guaranteed to be valid file names so need hashing.
        """
        if len(file_id) == 40 and re.match("^[a-f0-9]+$", file_id):
            return file_id
        # prefix with "re_" to avoid name collision with real fileids
        return "re_{}".format(hashlib.sha1(file_id).hexdigest())
