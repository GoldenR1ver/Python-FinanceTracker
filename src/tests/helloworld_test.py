"""
简单的测试示例，用于验证测试环境是否正常工作。
"""

def test_addition():
    """测试基本加法。"""
    assert 1 + 1 == 2

def test_subtraction():
    """测试基本减法。"""
    assert 3 - 2 == 1

def test_list_operations():
    """测试列表操作。"""
    test_list = [1, 2, 3]
    test_list.append(4)
    assert len(test_list) == 4
    assert test_list[0] == 1

def test_string_concatenation():
    """测试字符串拼接。"""
    result = "Hello" + " " + "World"
    assert result == "Hello World"

def test_dictionary():
    """测试字典操作。"""
    data = {"key1": "value1", "key2": "value2"}
    assert "key1" in data
    assert data["key2"] == "value2"

class TestSimpleMath:
    """测试简单数学运算的类。"""
    
    def test_multiplication(self):
        """测试乘法。"""
        assert 2 * 3 == 6
    
    def test_division(self):
        """测试除法。"""
        assert 10 / 2 == 5
    
    def test_division_by_zero(self):
        """测试除以零的情况。"""
        import math
        result = float('inf')
        assert math.isinf(result)

def test_with_fixture_demo(simple_fixture):
    """演示如何使用fixture。"""
    assert simple_fixture == "fixture_data"

def test_exception_handling():
    """测试异常处理。"""
    with pytest.raises(ZeroDivisionError):
        result = 1 / 0

# 如果需要使用pytest，需要导入
import pytest

@pytest.mark.parametrize("input_a, input_b, expected", [
    (1, 2, 3),
    (5, 5, 10),
    (-1, 1, 0),
    (0, 0, 0)
])
def test_parametrized_addition(input_a, input_b, expected):
    """参数化测试示例。"""
    assert input_a + input_b == expected

def test_environment():
    """测试环境设置。"""
    import sys
    # 检查Python版本
    assert sys.version_info.major == 3
    assert sys.version_info.minor >= 8  # 假设使用Python 3.8+
    
    # 检查必要的模块是否可用
    import json
    import os
    assert json is not None
    assert os is not None
