"""LarkRequests - 飞书浏览器请求类

本模块提供基于 Cookie 的飞书浏览器请求功能，用于访问需要浏览器认证的接口。

该类使用浏览器 Cookie 进行身份验证，主要用于访问飞书空间等需要登录才能访问的 API。
"""

from __future__ import annotations
import requests
from typing import Dict, Optional
from urllib.parse import urlencode


class LarkRequests:
    """飞书浏览器请求类
    
    提供基于 Cookie 的飞书请求功能，用于访问需要浏览器认证的接口。
    
    Args:
        cookie (str): 浏览器 Cookie 字符串
        
    Attributes:
        cookie (str): Cookie 字符串
        headers (dict): 请求头，包含 Cookie
        
    Examples:
        >>> cookie = "your_cookie_string"
        >>> lark_req = LarkRequests(cookie=cookie)
        >>> recent_list = lark_req.space_recent()
    """
    
    def __init__(self, cookie: str) -> None:
        """初始化 LarkRequests 实例
        
        Args:
            cookie (str): 浏览器 Cookie 字符串
        """
        self.cookie = cookie
        self.headers = {
            'Cookie': self.cookie,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def space_recent(
        self,
        last_label: Optional[str] = None,
        length: int = 22,
        thumbnail_width: int = 1028,
        thumbnail_height: int = 1028,
        thumbnail_policy: int = 4,
        obj_types: Optional[list] = None,
        type_opt: int = 1,
        rank: int = 6
    ) -> requests.Response:
        """获取飞书空间最近访问列表
        
        Args:
            last_label (str, optional): 最后一个标签. Defaults to None (不传递该参数).
            length (int, optional): 返回列表长度. Defaults to 22.
            thumbnail_width (int, optional): 缩略图宽度. Defaults to 1028.
            thumbnail_height (int, optional): 缩略图高度. Defaults to 1028.
            thumbnail_policy (int, optional): 缩略图策略. Defaults to 4.
            obj_types (list, optional): 对象类型列表. Defaults to [2, 22, 44, 3, 30, 8, 11, 12, 84].
            type_opt (int, optional): 类型选项. Defaults to 1.
            rank (int, optional): 排序方式. Defaults to 6.
            
        Returns:
            requests.Response: HTTP 响应对象
            
        Examples:
            >>> lark_req = LarkRequests(cookie="your_cookie")
            >>> response = lark_req.space_recent(length=10)
            >>> data = response.json()
        """
        if obj_types is None:
            obj_types = [2, 22, 44, 3, 30, 8, 11, 12, 84]
        
        base_url = "https://avrnf5fwjt.feishu.cn/space/api/explorer/recent/list/"
        
        # 构建查询参数，只添加非 None 的参数
        params = {
            "length": length,
            "thumbnail_width": thumbnail_width,
            "thumbnail_height": thumbnail_height,
            "thumbnail_policy": thumbnail_policy,
            "type_opt": type_opt,
            "rank": rank
        }
        
        # 如果提供了 last_label，则添加到参数中
        if last_label is not None:
            params["last_label"] = last_label
        
        # 添加多个 obj_type 参数
        param_parts = [f"{k}={v}" for k, v in params.items()]
        for obj_type in obj_types:
            param_parts.append(f"obj_type={obj_type}")
        
        url = f"{base_url}?{'&'.join(param_parts)}"
        
        response = requests.get(url, headers=self.headers)
        return response
