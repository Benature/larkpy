#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试卡片元素生成功能"""
import sys
from pathlib import Path
import pytest

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def _check_pandas_available():
    """检查 pandas 是否可用"""
    try:
        import pandas as pd
        return True
    except ImportError:
        return False


class TestCardElementGenerator:
    """测试 CardElementGenerator 类"""

    @pytest.fixture
    def generator(self):
        """创建 CardElementGenerator 实例"""
        from larkpy import CardElementGenerator
        return CardElementGenerator

    def test_markdown_element(self, generator):
        """测试 Markdown 元素生成"""
        markdown = generator.markdown("## 标题\\n这是 **粗体** 和 *斜体* 文本")
        assert markdown["tag"] == "markdown"
        assert "## 标题" in markdown["content"]

    def test_text_element(self, generator):
        """测试文本元素生成"""
        text = generator.text("普通文本内容")
        assert text["tag"] == "text"
        assert text["content"] == "普通文本内容"

    def test_button_element(self, generator):
        """测试按钮元素生成"""
        button = generator.button("访问链接", url="https://github.com/Benature/larkpy")
        assert button["tag"] == "button"
        assert button["text"]["content"] == "访问链接"
        assert "https://github.com/Benature/larkpy" in str(button)

    def test_hr_element(self, generator):
        """测试分割线元素生成"""
        hr = generator.hr()
        assert hr["tag"] == "hr"

    def test_image_element(self, generator):
        """测试图片元素生成"""
        image = generator.image("test_image_key", alt="测试图片")
        assert image["tag"] == "image"
        assert image["image_key"] == "test_image_key"

    @pytest.mark.skipif(not _check_pandas_available(), reason="pandas not available")
    def test_table_card_with_dataframe(self, generator):
        """测试 DataFrame 转表格卡片功能"""
        import pandas as pd
        from datetime import datetime

        df = pd.DataFrame({
            '名称': ['项目A', '项目B', '项目C'],
            '进度': [0.8, 0.6, 0.9],
            '完成': [True, False, True],
            '日期': [datetime(2024, 8, 28),
                   datetime(2024, 8, 29),
                   datetime(2024, 8, 30)]
        })

        table = generator.table_card(df, page_size=3)
        assert table["tag"] == "table"
        assert len(table["rows"]) >= 3  # 至少包含数据行

    def test_column_divider(self, generator):
        """测试列分割器元素生成"""
        divider = generator.column_divider()
        assert divider["tag"] == "column_divider"
