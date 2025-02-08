from __future__ import annotations
from .api import LarkAPI
from typing_extensions import Literal
from typing import List, Dict
import json
from pathlib import Path
import requests
from requests_toolbelt import MultipartEncoder
from .log import create_logger
from ._typing import UserId


class LarkMessage(LarkAPI):

    def __init__(self,
                 app_id,
                 app_secret,
                 receive_id: str = None,
                 log_level: Literal['INFO', 'DEBUG', 'WARNING',
                                    'ERROR'] = 'ERROR'):
        super().__init__(app_id, app_secret)
        self.url_im = "https://open.feishu.cn/open-apis/im/v1"
        self.logger = create_logger(stack_depth=2, level=log_level)
        self.receive_id = receive_id
        self.message_history = []

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
                     image_path: str | Path,
                     image_type: Literal['message', 'avatar'] = 'message'):
        """上传图片
        https://open.feishu.cn/document/server-docs/im-v1/image/create"""
        url = f"{self.url_im}/images"
        form = {
            'image_type': image_type,
            'image': (open(image_path, 'rb'))
        }  # 需要替换具体的path
        multi_form = MultipartEncoder(form)
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': multi_form.content_type
        }
        response = requests.post(url, headers=headers, data=multi_form)
        res = response.json()
        if res.get('code') == 0:
            return res['data']['image_key']
        print(res)
        return None

    def send_image(self, image_path: str | Path, receive_id: str = None):
        receive_id = receive_id or self.receive_id
        image_key = self.upload_image(image_path)
        if image_key is not None:
            return self.messages(receive_id,
                                 content=image_key,
                                 msg_type='image')

    def upload_file(self, file_path: str | Path, file_name: str = None):
        """上传文件
        https://open.feishu.cn/document/server-docs/im-v1/file/create
        """
        file_path = Path(file_path)

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
        }.get(file_path.suffix.lower(), 'stream')

        url = f"{self.url_im}/files"
        form = {
            'file_type': file_type,
            'file_name': file_name or file_path.name,
            'file': (file_path.name, open(file_path, 'rb'), 'text/plain')
        }  # 需要替换具体的path  具体的格式参考  https://www.w3school.com.cn/media/media_mimeref.asp
        multi_form = MultipartEncoder(form)
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': multi_form.content_type
        }
        response = requests.post(url, headers=headers, data=multi_form)
        res = response.json()
        if res.get('code') == 0:
            return res['data']['file_key']
        print(res)
        return None

    def send_file(self,
                  file_path: str | Path,
                  receive_id: str = None,
                  file_name: str = None):
        receive_id = receive_id or self.receive_id
        file_key = self.upload_file(file_path, file_name)
        if file_key is not None:
            return self.messages(receive_id, content=file_key, msg_type='file')

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
