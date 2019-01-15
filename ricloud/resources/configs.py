from __future__ import absolute_import, unicode_literals

import json

from ricloud.utils import decode_json, transform_csv_file_to_json, get_path_extension

from . import abase
from .tasks import Task


class ABConfigResource(
    abase.CreatableResource, abase.ListableResource, abase.UpdatableResource
):
    @classmethod
    def test_with_id(cls, id):
        resource = cls(id=id)
        return resource.test()

    def test(self):
        test_url = self.instance_url + "/test"
        response = self.request_handler.get(test_url)
        return Task(attrs=response)


class StorageConfig(ABConfigResource):
    RESOURCE = "storage_config"
    RESOURCE_PATH = "configs/storage"

    @staticmethod
    def read_credentials_file(credentials_path):
        """A helper to read in credentials from the standard files exported by
        Google Cloud Platform's Service Account key generator (JSON) or Amazon
        IAM's use creation process (CSV).
        """
        file_extension = get_path_extension(credentials_path)

        with open(credentials_path, "r") as credentials_file:
            # CSVs must be explicit. Usually are when exported from AWS console.
            if file_extension == ".csv":
                credentials = transform_csv_file_to_json(credentials_file)
            else:
                # Assume we are dealing with a JSON encoded file here.
                try:
                    credentials = json.load(credentials_file)
                except ValueError:
                    raise Exception(
                        "Could not read credentials file. Needs to be either JSON or CSV."
                    )

        return credentials


class WebhookConfig(ABConfigResource):
    RESOURCE = "webhook_config"
    RESOURCE_PATH = "configs/webhook"
