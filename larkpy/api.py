from __future__ import annotations
import requests
import json

from typing import List, Dict
from typing_extensions import Literal
from ._typing import UserId


class LarkAPI():

    def __init__(self,
                 app_id: str,
                 app_secret: str,
                 user_id_type: UserId = None) -> None:
        tenant_access_token = self._get_access_token(app_id, app_secret)
        self.access_token = tenant_access_token
        self.headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': f'Bearer {self.access_token}'
        }

        self.user_id_type = user_id_type  # default is "open_id"

    def request(self,
                method: Literal['GET', 'POST', 'PUT', 'DELETE'],
                url: str,
                payload: Dict = None,
                params: Dict = None):
        if params is not None:
            for key in ["user_id_type"]:
                if key in params:
                    params[key] = params[key] or self.__dict__[key]
            params_string = "&".join([
                f"{k}={str(v).strip()}" for k, v in (params or {}).items()
                if v is not None
            ])
            if "?" in url:
                url = url.rstrip(" &") + f"&{params_string}"
            else:
                url = url.rstrip("?") + f"?{params_string}"

        request_payload = {
            k: v
            for k, v in (payload or {}).items() if v is not None
        }
        return requests.request(method,
                                url,
                                headers=self.headers,
                                json=request_payload)

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

    def _get_access_token(self, app_id, app_secret):
        """获取访问凭证"""
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
        data = {"app_id": app_id, "app_secret": app_secret}
        response = requests.post(url, json=data)
        response_data = response.json()
        return response_data["tenant_access_token"]
