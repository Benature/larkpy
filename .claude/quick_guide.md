# LarkDocx 快速使用指南

## 安装

```bash
pip install larkpy
```

## 基本配置

```python
from larkpy import LarkDocx

APP_ID = "your_app_id"
APP_SECRET = "your_app_secret"
```

## 使用场景

### 场景1：创建新文档并编辑 ⭐

这是最常用的场景，推荐使用：

```python
# 1. 初始化（无需 document_id）
docx = LarkDocx(app_id=APP_ID, app_secret=APP_SECRET)

# 2. 创建文档
result = docx.create_document(title="我的文档")

# 3. 直接编辑（自动设置了 document_id）
docx.create_heading_block("欢迎", level=1)
docx.create_text_block("这是内容")
```

**优势**：
- ✅ 一次初始化
- ✅ 无需重复传递凭证
- ✅ 创建后立即编辑
- ✅ 代码简洁

### 场景2：编辑已有文档

```python
# 提供已有文档的 ID
docx = LarkDocx(
    app_id=APP_ID,
    app_secret=APP_SECRET,
    document_id="existing_doc_id"
)

# 直接编辑
docx.create_text_block("新增内容")
```

### 场景3：创建文档到指定文件夹

```python
docx = LarkDocx(app_id=APP_ID, app_secret=APP_SECRET)

# 指定文件夹 token
result = docx.create_document(
    title="项目文档",
    folder_token="folder_token_xxx"
)
```

## 常用操作

### 创建各种类型的块

```python
# 标题（1-9级）
docx.create_heading_block("一级标题", level=1)
docx.create_heading_block("二级标题", level=2)

# 文本
docx.create_text_block("这是一段文本")

# 无序列表
docx.create_bullet_block("列表项 1")
docx.create_bullet_block("列表项 2")

# 有序列表
docx.create_ordered_block("步骤 1")
docx.create_ordered_block("步骤 2")

# 自定义块（更灵活）
block = {
    "block_type": 2,  # 文本块
    "text": {
        "elements": [{"text_run": {"content": "自定义内容"}}],
        "style": {}
    }
}
docx.create_block(block)
```

### 读取文档内容

```python
# 获取所有块
all_blocks = docx.get_all_blocks()
for block in all_blocks:
    print(f"块ID: {block['block_id']}, 类型: {block['block_type']}")

# 获取特定块
block_info = docx.get_block("block_id_xxx")
```

### 更新块内容

```python
# 更新单个块
update_data = {
    "text": {
        "elements": [{"text_run": {"content": "更新后的文本"}}],
        "style": {}
    }
}
docx.update_block("block_id_xxx", update_data)

# 批量更新
requests_data = [
    {
        "block_id": "block1",
        "replace_text": {
            "elements": [{"text_run": {"content": "新文本 1"}}]
        }
    },
    {
        "block_id": "block2",
        "replace_text": {
            "elements": [{"text_run": {"content": "新文本 2"}}]
        }
    }
]
docx.batch_update_blocks(requests_data)
```

### 删除块

```python
# 删除第 0 到第 2 个子块（不包含第 2 个）
docx.delete_block(start_index=0, end_index=2)
```

## 完整示例

### 创建一个技术文档

```python
from larkpy import LarkDocx

# 初始化
docx = LarkDocx(
    app_id="your_app_id",
    app_secret="your_app_secret"
)

# 创建文档
result = docx.create_document(title="Python 快速入门")

if result.get('code') == 0:
    print(f"✓ 文档创建成功！ID: {docx.document_id}")
    
    # 添加标题
    docx.create_heading_block("Python 快速入门", level=1)
    
    # 添加简介
    docx.create_text_block("Python 是一门简单易学的编程语言。")
    
    # 添加特性部分
    docx.create_heading_block("主要特性", level=2)
    docx.create_bullet_block("语法简洁")
    docx.create_bullet_block("功能强大")
    docx.create_bullet_block("生态丰富")
    
    # 添加学习步骤
    docx.create_heading_block("学习步骤", level=2)
    docx.create_ordered_block("安装 Python")
    docx.create_ordered_block("学习基础语法")
    docx.create_ordered_block("实践项目")
    
    # 添加代码示例
    docx.create_heading_block("Hello World 示例", level=2)
    docx.create_text_block('print("Hello, World!")')
    
    print("✓ 文档编辑完成！")
```

### 批量处理文档

```python
# 创建多个文档
titles = ["文档1", "文档2", "文档3"]
doc_ids = []

for title in titles:
    docx = LarkDocx(app_id=APP_ID, app_secret=APP_SECRET)
    result = docx.create_document(title=title)
    
    if result.get('code') == 0:
        doc_ids.append(docx.document_id)
        # 为每个文档添加内容
        docx.create_heading_block(title, level=1)
        docx.create_text_block(f"这是{title}的内容")

print(f"创建了 {len(doc_ids)} 个文档")
```

## 错误处理

```python
try:
    docx = LarkDocx(app_id=APP_ID, app_secret=APP_SECRET)
    result = docx.create_document(title="测试文档")
    
    if result.get('code') != 0:
        print(f"创建失败: {result.get('msg')}")
    else:
        # 如果没有调用 create_document 或提供 document_id
        # 调用需要 document_id 的方法会抛出 ValueError
        docx.create_text_block("内容")
        
except ValueError as e:
    print(f"错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

## 最佳实践

1. **使用实例方法创建文档** ✅
   ```python
   # 推荐
   docx = LarkDocx(app_id, app_secret)
   docx.create_document(title="文档")
   ```

2. **复用同一个实例**
   ```python
   # 创建后直接编辑，无需重新初始化
   docx.create_document(title="文档")
   docx.create_heading_block("标题", level=1)
   ```

3. **检查返回结果**
   ```python
   result = docx.create_document(title="文档")
   if result.get('code') == 0:
       # 成功
       pass
   else:
       # 失败，处理错误
       print(result.get('msg'))
   ```

## 参考资料

- [飞书开放平台文档](https://open.feishu.cn/document/)
- [LarkDocx 源码](../src/larkpy/docx.py)
- [完整示例](../examples/create_document_example.py)
