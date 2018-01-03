import os
import re
import json
import time
import mock
import shutil
import MySQLdb
import subprocess

from ricloud.listener import Listener
from ricloud.asmaster_listener import (
    AsmasterSystemHandler, AsmasterFeedHandler, AsmasterMessageHandler, AsmasterDownloadFileHandler, database_handler
)
from ricloud import conf


SMS_FILE_ID = '3d0d7e5fb2ce288813306e4d4636395e047a3d28'
DOWNLOAD_FILE_HEADER = {
    "type": "download-file",
    "service": "iCloud",
    "account_id": 1987654321,
    "device_id": 1234567890,
    "device_tag": "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d",
    "file_id": SMS_FILE_ID,
}
SAMPLE_FILE_CONTENTS = "Sample file"


def process_consumed_task_sync(task):
    task.trigger_callback()


class TestAsmasterListener(object):
    DB_NAME = 'ricloud_test'

    def setup(self):
        self.remove_test_db()

        test_schema_path = "sql/create_schema_test.sql"
        with open("sql/create_schema.sql", "r") as original:
            with open(test_schema_path, "w+") as test:
                for line in original.readlines():
                    test.write(line.replace("ricloud", self.DB_NAME))

        subprocess.check_output(
            "mysql -u {} -p{} -h {} -P {} < {}".format(
                conf.LISTENER_DB_USER, conf.LISTENER_DB_PASSWORD,
                conf.LISTENER_DB_HOST, conf.LISTENER_DB_PORT, test_schema_path
            ),
            shell=True
        )
        os.remove(test_schema_path)

        self.conn = MySQLdb.connect(
            host=conf.LISTENER_DB_HOST,
            port=int(conf.LISTENER_DB_PORT),
            user=conf.LISTENER_DB_USER,
            passwd=conf.LISTENER_DB_PASSWORD,
            db=self.DB_NAME,
        )
        cursor = self.conn.cursor()
        self.counts = {}
        for table in ['feed', 'file', 'message', 'system']:
            self.counts[table] = cursor.execute("SELECT * FROM {}".format(table))

        api = mock.MagicMock()
        api.append_consumed_task = process_consumed_task_sync
        handlers = [AsmasterSystemHandler, AsmasterFeedHandler, AsmasterMessageHandler, AsmasterDownloadFileHandler]
        handlers_dict = dict((handler.TYPE, handler(api=api)) for handler in handlers)
        self.listener = Listener(handlers_dict)

    def new_lines(self, table):
        self.conn.commit()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM {}".format(table))
        return cursor.fetchall()

    @staticmethod
    def load_json_from_sql(sql_string):
        return json.loads(sql_string.decode('string-escape').strip('"'))

    def teardown(self):
        self.conn.close()
        self.remove_test_db()

        if os.path.isdir(conf.OUTPUT_DIR):
            shutil.rmtree(conf.OUTPUT_DIR)

    @classmethod
    def remove_test_db(cls):
        with MySQLdb.connect(
            host=conf.LISTENER_DB_HOST,
            port=int(conf.LISTENER_DB_PORT),
            user=conf.LISTENER_DB_USER,
            passwd=conf.LISTENER_DB_PASSWORD,
        ) as cursor:
            cursor.execute("DROP DATABASE IF EXISTS {};".format(cls.DB_NAME))

    def test_system_messages(self):
        stream = """
            {"message": "Message streaming has begun.",
             "code": "sample-code"}
        """
        headers = '{"type": "system"}'

        self.listener.on_message(headers, stream)
        time.sleep(0.1)
        result = self.new_lines('system')

        assert len(result) == 1

        result = result[0]

        assert len(result[2]) == len(headers)
        assert self.load_json_from_sql(result[3])["code"] == "sample-code"
        assert result[4] == "Message streaming has begun."
        assert result[5] == "sample-code"

    def test_long_system_messages(self):
        message = 'a' * 1000
        stream = '{"message": "' + message + '"}'

        self.listener.on_message('{"type": "system"}', stream)

        assert len(self.new_lines('system')) == 1

    def test_download_file_database_info(self):
        self.listener.on_message(json.dumps(DOWNLOAD_FILE_HEADER), SAMPLE_FILE_CONTENTS)

        result = self.new_lines('file')

        assert len(result) == 1

        result = result[0]

        assert result[1] == "iCloud"
        assert result[3] == DOWNLOAD_FILE_HEADER['account_id']
        assert result[4] == DOWNLOAD_FILE_HEADER['device_id']
        assert result[5] == DOWNLOAD_FILE_HEADER['device_tag']
        assert len(result[6]) == len(json.dumps(DOWNLOAD_FILE_HEADER))
        assert conf.OUTPUT_DIR in result[7]
        assert result[8] == DOWNLOAD_FILE_HEADER['file_id']

    def test_download_file_creates_file(self):
        self.listener.on_message(json.dumps(DOWNLOAD_FILE_HEADER), SAMPLE_FILE_CONTENTS)

        path = self.new_lines('file')[0][7]

        assert os.path.isfile(path)
        with open(path, 'r') as f:
            assert f.read() == SAMPLE_FILE_CONTENTS

    def test_download_file_long_filename(self):
        header = DOWNLOAD_FILE_HEADER
        header["file_id"] = "photo_library://127f718d304f10d8e23c1148759df433a7caf043bf8f28cbb9ce6c286458f140358b14e43c5d4e6fd09aff1ff9df6bac766cdb71755bc2eeb8fa79368d53e53ecce4bea41ebe4cdbea50c18e92413b1069d6d8c6ee8c91e1dc0e735680049176118e70aa88add4edde3e416154595f8f3c85d88da2a5642ea8ed4b728fad132310e5f4b39b26178dacf82df96a52c5b9754e48cd8870ca107aaf4a2356b628dd52f88b235cf988d3ad3515e4054f977a9229fc066b882b0c6a85f228a9e6b2342207f6bcb706a4eca5b0e423cdf798f1575192df674a319f6775f03ec94c348518489dc5107a73ec521e6f76a867f1fb982c78d6b958becbf227e02d8e92694f228a2d776fbcaa6e232779b8f1538b556e09121a6786b9fd8602903eba0a9d5f9df6d1f027229524874b2387001276fc9c0d85d5b245283cd3bfad419d61a5df9f14ce0dbe66a35f60b13b15da6c43d13cf0d9535dea7d940538818d6d721d9546ea80340b60cdb88dff4232ec52ebacd3d0e12348323f364babefc4498fa707e0ce8da9a38f79c4d0249b2f1d26a2338e2b5f456d9ab37bbea8ffe12796de14bafe4c4b93824b91c0c03ca9244fa87d900d42141a41b939197e1cbd0b5033bc2904fe0fc1d152f4e331a717c8d3bc07378fb68bf80b451a5eb7021f777c73bd7acc3e084cf0430835e571fae047b51d176531163d3344b6e706bd46cdb194748bc05312d368a48f0dcce4a5e244330747a79afb0b25aa92a8f4fdeaf37aaa889036e2be29655703924e95a27159ec97760312b5fe8235d85301071154a0c42a2fbaab482581a03684900942609bae03380ee5bd6a68791ebb12055327f2496408ea6a53f4031296e9dff061f5e45b792cc50f04989d11f020f71afa81ae2418bb3f427eddcd30355f98a2240780c9e429bef34aea606740657ac32c89f4c0dab4482d26cb0daf996edd94e096019e440aa63d33f912dda9393dbb418e3e89b54b530147ed38da1a4fb1ff793fa004065a79c2335408a3fdceb718560500222d60806f7a98a4695ea92228dceae008e35a3c6a544f50d683de7c20621dbe7d8e1f31f29d83249b1d2707f784ba42e3b6224d4e201f28bac792007bc997eaf375fa891fd1b3a80598c35c6457800d34b"

        self.listener.on_message(json.dumps(DOWNLOAD_FILE_HEADER), SAMPLE_FILE_CONTENTS)

        result = self.new_lines('file')[0]

        assert result[8] == DOWNLOAD_FILE_HEADER['file_id']

        path = result[7]

        assert os.path.isfile(path)
        with open(path, 'r') as f:
            assert f.read() == SAMPLE_FILE_CONTENTS

    def test_feeds(self):
        header = {
            "type": "fetch-data",
            "service": "iCloud",
            "account_id": 1987654321,
            "device_id": 1234567890,
            "device_tag": "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d",
        }
        feed = {
            "sms": [{
                "conversation_id": "+447910000000",
                "from_me": False,
                "handle": "vodafone",
                "attachments": [],
                "deleted": False,
                "type": "SMS",
                "date": "2016-09-16 11:52:53.000000",
                "text": "Welcome to Vodafone!",
                "group_handles": None,
                "id": 1
              }]
            }

        self.listener.on_message(json.dumps(header), json.dumps(feed))

        result = self.new_lines('feed')

        assert len(result) == 1

        js = self.load_json_from_sql(result[0][7])

        assert js['sms'][0]['text'] == "Welcome to Vodafone!"

    def test_message(self):
        header = {
            "type": "message",
            "service": "iCloud",
            "account_id": 1987654321,
            "device_id": 1234567890,
            "device_tag": "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d",
        }
        feed = {
            "message": "Login successful",
            "success": True
        }

        self.listener.on_message(json.dumps(header), json.dumps(feed))

        result = self.new_lines('message')

        assert len(result) == 1

        result = result[0]

        assert result[1] == "iCloud"
        assert result[3] == header['account_id']
        assert result[4] == header['device_id']
        assert result[5] == header['device_tag']
        assert len(result[6]) == len(json.dumps(header))

        js = self.load_json_from_sql(result[7])

        assert js['message'] == "Login successful"


class TestFileIdToFileName(object):
    def test_normal_fileid(self):
        assert AsmasterDownloadFileHandler.file_id_to_file_name(SMS_FILE_ID) == SMS_FILE_ID

    def test_alterate_fileid(self):
        result = AsmasterDownloadFileHandler.file_id_to_file_name("dtouch://749301")
        assert 43 == len(result)
        assert re.match("^[a-z0-9_]+$", result)
