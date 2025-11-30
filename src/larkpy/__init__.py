"""larkpy - 飞书开放平台 Python SDK

larkpy 是一个针对飞书开放平台的 Python SDK，提供了完整的飞书 API 接口封装，
包括机器人消息发送、文档操作、多维表格、即时通讯、日历管理等功能。

Examples:
    基本使用示例:
    
    .. code-block:: python
    
        from larkpy import LarkWebhook
        
        # 发送消息到飞书群
        webhook = LarkWebhook(webhook_url)
        webhook.send("Hello, World!")
        
        # 使用 API 接口
        from larkpy import LarkAPI
        
        api = LarkAPI(app_id, app_secret)
        node = api.get_node(wiki_token)

主要模块:
    - LarkWebhook: 飞书机器人 webhook 消息发送
    - LarkAPI: 飞书开放平台 API 调用基础类
    - LarkOAuth: OAuth 2.0 用户授权管理
    - TokenManager: 用户授权令牌持久化管理
    - LarkMessage: 即时通讯消息发送和管理
    - LarkDocx: 飞书文档的读取和操作
    - LarkBitTable: 多维表格的数据操作
    - LarkCalendar: 日历事件的管理
    - LarkTask: 飞书任务的查询和管理
    - LarkRequests: 基于 Cookie 的飞书浏览器请求
    - CardElementGenerator: 飞书卡片元素生成器
"""

__version__ = "0.4.0-dev"
__author__ = "Benature"
__github__ = "https://github.com/Benature/larkpy"
__homepage__ = __github__

from .webhook import LarkWebhook, WebhookConfig
from .card import CardElementGenerator

from .api import LarkAPI
from .auth import LarkOAuth
from .token_manager import TokenManager
from .docx import LarkDocx
from .bitTable import LarkBitTable
from .im import LarkMessage
from .calendar import LarkCalendar
from .task import LarkTask
from .browser import LarkRequests
