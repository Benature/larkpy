"""飞书卡片元素生成工具."""
import datetime
from typing import Dict, List, Literal, Union

try:
    import pandas as pd
    from pandas.api.types import (is_datetime64_any_dtype, is_numeric_dtype, is_string_dtype,
                                  is_bool_dtype, is_categorical_dtype)
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def parse_column_type(df) -> dict:
    """解析 DataFrame 列类型以生成飞书卡片."""
    if not PANDAS_AVAILABLE:
        raise ImportError("pandas is required for DataFrame operations")
    
    column_type_dict = {}

    for col in df.columns:
        if is_datetime64_any_dtype(df[col]):
            col_type = 'date'
        elif is_bool_dtype(df[col]):
            col_type = 'boolean'
        elif is_numeric_dtype(df[col]):
            col_type = 'numeric'
        elif is_string_dtype(df[col]):
            col_type = 'text'
        elif is_categorical_dtype(df[col]):
            col_type = 'category'
        else:
            col_type = 'other'

        column_type_dict[col] = col_type
    return column_type_dict


class CardElementGenerator:
    """飞书卡片元素生成工具."""

    @classmethod
    def hr(cls) -> Dict:
        """生成分割线元素."""
        return {"tag": "hr"}
    
    @classmethod
    def image(cls, image_key: str, alt: str = "", width: str = "auto", height: str = "auto") -> Dict:
        """生成图片元素."""
        return {
            "tag": "image",
            "image_key": image_key,
            "alt": alt,
            "width": width,
            "height": height
        }
    
    @classmethod
    def column_divider(cls) -> Dict:
        """生成列分割器元素."""
        return {"tag": "column_divider"}

    @classmethod
    def markdown(cls, text: str) -> Dict:
        """将文本转换为 markdown 格式的飞书卡片元素."""
        elements = {
            "tag": "markdown",
            "content": text,
            "margin": "0px 0px 0px 0px",
            "text_size": "normal_v2",
            "text_align": "left",
        }
        return elements

    @classmethod
    def table_card(cls,
                   df,
                   page_size: int = 5,
                   row_height: Literal['auto', 'low'] = 'auto',
                   row_max_height: int = 50,
                   freeze_first_column: bool = True,
                   element_id: str = None,
                   header_style: Dict[Literal['text_align', 'text_size', 'background_style', 'text_color',
                                              'bold', 'lines'], Union[str, bool, int]] = None,
                   display_header: bool = True) -> Dict:
        """将 DataFrame 转换为飞书表格卡片
        
        Args:
            df: pandas DataFrame
            page_size: 每页最大展示的数据行数，支持[1,10]整数，默认值 5
            row_height: 行高设置，默认值 'low'
            row_max_height: 当 row_height 为 'auto' 时的最大行高，默认 50px
            freeze_first_column: 是否冻结首列，默认 True
            element_id: 组件的唯一标识
            header_style: 表头样式配置
            display_header: 是否显示表头，默认 True
            
        Returns:
            Dict: 飞书表格卡片配置
            
        Reference:
            https://open.feishu.cn/document/feishu-cards/card-json-v2-components/content-components/table
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for DataFrame operations")
        
        columns_type = parse_column_type(df)
        columns = [
            dict(name=str(i), display_name=k, data_type=t, date_format='MM/DD HH:mm:ss')
            for i, (k, t) in enumerate(columns_type.items())
        ]

        # 以文本序号作为列名（不支持中文）
        raw_df = df.copy()
        raw_df.columns = list(map(str, range(len(raw_df.columns))))

        for i in [_i for _i, (k, t) in enumerate(columns_type.items()) if t == 'date']:
            raw_df[str(i)] = raw_df[str(i)].apply(lambda t: int(t.timestamp() * 1000))

        rows = raw_df.to_dict(orient='records')

        if not display_header:
            for c_info in columns:
                if c_info['data_type'] != 'date':
                    c_info['display_name'] = str(rows[0][c_info['name']])
                else:
                    c_info['display_name'] = datetime.datetime.fromtimestamp(
                        rows[0][c_info['name']] / 1000).strftime('%m-%d %H:%M:%S')
            rows = rows[1:]

        header_style4use = {
            "text_align": "left",
            "text_size": "normal",
            "background_style": "none",
            "text_color": "default",
            "bold": True,
            "lines": 1
        }
        header_style4use.update(header_style or {})

        elements = {
            "tag": "table",
            "element_id": element_id or str(datetime.datetime.now()),
            "margin": "0px 0px 0px 0px",
            "page_size": page_size,
            "row_height": row_height,
            "row_max_height": f"{row_max_height}px",
            "freeze_first_column": freeze_first_column,
            "header_style": header_style4use,
            "columns": columns,
            "rows": rows
        }
        return elements

    @classmethod
    def text(cls, content: str, **kwargs) -> Dict:
        """创建文本元素."""
        element = {
            "tag": "text",
            "content": content,
        }
        element.update(kwargs)
        return element

    @classmethod
    def button(cls,
              text: str,
              url: str = None,
              pc_url: str = None,
              ios_url: str = None,
              android_url: str = None,
              **kwargs) -> Dict:
        """创建按钮元素."""
        element = {
            "tag": "button",
            "text": {
                "tag": "plain_text",
                "content": text
            },
            "type": "default",
            "width": "default",
            "size": "medium",
            "behaviors": [{
                "type": "open_url",
                "default_url": url or "",
                "pc_url": pc_url or "",
                "ios_url": ios_url or "",
                "android_url": android_url or "",
            }],
            "margin": "0px 0px 0px 0px"
        }
        element.update(kwargs)
        return element