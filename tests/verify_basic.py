#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""基本功能验证脚本"""
import sys
import json
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_card_import():
    """测试 card 模块导入"""
    try:
        import importlib.util
        card_path = Path(__file__).parent.parent.absolute() / "src" / "larkpy" / "card.py"
        print(f"Looking for card.py at: {card_path}")
        print(f"File exists: {card_path.exists()}")
        
        spec = importlib.util.spec_from_file_location("card", card_path)
        card_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(card_module)
        
        print("Card module imported successfully")
        
        # 测试基本功能
        generator = card_module.CardElementGenerator()
        
        # 测试 markdown
        markdown = generator.markdown("Test **bold** text")
        assert markdown["tag"] == "markdown"
        print("Markdown element: OK")
        
        # 测试 text
        text = generator.text("Plain text")
        assert text["tag"] == "text"
        print("Text element: OK")
        
        # 测试 button
        button = generator.button("Click me", url="https://example.com")
        assert button["tag"] == "button"
        print("Button element: OK")
        
        print("Card module test: PASSED")
        return True
        
    except Exception as e:
        print(f"Card module test: FAILED - {e}")
        return False

def test_bot_import():
    """测试 bot 模块导入"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("bot", Path(__file__).parent.parent / "src" / "larkpy" / "bot.py")
        bot_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bot_module)
        
        print("Bot module imported successfully")
        
        # 测试配置管理
        config = bot_module.BotConfig()
        print("BotConfig created: OK")
        
        # 不测试实际的 LarkBot，因为需要 webhook
        print("Bot module test: PASSED")
        return True
        
    except Exception as e:
        print(f"Bot module test: FAILED - {e}")
        return False

def test_dataframe_functionality():
    """测试 DataFrame 功能"""
    try:
        import pandas as pd
        from datetime import datetime
        
        import importlib.util
        spec = importlib.util.spec_from_file_location("card", Path(__file__).parent.parent / "src" / "larkpy" / "card.py")
        card_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(card_module)
        
        # 创建测试数据
        df = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Age': [25, 30, 35],
            'Score': [85.5, 92.0, 78.5],
            'Pass': [True, True, False],
            'Date': [datetime(2024, 1, 1), datetime(2024, 1, 2), datetime(2024, 1, 3)]
        })
        
        # 测试列类型解析
        column_types = card_module.parse_column_type(df)
        print(f"Column types: {column_types}")
        
        # 测试表格卡片生成
        table_card = card_module.CardElementGenerator.table_card(df)
        assert table_card["tag"] == "table"
        print("Table card generation: OK")
        
        print("DataFrame functionality test: PASSED")
        return True
        
    except ImportError:
        print("DataFrame functionality test: SKIPPED (pandas not available)")
        return True
    except Exception as e:
        print(f"DataFrame functionality test: FAILED - {e}")
        return False

def main():
    """运行所有验证测试"""
    print("Starting basic functionality verification...")
    print("=" * 50)
    
    tests = [
        ("Card module", test_card_import),
        ("Bot module", test_bot_import),
        ("DataFrame functionality", test_dataframe_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All basic functionality tests passed!")
    else:
        print("Some tests failed. Please check the output above.")

if __name__ == "__main__":
    main()