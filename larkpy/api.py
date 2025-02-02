from __future__ import annotations
import requests
import json

from typing import List, Dict
from typing_extensions import Literal


class FeishuAPI():

    def __init__(self, app_id, app_secret) -> None:
        tenant_access_token = self._get_access_token(app_id, app_secret)
        self.access_token = tenant_access_token
        self.headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': f'Bearer {self.access_token}'
        }

    def request(self,
                method: Literal['GET', 'POST', 'PUT', 'DELETE'],
                url: str,
                payload: Dict = None):
        return requests.request(method,
                                url,
                                headers=self.headers,
                                json=payload)

    def _get_access_token(self, app_id, app_secret):
        """获取访问凭证"""
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
        data = {"app_id": app_id, "app_secret": app_secret}
        response = requests.post(url, json=data)
        response_data = response.json()
        return response_data["tenant_access_token"]

    def get_node(self,
                 token: str,
                 obj_type: Literal['doc', 'docx', 'sheet', 'mindnote',
                                   'bitable', 'file', 'slides',
                                   'wiki'] = None):
        # https://open.feishu.cn/document/server-docs/docs/wiki-v2/space-node/get_node
        url = f'https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node?token={token}'
        if obj_type is not None:
            url += f'&obj_type={obj_type}'
        response = requests.request("GET", url, headers=self.headers)
        data = response.json()
        node = data['data']['node']
        return node  # ['obj_token']
