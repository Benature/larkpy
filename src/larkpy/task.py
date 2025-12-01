"""LarkTask - 飞书任务 API 类

本模块提供了飞书任务的查询和管理功能。

该类继承自 LarkAPI，提供了任务相关的所有 API 接口封装。
"""

from __future__ import annotations
from typing import Optional

from .api import LarkAPI
from .utils import clean_params


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
                   start_create_time: str = None,
                   end_create_time: str = None,
                   page_size: int = 50,
                   page_token: str = None,
                   task_type: str = "my_tasks") -> dict:
        """查询任务列表（智能版本选择）
        
        根据输入参数自动选择使用 v1 或 v2 API：
        - 如果提供了时间范围参数（start_create_time 或 end_create_time），使用 v1 API
        - 否则使用 v2 API（性能更好）
        
        Args:
            completed (bool, optional): 过滤任务完成状态。
                - True: 仅返回已完成任务
                - False: 仅返回未完成任务
                - None: 返回所有任务. Defaults to None.
            start_create_time (str, optional): 查询开始时间（Unix毫秒时间戳字符串）。
                提供此参数将自动使用 v1 API. Defaults to None.
            end_create_time (str, optional): 查询结束时间（Unix毫秒时间戳字符串）。
                提供此参数将自动使用 v1 API. Defaults to None.
            page_size (int, optional): 每页返回的任务数量，范围 1-100. Defaults to 50.
            page_token (str, optional): 分页标记，第一次请求不传. Defaults to None.
            task_type (str, optional): 任务类型，目前仅支持 "my_tasks"（我负责的任务）。
                仅在使用 v2 API 时有效. Defaults to "my_tasks".
                
        Returns:
            dict: 任务列表信息，包含以下字段:
                - code (int): 状态码，0表示成功
                - msg (str): 状态消息
                - data (dict): 任务数据
                    - items (list): 任务列表
                    - page_token (str): 下一页的分页标记
                    - has_more (bool): 是否还有更多数据
                    
        Permissions:
            需要以下权限之一:
            - task:task:readonly - 查看任务
            - task:task - 查看、创建、编辑和删除任务
            
        References:
            - v2 API: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/list
            
        Note:
            本函数由 AI 辅助生成 (Claude Sonnet 4.5 thinking)
            v1 API 用于支持时间范围过滤，但官方文档可能已不可用
            
        Examples:
            >>> # 示例 1: 查询已完成的任务（自动使用 v2 API）
            >>> task_api = LarkTask(app_id='cli_xxx', app_secret='xxx')
            >>> result = task_api.list_tasks(completed=True)
            >>> for task in result['data']['items']:
            ...     print(task['summary'])
            
            >>> # 示例 2: 查询最近7天内已完成的任务（自动使用 v1 API）
            >>> import time
            >>> current_time = int(time.time() * 1000)
            >>> seven_days_ago = current_time - (7 * 24 * 60 * 60 * 1000)
            >>> result = task_api.list_tasks(
            ...     completed=True,
            ...     start_create_time=str(seven_days_ago),
            ...     end_create_time=str(current_time)
            ... )
            
            >>> # 示例 3: 查询某个时间点之后的所有任务（自动使用 v1 API）
            >>> timestamp = str(int(time.time() * 1000) - 30 * 24 * 60 * 60 * 1000)
            >>> result = task_api.list_tasks(start_create_time=timestamp)
            
            >>> # 示例 4: 分页查询
            >>> result = task_api.list_tasks(completed=False, page_size=20)
            >>> if result['data']['has_more']:
            ...     next_page = task_api.list_tasks(
            ...         completed=False,
            ...         page_token=result['data']['page_token']
            ...     )
        """
        # 如果提供了时间范围参数，使用 v1 API
        if start_create_time is not None or end_create_time is not None:
            return self._list_tasks_v1(
                task_completed=completed,
                start_create_time=start_create_time,
                end_create_time=end_create_time,
                page_size=page_size,
                page_token=page_token
            )
        
        # 否则使用 v2 API（性能更好）
        return self._list_tasks_v2(
            completed=completed,
            page_size=page_size,
            page_token=page_token,
            task_type=task_type
        )

    def _list_tasks_v2(self,
                       completed: bool = None,
                       page_size: int = 50,
                       page_token: str = None,
                       task_type: str = "my_tasks") -> dict:
        """查询任务列表（v2版本）- 内部方法
        
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

        params = clean_params({
            'page_size': page_size,
            'type': task_type,
            'user_id_type': self.user_id_type,
            'completed': completed,
            'page_token': page_token
        })

        response = self.request('GET', url, params=params)
        return response.json()

    def list_tasklists(self,
                       page_size: int = 50,
                       page_token: str = None,
                       user_id: str = None) -> dict:
        """获取调用身份可见的任务清单列表

        Args:
            page_size (int, optional): 返回的清单数量，范围 1-200。默认 50
            page_token (str, optional): 翻页标记，首次请求无需传递
            user_id (str, optional): 指定的用户 ID（受 user_id_type 影响），
                为空时默认使用当前调用身份

        Returns:
            dict: 接口返回数据，结构同官方文档

        References:
            https://open.feishu.cn/document/task-v2/tasklist/list
        """
        url = 'https://open.feishu.cn/open-apis/task/v2/tasklists'
        params = clean_params({
            'page_size': page_size,
            'page_token': page_token,
            'user_id': user_id,
            'user_id_type': self.user_id_type
        })

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
        params = clean_params({
            'page_size': page_size,
            'user_id_type': self.user_id_type,
            'completed': completed,
            'start_create_time': start_create_time,
            'end_create_time': end_create_time,
            'page_token': page_token
        })

        response = self.request('GET', url, params=params)
        return response.json()
        
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

    def _list_tasks_v1(self,
                       task_completed: bool = None,
                       start_create_time: str = None,
                       end_create_time: str = None,
                       page_size: int = 50,
                       page_token: str = None) -> dict:
        """查询任务列表（v1版本，支持时间范围过滤）- 内部方法
        
        不建议直接调用此方法，请使用 list_tasks() 方法。
        
        Args:
            task_completed (bool, optional): 是否已完成
            start_create_time (str, optional): 查询开始时间
            end_create_time (str, optional): 查询结束时间
            page_size (int, optional): 每页返回的任务数量
            page_token (str, optional): 分页标记
                
        Returns:
            dict: 任务列表信息
            
        Note:
            本函数由 AI 辅助生成 (Claude Sonnet 4.5 thinking)
        """
        url = 'https://open.feishu.cn/open-apis/task/v1/tasks'
        
        params = {
            'page_size': page_size
        }
        
        if task_completed is not None:
            params['task_completed'] = task_completed
            
        if start_create_time:
            params['start_create_time'] = start_create_time
            
        if end_create_time:
            params['end_create_time'] = end_create_time
            
        if page_token:
            params['page_token'] = page_token
            
        response = self.request('GET', url, params=params)
        return response.json()

    def create_task(self,
                    summary: str,
                    description: str = None,
                    due_time: str = None,
                    members: list = None,
                    tasklists: list = None,
                    client_token: str = None,
                    **kwargs) -> dict:
        """创建任务
        
        创建一个新的飞书任务。需要使用用户授权（user_access_token）。
        
        Args:
            summary (str): 任务标题，必填
            description (str, optional): 任务描述（富文本格式）
            due_time (str, optional): 截止时间（Unix毫秒时间戳字符串）
            members (list, optional): 任务成员列表，每个成员包含：
                - id (str): 成员ID（根据 user_id_type 决定格式）
                - role (str): 角色，可选值：
                    - "assignee": 负责人
                    - "follower": 关注人
            tasklists (list, optional): 要添加到的任务清单GUID列表
            client_token (str, optional): 幂等token，用于防止重复创建
            **kwargs: 其他可选参数，如 custom_fields（自定义字段）等
                
        Returns:
            dict: 创建结果，包含以下字段:
                - code (int): 状态码，0表示成功
                - msg (str): 状态消息
                - data (dict): 任务数据
                    - task (dict): 创建的任务信息
                        - guid (str): 任务GUID
                        - summary (str): 任务标题
                        - ...其他任务字段
                    
        Permissions:
            需要以下权限之一:
            - task:task - 查看、创建、编辑和删除任务
            - task:task:write - 创建和更新任务
            
        References:
            - API文档: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/create
            
        Note:
            本函数由 AI 辅助生成 (Claude Sonnet 4.5 thinking)
            - 必须使用用户授权模式（user_access_token）
            - 创建的任务归属于授权用户
            - 支持通过 client_token 实现幂等调用
            
        Examples:
            >>> # 创建简单任务
            >>> task_api = LarkTask(user_access_token='u-xxx')
            >>> result = task_api.create_task(
            ...     summary="完成项目文档",
            ...     description="需要完成技术设计文档"
            ... )
            >>> task_guid = result['data']['task']['guid']
            
            >>> # 创建带负责人和截止时间的任务
            >>> import time
            >>> due = str(int(time.time() * 1000) + 7 * 24 * 60 * 60 * 1000)  # 7天后
            >>> result = task_api.create_task(
            ...     summary="代码审查",
            ...     due_time=due,
            ...     members=[
            ...         {"id": "ou_xxx", "role": "assignee"}
            ...     ]
            ... )
        """
        url = 'https://open.feishu.cn/open-apis/task/v2/tasks'
        
        # 构建请求体
        body = {
            "summary": summary
        }
        
        if description:
            body["description"] = description
            
        if due_time:
            body["due"] = {
                "timestamp": due_time,
                "is_all_day": False
            }
            
        if members:
            body["members"] = members
            
        if tasklists:
            body["tasklists"] = [{"tasklist_guid": guid} for guid in tasklists]
            
        if client_token:
            body["client_token"] = client_token
            
        # 添加其他可选参数
        for key, value in kwargs.items():
            if value is not None:
                body[key] = value
        
        params = {
            'user_id_type': self.user_id_type
        }
        
        response = self.request('POST', url, params=params, json=body)
        return response.json()

    def create_subtask(self,
                       task_guid: str,
                       summary: str,
                       description: str = None,
                       due_time: str = None,
                       members: list = None,
                       client_token: str = None,
                       **kwargs) -> dict:
        """创建子任务
        
        在指定任务下创建子任务。需要使用用户授权（user_access_token）。
        
        Args:
            task_guid (str): 父任务的GUID，必填
            summary (str): 子任务标题，必填
            description (str, optional): 子任务描述（富文本格式）
            due_time (str, optional): 截止时间（Unix毫秒时间戳字符串）
            members (list, optional): 任务成员列表，格式同 create_task
            client_token (str, optional): 幂等token，用于防止重复创建
            **kwargs: 其他可选参数
                
        Returns:
            dict: 创建结果，格式同 create_task
                    
        Permissions:
            需要以下权限之一:
            - task:task - 查看、创建、编辑和删除任务
            - task:task:write - 创建和更新任务
            
        References:
            - API文档: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task-subtask/create
            
        Note:
            本函数由 AI 辅助生成 (Claude Sonnet 4.5 thinking)
            - 必须使用用户授权模式（user_access_token）
            - 需要对父任务有编辑权限
            - 子任务会自动继承父任务的清单关联
            
        Examples:
            >>> # 创建子任务
            >>> task_api = LarkTask(user_access_token='u-xxx')
            >>> result = task_api.create_subtask(
            ...     task_guid="parent_task_guid",
            ...     summary="子任务1：需求分析",
            ...     description="详细分析用户需求"
            ... )
            
            >>> # 批量创建子任务
            >>> parent_guid = "parent_task_guid"
            >>> subtasks = ["设计方案", "编写代码", "测试验证"]
            >>> for title in subtasks:
            ...     task_api.create_subtask(
            ...         task_guid=parent_guid,
            ...         summary=title
            ...     )
        """
        url = f'https://open.feishu.cn/open-apis/task/v2/tasks/{task_guid}/subtasks'
        
        # 构建请求体（与 create_task 类似）
        body = {
            "summary": summary
        }
        
        if description:
            body["description"] = description
            
        if due_time:
            body["due"] = {
                "timestamp": due_time,
                "is_all_day": False
            }
            
        if members:
            body["members"] = members
            
        if client_token:
            body["client_token"] = client_token
            
        # 添加其他可选参数
        for key, value in kwargs.items():
            if value is not None:
                body[key] = value
        
        params = {
            'user_id_type': self.user_id_type
        }
        
        response = self.request('POST', url, params=params, json=body)
        return response.json()

    # 向后兼容的别名方法
    def list_tasks_v2(self, *args, **kwargs) -> dict:
        """查询任务列表（v2版本）- 已弃用
        
        此方法已弃用，请使用 list_tasks() 方法。
        list_tasks() 会根据参数自动选择最合适的 API 版本。
        
        Note:
            此方法保留仅用于向后兼容，未来版本可能会移除。
        """
        return self._list_tasks_v2(*args, **kwargs)

    def list_tasks_v1(self, *args, **kwargs) -> dict:
        """查询任务列表（v1版本）- 已弃用
        
        此方法已弃用，请使用 list_tasks() 方法。
        list_tasks() 会根据参数自动选择最合适的 API 版本。
        
        Note:
            此方法保留仅用于向后兼容，未来版本可能会移除。
        """
        return self._list_tasks_v1(*args, **kwargs)
