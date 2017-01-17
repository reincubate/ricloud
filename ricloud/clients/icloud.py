from .base import BaseClient, sync


class iCloudClient(BaseClient):
    service = 'iCloud'

    @property
    def available_data(self):
        if 'permissions' in self.ricloud.api.services['iCloud']['Fetch Data']:
            return self.ricloud.api.services['iCloud']['Fetch Data']['permissions']['data']
        else:
            return None

    @sync
    def login(self, account, password):
        return self.ricloud.api.perform_task(
            service=self.service,
            task_name='log-in',
            account=account,
            payload={
                'password': password,
            },
        )

    @sync
    def start_2fa_auth(self, account, challenge=None):
        payload = {}

        if challenge is not None:
            payload['challenge'] = challenge

        return self.ricloud.api.perform_task(
            service=self.service,
            task_name='perform-2fa-challenge',
            account=account,
            payload=payload
        )

    @sync
    def finish_2fa_auth(self, account, code):
        return self.ricloud.api.perform_task(
            service=self.service,
            task_name='submit-2fa-challenge',
            account=account,
            payload={
                'code': code,
            },
        )

    def devices(self, account):
        return self.ricloud.api.perform_task(
            service=self.service,
            task_name='list-devices',
            account=account,
            payload={},
            callback=None)

    def data(self, account, device, data, callback=None):
        return self.ricloud.api.perform_task(
            service=self.service,
            task_name='fetch-data',
            account=account,
            payload={
                'data': data,
                'device': device
            },
            callback=callback
        )

    def download_file(self, account, device, file, callback=None):
        return self.ricloud.api.perform_task(
            service=self.service,
            task_name='download-file',
            account=account,
            payload={
                'file': file,
                'device': device,
            },
            callback=callback
        )
