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
from typing import List, Dict
import json
from pathlib import Path
import requests
from requests_toolbelt import MultipartEncoder
import io

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
