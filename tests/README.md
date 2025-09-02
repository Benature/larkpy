# larkpy 测试说明

本目录包含 larkpy 的功能测试和使用示例。

## 配置设置

### 1. 复制配置模板
```bash
cp test_config.json.template test_config.json
```

### 2. 填写配置信息

编辑 `test_config.json` 文件：

```json
{
  "bot": {
    "test_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_TOKEN"
  },
  "message": {
    "test_app": {
      "app_id": "cli_xxxxxxxxxx", 
      "app_secret": "your_app_secret_here",
      "receive_id": "ou_xxxxxxxxxx"
    }
  }
}
```

**获取配置信息：**

- **webhook URL**: 在飞书群中创建机器人后获得
- **app_id & app_secret**: 在[飞书开放平台](https://open.feishu.cn/)创建应用后获得
- **receive_id**: 用户或群聊的 ID

## 运行测试

### 运行所有测试
```bash
cd tests
python run_all_tests.py
```

### 运行单个模块测试
```bash
cd tests
python test_card.py    # 测试卡片功能
python test_bot.py     # 测试机器人功能
```

## 测试内容

### Card 模块测试 (`test_card.py`)
- ✅ 基本卡片元素生成（文本、按钮、Markdown）
- ✅ DataFrame 表格卡片生成（需要 pandas）
- ✅ 卡片与机器人集成测试

### Bot 模块测试 (`test_bot.py`)
- ✅ 配置管理（保存/读取 webhook）
- ✅ 多种消息发送方式
- ✅ 卡片发送（包括按钮）
- ✅ 折叠面板功能
- ✅ 错误处理

## 使用示例

### 基本机器人使用
```python
from larkpy import LarkBot

# 直接使用 webhook
bot = LarkBot("https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_TOKEN")

# 发送文本
bot.send("Hello, 飞书!")

# 发送卡片
bot.send_card(
    content="这是一个 **Markdown** 卡片",
    title="测试卡片",
    buttons=[{"content": "访问链接", "url": "https://example.com"}]
)
```

### 卡片元素生成
```python
from larkpy.card import CardElementGenerator

# 创建 Markdown 元素
markdown = CardElementGenerator.markdown("## 标题\n这是 **粗体** 文本")

# 创建按钮
button = CardElementGenerator.button("点击我", url="https://example.com")

# 创建表格卡片 (需要 pandas)
import pandas as pd
df = pd.DataFrame({
    '姓名': ['张三', '李四'],
    '分数': [85, 92]
})
table = CardElementGenerator.table_card(df)
```

### 配置管理
```python
# 保存配置
bot = LarkBot("webhook_url", save_config=True)

# 使用已保存的配置
bot = LarkBot("saved_config_name")
```

## 依赖要求

- **基础功能**: requests, typing_extensions
- **DataFrame 表格**: pandas（可选）
- **图片处理**: matplotlib（可选，用于测试）

## 注意事项

1. `test_config.json` 已添加到 `.gitignore`，不会被提交到版本控制
2. 所有包含真实 token 的配置文件都会被忽略
3. 测试会自动跳过缺少配置的部分
4. 建议在测试群中进行测试，避免打扰其他用户