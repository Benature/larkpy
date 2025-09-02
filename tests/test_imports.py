#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试模块导入"""
import sys
from pathlib import Path
import pytest

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_new_modules_import():
    """测试新添加的模块导入"""
    from larkpy import CardElementGenerator, BotConfig
    assert CardElementGenerator is not None
    assert BotConfig is not None


def test_original_modules_import():
    """测试原有模块导入"""
    from larkpy import LarkWebhook, LarkAPI, LarkMessage, LarkDocx, LarkBitTable, LarkCalendar
    assert LarkWebhook is not None
    assert LarkAPI is not None
    assert LarkMessage is not None
    assert LarkDocx is not None
    assert LarkBitTable is not None
    assert LarkCalendar is not None


def test_all_imports():
    """测试所有模块一次性导入"""
    from larkpy import (LarkWebhook, BotConfig, CardElementGenerator, LarkAPI, LarkMessage,
                        LarkDocx, LarkBitTable, LarkCalendar)
    modules = [
        LarkWebhook, BotConfig, CardElementGenerator, LarkAPI, LarkMessage, LarkDocx, LarkBitTable,
        LarkCalendar
    ]
    for module in modules:
        assert module is not None
