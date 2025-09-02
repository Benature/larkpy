"""测试 card.py 模块"""
import sys
import os
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from larkpy.card import CardElementGenerator, parse_column_type, PANDAS_AVAILABLE
except ImportError:
    # 如果找不到模块，尝试直接导入
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "card",
        Path(__file__).parent.parent / "src" / "larkpy" / "card.py")
    card_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(card_module)
    CardElementGenerator = card_module.CardElementGenerator
    parse_column_type = card_module.parse_column_type
    PANDAS_AVAILABLE = card_module.PANDAS_AVAILABLE
from test_utils import skip_if_no_config, test_config
import json


def test_card_element_generator_basic():
    """测试 CardElementGenerator 基本功能"""
    print("测试 CardElementGenerator 基本功能...")

    # 测试 markdown 元素
    markdown_element = CardElementGenerator.markdown("这是一段 **粗体** 文本")
    print("Markdown 元素:", json.dumps(markdown_element, ensure_ascii=False, indent=2))

    assert markdown_element["tag"] == "markdown"
    assert "这是一段" in markdown_element["content"]

    # 测试 text 元素
    text_element = CardElementGenerator.text("普通文本")
    print("Text 元素:", json.dumps(text_element, ensure_ascii=False, indent=2))

    assert text_element["tag"] == "text"
    assert text_element["content"] == "普通文本"

    # 测试 button 元素
    button_element = CardElementGenerator.button("点击访问", url="https://example.com")
    print("Button 元素:", json.dumps(button_element, ensure_ascii=False, indent=2))

    assert button_element["tag"] == "button"
    assert button_element["text"]["content"] == "点击访问"
    assert button_element["behaviors"][0]["default_url"] == "https://example.com"

    print("✅ CardElementGenerator 基本功能测试通过")


def test_card_dataframe_functionality():
    """测试 DataFrame 相关功能"""
    if not PANDAS_AVAILABLE:
        print("跳过 DataFrame 测试: pandas 未安装")
        return

    print("测试 DataFrame 相关功能...")

    import pandas as pd
    from datetime import datetime

    # 创建测试数据
    df = pd.DataFrame({
        '姓名': ['张三', '李四', '王五'],
        '年龄': [25, 30, 35],
        '分数': [85.5, 92.0, 78.5],
        '是否通过': [True, True, False],
        '创建时间': [datetime(2024, 1, 1),
                 datetime(2024, 1, 2),
                 datetime(2024, 1, 3)]
    })

    # 测试列类型解析
    column_types = parse_column_type(df)
    print("列类型:", column_types)

    assert column_types['姓名'] == 'text'
    assert column_types['年龄'] == 'numeric'
    assert column_types['分数'] == 'numeric'
    assert column_types['是否通过'] == 'boolean'
    assert column_types['创建时间'] == 'date'

    # 测试表格卡片生成
    table_card = CardElementGenerator.table_card(df, page_size=3)
    print("表格卡片结构:")
    print(json.dumps(table_card, ensure_ascii=False, indent=2)[:500] + "...")

    assert table_card["tag"] == "table"
    assert table_card["page_size"] == 3
    assert len(table_card["columns"]) == 5
    assert len(table_card["rows"]) == 3

    print("✅ DataFrame 功能测试通过")


@skip_if_no_config("bot")
def test_card_with_bot():
    """测试卡片与机器人集成"""
    print("测试卡片与机器人集成...")

    try:
        from larkpy import LarkWebhook
    except ImportError:
        # 直接导入
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "bot",
            Path(__file__).parent.parent / "src" / "larkpy" / "bot.py")
        bot_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bot_module)
        LarkWebhook = bot_module.LarkBot

    webhook_url = test_config.get_bot_webhook()
    if not webhook_url:
        print("跳过测试: 缺少 webhook 配置")
        return

    bot = LarkWebhook(webhook_url)

    # 创建卡片元素
    elements = [
        CardElementGenerator.markdown("## 测试卡片功能\n这是一个测试卡片，包含多种元素："),
        CardElementGenerator.text("普通文本内容"),
        CardElementGenerator.button("访问GitHub", url="https://github.com/Benature/larkpy")
    ]

    # 发送卡片
    response = bot.send_card(content=elements,
                             title="Card 功能测试",
                             subtitle="测试 CardElementGenerator",
                             echo=True)

    if response.status_code == 200:
        print("✅ 卡片发送成功")
    else:
        print(f"❌ 卡片发送失败: {response.status_code}, {response.text}")


def test_card_dataframe_with_bot():
    """测试 DataFrame 表格卡片发送"""
    if not PANDAS_AVAILABLE:
        print("跳过 DataFrame 表格测试: pandas 未安装")
        return

    webhook_url = test_config.get_bot_webhook()
    if not webhook_url:
        print("跳过测试: 缺少 webhook 配置")
        return

    print("测试 DataFrame 表格卡片发送...")

    import pandas as pd
    from datetime import datetime

    try:
        from larkpy import LarkWebhook
    except ImportError:
        # 直接导入
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "bot",
            Path(__file__).parent.parent / "src" / "larkpy" / "bot.py")
        bot_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bot_module)
        LarkWebhook = bot_module.LarkBot

    bot = LarkWebhook(webhook_url)

    # 创建示例数据
    df = pd.DataFrame({
        '产品': ['产品A', '产品B', '产品C', '产品D'],
        '销量': [120, 85, 200, 150],
        '收入': [12000.5, 8500.0, 20000.0, 15000.0],
        '上架': [True, True, False, True],
        '更新时间': [
            datetime(2024, 8, 25),
            datetime(2024, 8, 26),
            datetime(2024, 8, 27),
            datetime(2024, 8, 28)
        ]
    })

    # 生成表格卡片
    table_element = CardElementGenerator.table_card(df,
                                                    page_size=4,
                                                    row_height='auto',
                                                    freeze_first_column=True)

    # 发送表格卡片
    response = bot.send_card(content=[CardElementGenerator.markdown("## 产品销售数据报表"), table_element],
                             title="数据表格测试",
                             echo=True)

    if response.status_code == 200:
        print("✅ DataFrame 表格卡片发送成功")
    else:
        print(f"❌ DataFrame 表格卡片发送失败: {response.status_code}, {response.text}")


def main():
    """运行所有测试"""
    print("开始测试 card.py 模块...\n")

    try:
        test_card_element_generator_basic()
        print()

        test_card_dataframe_functionality()
        print()

        test_card_with_bot()
        print()

        test_card_dataframe_with_bot()
        print()

        print("🎉 所有测试完成！")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
