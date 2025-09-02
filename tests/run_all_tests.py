"""运行所有测试"""
import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from test_utils import TestConfig

def main():
    """运行所有测试"""
    print("🚀 开始运行 larkpy 功能测试\n")
    
    # 检查配置
    test_config = TestConfig()
    print("配置检查:")
    print(f"  - 机器人配置: {'✅ 已配置' if test_config.has_bot_config() else '❌ 未配置'}")
    print(f"  - 消息配置: {'✅ 已配置' if test_config.has_message_config() else '❌ 未配置'}")
    print()
    
    if not test_config.has_bot_config() and not test_config.has_message_config():
        print("⚠️  警告: 没有找到任何测试配置")
        print("请复制 test_config.json.template 为 test_config.json 并填入正确的配置")
        print()
    
    # 运行测试
    test_modules = [
        ("card", "test_card.py"),
        ("bot", "test_bot.py"),
    ]
    
    failed_tests = []
    
    for module_name, test_file in test_modules:
        print(f"📋 运行 {module_name} 模块测试...")
        print("-" * 50)
        
        try:
            # 动态导入并运行测试
            module_path = Path(__file__).parent / test_file
            if module_path.exists():
                # 执行测试文件
                exec_globals = {"__name__": "__main__"}
                with open(module_path, 'r', encoding='utf-8') as f:
                    exec(f.read(), exec_globals)
            else:
                print(f"❌ 测试文件不存在: {test_file}")
                failed_tests.append(module_name)
                
        except Exception as e:
            print(f"❌ {module_name} 测试失败: {e}")
            failed_tests.append(module_name)
        
        print("-" * 50)
        print()
    
    # 总结
    print("📊 测试总结:")
    if not failed_tests:
        print("🎉 所有测试都通过了！")
    else:
        print(f"❌ 以下测试失败: {', '.join(failed_tests)}")
    
    print("\n测试完成！")


if __name__ == "__main__":
    main()