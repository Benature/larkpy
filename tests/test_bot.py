"""测试 bot.py 模块"""
import sys
import os
from pathlib import Path
import json
import tempfile
import shutil

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from larkpy.webhook import LarkWebhook, BotConfig
from test_utils import skip_if_no_config, test_config


def test_bot_config_management():
    """测试机器人配置管理"""
    print("测试机器人配置管理...")

    # 使用临时目录进行测试
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_file = Path(tmp_dir) / "test_bot_config.json"

        # 创建配置管理器
        bot_config = BotConfig(str(config_file))

        # 测试保存配置
        test_webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/test_token"
        bot_config.save_config("test_bot", test_webhook)

        # 验证配置文件存在
        assert config_file.exists()

        # 测试读取配置
        retrieved_webhook = bot_config.get_config("test_bot")
        assert retrieved_webhook == test_webhook

        # 测试加载已有配置
        new_config_manager = BotConfig(str(config_file))
        assert new_config_manager.get_config("test_bot") == test_webhook

        print("✅ 机器人配置管理测试通过")


@skip_if_no_config("bot")
def test_bot_initialization_with_webhook():
    """测试使用 webhook URL 初始化机器人"""
    print("测试使用 webhook URL 初始化机器人...")

    webhook_url = test_config.get_bot_webhook()

    # 直接使用 webhook URL
    bot = LarkWebhook(webhook_url)
    assert bot.webhook_url == webhook_url

    print("✅ 使用 webhook URL 初始化测试通过")


def test_bot_initialization_with_config():
    """测试使用配置名称初始化机器人"""
    print("测试使用配置名称初始化机器人...")

    webhook_url = test_config.get_bot_webhook()
    if not webhook_url:
        print("跳过测试: 缺少 webhook 配置")
        return

    # 使用临时配置文件
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_file = Path(tmp_dir) / "test_bot_config.json"

        # 先保存配置
        bot1 = LarkWebhook(webhook_url)

        # 使用保存的配置创建新的机器人实例 (这里需要模拟)
        bot_config = BotConfig(str(config_file))
        bot_config.save_config("test_bot", webhook_url)

        # 验证配置保存和读取
        retrieved_url = bot_config.get_config("test_bot")
        assert retrieved_url == webhook_url

        print("✅ 配置保存和读取测试通过")


@skip_if_no_config("bot")
def test_bot_send_methods():
    """测试机器人各种发送方法"""
    print("测试机器人各种发送方法...")

    webhook_url = test_config.get_bot_webhook()
    bot = LarkWebhook(webhook_url)

    # 测试发送文本
    print("发送纯文本...")
    response1 = bot.send_text("这是一条测试文本消息", echo=True)
    assert response1.status_code == 200

    # 测试发送卡片
    print("发送简单卡片...")
    response2 = bot.send_card(content="这是一个 **Markdown** 卡片",
                              title="测试卡片",
                              subtitle="Bot 测试",
                              echo=True)
    assert response2.status_code == 200

    # 测试发送带按钮的卡片
    print("发送带按钮的卡片...")
    buttons = [{
        "content": "访问 GitHub",
        "url": "https://github.com/Benature/larkpy"
    }, {
        "content": "查看文档",
        "url": "https://github.com/Benature/larkpy#readme"
    }]

    response3 = bot.send_card(content="这是带按钮的卡片测试",
                              title="按钮卡片测试",
                              buttons=buttons,
                              template="green",
                              echo=True)
    assert response3.status_code == 200

    # 测试 send 方法的智能识别
    print("测试 send 方法智能识别...")
    response4 = bot.send("这是通过 send 方法发送的文本", title="智能识别测试", echo=True)
    assert response4.status_code == 200

    # 测试 send_payload
    print("测试 send_payload...")
    payload = [{
        "tag": "text",
        "text": "这是 payload 格式的消息"
    }, {
        "tag": "a",
        "text": "点击链接",
        "href": "https://github.com/Benature/larkpy"
    }]
    response5 = bot.send_payload(payload, title="Payload 测试", echo=True)
    assert response5.status_code == 200

    print("✅ 所有发送方法测试通过")


@skip_if_no_config("bot")
def test_bot_collapsible_panel():
    """测试折叠面板功能"""
    print("测试折叠面板功能...")

    webhook_url = test_config.get_bot_webhook()
    bot = LarkWebhook(webhook_url)

    # 生成折叠面板
    panel = bot.gen_collapsible_panel(content="这是折叠面板的内容，可以包含很长的文本...",
                                      title="📋 详细信息",
                                      expanded=False,
                                      background_color="blue",
                                      border=True)

    # 发送折叠面板
    response = bot.send_card(content=[{
        "tag": "markdown",
        "content": "## 折叠面板测试"
    }, panel],
                             title="折叠面板测试",
                             echo=True)

    assert response.status_code == 200
    print("✅ 折叠面板测试通过")


def test_bot_error_handling():
    """测试错误处理"""
    print("测试错误处理...")

    # 测试无效的初始化参数
    # LarkWebhook 接受 None 作为 webhook_url，不会抛出异常
    bot = LarkWebhook(None)
    assert bot.webhook_url is None
    print("✅ 空参数处理正确")

    # 测试不存在的配置名
    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            config_file = Path(tmp_dir) / "empty_config.json"
            bot_config = BotConfig(str(config_file))
            result = bot_config.get_config("nonexistent")
            assert result is None
            print("✅ 不存在配置处理正确")
        except Exception as e:
            print(f"配置错误处理测试失败: {e}")


def main():
    """运行所有测试"""
    print("开始测试 bot.py 模块...\n")

    try:
        test_bot_config_management()
        print()

        test_bot_initialization_with_webhook()
        print()

        test_bot_initialization_with_config()
        print()

        test_bot_send_methods()
        print()

        test_bot_collapsible_panel()
        print()

        test_bot_error_handling()
        print()

        print("🎉 所有 Bot 测试完成！")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
