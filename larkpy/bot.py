'''
@Created: 2024   
@Author: Benature  

```python title="示例代码"

```
'''
from __future__ import annotations
import requests
import json
from typing import List, Dict
from typing_extensions import Literal


class LarkBot:
    """飞书机器人
    https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN?lang=zh-CN
    """

    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.headers = {"Content-Type": "application/json"}

    def send_with_payload(self, payload: Dict):
        return requests.post(self.webhook_url,
                             data=json.dumps(payload),
                             headers=self.headers)

    def send(self, content, title):
        return self.send_card(content=content, title=title)

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
                  content: str | List[Dict] | Dict,
                  title: str = "",
                  subtitle: str = "",
                  elements: List[Dict] = [],
                  template="blue",
                  echo: bool = False):
        """发送飞书卡片"""
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

        for button in elements:
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
            print(data)
        return requests.post(self.webhook_url,
                             data=json.dumps(data),
                             headers=self.headers)

    def test(self):
        return self.send_post([{
            "tag": "text",
            "text": "项目有更新: "
        }, {
            "tag": "a",
            "text": "请查看",
            "href": "http://www.example.com/"
        }],
                              title="项目更新通知")

    def gen_collapsible_panel(self,
                              content: str,
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
