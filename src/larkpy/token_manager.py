#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用户授权令牌持久化助手

提供用户授权令牌的持久化存储和自动刷新功能。
将 user_access_token 和 refresh_token 保存到配置文件，避免每次都需要重新授权。

AI-generated: 本模块由 AI 辅助生成
"""

import yaml
import time
from pathlib import Path
from typing import Dict, Optional


class TokenManager:
    """用户授权令牌管理器
    
    管理用户授权令牌的持久化存储和自动刷新。
    
    Args:
        config_path (str): 配置文件路径
        oauth: LarkOAuth 实例，用于刷新令牌
        
    AI-generated: 本类由 AI 辅助生成
    """
    
    def __init__(self, config_path: str, oauth):
        """初始化令牌管理器"""
        self.config_path = Path(config_path)
        self.oauth = oauth
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """加载配置文件"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def _save_config(self):
        """保存配置文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
    
    def save_tokens(self, access_token: str, refresh_token: str, expires_in: int):
        """保存令牌到配置文件
        
        Args:
            access_token (str): 用户访问令牌
            refresh_token (str): 刷新令牌
            expires_in (int): 过期时间（秒）
        """
        if 'feishu' not in self.config:
            self.config['feishu'] = {}
        
        self.config['feishu']['user_access_token'] = access_token
        self.config['feishu']['refresh_token'] = refresh_token
        self.config['feishu']['token_expires_at'] = int(time.time()) + expires_in
        
        self._save_config()
        print(f"✅ 令牌已保存到配置文件")
    
    def get_valid_token(self) -> Optional[str]:
        """获取有效的用户访问令牌
        
        如果令牌过期，自动使用 refresh_token 刷新。
        
        Returns:
            Optional[str]: 有效的 user_access_token，如果无法获取则返回 None
        """
        feishu_config = self.config.get('feishu', {})
        access_token = feishu_config.get('user_access_token')
        refresh_token = feishu_config.get('refresh_token')
        expires_at = feishu_config.get('token_expires_at', 0)
        
        # 检查是否有保存的令牌
        if not access_token or not refresh_token:
            print("⚠️  未找到保存的令牌，需要重新授权")
            return None
        
        # 检查是否过期（提前 5 分钟刷新）
        if time.time() >= expires_at - 300:
            print("🔄 令牌即将过期，正在刷新...")
            new_token = self._refresh_token(refresh_token)
            if new_token:
                return new_token
            else:
                print("❌ 刷新令牌失败，需要重新授权")
                return None
        
        print("✅ 使用已保存的令牌")
        return access_token
    
    def _refresh_token(self, refresh_token: str) -> Optional[str]:
        """刷新访问令牌
        
        Args:
            refresh_token (str): 刷新令牌
            
        Returns:
            Optional[str]: 新的 access_token，失败返回 None
        """
        try:
            result = self.oauth.refresh_user_access_token(refresh_token)
            
            if result.get('code') == 0:
                data = result['data']
                self.save_tokens(
                    data['access_token'],
                    data['refresh_token'],
                    data['expires_in']
                )
                print("✅ 令牌刷新成功")
                return data['access_token']
            else:
                print(f"❌ 刷新失败: {result.get('msg')}")
                return None
        except Exception as e:
            print(f"❌ 刷新令牌时发生错误: {e}")
            return None
    
    def clear_tokens(self):
        """清除保存的令牌"""
        if 'feishu' in self.config:
            self.config['feishu'].pop('user_access_token', None)
            self.config['feishu'].pop('refresh_token', None)
            self.config['feishu'].pop('token_expires_at', None)
            self._save_config()
            print("✅ 令牌已清除")
