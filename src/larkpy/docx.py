from __future__ import annotations
import requests
import json
from enum import Enum
from typing import Optional, List, Dict, Any

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
    equation = 16  # 公式
    todo = 17  # 待办事项
    bitable = 18  # 多维表格
    callout = 19  # 高亮块
    chat_card = 20  # 群聊卡片
    diagram = 21  # 流程图 & UML
    divider = 22  # 分割线
    file = 23  # 文件
    grid = 24  # 分栏
    grid_column = 25  # 分栏列
    iframe = 26  # 内嵌块
    image = 27  # 图片
    isv = 28  # 三方块
    mindnote = 29  # 思维笔记
    sheet = 30  # 电子表格
    table = 31  # 表格
    table_cell = 32  # 表格单元格
    view = 33  # 视图
    undefined = 34  # 未定义
    quote_container = 35  # 引用容器
    task = 36  # 任务
    okr = 37  # OKR
    okr_objective = 38  # OKR Objective
    okr_key_result = 39  # OKR Key Result
    okr_progress = 40  # OKR 进度
    add_ons = 41  # 插件
    jira_issue = 42  # Jira 问题
    wiki_catalog = 43  # 知识库目录
    board = 44  # 画板
    agenda = 45  # 日程
    embed_page = 46  # 内嵌页面


