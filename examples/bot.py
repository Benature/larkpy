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
