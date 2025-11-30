"""LarkAPI - 飞书开放平台 API 调用基础类

本模块提供了飞书开放平台 API 的基础调用功能，包括身份验证、请求封装等。

该类作为其他所有 API 相关类的基类，提供了通用的身份验证和请求处理机制。

所有的子类都可以继承此类来获得基础的 API 调用能力。
"""

from __future__ import annotations
import requests
import json

from typing import List, Dict
from typing_extensions import Literal
from ._typing import UserId


class LarkAPI():
    """飞书开放平台 API 调用基础类
    
    提供飞书开放平台的基础API调用功能，包括身份验证、请求封装等。
    作为其他所有API相关类的基类。
    
    支持两种授权模式：
    1. 应用授权（tenant_access_token）：使用 app_id 和 app_secret
    2. 用户授权（user_access_token）：使用用户访问令牌，操作将以用户身份执行
    
    Args:
        app_id (str, optional): 飞书应用的 App ID，应用授权模式必需
        app_secret (str, optional): 飞书应用的 App Secret，应用授权模式必需  
        user_id_type (UserId, optional): 用户ID类型，可选值包括 'open_id', 'user_id', 'union_id'
        user_access_token (str, optional): 用户访问令牌，用户授权模式使用
        
    Attributes:
        access_token (str): 访问令牌（tenant_access_token 或 user_access_token）
        headers (dict): 请求头
        user_id_type (UserId): 用户ID类型
        
    Examples:
        应用授权模式:
        >>> api = LarkAPI('your_app_id', 'your_app_secret')
        >>> node = api.get_node('wiki_token')
        
        用户授权模式:
        >>> api = LarkAPI(user_access_token='u-xxx')
        >>> node = api.get_node('wiki_token')
        
    AI-generated: 由 AI 辅助扩展，支持用户授权模式
    """

    def __init__(self,
                 app_id: str = None,
                 app_secret: str = None,
                 user_id_type: UserId = None,
                 user_access_token: str = None) -> None:
        """初始化LarkAPI实例
        
        支持两种授权模式：
        1. 应用授权（tenant_access_token）：使用 app_id 和 app_secret
        2. 用户授权（user_access_token）：直接传入用户访问令牌
        
        Args:
            app_id (str, optional): 飞书应用的 App ID，应用授权模式必需
            app_secret (str, optional): 飞书应用的 App Secret，应用授权模式必需
            user_id_type (UserId, optional): 用户ID类型. Defaults to None.
            user_access_token (str, optional): 用户访问令牌，用户授权模式使用
            
        Examples:
            应用授权模式（原有方式）:
            >>> api = LarkAPI(app_id='cli_xxx', app_secret='xxx')
            
            用户授权模式（新增）:
            >>> from larkpy import LarkOAuth
            >>> oauth = LarkOAuth(app_id='cli_xxx', app_secret='xxx')
            >>> token_info = oauth.get_user_access_token(code='xxx')
            >>> api = LarkAPI(user_access_token=token_info['data']['access_token'])
            
        AI-generated: 由 AI 辅助扩展，支持用户授权模式
        """
        # 用户授权模式
        if user_access_token:
            self.access_token = user_access_token
        # 应用授权模式（原有逻辑）
        elif app_id and app_secret:
            tenant_access_token = self._get_access_token(app_id, app_secret)
            self.access_token = tenant_access_token
        else:
            raise ValueError("必须提供 user_access_token 或者 (app_id 和 app_secret)")

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
        """发送HTTP请求到飞书API
        
        Args:
            method (Literal['GET', 'POST', 'PUT', 'DELETE']): HTTP方法
            url (str): 请求URL
            payload (Dict, optional): 请求体数据. Defaults to None.
            params (Dict, optional): URL参数. Defaults to None.
            
        Returns:
            requests.Response: HTTP响应对象
        """
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
        """获取知识库节点信息
        
        通过wiki token获取对应的节点信息，包括obj_token等。
        
        Args:
            token (str): 知识库token
            obj_type (Literal, optional): 对象类型，可选值包括 'doc', 'docx', 'sheet', 
                'mindnote', 'bitable', 'file', 'slides', 'wiki'. Defaults to None.
                
        Returns:
            dict: 节点信息，包含obj_token等字段
            
        References:
            https://open.feishu.cn/document/server-docs/docs/wiki-v2/space-node/get_node
        """
        url = f'https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node?token={token}'
        if obj_type is not None:
            url += f'&obj_type={obj_type}'
        response = requests.request("GET", url, headers=self.headers)
        data = response.json()
        node = data['data']['node']
        return node  # ['obj_token']

    def download_file(self, file_key: str) -> bytes:
        """下载文件
        https://open.feishu.cn/document/server-docs/im-v1/file/get
        """
        url = f"https://open.feishu.cn/open-apis/im/v1/files/{file_key}"
        response = self.request("GET", url)
        response.raise_for_status()
        return response.content

    def create_wiki_node(self,
                         space_id: str,
                         obj_type: str = "docx",
                         title: str = "未命名文档",
                         parent_node_token: str = None,
                         node_type: str = "origin") -> dict:
        """在知识库空间中创建节点
        
        在指定的知识库空间中创建一个新的节点（文档）。
        
        Args:
            space_id (str): 知识库空间ID
            obj_type (str, optional): 文档类型，可选值: 'doc', 'docx', 'sheet', 
                'mindnote', 'bitable', 'file'. Defaults to "docx".
            title (str, optional): 文档标题. Defaults to "未命名文档".
            parent_node_token (str, optional): 父节点token，如果为空则创建在根目录. 
                Defaults to None.
            node_type (str, optional): 节点类型，'origin'表示创建新文档，
                'shortcut'表示创建快捷方式. Defaults to "origin".
                
        Returns:
            dict: 创建结果，包含以下字段:
                - code (int): 状态码，0表示成功
                - msg (str): 状态消息
                - data (dict): 节点信息
                    - node (dict): 节点详细信息
                        - space_id (str): 空间ID
                        - node_token (str): 节点token
                        - obj_token (str): 对象token (例如文档ID)
                        - obj_type (str): 对象类型
                        - parent_node_token (str): 父节点token
                        - title (str): 标题
                        
        References:
            https://open.feishu.cn/document/server-docs/docs/wiki-v2/space-node/create
        """
        url = f'https://open.feishu.cn/open-apis/wiki/v2/spaces/{space_id}/nodes'

        payload = {
            "obj_type": obj_type,
            "node_type": node_type,
            "title": title
        }

        if parent_node_token:
            payload["parent_node_token"] = parent_node_token

        response = requests.post(url,
                                 headers=self.headers,
                                 data=json.dumps(payload))
        return response.json()

    def get_wiki_node_children(self,
                               space_id: str,
                               parent_node_token: str = None,
                               page_size: int = 50,
                               page_token: str = None) -> dict:
        """获取知识库节点的子节点列表
        
        获取指定知识库空间或节点下的直接子节点列表。
        
        Args:
            space_id (str): 知识库空间ID
            parent_node_token (str, optional): 父节点token，如果为空则获取空间根节点的子节点. 
                Defaults to None.
            page_size (int, optional): 分页大小，最大 50. Defaults to 50.
            page_token (str, optional): 分页标记，第一次请求不传. Defaults to None.
                
        Returns:
            dict: 查询结果，包含以下字段:
                - code (int): 状态码，0表示成功
                - msg (str): 状态消息
                - data (dict): 节点列表信息
                    - items (list): 子节点列表
                        - space_id (str): 空间ID
                        - node_token (str): 节点token
                        - obj_token (str): 对象token (例如文档ID)
                        - obj_type (str): 对象类型
                        - parent_node_token (str): 父节点token
                        - node_type (str): 节点类型
                        - origin_node_token (str): 原始节点token
                        - has_child (bool): 是否有子节点
                        - title (str): 标题
                    - page_token (str): 下一页的分页标记
                    - has_more (bool): 是否还有更多数据
                        
        References:
            https://open.feishu.cn/document/server-docs/docs/wiki-v2/space-node/list
        """
        url = f'https://open.feishu.cn/open-apis/wiki/v2/spaces/{space_id}/nodes'

        params = {'page_size': page_size}

        if parent_node_token:
            params['parent_node_token'] = parent_node_token

        if page_token:
            params['page_token'] = page_token

        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def _get_access_token(self, app_id, app_secret):
        """获取tenant_access_token访问凭证
        
        使用app_id和app_secret向飞书API获取访问令牌。
        
        Args:
            app_id (str): 应用ID
            app_secret (str): 应用密钥
            
        Returns:
            str: tenant_access_token访问令牌
        """
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
        data = {"app_id": app_id, "app_secret": app_secret}
        response = requests.post(url, json=data)
        response_data = response.json()
        return response_data["tenant_access_token"]
