"""LarkTask - 飞书任务 API 类

本模块提供了飞书任务的查询和管理功能。

该类继承自 LarkAPI，提供了任务相关的所有 API 接口封装。
"""

from __future__ import annotations
from typing import Optional

from .api import LarkAPI


class LarkTask(LarkAPI):
    """飞书任务 API 类
    
    提供飞书任务的查询和管理功能，包括按完成状态、时间范围等条件查询任务。
    
    支持两种授权模式：
    1. 应用授权（tenant_access_token）：使用 app_id 和 app_secret
    2. 用户授权（user_access_token）：使用用户访问令牌
    
    Args:
        app_id (str, optional): 飞书应用的 App ID，应用授权模式必需
        app_secret (str, optional): 飞书应用的 App Secret，应用授权模式必需
        user_access_token (str, optional): 用户访问令牌，用户授权模式使用
        
    Attributes:
        access_token (str): 访问令牌
        headers (dict): 请求头
        user_id_type (str): 用户ID类型
        
    Permissions:
        使用本类的方法需要以下权限之一:
        - task:task:readonly - 查看任务
        - task:task - 查看、创建、编辑和删除任务
        
    Note:
        本类由 AI 辅助生成 (Claude Sonnet 4.5 thinking)
        
    Examples:
        应用授权模式:
        >>> task_api = LarkTask(app_id='cli_xxx', app_secret='xxx')
        >>> result = task_api.list_tasks_v2(completed=True)
        >>> for task in result['data']['items']:
        ...     print(task['summary'])
        
        用户授权模式:
        >>> from larkpy import LarkOAuth
        >>> oauth = LarkOAuth(app_id='cli_xxx', app_secret='xxx')
        >>> token_info = oauth.get_user_access_token(code='xxx')
        >>> task_api = LarkTask(user_access_token=token_info['data']['access_token'])
        >>> result = task_api.list_tasks_v2(completed=True)
    """

    def __init__(self,
                 app_id: str = None,
                 app_secret: str = None,
                 user_access_token: str = None) -> None:
        """初始化 LarkTask 实例
        
        支持两种授权模式：
        1. 应用授权：使用 app_id 和 app_secret
        2. 用户授权：使用 user_access_token
        
        Args:
            app_id (str, optional): 飞书应用的 App ID，应用授权模式必需
            app_secret (str, optional): 飞书应用的 App Secret，应用授权模式必需
            user_access_token (str, optional): 用户访问令牌，用户授权模式使用
            
        Examples:
            应用授权模式:
            >>> task_api = LarkTask(app_id='cli_xxx', app_secret='xxx')
            
            用户授权模式:
            >>> task_api = LarkTask(user_access_token='u-xxx')
        """
        super().__init__(app_id=app_id,
                         app_secret=app_secret,
                         user_access_token=user_access_token)

    def list_tasks(self,
                   completed: bool = None,
                   page_size: int = 50,
                   page_token: str = None,
                   task_type: str = "my_tasks") -> dict:
        """查询任务列表
        
        不建议直接调用此方法，请使用 list_tasks() 方法。
        
        Args:
            completed (bool, optional): 过滤任务完成状态
            page_size (int, optional): 每页返回的任务数量
            page_token (str, optional): 分页标记
            task_type (str, optional): 任务类型
                
        Returns:
            dict: 任务列表信息
            
        Note:
            本函数由 AI 辅助生成 (Claude Sonnet 4.5 thinking)
        """
        url = 'https://open.feishu.cn/open-apis/task/v2/tasks'

        params = {
            'page_size': page_size,
            'type': task_type,
            'user_id_type': self.user_id_type
        }

        if completed is not None:
            params['completed'] = completed

        if page_token:
            params['page_token'] = page_token

        response = self.request('GET', url, params=params)
        return response.json()

    def list_tasklist_tasks(self,
                            tasklist_guid: str,
                            completed: bool = None,
                            start_create_time: str = None,
                            end_create_time: str = None,
                            page_size: int = 50,
                            page_token: str = None) -> dict:
        """获取指定清单下的任务列表
        
        Args:
            tasklist_guid (str): 任务清单 GUID
            completed (bool, optional): 任务完成状态过滤条件，True 仅返回已完成任务。
                False 仅返回未完成任务。默认为 None，返回全部任务。
            start_create_time (str, optional): 任务创建时间起始（Unix 毫秒时间戳字符串）
            end_create_time (str, optional): 任务创建时间结束（Unix 毫秒时间戳字符串）
            page_size (int, optional): 每页返回的任务数量，1-100. Defaults to 50.
            page_token (str, optional): 分页标记，首次请求无需传入
            
        Returns:
            dict: 任务列表结果，结构同官方接口返回
            
        References:
            https://open.feishu.cn/document/task-v2/tasklist/tasks
        """
        if not tasklist_guid:
            raise ValueError("tasklist_guid is required")

        url = f'https://open.feishu.cn/open-apis/task/v2/tasklist/{tasklist_guid}/tasks'
        params = {'page_size': page_size, 'user_id_type': self.user_id_type}

        if completed is not None:
            params['completed'] = completed
        if start_create_time:
            params['start_create_time'] = start_create_time
        if end_create_time:
            params['end_create_time'] = end_create_time
        if page_token:
            params['page_token'] = page_token

        response = self.request('GET', url, params=params)
        return response.json()
