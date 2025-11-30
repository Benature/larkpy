#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAuth 2.0 用户授权示例

本示例展示如何使用 larkpy 的 OAuth 功能进行用户授权，
并以用户身份创建和编辑飞书文档。

使用用户授权的好处：
- 创建的资源（如文档）归属于用户，而非应用
- 用户可以直接访问和管理这些资源
- 适用于需要用户身份的场景

AI-generated: 本示例由 AI 辅助生成
"""

from larkpy import LarkOAuth, LarkAPI, LarkDocx
from datetime import datetime
import re


def main():
    """主函数：演示完整的 OAuth 授权流程"""
    
    # ========== 配置信息 ==========
    # 从飞书开放平台获取: https://open.feishu.cn/app
    APP_ID = "your_app_id"  # 替换为你的应用 ID
    APP_SECRET = "your_app_secret"  # 替换为你的应用密钥
    
    # ========== 步骤1: 创建 OAuth 实例 ==========
    print("🔐 步骤1: 初始化 OAuth")
    oauth = LarkOAuth(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        redirect_uri="http://localhost:8080/callback"  # 需在应用后台配置
    )
    
    # ========== 步骤2: 生成授权 URL ==========
    print("\n📋 步骤2: 生成用户授权 URL")
    # scope 参数指定需要的权限范围
    auth_url = oauth.get_auth_url(scope="drive:drive")
    
    print("请在浏览器中打开以下 URL 进行授权:")
    print("=" * 80)
    print(auth_url)
    print("=" * 80)
    print("\n授权后，浏览器会跳转到回调地址（可能无法访问）")
    print("请复制地址栏中的完整 URL（包含 code 参数）")
    
    # ========== 步骤3: 获取授权码 ==========
    callback_url = input("\n请粘贴回调 URL: ").strip()
    
    # 从 URL 中提取 code
    code_match = re.search(r'code=([^&]+)', callback_url)
    if not code_match:
        print("❌ 未找到授权码，请确保复制了完整的 URL")
        return
    
    code = code_match.group(1)
    print(f"✅ 获取到授权码")
    
    # ========== 步骤4: 获取用户访问令牌 ==========
    print("\n🔑 步骤4: 获取用户访问令牌")
    token_result = oauth.get_user_access_token(code)
    
    if token_result.get('code') != 0:
        print(f"❌ 获取 token 失败: {token_result.get('msg')}")
        return
    
    user_access_token = token_result['data']['access_token']
    refresh_token = token_result['data']['refresh_token']
    expires_in = token_result['data']['expires_in']
    
    print(f"✅ 成功获取用户访问令牌")
    print(f"   - 有效期: {expires_in} 秒 ({expires_in // 3600} 小时)")
    print(f"   - Refresh Token 有效期: 30 天")
    
    # ========== 步骤5: 使用用户身份创建文档 ==========
    print("\n📝 步骤5: 以用户身份创建文档")
    
    # 使用用户访问令牌初始化文档操作类
    docx = LarkDocx(user_access_token=user_access_token)
    
    # 创建文档
    title = f"用户授权测试文档 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    result = docx.create_document(title=title)
    
    if result.get('code') != 0:
        print(f"❌ 创建文档失败: {result.get('msg')}")
        return
    
    document_id = result['data']['document']['document_id']
    print(f"✅ 文档创建成功！")
    print(f"   - 文档 ID: {document_id}")
    print(f"   - 文档链接: https://bytedance.larkoffice.com/docx/{document_id}")
    
    # ========== 步骤6: 向文档添加内容 ==========
    print("\n✍️  步骤6: 向文档添加内容")
    
    # 添加标题文本
    heading_block = {
        "block_type": 3,  # Heading 1
        "heading1": {
            "elements": [{
                "text_run": {
                    "content": "通过 OAuth 用户授权创建"
                }
            }],
            "style": {}
        }
    }
    
    # 添加正文文本
    text_block = {
        "block_type": 2,  # Text
        "text": {
            "elements": [{
                "text_run": {
                    "content": f"这个文档是通过 OAuth 2.0 用户授权流程创建的，因此文档的所有者是你本人，而不是应用。\n\n创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            }],
            "style": {}
        }
    }
    
    # 批量添加块
    blocks_result = docx.create_block(
        block_children=[heading_block, text_block],
        index=-1
    )
    
    if blocks_result.get('code') == 0:
        print("✅ 内容添加成功")
    else:
        print(f"⚠️  添加内容失败: {blocks_result.get('msg')}")
    
    # ========== 完成 ==========
    print("\n🎉 示例完成！")
    print(f"📄 文档链接: https://bytedance.larkoffice.com/docx/{document_id}")
    print("\n💡 提示:")
    print("   1. 这个文档归属于你的账号，可以直接访问和编辑")
    print("   2. 访问令牌有效期为 2 小时")
    print("   3. 可以使用 refresh_token 刷新访问令牌")
    print(f"   4. Refresh Token: {refresh_token[:20]}...")
    
    # ========== 可选: 演示刷新令牌 ==========
    print("\n🔄 演示 Refresh Token（可选）")
    demo_refresh = input("是否演示刷新访问令牌？(y/n): ").strip().lower()
    
    if demo_refresh == 'y':
        print("正在刷新访问令牌...")
        refresh_result = oauth.refresh_user_access_token(refresh_token)
        
        if refresh_result.get('code') == 0:
            new_token = refresh_result['data']['access_token']
            print(f"✅ 访问令牌刷新成功")
            print(f"   - 新 Token 前缀: {new_token[:20]}...")
        else:
            print(f"❌ 刷新失败: {refresh_result.get('msg')}")


if __name__ == "__main__":
    main()
