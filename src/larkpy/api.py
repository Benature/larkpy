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
    
    Args:
        app_id (str): 飞书应用的 App ID
        app_secret (str): 飞书应用的 App Secret  
        user_id_type (UserId, optional): 用户ID类型，可选值包括 'open_id', 'user_id', 'union_id'
        
    Attributes:
        access_token (str): 访问令牌
        headers (dict): 请求头
        user_id_type (UserId): 用户ID类型
        
    Examples:
        >>> api = LarkAPI('your_app_id', 'your_app_secret')
        >>> node = api.get_node('wiki_token')
    """

    def __init__(self,
                 app_id: str,
                 app_secret: str,
                 user_id_type: UserId = None) -> None:
        """初始化LarkAPI实例
        
        Args:
            app_id (str): 飞书应用的 App ID
            app_secret (str): 飞书应用的 App Secret
            user_id_type (UserId, optional): 用户ID类型. Defaults to None.
        """
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
