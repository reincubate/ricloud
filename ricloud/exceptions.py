class ApiException(Exception):

    def __init__(self, response, url, data):
        self.content = response.content
        self.json = response.json()
        self.error = self.json['error']
        self.status_code = response.status_code
        self.curl = self._curl_request(url, data)

    def __str__(self):
        sc_str = 'status-code: {0}\n'.format(self.status_code)
        err_str = 'error: {0}\n'.format(self.error)
        fr_str = 'full reply: {0}\n'.format(self.json)
        curl_str = 'curl request: {0}\n'.format(self.curl)

        return str(sc_str + err_str + fr_str + curl_str)

    def _curl_request(self, url, data):
        curl_call = "curl -L -v -X POST --user \"USER:KEY\" --header "\
                    "Accept: application/vnd.icloud-api.v1"
        curl_data = ''
        for e in data:
            curl_data = curl_data+' --data-urlencode \"{0}={1}\"'.format(e, data[e])
        curl_url = ' ' + url
        return curl_call + curl_data + curl_url


class TwoFactorAuthenticationRequired(Exception):
    pass


class AccManagementException(ApiException):
    pass


class BackupException(ApiException):
    pass


class InputError(Exception):

    def __init__(self, msg):
        self.msg

    def __str__(self):
        return str(self.msg)
