"""LarkMessage - 飞书即时通讯消息发送模块

本模块提供了飞书即时通讯的消息发送功能，支持发送文本、图片、文件等多种类型的消息。

主要功能：
    - 消息发送：支持文本、图片、文件消息发送
    - 文件上传：支持图片和文件上传
    - 群组管理：获取群组列表
    - 消息撤回：支持消息撤回功能
    - 智能类型检测：自动检测内容类型并选择合适的发送方式
"""

from __future__ import annotations
from .api import LarkAPI
from typing_extensions import Literal
from typing import List, Dict, Any, Optional, Tuple
import json
from pathlib import Path
import requests
from requests_toolbelt import MultipartEncoder
import io
import time
from datetime import datetime

from .log import create_logger
from ._typing import UserId


class LarkMessage(LarkAPI):
    """飞书即时通讯消息发送类
    
    继承自 LarkAPI，提供飞书即时通讯的消息发送功能。
    支持发送文本、图片、文件等多种类型的消息，并提供消息撤回功能。
    
    Args:
        app_id (str): 飞书应用 ID
        app_secret (str): 飞书应用密钥
        receive_id (str, optional): 默认接收者 ID. Defaults to None.
        log_level (Literal, optional): 日志级别. Defaults to 'ERROR'.
        
    Attributes:
        url_im (str): 即时通讯 API 基础 URL
        logger: 日志记录器
        receive_id (str): 接收者 ID
        message_history (list): 消息发送历史
        
    Examples:
        >>> lark_msg = LarkMessage('app_id', 'app_secret', 'user_id')
        >>> lark_msg.send('Hello World')
        >>> lark_msg.send_image('/path/to/image.png')
    """

    def __init__(self,
                 app_id,
                 app_secret,
                 receive_id: str = None,
                 log_level: Literal['INFO', 'DEBUG', 'WARNING',
                                    'ERROR'] = 'ERROR'):
        """初始化 LarkMessage 实例
        
        Args:
            app_id (str): 飞书应用 ID
            app_secret (str): 飞书应用密钥
            receive_id (str, optional): 默认接收者 ID. Defaults to None.
            log_level (Literal, optional): 日志级别. Defaults to 'ERROR'.
        """
        super().__init__(app_id, app_secret)
        self.url_im = "https://open.feishu.cn/open-apis/im/v1"
        self.logger = create_logger(stack_depth=2, level=log_level)
        self.receive_id = receive_id
        self.message_history = []
        self._user_cache: Dict[str, Dict[str, Any]] = {}

    def send(self,
             content: str | Path | Dict,
             receive_id: str = None,
             **kwargs):
        """智能发送消息（通用接口）
        
        根据内容类型智能选择合适的发送方式：
        - 字符串：作为文本消息发送
        - 文件路径：根据文件类型自动选择图片或文件发送
        - DataFrame/Figure：支持 pandas DataFrame 和 matplotlib Figure
        
        Args:
            content (str | Path | Dict): 消息内容
            receive_id (str, optional): 接收者 ID. Defaults to None.
            **kwargs: 其他参数
            
        Returns:
            dict: 发送结果
        """
        if isinstance(content, (str, Path)):
            test_path = Path(content)
            if test_path.exists():
                if test_path.suffix.lower() in [
                        '.png', '.jpg', '.jpeg', '.gif'
                ]:
                    return self.send_image(test_path,
                                           receive_id=receive_id,
                                           **kwargs)
                else:
                    return self.send_file(test_path,
                                          receive_id=receive_id,
                                          **kwargs)
            else:
                return self.messages(content, receive_id=receive_id, **kwargs)
        else:
            try:
                from pandas.core.frame import DataFrame
                if isinstance(content, DataFrame):
                    return self.send_file(content,
                                          receive_id=receive_id,
                                          **kwargs)
            except ModuleNotFoundError:
                pass

            try:
                from matplotlib.figure import Figure
                if isinstance(content, Figure):
                    return self.send_image(content,
                                           receive_id=receive_id,
                                           **kwargs)
            except ModuleNotFoundError:
                pass

    @staticmethod
    def _normalize_timestamp(value: datetime | int | float | str) -> int:
        """将多种时间格式转换为秒级时间戳"""
        if isinstance(value, datetime):
            return int(value.timestamp())
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            try:
                return int(datetime.fromisoformat(value).timestamp())
            except ValueError:
                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
                    try:
                        return int(datetime.strptime(value, fmt).timestamp())
                    except ValueError:
                        continue
            raise ValueError(f"Unsupported time format: {value}")
        raise TypeError(f"Unsupported time type: {type(value)}")

    def list_chat_messages(self,
                           chat_id: str,
                           start_time: datetime | int | float | str = None,
                           page_size: int = 50,
                           max_pages: int = 10,
                           page_token: str = None,
                           delay: float = 0.1) -> Dict[str, Any]:
        """获取群聊消息（支持自动分页）

        Args:
            chat_id: 群聊ID
            start_time: 起始时间，支持 datetime、时间戳或字符串
            page_size: 每页条数，默认 50
            max_pages: 最大分页数
            page_token: 起始 page_token，用于继续翻页
            delay: 每次翻页之间的 sleep 秒数，避免触发限流

        Returns:
            dict: {
                "items": 消息列表,
                "has_more": 是否还有更多,
                "next_page_token": 下一页的游标
            }
        """
        url = f"{self.url_im}/messages"
        params: Dict[str, Any] = {
            "container_id_type": "chat",
            "container_id": chat_id,
            "page_size": page_size
        }
        if start_time:
            params["start_time"] = str(self._normalize_timestamp(start_time))

        all_messages: List[Dict[str, Any]] = []
        current_page = 1
        next_token = page_token
        has_more = False

        while current_page <= max_pages:
            request_params = params.copy()
            if next_token:
                request_params["page_token"] = next_token

            response = requests.get(url, headers=self.headers, params=request_params)
            response.raise_for_status()
            data = response.json()
            if data.get("code") != 0:
                raise RuntimeError(
                    f"Failed to fetch messages: {data.get('code')} {data.get('msg')}")

            page_messages = data.get("data", {}).get("items", [])
            if not page_messages:
                break

            all_messages.extend(page_messages)
            has_more = data.get("data", {}).get("has_more", False)
            next_token = data.get("data", {}).get("page_token")

            if not has_more or not next_token or len(page_messages) < page_size:
                break

            current_page += 1
            if delay:
                time.sleep(delay)

        return {
            "items": all_messages,
            "has_more": has_more,
            "next_page_token": next_token
        }

    def fetch_chat_messages(self,
                            chat_id: str,
                            start_time: datetime | int | float | str = None,
                            page_size: int = 50,
                            max_pages: int = 10,
                            page_token: str = None,
                            delay: float = 0.1,
                            skip_first: bool = False) -> List[Dict[str, Any]]:
        """便捷获取群聊消息列表。

        这是 :meth:`list_chat_messages` 的封装，直接返回消息列表，
        并提供 ``skip_first`` 参数来兼容增量拉取的场景。
        """
        result = self.list_chat_messages(chat_id=chat_id,
                                         start_time=start_time,
                                         page_size=page_size,
                                         max_pages=max_pages,
                                         page_token=page_token,
                                         delay=delay)
        items = result.get("items", [])
        if skip_first and items:
            return items[1:]
        return items

    def get_user(self,
                 user_id: str,
                 user_id_type: UserId = None) -> Optional[Dict[str, Any]]:
        """获取用户信息并自动缓存"""
        if not user_id:
            return None

        resolved_type = user_id_type or self.user_id_type or 'open_id'
        cache_key = f"{user_id}:{resolved_type}"
        if cache_key in self._user_cache:
            return self._user_cache[cache_key]

        url = f"https://open.feishu.cn/open-apis/contact/v3/users/{user_id}"
        params = {"user_id_type": resolved_type}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("code") != 0:
            self.logger.warning("get_user failed: %s", data.get("msg"))
            return None

        user = data.get("data", {}).get("user")
        if user:
            self._user_cache[cache_key] = user
        return user

    def get_user_name(self,
                      user_id: str,
                      default: str = "未知",
                      user_id_type: UserId = None) -> str:
        """获取用户姓名（失败时返回默认值或原始ID）"""
        user = self.get_user(user_id, user_id_type=user_id_type)
        if user and user.get("name"):
            return user["name"]
        return user_id or default


    def messages(
        self,
        content: str | Dict,
        receive_id: str = None,
        msg_type: Literal['text', 'post', 'image', 'file', 'audio', 'media',
                          'sticker', 'interactive', 'share_chat', 'share_user',
                          'system'] = 'text',
        receive_id_type: Literal['open_id', 'user_id', 'union_id', 'email',
                                 'chat_id'] = None,
    ):
        """发送消息
        https://open.feishu.cn/document/server-docs/im-v1/message/create
        https://open.feishu.cn/document/server-docs/im-v1/message-content-description/create_json
        """
        receive_id = receive_id or self.receive_id
        if receive_id_type is None:
            if receive_id.startswith('ou_'):
                receive_id_type = 'open_id'
            elif receive_id.startswith('on_'):
                receive_id_type = 'union_id'
            elif receive_id.startswith('oc_'):
                receive_id_type = 'chat_id'
            elif '@' in receive_id:
                receive_id_type = 'email'
            else:
                receive_id_type = 'user_id'

        if isinstance(content, dict):
            content = json.dumps(content)
        else:
            if msg_type == 'text':
                content = f"""{{"text":"{content}"}}"""
            elif msg_type == 'image':
                content = f"""{{"image_key":"{content}"}}"""
            elif msg_type == 'file':
                content = f"""{{"file_key":"{content}"}}"""
            # TODO: 其他类型消息的content

        url = f'{self.url_im}/messages?receive_id_type={receive_id_type}'
        payload = dict(
            receive_id=receive_id,
            content=content,
            msg_type=msg_type,
        )
        response = self.request("POST", url, payload)
        self.logger.info("messages response: " + response.text)
        self.message_history.append(response.json())
        return response.json()

    def send_interactive_card(
        self,
        card_content: Dict[str, Any],
        receive_id: str = None,
        receive_id_type: Literal['open_id', 'user_id', 'union_id', 'email',
                                 'chat_id'] = None,
        with_response: bool = False
    ) -> Optional[str] | Tuple[Optional[str], Dict[str, Any]]:
        """发送交互式卡片，默认返回 message_id。

        Args:
            card_content: 卡片 JSON 内容 (Python dict)
            receive_id: 接收者 ID
            receive_id_type: 接收者 ID 类型，不传则自动判断
            with_response: 是否同时返回原始响应
        """
        response = self.messages(content=card_content,
                                 receive_id=receive_id,
                                 msg_type='interactive',
                                 receive_id_type=receive_id_type)
        message_id = None
        if response.get('code') == 0:
            message_id = response.get('data', {}).get('message_id')
        else:
            self.logger.warning("send_interactive_card failed: %s", response.get('msg'))

        if with_response:
            return message_id, response
        return message_id

    def upload_image(self,
                     image: str | Path,
                     image_type: Literal['message', 'avatar'] = 'message'):
        """上传图片
        https://open.feishu.cn/document/server-docs/im-v1/image/create"""
        if isinstance(image, (str, Path)):
            image = Path(image)
            buffer = open(image, 'rb')
        else:
            buffer = io.BytesIO()
            from matplotlib.figure import Figure
            if isinstance(image, Figure):
                image.savefig(buffer, format='png')
            if buffer.getbuffer().nbytes == 0:
                raise ValueError(f"Unknown `file` type {type(file)}")
            buffer.seek(0)
            raise ValueError(f"Unknown `image_path` type {type(image)}")

        form = {'image_type': image_type, 'image': (buffer)}  # 需要替换具体的path
        multi_form = MultipartEncoder(form)
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': multi_form.content_type
        }
        response = requests.post(f"{self.url_im}/images",
                                 headers=headers,
                                 data=multi_form)
        res = response.json()
        if res.get('code') == 0:
            return res['data']['image_key']
        print(res)
        try:
            image.close()
        except:
            pass
        return None

    def send_image(self, image: str | Path, receive_id: str = None):
        receive_id = receive_id or self.receive_id
        image_key = self.upload_image(image)
        if image_key is not None:
            return self.messages(content=image_key,
                                 receive_id=receive_id,
                                 msg_type='image')

    def upload_file(self, file: str | Path, file_name: str = None):
        """上传文件
        https://open.feishu.cn/document/server-docs/im-v1/file/create
        """
        if isinstance(file, (str, Path)):
            file = Path(file)
            buffer = open(file, 'rb')
            file_type = {
                '.opus': 'opus',
                '.mp4': 'mp4',
                '.pdf': 'pdf',
                '.doc': 'doc',
                '.docx': 'doc',
                '.xls': 'xls',
                '.xlsx': 'xls',
                '.ppt': 'ppt',
                '.pptx': 'ppt',
            }.get(file.suffix.lower(), 'stream')
            _file_name = file.name
        else:
            buffer = io.BytesIO()
            import pandas as pd
            if isinstance(file, pd.DataFrame):
                file.to_excel(buffer, engine='openpyxl')
            file_type = 'xls'
            _file_name = 'dataframe.xlsx'
            if file_name is not None:
                file_name = Path(file_name).with_suffix('.xlsx').name
            if buffer.getbuffer().nbytes == 0:
                raise ValueError(f"Unknown `file` type {type(file)}")
            buffer.seek(0)

        form = {
            'file_type': file_type,
            'file_name': file_name or _file_name,
            'file': (_file_name, buffer, 'text/plain')
        }  # 需要替换具体的 path 具体的格式参考  https://www.w3school.com.cn/media/media_mimeref.asp

        multi_form = MultipartEncoder(form)
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': multi_form.content_type
        }
        response = requests.post(f"{self.url_im}/files",
                                 headers=headers,
                                 data=multi_form)

        res = response.json()
        if res.get('code') == 0:
            return res['data']['file_key']
        print(res)
        try:
            buffer.close()
        except:
            pass
        return None

    def send_file(self,
                  file: str | Path,
                  receive_id: str = None,
                  file_name: str = None):
        receive_id = receive_id or self.receive_id
        file_key = self.upload_file(file, file_name)
        if file_key is not None:
            return self.messages(content=file_key,
                                 receive_id=receive_id,
                                 msg_type='file')

    def get_group_chat_list(
            self,
            sort_type: Literal['ByActiveTimeDesc',
                               'ByCreateTimeAsc'] = 'ByCreateTimeAsc',
            user_id_type: UserId = None,
            page_token: str = None,
            page_size: int = None):
        """获取用户或机器人所在的群列表
        https://open.feishu.cn/document/server-docs/group/chat/list
        """
        params = dict(user_id_type=user_id_type,
                      sort_type=sort_type,
                      page_token=page_token,
                      page_size=page_size)
        return self.request("GET", f"{self.url_im}/chats",
                            params=params).json()

    def recall(self, message_id: str):
        """撤回消息
        https://open.feishu.cn/document/server-docs/im-v1/message/delete
        """
        url = f'{self.url_im}/messages/{message_id}'
        return self.request("DELETE", url).json()

    def recall_all(self):
        """撤回所有可撤回的历史消息"""
        for m in self.message_history:
            if m['code'] != 0: continue
            message_id = m['data']['message_id']
            recall_response = self.recall(message_id)
            if recall_response['code'] != 0:
                msg = f"Failed to recall message {message_id} {m['data']['body']}. Reason: {recall_response['msg']}"
            else:
                msg = f"Successfully recall message {message_id} {m['data']['body']}"
            print(msg)

    def get_message_reactions(self, message_id: str) -> List[Dict[str, Any]]:
        """获取消息的表情回应列表"""
        url = f"{self.url_im}/messages/{message_id}/reactions"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()

        if data.get("code") != 0:
            self.logger.warning("get_message_reactions failed: %s", data.get("msg"))
            return []

        return data.get("data", {}).get("items", [])

    def add_reaction(self, message_id: str, emoji_type: str = "DONE") -> bool:
        """给指定消息添加表情回应"""
        url = f"{self.url_im}/messages/{message_id}/reactions"
        payload = {"reaction_type": {"emoji_type": emoji_type}}
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        data = response.json()

        if data.get("code") == 0:
            return True

        self.logger.warning("add_reaction failed: %s", data.get("msg"))
        return False

    def reply_to_message(
        self,
        message_id: str,
        content: str | Dict[str, Any],
        msg_type: Literal['text', 'post', 'image', 'file', 'audio', 'media',
                          'sticker', 'interactive', 'share_chat', 'share_user',
                          'system'] = 'text',
    ) -> bool:
        """在消息下回复（线程回复）"""
        url = f"{self.url_im}/messages/{message_id}/reply"

        if isinstance(content, dict):
            payload_content = json.dumps(content)
        else:
            if msg_type == 'text':
                payload_content = json.dumps({"text": content})
            else:
                payload_content = content

        payload = {"content": payload_content, "msg_type": msg_type}
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        data = response.json()

        if data.get("code") == 0:
            return True

        self.logger.warning("reply_to_message failed: %s", data.get("msg"))
        return False

    def format_messages_for_display(
        self,
        messages: List[Dict[str, Any]],
        include_quote: bool = True,
        include_user_id: bool = True,
        time_format: str = "%Y-%m-%d %H:%M:%S",
        skip_system: bool = True,
        resolve_user_names: bool = False
    ) -> str:
        """将消息列表格式化为易读文本

        Args:
            messages: 消息列表
            include_quote: 是否包含引用/回复信息
            include_user_id: 是否显示用户ID
            time_format: 时间格式字符串
            skip_system: 是否跳过系统消息
            resolve_user_names: 是否解析用户名（需要API调用）

        Returns:
            str: 格式化的消息文本
        """
        formatted_lines = []

        # 创建消息ID到内容的映射，用于处理引用
        msg_map = {}
        for msg in messages:
            msg_id = msg.get("message_id", "")
            msg_map[msg_id] = msg

        for msg in messages:
            # 提取消息基本信息
            msg_id = msg.get("message_id", "")
            create_time = msg.get("create_time", "")
            sender_obj = msg.get("sender", {})
            sender_id = sender_obj.get("id", "未知用户ID")
            msg_type = msg.get("msg_type", "")
            body = msg.get("body", {})

            # 忽略 system 类型消息
            if skip_system and msg_type == "system":
                continue

            # 格式化时间
            if create_time:
                time_str = datetime.fromtimestamp(int(create_time) / 1000).strftime(time_format)
            else:
                time_str = "未知时间"

            # 解析用户名（如果启用）
            if resolve_user_names and sender_id != "未知用户ID":
                sender_display = self.get_user_name(sender_id, default=sender_id)
            elif include_user_id:
                sender_display = sender_id
            else:
                sender_display = "用户"

            # 提取消息内容
            content = ""
            if msg_type == "text":
                content = body.get("content", "")
            elif msg_type == "post":
                # 富文本消息
                post_content = body.get("content", "{}")
                try:
                    post_data = json.loads(post_content) if isinstance(post_content, str) else post_content
                    content = str(post_data)
                except:
                    content = "[富文本消息]"
            elif msg_type == "image":
                content = "[图片]"
            elif msg_type == "file":
                content = "[文件]"
            else:
                content = f"[{msg_type} 类型消息]"

            # 检查是否有引用/回复
            quote_info = ""
            if include_quote:
                parent_id = msg.get("parent_id")
                if parent_id and parent_id in msg_map:
                    parent_msg = msg_map[parent_id]
                    parent_sender = parent_msg.get("sender", {}).get("id", "未知")
                    parent_body = parent_msg.get("body", {})
                    parent_content = parent_body.get("content", "")[:50]
                    quote_info = f" [回复 {parent_sender}: {parent_content}...]"

            # 格式化单条消息
            formatted_lines.append(f"[{time_str}] {sender_display}{quote_info}: {content}")

        return "\n".join(formatted_lines)

    def send_confirmation_card(
        self,
        title: str,
        content: str,
        receive_id: str = None,
        color: str = "blue",
        note: str = "👍 点赞保存 | 👎 点踩跳过",
        receive_id_type: Literal['open_id', 'user_id', 'union_id', 'email', 'chat_id'] = None
    ) -> Optional[str]:
        """发送带确认按钮的交互式卡片

        Args:
            title: 卡片标题
            content: 卡片内容（支持 Markdown）
            receive_id: 接收者 ID
            color: 卡片颜色，可选值: blue, wathet, turquoise, green, yellow, orange, red, carmine, violet, purple, indigo, grey
            note: 底部提示文本
            receive_id_type: 接收者 ID 类型

        Returns:
            str: 消息ID，发送失败返回 None
        """
        card_content = {
            "header": {
                "template": color,
                "title": {
                    "content": title,
                    "tag": "plain_text"
                }
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "content": content,
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": note
                        }
                    ]
                }
            ]
        }

        return self.send_interactive_card(
            card_content=card_content,
            receive_id=receive_id,
            receive_id_type=receive_id_type
        )

    def check_reaction_status(
        self,
        reactions: List[Dict[str, Any]],
        confirm_types: List[str] = None,
        cancel_types: List[str] = None
    ) -> Optional[bool]:
        """检查表情回应状态

        Args:
            reactions: 表情回应列表（通过 get_message_reactions 获取）
            confirm_types: 确认表情类型列表，默认 ["THUMBSUP"]
            cancel_types: 取消表情类型列表，默认 ["THUMBSDOWN"]

        Returns:
            bool or None: True=确认, False=取消, None=无回应
        """
        if confirm_types is None:
            confirm_types = ["THUMBSUP"]
        if cancel_types is None:
            cancel_types = ["THUMBSDOWN"]

        has_confirm = False

        for reaction in reactions:
            emoji_type = reaction.get("reaction_type", {}).get("emoji_type", "")

            # 优先判断取消表情
            if emoji_type in cancel_types:
                return False

            # 记录是否有确认表情
            if emoji_type in confirm_types:
                has_confirm = True

        if has_confirm:
            return True

        return None  # 无回应
