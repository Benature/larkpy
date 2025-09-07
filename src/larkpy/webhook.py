"""LarkWebhook - 飞书机器人 Webhook 消息发送模块

本模块提供了通过 Webhook 向飞书群聊发送消息的功能，支持文本、富文本、卡片等多种格式。

主要类：
    - WebhookConfig: Webhook 配置管理类
    - LarkWebhook: 飞书机器人 Webhook 消息发送类
    - CollapsiblePanel: 折叠面板类，用于生成卡片元素

@Created: 2024   
@Author: Benature  
"""
from __future__ import annotations
import requests
import json
import os
from pathlib import Path
from typing import List, Dict, Union
from typing_extensions import Literal


class WebhookConfig:
    """飞书机器人 Webhook 配置管理类
    
    用于管理和存储飞书机器人的 Webhook URL 配置信息。
    支持将配置保存到本地文件，方便管理多个机器人配置。
    
    Args:
        config_file (str, optional): 配置文件路径，默认为 ~/.larkpy/webhook_config.json
        
    Examples:
        >>> config = WebhookConfig()
        >>> config.save_config('bot1', 'https://open.feishu.cn/...')
        >>> webhook_url = config.get_config('bot1')
    """

    def __init__(self, config_file: str = None):
        """初始化 WebhookConfig 实例
        
        Args:
            config_file (str, optional): 配置文件路径. Defaults to None.
                如果为 None，则使用默认路径 ~/.larkpy/webhook_config.json
        """
        self.config_file = Path(config_file) if config_file else Path.home(
        ) / '.larkpy' / 'webhook_config.json'
        self.config_file.parent.mkdir(exist_ok=True)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_config(self, name: str, webhook_url: str):
        """保存 Webhook 配置
        
        Args:
            name (str): 配置名称
            webhook_url (str): Webhook URL
        """
        self.config[name] = webhook_url
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def get_config(self, name: str) -> str:
        """获取 Webhook 配置
        
        Args:
            name (str): 配置名称
            
        Returns:
            str: Webhook URL，如果不存在返回 None
        """
        return self.config.get(name)


