# Docstring 编写规则

## 适用范围
本规则适用于 larkpy 项目中所有 Python 函数和类的文档字符串。

## 基本格式

### 函数 Docstring
```python
def function_name(param1: Type1, param2: Type2 = default) -> ReturnType:
    """简短的一句话描述
    
    可选的详细描述，解释函数的用途和行为。
    如果有多行，用空行分隔。
    
    Args:
        param1 (Type1): 参数1的描述
        param2 (Type2, optional): 参数2的描述. Defaults to default.
        
    Returns:
        ReturnType: 返回值的描述
        
    Raises:
        ExceptionType: 何时会抛出这个异常（如果适用）
        
    References:
        相关的官方文档链接（如果适用）
        
    Note:
        本函数由 AI 辅助生成 (Claude Sonnet 4.5 thinking)
        （仅在函数由 AI 辅助生成时添加此行）
        
    Examples:
        >>> # 使用示例
        >>> result = function_name(arg1, arg2)
        >>> print(result)
    """
```

### 类 Docstring
```python
class ClassName:
    """类的简短描述
    
    详细描述类的用途、功能和使用场景。
    
    Args:
        param1 (Type1): 初始化参数1的描述
        param2 (Type2): 初始化参数2的描述
        
    Attributes:
        attr1 (Type1): 属性1的描述
        attr2 (Type2): 属性2的描述
        
    Note:
        本类由 AI 辅助生成 (Claude Sonnet 4.5 thinking)
        （仅在类由 AI 辅助生成时添加此行）
        
    Examples:
        >>> instance = ClassName(arg1, arg2)
        >>> instance.method()
    """
```

## 详细规则

### 1. 描述性文字
- **首行**：简短的一句话描述，不超过80个字符
- **详细描述**：在首行后空一行，可以包含多段文字
- 使用中文描述（本项目为中文项目）
- 描述应清晰、准确、易懂

### 2. Args（参数）部分
- 每个参数单独一行
- 格式：`param_name (Type, optional): 描述. Defaults to value.`
- 可选参数必须标注 `optional` 并说明默认值
- 类型使用 Python 类型提示的形式

### 3. Returns（返回值）部分
- 格式：`Type: 返回值描述`
- 如果返回多个值，可以分行说明
- 对于复杂的返回结构（如字典），可以详细说明结构

### 4. References（参考）部分
- 如果函数基于飞书开放平台 API，必须添加官方文档链接
- 格式：直接写 URL

### 5. Note（注意）部分
- **AI 辅助生成声明**：所有由 AI 辅助生成的函数/类必须标注模型名称和版本
  - **必须包含**：模型名称 + 版本号
  - 格式：`本函数由 AI 辅助生成 (模型名称 版本号)`
  - 示例：
    - `本函数由 AI 辅助生成 (Claude Sonnet 4.5)`
    - `本函数由 AI 辅助生成 (Claude Sonnet 3.5)`
    - `本函数由 AI 辅助生成 (GPT-4 Turbo)`
    - `本类由 AI 辅助生成 (Claude Sonnet 4.5)`
    - `本模块由 AI 辅助生成 (Claude Sonnet 4.5)`
  - **警告**：不要使用模糊的描述如"由 AI 辅助生成"，必须明确模型和版本
- 其他重要注意事项也可以添加在此部分

### 6. Examples（示例）部分
- 必须提供实用的代码示例
- 使用 doctest 格式（`>>>`）
- 示例应该是可运行的（除非需要真实凭证）
- 复杂功能建议提供多个示例

### 7. Raises（异常）部分（可选）
- 如果函数会抛出特定异常，应该说明
- 格式：`ExceptionType: 触发条件的描述`

## 特殊说明

### AI 辅助生成标注
当函数或类由 AI（如 Claude）辅助生成时，必须在 `Note` 部分添加以下声明：
```
Note:
    本函数由 AI 辅助生成 (Claude Sonnet 4.5 thinking)
```

对于不同的 AI 模型，请使用相应的模型名称和版本号。

### 便捷方法
对于便捷方法（wrapper 函数），建议在描述中注明"（便捷方法）"，并简化文档：
```python
def create_text_block(content: str) -> dict:
    """创建文本块（便捷方法）
    
    Args:
        content (str): 文本内容
        
    Returns:
        dict: 创建结果
        
    Note:
        本函数由 AI 辅助生成 (Claude Sonnet 4.5 thinking)
        
    Examples:
        >>> result = docx.create_text_block("这是一段文本")
    """
```

## 示例

完整的函数示例：
```python
def update_block(self,
                block_id: str,
                update_data: dict,
                document_revision_id: int = -1,
                user_id_type: str = "open_id") -> dict:
    """更新块的内容
    
    通过提供块ID和新内容来更新飞书文档中的特定块。
    
    Args:
        block_id (str): 块的唯一标识
        update_data (dict): 更新的数据，包含块类型和对应的内容
        document_revision_id (int, optional): 文档版本号，-1 表示最新版本. Defaults to -1.
        user_id_type (str, optional): 用户 ID 类型. Defaults to "open_id".
        
    Returns:
        dict: 更新后的块信息，包含新的版本号和内容
        
    References:
        https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document-block/patch
        
    Note:
        本函数由 AI 辅助生成 (Claude Sonnet 4.5 thinking)
        
    Examples:
        >>> # 更新文本块
        >>> update_data = {
        ...     "text": {
        ...         "elements": [{"text_run": {"content": "Updated text"}}],
        ...         "style": {}
        ...     }
        ... }
        >>> result = docx.update_block("block_id_xxx", update_data)
        >>> print(result['data']['block']['block_id'])
    """
```

## 遵守要点

1. ✅ 所有公开函数和类都必须有 docstring
2. ✅ AI 生成的代码必须标注
3. ✅ 提供实用的示例
4. ✅ 参数和返回值类型清晰
5. ✅ 包含官方 API 文档链接（如适用）
6. ✅ 使用中文描述
7. ✅ 保持格式一致性
