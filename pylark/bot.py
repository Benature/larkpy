'''
@Created: 2024   
@Author: Benature  

```python title="示例代码"

```
'''
from __future__ import annotations
import requests
import json

from typing_extensions import List, Dict, Literal


class FeishuBot:
    """飞书机器人
    https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN?lang=zh-CN
    """

    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.headers = {"Content-Type": "application/json"}

    def send(self,
             content: str | List[Dict],
             title: str = None,
             echo: bool = False) -> requests.Response:
        """发送消息
        
        Args:
            content (str | List[Dict]): 消息内容
            title (str, optional): 消息标题. Defaults to None.
            echo (bool, optional): 是否打印发送内容. Defaults to False.

        Returns:
            requests.Response: 响应对象
        """
        if isinstance(content, str):
            assert title is None, "title should be None when content is str"
            if echo:
                print(content)
            return self.send([dict(tag="text", text=content)])
        elif isinstance(content, list):
            data = {
                "msg_type": "post",
                "content": {
                    "post": {
                        "zh_cn": {
                            "title": title or "",
                            "content": [content],
                        },
                    },
                },
            }
            if echo:
                print(data)
            return requests.post(self.webhook_url,
                                 data=json.dumps(data),
                                 headers=self.headers)

    def test(self):
        return self.send([{
            "tag": "text",
            "text": "项目有更新: "
        }, {
            "tag": "a",
            "text": "请查看",
            "href": "http://www.example.com/"
        }],
                         title="项目更新通知")
