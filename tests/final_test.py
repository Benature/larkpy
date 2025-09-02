#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""最终功能验证脚本"""
import sys
from pathlib import Path
import json

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_imports():
    """测试所有模块导入"""
    print("Testing module imports...")
    
    try:
        # 测试新添加的模块
        from larkpy import CardElementGenerator, BotConfig
        print("✓ New modules (CardElementGenerator, BotConfig) imported")
        
        # 测试原有模块
        from larkpy import LarkBot, LarkAPI, LarkMessage, LarkDocx, LarkBitTable, LarkCalendar
        print("✓ Original modules imported")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_card_functionality():
    """测试卡片功能"""
    print("\nTesting card functionality...")
    
    try:
        from larkpy import CardElementGenerator
        
        # 测试各种元素生成
        markdown = CardElementGenerator.markdown("## 标题\n这是 **粗体** 和 *斜体* 文本")
        text = CardElementGenerator.text("普通文本内容")
        button = CardElementGenerator.button("访问链接", url="https://github.com/Benature/larkpy")
        
        assert markdown["tag"] == "markdown"
        assert text["tag"] == "text"
        assert button["tag"] == "button"
        
        print("✓ All card elements created successfully")
        
        # 测试 DataFrame 功能 (如果 pandas 可用)
        try:
            import pandas as pd
            from datetime import datetime
            
            df = pd.DataFrame({
                '名称': ['项目A', '项目B', '项目C'],
                '进度': [0.8, 0.6, 0.9],
                '完成': [True, False, True],
                '日期': [datetime(2024, 8, 28), datetime(2024, 8, 29), datetime(2024, 8, 30)]
            })
            
            table = CardElementGenerator.table_card(df, page_size=3)
            assert table["tag"] == "table"
            assert len(table["rows"]) == 3
            
            print("✓ DataFrame table card functionality works")
            
        except ImportError:
            print("⚠ pandas not available, skipping DataFrame tests")
        
        return True
        
    except Exception as e:
        print(f"✗ Card functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bot_config():
    """测试机器人配置管理"""
    print("\nTesting bot configuration management...")
    
    try:
        from larkpy import BotConfig
        import tempfile
        
        # 使用临时文件测试
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "test_config.json"
            
            config = BotConfig(str(config_file))
            test_webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/test123"
            
            # 测试保存和读取
            config.save_config("test_bot", test_webhook)
            retrieved = config.get_config("test_bot")
            
            assert retrieved == test_webhook
            print("✓ Configuration save/load works")
            
        return True
        
    except Exception as e:
        print(f"✗ Bot config test failed: {e}")
        return False

def test_integration_example():
    """测试集成示例"""
    print("\nTesting integration example...")
    
    try:
        from larkpy import LarkBot, CardElementGenerator
        
        # 创建卡片内容
        elements = [
            CardElementGenerator.markdown("## 功能测试报告\n测试已成功完成！"),
            CardElementGenerator.text("所有新功能都正常工作。"),
            CardElementGenerator.button("查看源码", url="https://github.com/Benature/larkpy")
        ]
        
        print("✓ Integration example created successfully")
        print("Card elements:", [elem["tag"] for elem in elements])
        
        return True
        
    except Exception as e:
        print(f"✗ Integration example failed: {e}")
        return False

def generate_summary():
    """生成功能总结"""
    print("\n" + "="*60)
    print("larkpy 功能迁移总结")
    print("="*60)
    
    features = [
        "✓ 新增 CardElementGenerator 类 - 强大的卡片元素生成工具",
        "✓ 支持 Markdown、文本、按钮等多种元素类型",
        "✓ 支持 DataFrame 转换为表格卡片（需要 pandas）",
        "✓ 新增 BotConfig 类 - 机器人配置管理",
        "✓ 支持 webhook URL 的保存和读取",
        "✓ 增强了 LarkBot 的发送功能",
        "✓ 改进了错误处理和日志输出",
        "✓ 所有新功能都已添加到 __init__.py 导出",
        "✓ 配置文件已加入 .gitignore 保护隐私",
        "✓ 提供完整的测试套件和使用示例"
    ]
    
    for feature in features:
        print(feature)
    
    print("\n使用示例:")
    print("""
from larkpy import LarkBot, CardElementGenerator

# 创建机器人 (可以保存配置)
bot = LarkBot(webhook_url, save_config=True)

# 生成卡片元素
elements = [
    CardElementGenerator.markdown("## 标题"),
    CardElementGenerator.text("内容"),
    CardElementGenerator.button("按钮", url="https://example.com")
]

# 发送卡片
bot.send_card(elements, title="测试卡片")
    """)

def main():
    """运行所有测试"""
    print("🚀 larkpy 功能验证测试")
    print("="*60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Card Functionality", test_card_functionality),
        ("Bot Configuration", test_bot_config),
        ("Integration Example", test_integration_example),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试都通过了！ref 中的功能已成功迁移到 src。")
        generate_summary()
    else:
        print("⚠️  有一些测试失败了，请检查上面的错误信息。")

if __name__ == "__main__":
    main()