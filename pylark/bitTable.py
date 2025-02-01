from __future__ import annotations
import requests
import json

from typing_extensions import Union, List, Dict, Literal

from .api import FeishuAPI


class FeishuBitTable(FeishuAPI):

    def __init__(self, app_id, app_secret, wiki_token, table_id) -> None:
        super().__init__(app_id, app_secret)
        self.obj_token = self.get_node(wiki_token)['obj_token']
        self.table_id = table_id

    def parse_bitable_data(self, data, columns=None):
        """解析bitable数据"""
        import pandas as pd

        table_data = self.get_bitable_data(self.obj_token, self.table_id)
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

    def get_df(self, columns=None):
        table_data = self.get_bitable_data(self.obj_token, self.table_id)
        return self.parse_bitable_data(table_data, columns=columns)
