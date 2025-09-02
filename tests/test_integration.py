#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""集成测试"""
import sys
from pathlib import Path
import pytest

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestIntegration:
    """集成测试类"""

    def test_bot_with_card_elements(self):
        """测试机器人与卡片元素集成"""
        from larkpy import LarkWebhook, CardElementGenerator

        # 创建卡片内容
        elements = [
            CardElementGenerator.markdown("## 功能测试报告\\n测试已成功完成！"),
            CardElementGenerator.text("所有新功能都正常工作。"),
            CardElementGenerator.button("查看源码", url="https://github.com/Benature/larkpy")
        ]

        # 验证元素类型
        assert elements[0]["tag"] == "markdown"
        assert elements[1]["tag"] == "text"
        assert elements[2]["tag"] == "button"

        # 验证可以创建机器人实例（不实际发送）
        test_webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/test"
        bot = LarkWebhook(test_webhook)
        assert bot.webhook_url == test_webhook

    def test_config_integration_with_bot(self):
        """测试配置管理与机器人集成"""
        from larkpy import LarkWebhook, BotConfig
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "integration_config.json"
            config = BotConfig(str(config_file))

            test_webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/integration_test"
            config.save_config("integration_bot", test_webhook)

            # 从配置创建机器人
            retrieved_webhook = config.get_config("integration_bot")
            bot = LarkWebhook(retrieved_webhook)

            assert bot.webhook_url == test_webhook

    def test_complex_card_creation(self):
        """测试复杂卡片创建"""
        from larkpy import CardElementGenerator

        # 创建包含多种元素的复杂卡片
        elements = [
            CardElementGenerator.markdown("## 项目状态报告"),
            CardElementGenerator.hr(),
            CardElementGenerator.text("项目进展顺利，所有功能模块已完成开发。"),
            CardElementGenerator.hr(),
            CardElementGenerator.markdown("### 功能清单"),
            CardElementGenerator.text("✓ 卡片元素生成器"),
            CardElementGenerator.text("✓ 机器人配置管理"),
            CardElementGenerator.text("✓ 增强的消息发送功能"),
            CardElementGenerator.hr(),
            CardElementGenerator.button("访问项目", url="https://github.com/Benature/larkpy"),
            CardElementGenerator.button("查看文档", url="https://docs.example.com")
        ]

        # 验证所有元素都创建成功
        expected_tags = [
            "markdown", "hr", "text", "hr", "markdown", "text", "text", "text", "hr", "button",
            "button"
        ]
        actual_tags = [elem["tag"] for elem in elements]

        assert actual_tags == expected_tags
        assert len(elements) == 11
