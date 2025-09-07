from __future__ import annotations
import requests
import json
from enum import Enum

from .api import LarkAPI


class BlockType(Enum):
    """块类型   
    https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document-block/create#1b8abd5d
    """
    page = 1  # 页面
    text = 2  # 文本
    heading1 = 3  # 标题 1
    heading2 = 4  # 标题 2
    heading3 = 5  # 标题 3
    heading4 = 6  # 标题 4
    heading5 = 7  # 标题 5
    heading6 = 8  # 标题 6
    heading7 = 9  # 标题 7
    heading8 = 10  # 标题 8
    heading9 = 11  # 标题 9
    bullet = 12  # 无序列表
    ordered = 13  # 有序列表
    code = 14  # 代码块
    quote = 15  # 引用
    # equation
    todo = 17  # 待办事项


class LarkDocx(LarkAPI):
    docx_url = "https://open.feishu.cn/open-apis/docx/v1/documents"

    def __init__(self, app_id, app_secret, document_id) -> None:
        super().__init__(app_id, app_secret)
        self.document_id = document_id
        self.blocks_url = f"{self.docx_url}/{self.document_id}/blocks"
        # self.obj_token = self.get_node(wiki_token)['obj_token']

    def create_block(self,
                     block_children: dict | list[dict],
                     index: int = -1,
                     block_id: str = None,
                     document_revision_id: int = -1) -> dict:
        """创建文档块
        Args:
            block_children (dict): 块内容
            index (int, optional): 块索引，默认在最后追加
            block_id (str, optional): 块id，默认在文档根节点追加，即为 document_id
            document_revision_id (int, optional): 文档版本号，默认最新版本
        Returns:
            dict: 响应数据
            
        https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document-block/create
        """
        block_id = block_id or self.document_id
        if isinstance(block_children, dict):
            block_children = [block_children]

        url = f"{self.blocks_url}/{block_id}/children?document_revision_id={document_revision_id}"
        payload = {
            "children": block_children,
            "index": index,
        }
        response = requests.request("POST",
                                    url,
                                    headers=self.headers,
                                    data=json.dumps(payload))
        return response.json()

    def delete_block(self,
                     start_index: int,
                     end_index: int,
                     block_id: str = None,
                     document_revision_id: int = -1) -> dict:
        """批量删除文档块
        Args:
            start_index (int): 开始索引
            end_index (int): 结束索引
            block_id (str): 块id
            document_revision_id (int, optional): 文档版本号，默认最新版本
        Returns:
            dict: 响应数据

        """
        url = f"{self.blocks_url}/{block_id}/children?batch_delete={document_revision_id}"
        payload = dict(end_index=end_index, start_index=start_index)
        response = requests.request("POST",
                                    url,
                                    headers=self.headers,
                                    data=json.dumps(payload))
        return response.json()
