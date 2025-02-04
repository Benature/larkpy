from __future__ import annotations
from .api import LarkAPI
from typing_extensions import Literal
from typing import List, Dict
import json
from pathlib import Path
import requests
from requests_toolbelt import MultipartEncoder
from .log import create_logger


class LarkMessage(LarkAPI):

    def __init__(self,
                 app_id,
                 app_secret,
                 level: Literal['INFO', 'DEBUG'] = 'INFO'):
        super().__init__(app_id, app_secret)
        self.url_im = "https://open.feishu.cn/open-apis/im/v1"
        self.logger = create_logger(stack_depth=2)

    def messages(
        self,
        receive_id: str,
        content: str | Dict,
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
        return response

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

    def send_image(self, receive_id: str, image_path: str | Path):
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
                  receive_id: str,
                  file_path: str | Path,
                  file_name: str = None):
        file_key = self.upload_file(file_path, file_name)
        if file_key is not None:
            return self.messages(receive_id, content=file_key, msg_type='file')

    def recall(self, message_id: str):
        """撤回消息
        https://open.feishu.cn/document/server-docs/im-v1/message/delete
        """
        url = f'{self.url_im}/messages/{message_id}'
        self.request("DELETE", url)
