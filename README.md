<a href="https://wucaiapp.com/"><img src="https://p1-hera.feishucdn.com/tos-cn-i-jbbdkfciu3/84a9f036fe2b44f99b899fff4beeb963~tplv-jbbdkfciu3-image:0:0.image" height="50" align="right"></a>

# lark.py
飞书开放平台 Python 接口 | Python SDK for Lark

## 安装 Install

```shell
pip install larkpy
```

## 快速开始 Quick Start

```python
from larkpy import LarkBot

url_webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxx"
feishu = LarkBot(url_webhook)

# example 1
feishu.send_text(f"test")

# example 2
payload = [
    dict(tag="text", text=f"随便说点啥，然后配个链接" + "\n"),
    dict(tag="a", text="🔗 link", href="https://www.github.com")
]
feishu.send_with_payload(payload, title="标题")
```