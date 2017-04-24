import os
import re
import json
import shutil
import hashlib
import logging
import MySQLdb
from io import BytesIO
from cached_property import cached_property

from .api import Api
from conf import (
    OUTPUT_DIR, LISTENER_DB_HOST, LISTENER_DB_PORT, LISTENER_DB_NAME,
    LISTENER_DB_USER, LISTENER_DB_PASSWORD
)
from .ricloud import RiCloud
from .listener import Listener
from .handlers import RiCloudHandler, StreamError
from .asmaster_api import AsmasterApi


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
    def __init__(self, api=None, callback=None, db=LISTENER_DB_NAME, file_location=OUTPUT_DIR):
        self.conn = MySQLdb.connect(
            host=LISTENER_DB_HOST,
            port=int(LISTENER_DB_PORT),
            user=LISTENER_DB_USER,
            passwd=LISTENER_DB_PASSWORD,
            db=db,
        )
        self.file_location = file_location
        super(DatabaseWrtingHandler, self).__init__(api, callback)
        
    def on_complete_message(self, header, stream):
        if header['type'] == 'system':
            body = stream.read()
            json_body = json.loads(body)
            try:
                code = json_body['code'][:200]
            except KeyError:
                code = None

            cursor = self.conn.cursor()

            cursor.execute("""
                INSERT INTO system (`received`, `headers`, `body`, `message`, `code`)
                VALUES (NOW(), %s, %s, %s, %s)""", (
                    json.dumps(header),
                    body,
                    json_body['message'][:200],
                    code,
                )
            )
            self.conn.commit()

            if "error" in body:
                raise StreamError(body)

        elif header['type'] in {'fetch-data', 'message'}:
            if header['type'] == 'fetch-data':
                table = 'feed'
            else:
                table = header['type']

            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO {} (`service`, `received`, `account_id`, `device_id`, `device_tag`, `headers`, `body`)
                VALUES (%s, NOW(), %s, %s, %s, %s, %s)""".format(table), (
                    header['service'],
                    header.get('account_id', None),
                    header.get('device_id', None),
                    header.get('device_tag', None),
                    json.dumps(header),
                    json.dumps(stream.read()),
                )
            )
            self.conn.commit()

        elif header['type'] == 'download-file':
            try:
                file_id = header['file_id']
            except KeyError:
                raise StreamError("Invalid download file request, no file_id")
            if len(file_id) > 4096:
                raise StreamError("Invalid download file request, file_id is too long")

            file_path = self.save_stream_to_file(header, stream, self.file_location)
            
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO file (`service`, `received`, `account_id`, `device_id`, `device_tag`, `headers`, `location`, `file_id`)
                VALUES (%s, NOW(), %s, %s, %s, %s, %s, %s)""", (
                    header['service'],
                    header.get('account_id', None),
                    header.get('device_id', None),
                    header.get('device_tag', None),
                    json.dumps(header),
                    file_path,
                    file_id,
                )
            )
            self.conn.commit()

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
