"""测试工具模块"""
import json
import os
from pathlib import Path


class TestConfig:
    """测试配置管理器"""
    
    def __init__(self):
        self.config_file = Path(__file__).parent / "test_config.json"
        self.template_file = Path(__file__).parent / "test_config.json.template"
        self.config = self._load_config()
    
    def _load_config(self):
        """加载测试配置"""
        if not self.config_file.exists():
            print(f"测试配置文件不存在: {self.config_file}")
            print(f"请复制 {self.template_file} 为 {self.config_file} 并填入正确的配置")
            return {}
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}
    
    def get_bot_webhook(self, name="test_webhook"):
        """获取机器人 webhook"""
        return self.config.get("bot", {}).get(name)
    
    def get_message_config(self, name="test_app"):
        """获取消息应用配置"""
        return self.config.get("message", {}).get(name, {})
    
    def has_bot_config(self):
        """检查是否有机器人配置"""
        return bool(self.get_bot_webhook())
    
    def has_message_config(self):
        """检查是否有消息配置"""
        config = self.get_message_config()
        return bool(config.get("app_id") and config.get("app_secret"))


def skip_if_no_config(config_type="bot"):
    """装饰器：如果没有配置则跳过测试"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            test_config = TestConfig()
            
            if config_type == "bot" and not test_config.has_bot_config():
                print(f"跳过测试 {func.__name__}: 缺少机器人配置")
                return
            elif config_type == "message" and not test_config.has_message_config():
                print(f"跳过测试 {func.__name__}: 缺少消息配置")
                return
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# 全局测试配置实例
test_config = TestConfig()