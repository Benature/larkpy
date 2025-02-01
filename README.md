# lark.py
飞书开放平台 Python 接口 | Python SDK for Lark

## 安装 Install

```shell
pip install pylark
```

## 快速开始 Quick Start

```python

from larkpy import FeishuBot

url_webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxx"
feishu = FeishuBot(url_webhook)

# example 1
feishu.send_text(f"test")

# example 2
payload = [
    dict(tag="text", text=f"随便说点啥，然后配个链接" + "\n"),
    dict(tag="a", text="🔗 link", href="https://www.github.com")
]
feishu.send_with_payload(payload, title="标题")
```