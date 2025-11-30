"""LarkOAuth - 飞书 OAuth 2.0 用户授权模块

本模块提供飞书 OAuth 2.0 用户授权流程的完整实现，包括：
- 生成用户授权 URL
- 使用授权码获取用户访问令牌
- 刷新用户访问令牌

使用用户授权可以让应用以用户身份执行操作，创建的资源（如文档）将归属于用户。

AI-generated: 本模块基于飞书官方 OAuth 2.0 文档，由 AI 辅助生成
"""

from __future__ import annotations
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
