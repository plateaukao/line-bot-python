import os
from linebot.http_client import (
        HttpClient, RequestsHttpClient,RequestsHttpResponse
)

proxies = {
        "http": os.environ['QUOTAGUARDSTATIC_URL'],
        "https": os.environ['QUOTAGUARDSTATIC_URL']
        }

class MyRequestsHttpClient(RequestsHttpClient):
    def __init__(self, timeout=HttpClient.DEFAULT_TIMEOUT):
        super(RequestsHttpClient, self).__init__(timeout)

    def get(self, url, headers=None, params=None, stream=False, timeout=None):
        if timeout is None:
            timeout = self.timeout

        response = requests.get(
            url, headers=headers, params=params, stream=stream, timeout=timeout, proxies = proxies
        )

        return RequestsHttpResponse(response)

    def post(self, url, headers=None, data=None, timeout=None):
        if timeout is None:
            timeout = self.timeout

        response = requests.post(
            url, headers=headers, data=data, timeout=timeout, proxies = proxies
        )

        return RequestsHttpResponse(response)

