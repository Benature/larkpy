from __future__ import annotations
import requests
import json
import pandas as pd
from typing import List, Dict

from .api import FeishuAPI


class FeishuBitTable(FeishuAPI):
    """飞书多维表格"""

    def __init__(self, app_id, app_secret, wiki_token, table_id) -> None:
        super().__init__(app_id, app_secret)
        self.app_token = self.get_node(wiki_token)['obj_token']
        self.table_id = table_id
        self.url_prefix = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/records"

    def search(self) -> Dict:
        """获取多维表格数据"""
        # https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/bitable-v1/app-table-record/search
        url = f"{self.url_prefix}/search"
        payload = json.dumps({})
        response = requests.request("POST",
                                    url,
                                    headers=self.headers,
                                    data=payload)
        return response.json()

    def update(self, fields: Dict, record_id: str | int):
        # https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/update
        url = f'{self.url_prefix}/{record_id}'
        if 'fields' not in fields:
            fields = {'fields': fields}
        payload = json.dumps(fields)
        response = requests.request("PUT",
                                    url,
                                    headers=self.headers,
                                    data=payload)
        return response.json()

    def batch_update(self, records: List | Dict[str, List]):
        url = f"{self.url_prefix}/batch_update"
        if isinstance(records, list):
            records = {'records': records}
        payload = json.dumps(records)
        response = requests.request("POST",
                                    url,
                                    headers=self.headers,
                                    data=payload)
        return response.json()

    def table2df(self,
                 table_data: Dict,
                 columns: List[str] = None) -> pd.DataFrame:
        """解析 bitable 数据"""

        items = table_data['data']['items']
        data = []
        for item in items:
            _d = {}
            for col in item['fields'].keys():
                if columns is not None and col not in columns: continue
                value = item['fields'].get(col, None)
                if isinstance(value, list):
                    value = value[0]
                    if 'text' in value:
                        value = value['text']
                _d[col] = value
            data.append(_d)
        df = pd.DataFrame(data)
        return df

    def to_frame(self, columns=None):
        """convert bitable to pandas dataframe"""
        table_data = self.search()
        return self.table2df(table_data, columns=columns)
