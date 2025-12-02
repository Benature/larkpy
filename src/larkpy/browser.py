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

    def __init__(self, cookie: str, domain: str) -> None:
        """初始化 LarkRequests 实例
        
        Args:
            cookie (str): 浏览器 Cookie 字符串
        """
        self.cookie = cookie
        self.domain = domain
        self.headers = {
            'Cookie':
            self.cookie,
            'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def space_recent(self,
                     last_label: Optional[str] = None,
                     length: int = 22,
                     thumbnail_width: int = 1028,
                     thumbnail_height: int = 1028,
                     thumbnail_policy: int = 4,
                     obj_types: Optional[list] = None,
                     type_opt: int = 1,
                     rank: int = 6) -> requests.Response:
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
            requests.Response: HTTP 响应对象，包含 JSON 数据
            
            响应 JSON 数据结构:
            {
                "code": 0,           # 状态码，0 表示成功
                "msg": "Success",    # 状态消息
                "data": {
                    "node_list": ["节点ID1", "节点ID2", ...],  # 节点ID列表
                    "total": 0,      # 总数
                    "entities": {
                        "nodes": {   # 节点详细信息字典，key 为节点ID
                            "节点ID": {
                                "obj_token": str,        # 对象token
                                "name": str,             # 文档名称
                                "type": int,             # 对象类型 (8:多维表格, 16:知识库, 22:文档, 12:文件等)
                                "url": str,              # 访问链接
                                "open_time": int,        # 打开时间（Unix时间戳，秒）
                                "create_time": int,      # 创建时间（Unix时间戳，秒）
                                "edit_time": int,        # 编辑时间（Unix时间戳，秒）
                                "activity_time": int,    # 活动时间（Unix时间戳，秒）
                                "my_edit_time": int,     # 我的编辑时间（Unix时间戳，秒）
                                "owner_id": str,         # 所有者ID
                                "owner_type": int,       # 所有者类型
                                "edit_uid": str,         # 编辑者ID
                                "is_pined": bool,        # 是否置顶
                                "is_stared": bool,       # 是否收藏
                                "thumbnail": str,        # 缩略图URL
                                "icon_info": str,        # 图标信息（JSON字符串）
                                "path_count": int,       # 路径数量
                                "delete_flag": int,      # 删除标记
                                "delete_uid": str,       # 删除者ID
                                "obj_biz_type": int,     # 对象业务类型 (1:个人空间, 2:共享空间)
                                "extra": {               # 额外信息
                                    "biz_type": int,     # 业务类型
                                    "template_type": int, # 模板类型
                                    "is_external": bool, # 是否外部
                                    "display_tag": {...},# 显示标签
                                    # 知识库文档特有字段:
                                    "wiki_space_id": str,        # 知识库空间ID
                                    "wiki_space_name": str,      # 知识库空间名称
                                    "wiki_space_type": int,      # 知识库空间类型
                                    "wiki_sub_token": str,       # 知识库子token
                                    "wiki_subtype": int,         # 知识库子类型
                                    "wiki_version": str,         # 知识库版本
                                    "wiki_homepage": str,        # 知识库主页
                                    "wiki_space_create_uid": str,# 知识库创建者ID
                                    # 文件特有字段:
                                    "parent_folder_obj_token": str,  # 父文件夹token
                                    "parent_folder_obj_type": int,   # 父文件夹类型
                                    "parent_folder_name": str,       # 父文件夹名称
                                    "size": str,                     # 文件大小
                                    "subtype": str,                  # 文件子类型
                                    "version": str,                  # 版本号
                                    "data_version": str,             # 数据版本号
                                    "file_risk_tag": bool,           # 文件风险标记
                                    "copiable": bool,                # 是否可复制
                                },
                                "thumbnail_extra": {...}, # 缩略图额外信息
                                "can_set_sec_label": int, # 是否可设置安全标签
                                "secret_key_delete": bool,# 密钥删除
                                "security_name": str,     # 安全等级名称（如 "L1 - Public"）
                                "security_level": int,    # 安全等级
                                "security_label_id": str, # 安全标签ID
                                "get_sec_label_code": int,# 获取安全标签代码
                            }
                        }
                    }
                }
            }
            
        Examples:
            >>> lark_req = LarkRequests(cookie="your_cookie")
            >>> response = lark_req.space_recent(length=10)
            >>> data = response.json()
            >>> 
            >>> # 访问节点列表
            >>> node_list = data['data']['node_list']
            >>> nodes = data['data']['entities']['nodes']
            >>> 
            >>> # 遍历所有节点
            >>> for node_id in node_list:
            >>>     node_info = nodes[node_id]
            >>>     print(f"名称: {node_info['name']}")
            >>>     print(f"打开时间: {node_info['open_time']}")
            >>>     print(f"URL: {node_info['url']}")
        """
        if obj_types is None:
            obj_types = [2, 22, 44, 3, 30, 8, 11, 12, 84]

        base_url = f"https://{self.domain}/space/api/explorer/recent/list/"

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
