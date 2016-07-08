"""
Allows a client with the appropriate permissions to communnicate with the
account management endpoints of the icloudextractor-api.

"""

import requests

from ricloud.exceptions import InputError, AccManagementException
from ricloud.conf import settings


class AccManagementClient(object):
    """
    N.B.:   AccManagementException may be raised if the device_id or
            account_id are incorrect or the client does not have sufficient
            permissions to perform the account management action.
    """

    def __init__(self, api):
        self.api = api

    def deactivate_device(self, device_id):
        """
            Deactive a device.

            Args:
            device_id - the id of the device we wish to deactivate.

            Raises:
            AccManagementException - if status code response is not 200.
        """

        return self._perform_acc_management(
            {'device': device_id, 'action': 'deactivation'}
            )

    def activate_device(self, device_id):
        """
            Activate a device.

            Args:
            device_id - the id of the device we wish to activate.

            Raises:
            AccManagementException - if status code response is not 200.
        """

        return self._perform_acc_management(
            {'device': device_id, 'action': 'activation'}
            )

    def activate_account(self, account_id):
        """
            Activate an account.

            Args:
            account_id - the number of the account we wish to activate.

            Raises:
            AccManagementException - if status code response is not 200.
        """

        return self._perform_acc_management(
            {'account': account_id, 'action': 'activation'}
            )

    def deactivate_account(self, account_id):
        """
            Deactivate an account.

            Args:
            account_id - the number of the account we wish to deactivate.

            Raises:
            AccManagementException - if status code response is not 200.
        """

        return self._perform_acc_management(
            {'account': account_id, 'action': 'deactivation'}
            )

    def _perform_acc_management(self, data):

        post_data = {}
        post_data['key'] = self.api.session_key

        if 'account' in data and 'device' in data:
            raise InputError("A account and device cannot be"
                             " (de)activate simultaneously.")
        elif 'account' in data:
            post_data['account'] = data['account']
        elif 'device' in data:
            post_data['device'] = data['device']
        else:
            raise InputError("The device or account must be specified for"
                             " (de)activation.")
        url = settings.get('endpoints', data['action'])
        response = requests.post(url, auth=self.api.auth, data=post_data,
                                 headers=self.api.headers)

        if not response.ok:
            raise AccManagementException(response, url, post_data)

        return response.json()
