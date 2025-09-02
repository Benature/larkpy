#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试机器人配置管理功能"""
import sys
from pathlib import Path
import pytest
import tempfile
import json

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestBotConfig:
    """测试 BotConfig 类"""
    
    def test_config_creation(self):
        """测试配置文件创建"""
        from larkpy import BotConfig
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "test_config.json"
            config = BotConfig(str(config_file))
            assert config.config_file == config_file
    
    def test_save_and_load_config(self):
        """测试配置保存和加载"""
        from larkpy import BotConfig
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "test_config.json"
            config = BotConfig(str(config_file))
            test_webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/test123"
            
            # 测试保存
            config.save_config("test_bot", test_webhook)
            assert config_file.exists()
            
            # 测试加载
            retrieved = config.get_config("test_bot")
            assert retrieved == test_webhook
    
    def test_config_file_content(self):
        """测试配置文件内容格式"""
        from larkpy import BotConfig
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "test_config.json"
            config = BotConfig(str(config_file))
            
            test_webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/test456"
            config.save_config("test_bot", test_webhook)
            
            # 读取并验证文件内容
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert "test_bot" in data
            assert data["test_bot"] == test_webhook
    
    def test_multiple_configs(self):
        """测试多个配置存储"""
        from larkpy import BotConfig
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "test_config.json"
            config = BotConfig(str(config_file))
            
            # 保存多个配置
            configs = {
                "bot1": "https://open.feishu.cn/open-apis/bot/v2/hook/test1",
                "bot2": "https://open.feishu.cn/open-apis/bot/v2/hook/test2",
                "bot3": "https://open.feishu.cn/open-apis/bot/v2/hook/test3"
            }
            
            for name, webhook in configs.items():
                config.save_config(name, webhook)
            
            # 验证所有配置都能正确加载
            for name, webhook in configs.items():
                retrieved = config.get_config(name)
                assert retrieved == webhook
    
    def test_nonexistent_config(self):
        """测试获取不存在的配置"""
        from larkpy import BotConfig
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "test_config.json"
            config = BotConfig(str(config_file))
            
            # 获取不存在的配置应返回 None
            result = config.get_config("nonexistent_bot")
            assert result is None