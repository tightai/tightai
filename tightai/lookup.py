# AUTOGENERATED! DO NOT EDIT! File to edit: 04_lookup.py.ipynb (unless otherwise specified).

__all__ = ['Lookup']

# Cell
import requests
import tempfile
import os
import re
from io import BytesIO
import shutil
import json

# Cell
from .exceptions import RequestError
from .handlers import credentials
from .conf import API_ENDPOINT, CLI_ENDPOINT, USER_HOME

# Cell
class Lookup:
    '''
    API calls with headers built in
    '''
    api = CLI_ENDPOINT

    @classmethod
    def get_request_path(self, path, next_url=None):
        if path.startswith("http"):
            request_path = path
        else:
            if not path.startswith("/"):
                path = '/' + path
            request_path = "{api}{path}".format(api=self.api, path=path)
            if next_url is not None:
                request_path = next_url
        return request_path

    @classmethod
    def get_http_headers(self):
        token = credentials.get_encoded_token()
        authorization_header = f"Token {token}"
        return {'Authorization': authorization_header}

    @classmethod
    def perform_request(self, method, endpoint_path, data=None, next_url=None):
        headers = self.get_http_headers()
        path = self.get_request_path(endpoint_path)
        return requests.request(method, path, data=data, headers=headers)

    @classmethod
    def http_get(self, endpoint_path, next_url=None, **kwargs):
        return self.perform_request("get", endpoint_path, data=kwargs, next_url=next_url)

    @classmethod
    def http_put(self, endpoint_path, data={}, **kwargs):
        return self.perform_request("put", endpoint_path, data=data)

    @classmethod
    def http_delete(self, endpoint_path, data={}, **kwargs):
        return self.perform_request("delete", endpoint_path, data=data)

    @classmethod
    def http_post(self, endpoint_path, data={}, **kwargs):
        return self.perform_request("post", endpoint_path, data=data)

    @classmethod
    def handle_invalid_lookup(self, response, expected_status_code=200):
        r = response
        if not r.status_code == expected_status_code:
            try:
                msg = r.json()
            except:
                msg = r.text
            if isinstance(msg, dict):
                if "detail" in msg:
                    msg = msg['detail']
                else:
                    final_msg = []
                    for k, v in msg.items():
                        sub_v = v
                        if isinstance(v, list):
                            sub_v = ", ".join(v)
                        _msg = f"{k}: {sub_v}"
                        final_msg.append(_msg)
                    msg = final_msg
            if isinstance(msg, list):
                msg = ", ".join(msg)
            raise RequestError(f"{msg}", status=r.status_code)