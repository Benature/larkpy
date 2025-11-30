# LarkDocx 设计改进

## 问题
之前的设计将 `create_document` 设计为静态方法，导致：
- ❌ 每次创建文档都要重复传递 `app_id` 和 `app_secret`
- ❌ 创建文档后需要重新初始化才能编辑
- ❌ API 使用不够优雅

```python
# 旧设计（不推荐）
result = LarkDocx.create_document(
    app_id=APP_ID,           # 重复传递
    app_secret=APP_SECRET,   # 重复传递
    title="文档"
)
document_id = result['data']['document']['document_id']

# 还需要重新初始化
docx = LarkDocx(
    app_id=APP_ID,           # 又要传递一次
    app_secret=APP_SECRET,   # 又要传递一次
    document_id=document_id
)
docx.create_text_block("内容")
```

## 解决方案
将 `create_document` 改为实例方法，`document_id` 改为可选参数：

### 核心改进：

1. **`document_id` 变为可选参数**
   ```python
   def __init__(self, app_id: str, app_secret: str, document_id: str = None)
   ```

2. **`create_document` 改为实例方法**
   - 不再需要传递 `app_id` 和 `app_secret`
   - 创建成功后自动设置 `self.document_id`
   - 可以立即继续编辑文档

3. **添加 `_ensure_document_id()` 检查**
   - 在需要 document_id 的方法中调用
   - 提供友好的错误提示

## 新用法

### 方式1：创建新文档并编辑（推荐）
```python
# 一次初始化，无需重复传递凭证
docx = LarkDocx(app_id=APP_ID, app_secret=APP_SECRET)

# 创建文档
result = docx.create_document(title="我的文档")

# 自动设置了 document_id，可以直接编辑
docx.create_heading_block("标题", level=1)
docx.create_text_block("内容")
```

### 方式2：编辑已有文档
```python
# 提供已有文档的 ID
docx = LarkDocx(
    app_id=APP_ID, 
    app_secret=APP_SECRET,
    document_id="existing_doc_id"
)

# 直接编辑
docx.create_text_block("新内容")
```

## 优势对比

| 特性 | 旧设计（静态方法） | 新设计（实例方法） |
|------|------------------|------------------|
| **重复传递凭证** | ❌ 需要 | ✅ 不需要 |
| **创建后编辑** | ❌ 需重新初始化 | ✅ 直接编辑 |
| **代码简洁性** | ❌ 冗长 | ✅ 简洁 |
| **面向对象** | ❌ 不符合 | ✅ 符合 |
| **易用性** | ❌ 一般 | ✅ 优秀 |

## 技术细节

### 1. 可选 document_id
```python
def __init__(self, app_id: str, app_secret: str, document_id: str = None):
    super().__init__(app_id, app_secret)
    self.document_id = document_id
    if document_id:
        self.blocks_url = f"{self.docx_url}/{self.document_id}/blocks"
    else:
        self.blocks_url = None
```

### 2. 自动设置 document_id
```python
def create_document(self, title: str = "未命名文档", folder_token: str = None):
    # ... 创建文档的代码 ...
    
    result = response.json()
    
    # 如果创建成功，自动设置 document_id
    if result.get('code') == 0:
        self.document_id = result['data']['document']['document_id']
        self.blocks_url = f"{self.docx_url}/{self.document_id}/blocks"
    
    return result
```

### 3. 安全检查
```python
def _ensure_document_id(self):
    """确保 document_id 已设置"""
    if not self.document_id:
        raise ValueError(
            "document_id 未设置。请先调用 create_document() 创建文档，"
            "或在初始化时提供 document_id 参数。"
        )

def create_block(self, ...):
    self._ensure_document_id()  # 调用前检查
    # ... 创建块的代码 ...
```

## 完整示例

```python
from larkpy import LarkDocx

# 初始化
docx = LarkDocx(
    app_id="your_app_id",
    app_secret="your_app_secret"
)

# 创建文档
result = docx.create_document(title="技术文档")

if result.get('code') == 0:
    print(f"✓ 文档创建成功！ID: {docx.document_id}")
    
    # 直接编辑，无需重新初始化
    docx.create_heading_block("API 文档", level=1)
    docx.create_text_block("这是API使用说明。")
    
    docx.create_heading_block("快速开始", level=2)
    docx.create_ordered_block("安装依赖")
    docx.create_ordered_block("配置凭证")
    docx.create_ordered_block("运行示例")
    
    print("✓ 文档编辑完成！")
```

## 向后兼容性

新设计完全兼容原有的使用方式：
```python
# 原有方式仍然可用
docx = LarkDocx(
    app_id="app_id",
    app_secret="app_secret",
    document_id="doc_id"  # 显式提供 document_id
)
```

## 总结

这次改进使 `LarkDocx` 类的设计更加符合面向对象的原则，使用更加优雅，避免了重复传递参数的问题。用户体验得到了显著提升。✨