class LarkWebhook:
    """飞书机器人 Webhook 消息发送类
    
    通过 Webhook 向飞书群聊发送消息，支持文本、富文本、卡片等多种格式。
    
    Args:
        webhook_url (str): 飞书机器人的 Webhook URL
        
    Attributes:
        webhook_url (str): Webhook URL
        headers (dict): HTTP 请求头
        
    Examples:
        >>> webhook = LarkWebhook('https://open.feishu.cn/...')
        >>> webhook.send('Hello World')
        >>> webhook.send_card('Hello Card', title='测试卡片')
        
    References:
        https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN?lang=zh-CN
    """

    def __init__(self, webhook_url):
        """初始化 LarkWebhook 实例
        
        Args:
            webhook_url (str): 飞书机器人的 Webhook URL
        """
        self.webhook_url = webhook_url
        self.headers = {"Content-Type": "application/json"}

    def send_with_payload(self, payload: Dict):
        """直接使用 payload 发送消息
        
        Args:
            payload (Dict): 消息载荷
            
        Returns:
            requests.Response: HTTP 响应对象
        """
        return requests.post(self.webhook_url,
                             data=json.dumps(payload),
                             headers=self.headers)

    def send(self,
             content: Union[str, List[Dict], Dict],
             title: str = "",
             echo: bool = False):
        """发送消息到飞书群
        
        Args:
            content: 消息内容，可以是字符串或字典列表
            title: 消息标题
            echo: 是否打印请求数据
            
        Returns:
            requests.Response: HTTP响应对象
        """
        if isinstance(content, str):
            return self.send_text(content, title=title, echo=echo)
        else:
            return self.send_card(content=content, title=title, echo=echo)

    def send_text(self,
                  content: str | Dict,
                  title: str = "",
                  echo: bool = False) -> requests.Response:
        """发送纯文本消息
        
        Args:
            content: 要发送的文本内容
            title: 消息标题
            echo: 是否打印请求数据
            
        Returns:
            requests.Response: HTTP响应对象
        """

        if isinstance(content, dict):
            payload = content
        else:
            payload = [dict(tag="text", text=content)]
        return self.send_payload(payload, title=title, echo=echo)

    def send_payload(self,
                     payload_content: List[Dict],
                     title: str = "",
                     echo: bool = False) -> requests.Response:
        """以 payload 形式发送消息
        
        Args:
            payload_content: 消息内容
            title: 消息标题
            echo: 是否打印发送内容

        Returns:
            requests.Response: 响应对象
        """
        data = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [payload_content],
                    },
                },
            },
        }
        if echo:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        return requests.post(self.webhook_url,
                             data=json.dumps(data),
                             headers=self.headers)

    def send_post(self,
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
            return self.send_post([dict(tag="text", text=content)])
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

    def send_card(self,
                  content: Union[str, List[Dict], Dict],
                  title: str = "",
                  subtitle: str = "",
                  buttons: List[Dict] = None,
                  template: str = "blue",
                  echo: bool = False):
        """发送飞书交互式卡片消息
        
        Args:
            content (Union[str, List[Dict], Dict]): 卡片内容，可以是字符串、字典列表或字典
            title (str, optional): 卡片标题. Defaults to "".
            subtitle (str, optional): 卡片副标题. Defaults to "".
            buttons (List[Dict], optional): 按钮列表. Defaults to None.
            template (str, optional): 卡片模板颜色. Defaults to "blue".
            echo (bool, optional): 是否打印请求数据. Defaults to False.
            
        Returns:
            requests.Response: HTTP 响应对象
        """
        if isinstance(content, str):
            card_elements = [{
                "tag": "markdown",
                "content": content,
                "text_align": "left",
                "text_size": "normal_v2",
                "margin": "0px 0px 0px 0px"
            }]
        elif isinstance(content, list):
            card_elements = content
        elif isinstance(content, (dict, CollapsiblePanel)):
            card_elements = [content]
        else:
            raise ValueError(f"Unknown content type {type(content)}")

        for button in (buttons or []):
            card_elements.append({
                "tag":
                "button",
                "text": {
                    "tag": "plain_text",
                    "content": button['content']
                },
                "type":
                "default",
                "width":
                "default",
                "size":
                "medium",
                "behaviors": [{
                    "type":
                    "open_url",
                    "default_url":
                    button.get("default_url", None) or button.get("url", None)
                    or "",
                    "pc_url":
                    button.get("pc_url", ""),
                    "ios_url":
                    button.get("ios_url", ""),
                    "android_url":
                    button.get("android_url", ""),
                }],
                "margin":
                "0px 0px 0px 0px"
            })
        data = {
            "msg_type": "interactive",
            "card": {
                "schema": "2.0",
                "config": {
                    "update_multi": True,
                    "style": {
                        "text_size": {
                            "normal_v2": {
                                "default": "normal",
                                "pc": "normal",
                                "mobile": "heading"
                            }
                        }
                    }
                },
                "body": {
                    "direction": "vertical",
                    "padding": "12px 12px 12px 12px",
                    "elements": card_elements
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    },
                    "subtitle": {
                        "tag": "plain_text",
                        "content": subtitle
                    },
                    "template": template,
                    "padding": "12px 12px 12px 12px"
                }
            }
        }

        if echo:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        return requests.post(self.webhook_url,
                             data=json.dumps(data),
                             headers=self.headers)

    def test(self):
        """测试消息发送功能
        
        发送一条测试消息到飞书群。
        
        Returns:
            requests.Response: HTTP 响应对象
        """
        return self.send_post([{
            "tag": "text",
            "text": "项目有更新: "
        }, {
            "tag": "a",
            "text": "请查看",
            "href": "http://www.example.com/"
        }],
                              title="项目更新通知")

    @staticmethod
    def gen_collapsible_panel(content: str,
                              title: str = "",
                              expanded: bool = False,
                              direction: Literal["vertical",
                                                 "horizontal"] = "vertical",
                              background_color: Literal["red", "orange",
                                                        "yellow", "green",
                                                        "blue", "purple",
                                                        "gray"] = None,
                              width: Literal["auto", "fill",
                                             "auto_when_fold"] = "fill",
                              border: bool = False):
        """生成折叠面板
        
        Args:
            content (str): 面板内容
            title (str, optional): 面板标题. Defaults to "".
            expanded (bool, optional): 面板是否展开. Defaults to False.
            direction (Literal["vertical", "horizontal"], optional): 面板方向. Defaults to "vertical".
            background_color (str, optional): 面板背景色. Defaults to None.
            width (str, optional): 标题区的宽度. Defaults to "fill".
            border (bool, optional): 是否显示边框. Defaults to False.
            
        Returns:
            CollapsiblePanel: 折叠面板对象
        """
        cp = CollapsiblePanel(
            tag="collapsible_panel",  # 折叠面板的标签。
            # 操作组件的唯一标识。JSON 2.0 新增属性。用于在调用组件相关接口中指定组件。需开发者自定义。
            # element_id="custom_id",
            # 面板内组件的排列方向。JSON 2.0 新增属性。可选值："vertical"（垂直排列）、"horizontal"（水平排列）。默认为 "vertical"。
            direction=direction,
            # # 面板内组件的垂直间距。JSON 2.0 新增属性。可选值："small"(4px)、"medium"(8px)、"large"(12px)、"extra_large"(16px)或[0,99]px。
            # vertical_spacing="8px",
            # # 面板内组件内的垂直间距。JSON 2.0 新增属性。可选值："small"(4px)、"medium"(8px)、"large"(12px)、"extra_large"(16px)或[0,99]px。
            # horizontal_spacing="8px",
            # # 面板内组件的垂直居中方式。JSON 2.0 新增属性。默认值为 top。
            # vertical_align="top",
            # # 面板内组件的水平居中方式。JSON 2.0 新增属性。默认值为 left。
            # horizontal_align="left",
            # # 折叠面板的内边距。JSON 2.0 新增属性。支持范围 [0,99]px。
            # padding="8px 8px 8px 8px",
            # # 折叠面板的外边距。JSON 2.0 新增属性。默认值 "0"，支持范围 [-99,99]px。
            # margin="0px 0px 0px 0px",
            expanded=expanded,  # 面板是否展开。默认值 false。
            background_color=background_color,  # 折叠面板的背景色，默认为透明。
            header={
                # 折叠面板的标题设置。
                "title": {
                    # 标题文本设置。支持 plain_text 和 markdown。
                    "tag": "markdown",
                    "content": title
                },
                "background_color": background_color,  # 标题区的背景色，默认为透明。
                "vertical_align": "center",  # 标题区的垂直居中方式。
                "padding": "4px 0px 4px 8px",  # 标题区的内边距。
                "position": "top",  # 标题区的位置。
                "width": width,  # 标题区的宽度。默认值为 fill。
                "icon": {
                    "tag": "standard_icon",
                    "token": "down-small-ccm_outlined",
                    "color": "",
                    "size": "16px 16px"
                },
                "icon_position": "follow_text",  # 图标的位置。默认值为 right。
                # 折叠面板展开时图标旋转的角度，正值为顺时针，负值为逆时针。默认值为 180。
                "icon_expanded_angle": -180
            },
            border={
                # 边框设置。默认不显示边框。
                "color": "grey",  # 边框的颜色。
                "corner_radius": "5px"  # 圆角设置。
            },
            elements=[
                # 此处可添加各个组件的 JSON 结构。暂不支持表单（form）组件。
                {
                    "tag": "markdown",
                    "content": content
                }
            ])
        if border:
            cp['border'] = dict(
                color="grey",  # 边框的颜色。
                corner_radius="5px",  # 圆角设置。
            )
        return cp


class CollapsiblePanel(dict):
    """折叠面板类
    
    用于创建飞书卡片中的折叠面板元素。继承自 dict，可以像字典一样使用。
    """

    def __init__(self, *args, **kwargs):
        """初始化折叠面板实例
        
        Args:
            *args: 传递给 dict 的位置参数
            **kwargs: 传递给 dict 的关键字参数
        """
        super().__init__(*args, **kwargs)