class LarkDocx(LarkAPI):
    """飞书云文档 API 类
    
    提供飞书云文档的完整编辑功能，包括创建、读取、更新、删除块等操作。
    
    支持两种授权模式：
    1. 应用授权（tenant_access_token）：使用 app_id 和 app_secret
    2. 用户授权（user_access_token）：使用用户访问令牌，创建的文档归属于用户
    
    Args:
        app_id (str, optional): 飞书应用的 App ID，应用授权模式必需
        app_secret (str, optional): 飞书应用的 App Secret，应用授权模式必需
        document_id (str, optional): 文档 ID，如果不提供则需要先调用 create_document 创建文档. Defaults to None.
        user_access_token (str, optional): 用户访问令牌，用户授权模式使用
        
    Examples:
        应用授权模式 - 方式1：创建新文档后编辑
        >>> docx = LarkDocx(app_id="your_app_id", app_secret="your_app_secret")
        >>> result = docx.create_document(title="我的文档")
        >>> # 创建后自动设置了 document_id，可以直接编辑
        >>> docx.create_text_block("Hello, World!")
        
        应用授权模式 - 方式2：使用已有文档
        >>> docx = LarkDocx(
        ...     app_id="your_app_id", 
        ...     app_secret="your_app_secret",
        ...     document_id="existing_document_id"
        ... )
        >>> docx.create_text_block("编辑已有文档")
        
        用户授权模式：
        >>> docx = LarkDocx(user_access_token="u-xxx")
        >>> result = docx.create_document(title="用户文档")
        >>> docx.create_text_block("这个文档属于用户")
        
    AI-generated: 由 AI 辅助扩展，支持用户授权模式
    """
    docx_url = "https://open.feishu.cn/open-apis/docx/v1/documents"

    def __init__(self, 
                 app_id: str = None, 
                 app_secret: str = None, 
                 document_id: str = None,
                 user_access_token: str = None) -> None:
        """初始化 LarkDocx 实例
        
        支持两种授权模式：
        1. 应用授权：使用 app_id 和 app_secret
        2. 用户授权：使用 user_access_token
        
        Args:
            app_id (str, optional): 飞书应用的 App ID，应用授权模式必需
            app_secret (str, optional): 飞书应用的 App Secret，应用授权模式必需
            document_id (str, optional): 文档 ID. Defaults to None.
            user_access_token (str, optional): 用户访问令牌，用户授权模式使用
            
        AI-generated: 由 AI 辅助扩展，支持用户授权模式
        """
        super().__init__(
            app_id=app_id, 
            app_secret=app_secret,
            user_access_token=user_access_token
        )
        self.document_id = document_id
        if document_id:
            self.blocks_url = f"{self.docx_url}/{self.document_id}/blocks"
        else:
            self.blocks_url = None

    def create_document(self,
                       title: str = "未命名文档",
                       folder_token: str = None) -> dict:
        """创建新的飞书云文档
        
        创建一个新的空白云文档，创建成功后会自动设置 document_id，
        可以直接使用其他方法编辑该文档。
        
        Args:
            title (str, optional): 文档标题. Defaults to "未命名文档".
            folder_token (str, optional): 文档所在文件夹的 token，不传则创建在根目录. Defaults to None.
            
        Returns:
            dict: 创建结果，包含以下字段:
                - code (int): 状态码，0 表示成功
                - msg (str): 状态消息
                - data (dict): 文档信息
                    - document (dict): 文档详细信息
                        - document_id (str): 文档ID
                        - revision_id (int): 版本ID
                        - title (str): 文档标题
                        
        References:
            https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document/create
            
        Note:
            本函数由 AI 辅助生成 (Claude Sonnet 4.5 thinking)
            
        Examples:
            >>> # 创建文档并继续编辑
            >>> docx = LarkDocx(app_id="your_app_id", app_secret="your_app_secret")
            >>> result = docx.create_document(title="我的新文档")
            >>> print(f"文档ID: {docx.document_id}")
            >>> # 创建成功后可以直接编辑
            >>> docx.create_heading_block("标题", level=1)
            >>> docx.create_text_block("这是内容")
            >>> 
            >>> # 创建文档到指定文件夹
            >>> result = docx.create_document(
            ...     title="项目文档",
            ...     folder_token="folder_token_xxx"
            ... )
        """
        url = self.docx_url
        
        payload = {
            "title": title
        }
        
        if folder_token:
            payload["folder_token"] = folder_token
        
        response = requests.post(
            url,
            headers=self.headers,
            data=json.dumps(payload)
        )
        
        result = response.json()
        
        # 如果创建成功，自动设置 document_id
        if result.get('code') == 0:
            self.document_id = result['data']['document']['document_id']
            self.blocks_url = f"{self.docx_url}/{self.document_id}/blocks"
        
        return result

    def _ensure_document_id(self):
        """确保 document_id 已设置
        
        内部方法，用于在调用需要 document_id 的方法前检查。
        
        Raises:
            ValueError: 如果 document_id 未设置
        """
        if not self.document_id:
            raise ValueError(
                "document_id 未设置。请先调用 create_document() 创建文档，"
                "或在初始化时提供 document_id 参数。"
            )

    def create_block(self,
                     block_children: dict | list[dict],
                     index: int = -1,
                     block_id: str = None,
                     document_revision_id: int = -1) -> dict:
        """创建文档块
        
        在指定的父块下创建一个或多个子块。
        
        Args:
            block_children (dict | list[dict]): 块内容，可以是单个字典或字典列表
            index (int, optional): 块索引，-1 表示在最后追加. Defaults to -1.
            block_id (str, optional): 父块 ID，默认为文档根节点. Defaults to None.
            document_revision_id (int, optional): 文档版本号，-1 表示最新版本. Defaults to -1.
            
        Returns:
            dict: 响应数据，包含创建的块信息
            
        References:
            https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document-block/create
            
        Examples:
            >>> # 创建单个文本块
            >>> block = {
            ...     "block_type": 2,  # 文本块
            ...     "text": {
            ...         "elements": [{"text_run": {"content": "Hello"}}],
            ...         "style": {}
            ...     }
            ... }
            >>> result = docx.create_block(block)
        """
        self._ensure_document_id()
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

    def get_block(self, 
                  block_id: str,
                  document_revision_id: int = -1,
                  user_id_type: str = "open_id") -> dict:
        """获取指定块的富文本内容
        
        Args:
            block_id (str): 块的唯一标识
            document_revision_id (int, optional): 文档版本号，-1 表示最新版本. Defaults to -1.
            user_id_type (str, optional): 用户 ID 类型. Defaults to "open_id".
            
        Returns:
            dict: 块的详细信息
            
        References:
            https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document-block/get
            
        Note:
            本函数由 AI 辅助生成 (Claude Sonnet 4.5 thinking)
            
        Examples:
            >>> block_info = docx.get_block("block_id_xxx")
            >>> print(block_info['data']['block'])
        """
        url = f"{self.blocks_url}/{block_id}"
        params = {
            "document_revision_id": document_revision_id,
            "user_id_type": user_id_type
        }
        response = self.request("GET", url, params=params)
        return response.json()

    def get_block_children(self,
                          block_id: str = None,
                          page_size: int = 500,
                          page_token: str = None,
                          document_revision_id: int = -1,
                          user_id_type: str = "open_id") -> dict:
        """获取指定块的所有子块
        
        Args:
            block_id (str, optional): 块的唯一标识，默认为文档根节点. Defaults to None.
            page_size (int, optional): 分页大小，最大 500. Defaults to 500.
            page_token (str, optional): 分页标记. Defaults to None.
            document_revision_id (int, optional): 文档版本号. Defaults to -1.
            user_id_type (str, optional): 用户 ID 类型. Defaults to "open_id".
            
        Returns:
            dict: 包含子块列表的响应数据
            
        References:
            https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document-block/list_children
            
        Note:
            本函数由 AI 辅助生成 (Claude Sonnet 4.5 thinking)
            
        Examples:
            >>> children = docx.get_block_children()
            >>> for item in children['data']['items']:
            ...     print(item['block_id'], item['block_type'])
        """
        block_id = block_id or self.document_id
        url = f"{self.blocks_url}/{block_id}/children"
        params = {
            "page_size": page_size,
            "document_revision_id": document_revision_id,
            "user_id_type": user_id_type
        }
        if page_token:
            params["page_token"] = page_token
            
        response = self.request("GET", url, params=params)
        return response.json()
    
    def get_all_blocks(self,
                      block_id: str = None,
                      document_revision_id: int = -1) -> List[dict]:
        """获取文档的所有子块（自动处理分页）
        
        Args:
            block_id (str, optional): 块的唯一标识，默认为文档根节点. Defaults to None.
            document_revision_id (int, optional): 文档版本号. Defaults to -1.
            
        Returns:
            List[dict]: 所有子块的列表
            
        Note:
            本函数由 AI 辅助生成 (Claude Sonnet 4.5 thinking)
            
        Examples:
            >>> all_blocks = docx.get_all_blocks()
            >>> print(f"共有 {len(all_blocks)} 个块")
        """
        all_items = []
        page_token = None
        
        while True:
            result = self.get_block_children(
                block_id=block_id,
                page_token=page_token,
                document_revision_id=document_revision_id
            )
            
            if result.get('code') != 0:
                break
                
            items = result.get('data', {}).get('items', [])
            all_items.extend(items)
            
            # 检查是否还有更多页
            page_token = result.get('data', {}).get('page_token')
            has_more = result.get('data', {}).get('has_more', False)
            
            if not has_more or not page_token:
                break
                
        return all_items

    def update_block(self,
                    block_id: str,
                    update_data: dict,
                    document_revision_id: int = -1,
                    user_id_type: str = "open_id") -> dict:
        """更新块的内容
        
        Args:
            block_id (str): 块的唯一标识
            update_data (dict): 更新的数据，包含块类型和对应的内容
            document_revision_id (int, optional): 文档版本号. Defaults to -1.
            user_id_type (str, optional): 用户 ID 类型. Defaults to "open_id".
            
        Returns:
            dict: 更新后的块信息
            
        References:
            https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document-block/patch
            
        Note:
            本函数由 AI 辅助生成 (Claude Sonnet 4.5 thinking)
            
        Examples:
            >>> # 更新文本块
            >>> update_data = {
            ...     "text": {
            ...         "elements": [{"text_run": {"content": "Updated text"}}],
            ...         "style": {}
            ...     }
            ... }
            >>> result = docx.update_block("block_id_xxx", update_data)
        """
        url = f"{self.blocks_url}/{block_id}"
        params = {
            "document_revision_id": document_revision_id,
            "user_id_type": user_id_type
        }
        response = requests.patch(
            url,
            params=params,
            headers=self.headers,
            data=json.dumps(update_data)
        )
        return response.json()

    def batch_update_blocks(self,
                           requests_data: List[dict],
                           document_revision_id: int = -1,
                           user_id_type: str = "open_id") -> dict:
        """批量更新块
        
        Args:
            requests_data (List[dict]): 批量更新请求列表，每个请求包含 block_id 和更新数据
            document_revision_id (int, optional): 文档版本号. Defaults to -1.
            user_id_type (str, optional): 用户 ID 类型. Defaults to "open_id".
            
        Returns:
            dict: 批量更新的响应数据
            
        References:
            https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document-block/batch_update
            
        Note:
            本函数由 AI 辅助生成 (Claude Sonnet 4.5 thinking)
            
        Examples:
            >>> requests_data = [
            ...     {
            ...         "block_id": "block1",
            ...         "replace_text": {
            ...             "elements": [{"text_run": {"content": "New text 1"}}]
            ...         }
            ...     },
            ...     {
            ...         "block_id": "block2",
            ...         "replace_text": {
            ...             "elements": [{"text_run": {"content": "New text 2"}}]
            ...         }
            ...     }
            ... ]
            >>> result = docx.batch_update_blocks(requests_data)
        """
        url = f"{self.docx_url}/{self.document_id}/blocks/batch_update"
        params = {
            "document_revision_id": document_revision_id,
            "user_id_type": user_id_type
        }
        payload = {"requests": requests_data}
        
        response = requests.patch(
            url,
            params=params,
            headers=self.headers,
            data=json.dumps(payload)
        )
        return response.json()

    def delete_block(self,
                     start_index: int,
                     end_index: int,
                     block_id: str = None,
                     document_revision_id: int = -1) -> dict:
        """批量删除块的子块
        
        指定需要删除的子块的起始位置和结束位置。
        
        Args:
            start_index (int): 删除的起始索引（从 0 开始）
            end_index (int): 删除的结束索引（不包含）
            block_id (str, optional): 父块 ID，默认为文档根节点. Defaults to None.
            document_revision_id (int, optional): 文档版本号. Defaults to -1.
            
        Returns:
            dict: 删除操作的响应数据
            
        References:
            https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document-block-children/batch_delete
            
        Examples:
            >>> # 删除第 0 到第 2 个子块 (不包含第 2 个)
            >>> result = docx.delete_block(start_index=0, end_index=2)
        """
        block_id = block_id or self.document_id
        url = f"{self.blocks_url}/{block_id}/children/batch_delete"
        params = {"document_revision_id": document_revision_id}
        payload = {
            "start_index": start_index,
            "end_index": end_index
        }
        
        response = requests.delete(
            url,
            params=params,
            headers=self.headers,
            data=json.dumps(payload)
        )
        return response.json()

    # 便捷方法：创建常用类型的块
    
    def create_text_block(self,
                         content: str,
                         block_id: str = None,
                         index: int = -1,
                         style: dict = None) -> dict:
        """创建文本块（便捷方法）
        
        Args:
            content (str): 文本内容
            block_id (str, optional): 父块 ID. Defaults to None.
            index (int, optional): 插入位置. Defaults to -1.
            style (dict, optional): 文本样式. Defaults to None.
            
        Returns:
            dict: 创建结果
            
        Note:
            本函数由 AI 辅助生成 (Claude Sonnet 4.5 thinking)
            
        Examples:
            >>> result = docx.create_text_block("这是一段文本")
        """
        block = {
            "block_type": BlockType.text.value,
            "text": {
                "elements": [{"text_run": {"content": content}}],
                "style": style or {}
            }
        }
        return self.create_block(block, index=index, block_id=block_id)
    
    def create_heading_block(self,
                            content: str,
                            level: int = 1,
                            block_id: str = None,
                            index: int = -1) -> dict:
        """创建标题块（便捷方法）
        
        Args:
            content (str): 标题内容
            level (int, optional): 标题级别 (1-9). Defaults to 1.
            block_id (str, optional): 父块 ID. Defaults to None.
            index (int, optional): 插入位置. Defaults to -1.
            
        Returns:
            dict: 创建结果
            
        Note:
            本函数由 AI 辅助生成 (Claude Sonnet 4.5 thinking)
            
        Examples:
            >>> result = docx.create_heading_block("一级标题", level=1)
        """
        if not 1 <= level <= 9:
            raise ValueError("标题级别必须在 1-9 之间")
            
        block_type = getattr(BlockType, f"heading{level}").value
        block = {
            "block_type": block_type,
            f"heading{level}": {
                "elements": [{"text_run": {"content": content}}],
                "style": {}
            }
        }
        return self.create_block(block, index=index, block_id=block_id)
    
    def create_bullet_block(self,
                           content: str,
                           block_id: str = None,
                           index: int = -1) -> dict:
        """创建无序列表块（便捷方法）
        
        Args:
            content (str): 列表项内容
            block_id (str, optional): 父块 ID. Defaults to None.
            index (int, optional): 插入位置. Defaults to -1.
            
        Returns:
            dict: 创建结果
            
        Note:
            本函数由 AI 辅助生成 (Claude Sonnet 4.5 thinking)
            
        Examples:
            >>> result = docx.create_bullet_block("列表项 1")
        """
        block = {
            "block_type": BlockType.bullet.value,
            "bullet": {
                "elements": [{"text_run": {"content": content}}],
                "style": {}
            }
        }
        return self.create_block(block, index=index, block_id=block_id)
    
    def create_ordered_block(self,
                            content: str,
                            block_id: str = None,
                            index: int = -1) -> dict:
        """创建有序列表块（便捷方法）
        
        Args:
            content (str): 列表项内容
            block_id (str, optional): 父块 ID. Defaults to None.
            index (int, optional): 插入位置. Defaults to -1.
            
        Returns:
            dict: 创建结果
            
        Note:
            本函数由 AI 辅助生成 (Claude Sonnet 4.5 thinking)
            
        Examples:
            >>> result = docx.create_ordered_block("列表项 1")
        """
        block = {
            "block_type": BlockType.ordered.value,
            "ordered": {
                "elements": [{"text_run": {"content": content}}],
                "style": {}
            }
        }
        return self.create_block(block, index=index, block_id=block_id)
