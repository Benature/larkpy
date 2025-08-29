# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

larkpy 是一个飞书开放平台的 Python SDK，提供了飞书机器人、API 调用、文档操作、多维表格、即时通讯和日历等功能的接口封装。

## 常用命令

### 开发环境准备
```bash
make prepare        # 安装依赖
```

### 构建和发布
```bash
make clean          # 清理构建文件
make build          # 构建包 (python setup.py sdist bdist_wheel)
make install        # 本地安装包
make uninstall      # 卸载包
make all            # 完整重新构建和安装流程
make upload         # 上传到 PyPI (使用 twine)
```

### 包管理
- 项目使用传统的 setup.py 进行包管理
- 依赖包通过 setup.py 中的 install_requires 定义：requests, bs4, lxml, pandas, requests_toolbelt
- 版本号在 larkpy/__init__.py 中的 __version__ 变量中定义

## 代码架构

### 核心模块结构
```
larkpy/
├── __init__.py        # 主要类的导出
├── bot.py            # LarkBot - 飞书机器人 webhook 消息发送
├── api.py            # LarkAPI - 飞书开放平台 API 调用基础类
├── im.py             # LarkMessage - 即时通讯相关功能
├── docx.py           # LarkDocx - 文档操作
├── bitTable.py       # LarkBitTable - 多维表格操作
├── calendar.py       # LarkCalendar - 日历相关功能
├── _typing.py        # 类型定义
└── log.py            # 日志工具
```

### 主要类和功能
1. **LarkBot** (`bot.py`): 通过 webhook 发送飞书消息，支持文本、富文本、卡片等格式
2. **LarkAPI** (`api.py`): 飞书开放平台 API 调用的基础类，处理认证和请求
3. **LarkMessage** (`im.py`): 即时通讯消息发送和管理
4. **LarkDocx** (`docx.py`): 飞书文档的读取和操作
5. **LarkBitTable** (`bitTable.py`): 多维表格的数据操作
6. **LarkCalendar** (`calendar.py`): 日历事件的管理

### 认证机制
- API 类使用 app_id 和 app_secret 获取 tenant_access_token 进行认证
- Bot 类使用 webhook_url 进行消息发送，无需额外认证

## 开发注意事项

- 所有模块都支持 Python 3.7+
- 使用 typing_extensions 提供更好的类型支持
- 请求处理统一通过 requests 库
- 项目没有配置测试框架，修改代码时需要手动测试
- examples/ 目录提供了使用示例