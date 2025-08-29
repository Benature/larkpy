from __future__ import annotations
import requests
import json
import pandas as pd

from .api import LarkAPI
from ._typing import UserId, BitTableOperator, List, Dict, Literal


class LarkBitTable(LarkAPI):
    """飞书多维表格"""

    def __init__(self,
                 app_id,
                 app_secret,
                 wiki_token,
                 table_id,
                 view_id: str = None,
                 user_id_type: UserId = None) -> None:
        super().__init__(app_id, app_secret, user_id_type)
        self.app_token = self.get_node(wiki_token)['obj_token']
        self.table_id = table_id
        self.view_id = view_id

    @property
    def pre_url(self):
        return f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/records"

    def search(self,
               view_id: str = None,
               fields: List[str] = None,
               order: List[Dict[str, str | bool]] = None,
               filter: Dict[str, str
                            | List[Dict[str, str | List[str, str]]]] = None,
               automatic_fields: bool = None,
               user_id_type: UserId = None,
               page_token: str = None,
               page_size: int = None,
               out=Literal[dict, pd.DataFrame]) -> Dict:
        """查询记录"""
        # https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/bitable-v1/app-table-record/search
        params = dict(user_id_type=user_id_type or self.user_id_type,
                      page_token=page_token,
                      page_size=page_size)

        payload = dict(view_id=view_id or self.view_id,
                       field_names=fields,
                       sort=order,
                       filter=filter,
                       automatic_fields=automatic_fields)
        response = self.request("POST", f"{self.pre_url}/search", payload,
                                params)
        res = response.json()
        if out == dict:
            return res
        elif out == pd.DataFrame:
            return self.table2df(res)
        return res

    @classmethod
    def _cond(_, field: str, operator: BitTableOperator, value: List[str]):
        """生成条件（类方法、实例方法）"""
        if not isinstance(value, list):
            value = [value]
        return dict(field_name=field, operator=operator, value=value)

    def update(self, record_id: str | int, fields: Dict):
        # https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/update
        url = f'{self.pre_url}/{record_id}'
        if 'fields' not in fields:
            fields = {'fields': fields}
        payload = json.dumps(fields)
        response = requests.request("PUT",
                                    url,
                                    headers=self.headers,
                                    data=payload)
        return response.json()

    def batch_update(self, records: List | Dict[str, List]):
        url = f"{self.pre_url}/batch_update"
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

    def to_frame(self, data=None, columns=None):
        """convert bitable to pandas dataframe"""
        table_data = data or self.search()
        return self.table2df(table_data, columns=columns)
