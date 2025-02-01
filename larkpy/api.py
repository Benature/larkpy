from __future__ import annotations
import requests
import json

from typing_extensions import Union, List, Dict, Literal


class FeishuAPI():

    def __init__(self, app_id, app_secret) -> None:
        tenant_access_token = self._get_access_token(app_id, app_secret)
        self.headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': f'Bearer {tenant_access_token}'
        }

    def _get_access_token(self, app_id, app_secret):
        """获取访问凭证"""
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
        data = {"app_id": app_id, "app_secret": app_secret}
        response = requests.post(url, json=data)
        response_data = response.json()
        return response_data["tenant_access_token"]

    def get_node(self, token: str, obj_type='wiki'):
        # https://open.feishu.cn/document/server-docs/docs/wiki-v2/space-node/get_node
        url = f'https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node?token={token}'  # &obj_type={obj_type}'
        response = requests.get(url, headers=self.headers)
        data = response.json()
        node = data['data']['node']
        return node  # ['obj_token']

    def get_bitable_data(self, app_token, table_id):
        """获取多维表格数据"""
        # https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/bitable-v1/app-table-record/search?appId=cli_a644c99a03fbd00d
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search"
        payload = json.dumps({})
        response = requests.request("POST",
                                    url,
                                    headers=self.headers,
                                    data=payload)
        return response.json()

    def update_bitable_record(self, fields: Dict, app_token, table_id,
                              record_id):
        # https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/update?appId=cli_a644c99a03fbd00d
        url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}'
        if 'fields' not in fields:
            fields = {'fields': fields}
        payload = json.dumps(fields)
        response = requests.request("PUT",
                                    url,
                                    headers=self.headers,
                                    data=payload)
        return response.json()

    def batch_update_bitable_records(self, records: Union[List, Dict],
                                     app_token, table_id):
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_update"
        if isinstance(records, list):
            records = {'records': records}
        payload = json.dumps(records)
        response = requests.request("POST",
                                    url,
                                    headers=self.headers,
                                    data=payload)
        return response.json()
