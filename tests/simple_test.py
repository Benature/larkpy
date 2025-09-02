#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""简单的功能测试脚本"""
import sys
from pathlib import Path
import os

# 设置当前工作目录
os.chdir(Path(__file__).parent)

# 添加 src 目录到路径
sys.path.insert(0, str(Path.cwd().parent / "src"))

def main():
    print("Testing larkpy functionality...")
    print("Current directory:", Path.cwd())
    
    try:
        # 直接导入 larkpy 模块
        from larkpy.card import CardElementGenerator
        from larkpy.bot import LarkBot, BotConfig
        
        print("✓ Modules imported successfully")
        
        # 测试 CardElementGenerator
        generator = CardElementGenerator()
        
        markdown = generator.markdown("Test **bold** text")
        print("✓ Markdown element created:", markdown["tag"])
        
        text = generator.text("Plain text")
        print("✓ Text element created:", text["tag"])
        
        button = generator.button("Click me", url="https://example.com")
        print("✓ Button element created:", button["tag"])
        
        # 测试 BotConfig
        config = BotConfig()
        print("✓ BotConfig created")
        
        print("\n🎉 All basic tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()