"""LarkOAuth - 飞书 OAuth 2.0 用户授权模块

本模块提供飞书 OAuth 2.0 用户授权流程的完整实现，包括：
- 生成用户授权 URL
- 使用授权码获取用户访问令牌
- 刷新用户访问令牌

使用用户授权可以让应用以用户身份执行操作，创建的资源（如文档）将归属于用户。

AI-generated: 本模块基于飞书官方 OAuth 2.0 文档，由 AI 辅助生成
"""

from __future__ import annotations
import json
import os
import time
from pathlib import Path
import requests
from urllib.parse import urlencode
from typing import Optional, Dict, Any


class LarkOAuth:
    """飞书 OAuth 2.0 用户授权类
    
    提供完整的 OAuth 2.0 用户授权流程支持，包括生成授权 URL、
    获取和刷新用户访问令牌等功能。
    
    Args:
        app_id (str): 飞书应用的 App ID
        app_secret (str): 飞书应用的 App Secret
        redirect_uri (str, optional): 授权回调地址. Defaults to "http://localhost:8080/callback".
        
    Attributes:
        app_id (str): 应用 ID
        app_secret (str): 应用密钥
        redirect_uri (str): 回调地址
        
    Examples:
        >>> oauth = LarkOAuth(app_id="cli_xxx", app_secret="xxx")
        >>> auth_url = oauth.get_auth_url(scope="drive:drive")
        >>> print(f"请访问: {auth_url}")
        >>> # 用户授权后获取 code
        >>> token_info = oauth.get_user_access_token(code="xxx")
        >>> user_token = token_info['data']['access_token']
        
    References:
        - OAuth 文档: https://open.feishu.cn/document/common-capabilities/sso/api/get-user-info
        - 获取 token: https://open.feishu.cn/document/common-capabilities/sso/api/obtain-user-access-token
        
    AI-generated: 本类由 AI 辅助生成，基于飞书官方 OAuth 2.0 API 文档
    """
    
    def __init__(self, 
                 app_id: str, 
                 app_secret: str,
                 redirect_uri: str = "http://localhost:8080/callback") -> None:
        """初始化 LarkOAuth 实例
        
        Args:
            app_id (str): 飞书应用的 App ID
            app_secret (str): 飞书应用的 App Secret
            redirect_uri (str, optional): 授权回调地址. Defaults to "http://localhost:8080/callback".
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
    
    def get_auth_url(self, 
                     scope: str = "drive:drive",
                     state: Optional[str] = None) -> str:
        """生成用户授权 URL
        
        生成用户需要访问的授权 URL，用户访问该 URL 并授权后，
        会跳转到 redirect_uri 并携带授权码 code。
        
        Args:
            scope (str, optional): 权限范围，多个权限用空格分隔. Defaults to "drive:drive".
                常用权限范围：
                - "drive:drive": 云空间权限，包含文档创建、编辑等
                - "contact:user.base:readonly": 获取用户基本信息
                - "im:message": 发送消息
            state (str, optional): 状态码，用于防止 CSRF 攻击. Defaults to None.
            
        Returns:
            str: 用户授权 URL
            
        Examples:
            >>> oauth = LarkOAuth(app_id="cli_xxx", app_secret="xxx")
            >>> url = oauth.get_auth_url(scope="drive:drive")
            >>> print(url)
            
        References:
            https://open.feishu.cn/document/common-capabilities/sso/api/get-user-info
            
        AI-generated: 由 AI 辅助生成
        """
        params = {
            "app_id": self.app_id,
            "redirect_uri": self.redirect_uri,
            "scope": scope,
        }
        if state:
            params["state"] = state
            
        base_url = "https://open.feishu.cn/open-apis/authen/v1/index"
        return f"{base_url}?{urlencode(params)}"
    
    def get_user_access_token(self, code: str) -> Dict[str, Any]:
        """使用授权码获取用户访问令牌
        
        用户授权后会获得一个授权码 code，使用该 code 可以换取用户的访问令牌。
        访问令牌包含 access_token、refresh_token、expires_in 等信息。
        
        Args:
            code (str): 用户授权后获得的授权码
            
        Returns:
            Dict[str, Any]: 包含访问令牌信息的字典，格式如下：
                {
                    "code": 0,
                    "msg": "success",
                    "data": {
                        "access_token": "u-xxx",
                        "token_type": "Bearer",
                        "expires_in": 7200,
                        "refresh_token": "ur-xxx",
                        "refresh_expires_in": 2592000,
                        "scope": "drive:drive"
                    }
                }
                
        Examples:
            >>> oauth = LarkOAuth(app_id="cli_xxx", app_secret="xxx")
            >>> result = oauth.get_user_access_token(code="4HSuK00...")
            >>> if result['code'] == 0:
            ...     token = result['data']['access_token']
            ...     print(f"访问令牌: {token}")
            
        References:
            https://open.feishu.cn/document/common-capabilities/sso/api/obtain-user-access-token
            
        AI-generated: 由 AI 辅助生成，修正了之前 Basic Auth 的错误实现
        """
        url = "https://open.feishu.cn/open-apis/authen/v1/access_token"
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "app_id": self.app_id,
            "app_secret": self.app_secret,
        }
        
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    
    def refresh_user_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """刷新用户访问令牌
        
        用户访问令牌有效期为 2 小时，过期后可以使用 refresh_token 刷新。
        refresh_token 有效期为 30 天。
        
        Args:
            refresh_token (str): 刷新令牌
            
        Returns:
            Dict[str, Any]: 包含新访问令牌信息的字典，格式同 get_user_access_token
            
        Examples:
            >>> oauth = LarkOAuth(app_id="cli_xxx", app_secret="xxx")
            >>> result = oauth.refresh_user_access_token(refresh_token="ur-xxx")
            >>> if result['code'] == 0:
            ...     new_token = result['data']['access_token']
            
        References:
            https://open.feishu.cn/document/common-capabilities/sso/api/refresh-user-access-token
            
        AI-generated: 由 AI 辅助生成
        """
        url = "https://open.feishu.cn/open-apis/authen/v1/refresh_access_token"
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "app_id": self.app_id,
            "app_secret": self.app_secret,
        }
        
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    
    def get_user_info(self, user_access_token: str) -> Dict[str, Any]:
        """获取用户信息
        
        使用 user_access_token 获取登录用户的身份信息（open_id, union_id, name 等）。
        
        Args:
            user_access_token (str): 用户访问令牌
            
        Returns:
            Dict[str, Any]: 用户信息
            
        References:
            https://open.feishu.cn/document/common-capabilities/sso/api/get-user-info
        """
        url = "https://open.feishu.cn/open-apis/authen/v1/user_info"
        headers = {
            "Authorization": f"Bearer {user_access_token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        response = requests.get(url, headers=headers)
        return response.json()
    
    def save_token_to_file(self, token_data: Dict[str, Any], file_path: str) -> None:
        """保存 token 到文件
        
        将 token 数据保存到 JSON 文件，并添加创建时间戳用于过期检测。
        
        Args:
            token_data (Dict[str, Any]): token 数据，应包含 access_token、refresh_token 等
            file_path (str): 保存路径
            
        Examples:
            >>> oauth = LarkOAuth(app_id="cli_xxx", app_secret="xxx")
            >>> token_data = oauth.get_user_access_token(code="xxx")
            >>> oauth.save_token_to_file(token_data['data'], "data/user_token.json")
            
        AI-generated: 由 AI 辅助生成 (Google Gemini 2.0 Flash Thinking Experimental)
        """
        # 确保目录存在
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 添加创建时间戳
        token_with_timestamp = token_data.copy()
        token_with_timestamp['created_at'] = time.time()
        
        # 保存到文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(token_with_timestamp, f, indent=2, ensure_ascii=False)
    
    def load_token_from_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """从文件加载 token
        
        从 JSON 文件读取 token 数据。
        
        Args:
            file_path (str): token 文件路径
            
        Returns:
            Optional[Dict[str, Any]]: token 数据，如果文件不存在返回 None
            
        Examples:
            >>> oauth = LarkOAuth(app_id="cli_xxx", app_secret="xxx")
            >>> token_data = oauth.load_token_from_file("data/user_token.json")
            >>> if token_data:
            ...     print(f"Token: {token_data['access_token']}")
            
        AI-generated: 由 AI 辅助生成 (Google Gemini 2.0 Flash Thinking Experimental)
        """
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def is_token_expired(self, token_data: Dict[str, Any], buffer_seconds: int = 300) -> bool:
        """检查 token 是否过期
        
        基于 created_at 和 expires_in 判断 token 是否过期。
        为了避免边界情况，会提前 buffer_seconds 秒判定为过期。
        
        Args:
            token_data (Dict[str, Any]): token 数据，需包含 created_at 和 expires_in
            buffer_seconds (int, optional): 缓冲时间（秒），提前判定过期. Defaults to 300.
            
        Returns:
            bool: True 表示已过期，False 表示未过期
            
        Examples:
            >>> oauth = LarkOAuth(app_id="cli_xxx", app_secret="xxx")
            >>> token_data = oauth.load_token_from_file("data/user_token.json")
            >>> if oauth.is_token_expired(token_data):
            ...     print("Token 已过期，需要刷新")
            
        AI-generated: 由 AI 辅助生成 (Google Gemini 2.0 Flash Thinking Experimental)
        """
        # 检查必要字段
        if 'created_at' not in token_data or 'expires_in' not in token_data:
            return True  # 缺少必要字段，视为过期
        
        created_at = token_data['created_at']
        expires_in = token_data['expires_in']
        
        # 计算过期时间
        current_time = time.time()
        time_elapsed = current_time - created_at
        
        # 提前 buffer_seconds 判定为过期
        return time_elapsed >= (expires_in - buffer_seconds)
    
    def ensure_valid_token(self, 
                          token_file: str,
                          scope: str = "task:task,drive:drive") -> str:
        """确保获取有效的 token（自动刷新或引导重新授权）
        
        这是一个便捷方法，会自动处理以下情况：
        1. 从文件加载 token
        2. 检查是否过期
        3. 如果过期且有 refresh_token，自动刷新
        4. 如果刷新失败或无 refresh_token，引导用户重新授权
        5. 保存新 token 到文件
        
        Args:
            token_file (str): token 文件路径
            scope (str, optional): OAuth 权限范围. Defaults to "task:task,drive:drive".
            
        Returns:
            str: 有效的 access_token
            
        Raises:
            Exception: 当无法获取有效 token 时（用户取消授权等）
            
        Examples:
            >>> oauth = LarkOAuth(
            ...     app_id="cli_xxx",
            ...     app_secret="xxx",
            ...     redirect_uri="http://localhost:8080/callback"
            ... )
            >>> access_token = oauth.ensure_valid_token("data/user_token.json")
            >>> print(f"有效的 token: {access_token}")
            
        AI-generated: 由 AI 辅助生成 (Google Gemini 2.0 Flash Thinking Experimental)
        """
        # 1. 尝试从文件加载 token
        token_data = self.load_token_from_file(token_file)
        
        # 2. 如果文件存在且 token 未过期，直接返回
        if token_data and not self.is_token_expired(token_data):
            return token_data['access_token']
        
        # 3. Token 过期或不存在，尝试刷新
        if token_data and 'refresh_token' in token_data:
            print("🔄 Token 已过期，正在自动刷新...")
            refresh_result = self.refresh_user_access_token(token_data['refresh_token'])
            
            if refresh_result.get('code') == 0:
                # 刷新成功
                new_token_data = refresh_result['data']
                self.save_token_to_file(new_token_data, token_file)
                print("✅ Token 刷新成功")
                return new_token_data['access_token']
            else:
                print(f"⚠️  Token 刷新失败: {refresh_result.get('msg')}")
                print("需要重新授权...")
        
        # 4. 需要重新授权
        print("\n" + "=" * 80)
        print("🔐 需要进行用户授权")
        print("=" * 80)
        
        # 生成授权 URL
        auth_url = self.get_auth_url(scope=scope)
        
        print("\n请在浏览器中打开以下 URL 进行授权:")
        print("-" * 80)
        print(auth_url)
        print("-" * 80)
        print("\n授权后，浏览器会跳转到回调地址（可能无法访问）")
        print("请复制地址栏中的完整 URL（包含 code 参数）\n")
        
        # 获取授权码
        callback_url = input("请粘贴回调 URL: ").strip()
        
        import re
        code_match = re.search(r'code=([^&]+)', callback_url)
        if not code_match:
            raise Exception("未找到授权码，请确保复制了完整的 URL")
        
        code = code_match.group(1)
        print("✅ 获取到授权码")
        
        # 获取访问令牌
        print("\n🔑 正在获取访问令牌...")
        token_result = self.get_user_access_token(code)
        
        if token_result.get('code') != 0:
            raise Exception(f"获取 token 失败: {token_result.get('msg')}")
        
        # 保存 token
        new_token_data = token_result['data']
        self.save_token_to_file(new_token_data, token_file)
        
        print(f"✅ Token 已保存到: {token_file}")
        print(f"   有效期: {new_token_data['expires_in']} 秒")
        
        return new_token_data['access_token']

