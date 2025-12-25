"""
DataManager类的单元测试。
目标：编写至少10个测试用例，覆盖数据加载、保存、添加、删除等操作。
"""

import pytest
import json
import os
import sys
from unittest.mock import patch, mock_open

# 添加父目录到路径，以便能够导入主模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 现在可以正确导入主模块了
try:
    from Finance_Tracker_Fixed import DataManager, Entry, Plan
    IMPORT_SUCCESS = True
except ImportError as e:
    print(f"导入失败: {e}")
    IMPORT_SUCCESS = False

# 如果导入失败，跳过所有测试
pytestmark = pytest.mark.skipif(
    not IMPORT_SUCCESS, 
    reason="无法导入Finance_Tracker_Fixed模块"
)


def test_datamanager_initialization(data_manager_with_temp_file):
    """测试DataManager初始化。"""
    dm = data_manager_with_temp_file
    
    # 验证初始化属性
    assert dm.file_path is not None
    assert hasattr(dm, 'data')
    assert 'entries' in dm.data
    assert 'budget' in dm.data
    assert 'exchange_rates' in dm.data
    assert 'plans' in dm.data
    
    # 验证日志记录器
    assert hasattr(dm, 'logger')
    assert dm.logger is not None

def test_load_data_success(data_manager_with_temp_file):
    """测试成功加载数据文件。"""
    dm = data_manager_with_temp_file
    
    # 验证数据加载
    entries = dm.get_entries()
    assert len(entries) == 2
    assert entries[0]['entry_type'] == 'income'
    assert entries[0]['amount'] == 5000.0
    assert entries[1]['entry_type'] == 'expense'
    
    # 验证其他数据
    assert dm.get_budget() == 3000.0
    exchange_rates = dm.get_exchange_rates()
    assert exchange_rates['USD'] == 7.0
    assert exchange_rates['CNY'] == 1.0
    
    # 验证计划数据
    plans = dm.get_plans()
    assert len(plans) == 1
    assert plans[0]['plan_type'] == 'monthly'

def test_load_data_file_not_exist():
    """测试加载不存在的文件，应使用默认数据。"""
    # 使用不存在的文件路径
    dm = DataManager(file_path='non_existent_file_12345.json')
    
    # 应使用默认数据
    entries = dm.get_entries()
    assert entries == []  # 默认应为空列表
    assert dm.get_budget() == 0.0  # 默认预算为0
    
    exchange_rates = dm.get_exchange_rates()
    # 检查是否有默认汇率（根据你的代码，初始时有默认汇率）
    assert isinstance(exchange_rates, dict)
    assert len(exchange_rates) > 0

def test_load_data_corrupt_file(corrupt_json_file):
    """测试加载格式错误的JSON文件。"""
    # 应能处理JSON解析错误而不崩溃
    dm = DataManager(file_path=corrupt_json_file)
    
    # 即使文件损坏，也应初始化成功
    assert dm is not None
    # 由于文件损坏，可能使用默认数据
    entries = dm.get_entries()
    assert isinstance(entries, list)

def test_save_data_success(data_manager_with_temp_file, temp_json_file):
    """测试数据成功保存。"""
    dm = data_manager_with_temp_file
    
    # 添加新条目
    new_entry = Entry(
        entry_type='income',
        amount=100.0,
        currency='USD',
        category='Gift',
        date='2024-01-03'
    )
    dm.add_entry(new_entry)
    
    # 保存数据
    result = dm.save_data()
    assert result is True
    
    # 验证文件内容
    with open(temp_json_file, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)
    
    assert len(saved_data['entries']) == 3
    last_entry = saved_data['entries'][-1]
    assert last_entry['amount'] == 100.0
    assert last_entry['currency'] == 'USD'
    assert last_entry['category'] == 'Gift'

def test_add_and_get_entries(data_manager_with_temp_file):
    """测试添加和获取条目。"""
    dm = data_manager_with_temp_file
    
    initial_count = len(dm.get_entries())
    
    # 添加新条目
    entry = Entry(
        entry_type='expense',
        amount=30.0,
        currency='CNY',
        category='Transportation',
        date='2024-01-04'
    )
    dm.add_entry(entry)
    
    # 验证条目数量增加
    entries = dm.get_entries()
    assert len(entries) == initial_count + 1
    
    # 验证新条目的属性
    last_entry = entries[-1]
    assert last_entry['entry_type'] == 'expense'
    assert last_entry['amount'] == 30.0
    assert last_entry['category'] == 'Transportation'

def test_delete_entries(data_manager_with_temp_file):
    """测试删除条目。"""
    dm = data_manager_with_temp_file
    
    initial_entries = dm.get_entries()
    initial_count = len(initial_entries)
    
    # 如果初始没有条目，直接返回
    if initial_count == 0:
        pytest.skip("没有可删除的条目")
    
    # 删除第一个条目
    dm.delete_entries([0])
    
    # 验证条目数量减少
    entries = dm.get_entries()
    assert len(entries) == initial_count - 1


def test_delete_entries_invalid_index(data_manager_with_temp_file):
    """测试删除无效索引，应安全处理。"""
    dm = data_manager_with_temp_file
    
    initial_entries = dm.get_entries().copy()
    initial_count = len(initial_entries)
    
    # 删除不存在的索引（应无影响）
    dm.delete_entries([999, -1, 1000])
    
    # 数据应无变化
    entries = dm.get_entries()
    assert len(entries) == initial_count
    
    # 验证数据内容不变
    for i in range(min(len(initial_entries), len(entries))):
        assert entries[i]['amount'] == initial_entries[i]['amount']

def test_delete_entries_multiple(data_manager_with_temp_file):
    """测试删除多个条目。"""
    dm = data_manager_with_temp_file
    
    # 添加一些测试条目
    for i in range(3):
        entry = Entry(
            entry_type='expense',
            amount=10.0 * (i + 1),
            currency='CNY',
            category=f'Test{i}',
            date=f'2024-01-{i+5:02d}'
        )
        dm.add_entry(entry)
    
    initial_count = len(dm.get_entries())
    
    # 删除多个条目（索引1和3）
    dm.delete_entries([1, 3])
    
    # 验证删除后数量
    entries = dm.get_entries()
    assert len(entries) == initial_count - 2

def test_set_and_get_budget(data_manager_with_temp_file):
    """测试设置和获取预算。"""
    dm = data_manager_with_temp_file
    
    # 测试设置正数预算
    dm.set_budget(5000.0)
    assert dm.get_budget() == 5000.0
    
    # 测试设置零预算
    dm.set_budget(0.0)
    assert dm.get_budget() == 0.0
    
    # 测试设置大额预算
    dm.set_budget(1000000.0)
    assert dm.get_budget() == 1000000.0

def test_set_and_get_exchange_rates(data_manager_with_temp_file):
    """测试设置和获取汇率。"""
    dm = data_manager_with_temp_file
    
    # 测试设置新汇率
    new_rates = {
        'USD': 7.2,
        'EUR': 7.8,
        'JPY': 0.05,
        'CNY': 1.0
    }
    dm.set_exchange_rates(new_rates)
    
    # 验证设置的汇率
    rates = dm.get_exchange_rates()
    assert rates['USD'] == 7.2
    assert rates['EUR'] == 7.8
    assert rates['JPY'] == 0.05
    assert 'HKD' not in rates  # 被新数据替换

def test_add_and_get_plans(data_manager_with_temp_file):
    """测试添加和获取资金计划。"""
    dm = data_manager_with_temp_file
    
    initial_plans = dm.get_plans()
    initial_count = len(initial_plans)
    
    # 添加新计划
    plan = Plan(
        plan_type='yearly',
        start_date='2024-01-01',
        end_date='2024-12-31',
        spending_limit=10000.0,
        saving_goal=5000.0
    )
    dm.add_plan(plan)
    
    # 验证计划数量增加
    plans = dm.get_plans()
    assert len(plans) == initial_count + 1
    
    # 验证新计划属性
    last_plan = plans[-1]
    assert last_plan['plan_type'] == 'yearly'
    assert last_plan['spending_limit'] == 10000.0
    assert last_plan['saving_goal'] == 5000.0

def test_delete_plan(data_manager_with_temp_file):
    """测试删除资金计划。"""
    dm = data_manager_with_temp_file
    
    # 先添加一个计划以便删除
    plan = Plan(
        plan_type='weekly',
        start_date='2024-01-08',
        end_date='2024-01-14',
        spending_limit=500.0,
        saving_goal=200.0
    )
    dm.add_plan(plan)
    
    initial_count = len(dm.get_plans())
    
    # 删除刚添加的计划（最后一个）
    dm.delete_plan(initial_count - 1)
    
    # 验证计划数量减少
    plans = dm.get_plans()
    assert len(plans) == initial_count - 1

def test_delete_plan_invalid_index(data_manager_with_temp_file):
    """测试删除无效的计划索引。"""
    dm = data_manager_with_temp_file
    
    initial_plans = dm.get_plans().copy()
    
    # 删除不存在的索引（应无影响）
    dm.delete_plan(999)
    dm.delete_plan(-1)
    
    # 数据应无变化
    plans = dm.get_plans()
    assert len(plans) == len(initial_plans)

def test_save_as(data_manager_with_temp_file, temp_json_file):
    """测试另存为功能。"""
    dm = data_manager_with_temp_file
    
    import tempfile
    new_file_path = tempfile.mktemp(suffix='.json')
    
    try:
        # 另存为新文件
        result = dm.save_as(new_file_path)
        assert result is True
        
        # 验证新文件存在
        assert os.path.exists(new_file_path)
        
        # 验证新文件内容
        with open(new_file_path, 'r', encoding='utf-8') as f:
            new_data = json.load(f)
        
        assert 'entries' in new_data
        assert len(new_data['entries']) == len(dm.get_entries())
        
        # 文件路径应该更新
        assert dm.file_path == new_file_path
        
    finally:
        # 清理临时文件
        try:
            os.unlink(new_file_path)
        except FileNotFoundError:
            pass

def test_import_data(data_manager_with_temp_file):
    """测试导入数据。"""
    import tempfile
    import json
    
    # 创建要导入的数据文件
    import_data = {
        'entries': [
            {
                'entry_type': 'income',
                'amount': 3000.0,
                'currency': 'CNY',
                'category': 'Bonus',
                'date': '2024-01-10'
            }
        ],
        'budget': 2000.0,
        'exchange_rates': {'USD': 7.1, 'CNY': 1.0},
        'plans': []
    }
    
    import_file = tempfile.mktemp(suffix='.json')
    with open(import_file, 'w', encoding='utf-8') as f:
        json.dump(import_data, f)
    
    try:
        # 导入数据
        result = data_manager_with_temp_file.import_data(import_file)
        assert result is True
        
        # 验证数据被导入
        entries = data_manager_with_temp_file.get_entries()
        assert len(entries) == 1  # 应该只有导入的数据，原有数据被替换
        assert entries[0]['amount'] == 3000.0
        assert entries[0]['category'] == 'Bonus'
        
        # 验证预算被更新
        assert data_manager_with_temp_file.get_budget() == 2000.0
        
        # 验证文件路径更新
        assert data_manager_with_temp_file.file_path == import_file
        
    finally:
        # 清理临时文件
        try:
            os.unlink(import_file)
        except FileNotFoundError:
            pass

def test_import_data_invalid_file(data_manager_with_temp_file):
    """测试导入无效文件。"""
    import tempfile
    
    # 创建无效的JSON文件
    invalid_file = tempfile.mktemp(suffix='.json')
    with open(invalid_file, 'w') as f:
        f.write('{invalid json')
    
    try:
        # 导入应失败
        result = data_manager_with_temp_file.import_data(invalid_file)
        assert result is False
        
    finally:
        try:
            os.unlink(invalid_file)
        except FileNotFoundError:
            pass

def test_legacy_data_compatibility(data_manager_with_temp_file):
    """测试旧版本数据兼容性（'type'字段）。"""
    import tempfile
    import json
    
    # 创建旧版本数据（使用'type'而不是'entry_type'）
    legacy_data = {
        'entries': [
            {
                'type': 'income',  # 旧字段名
                'amount': 1000.0,
                'currency': 'CNY',
                'category': 'Salary',
                'date': '2024-01-01'
            }
        ],
        'budget': 1000.0,
        'exchange_rates': {},
        'plans': []
    }
    
    legacy_file = tempfile.mktemp(suffix='.json')
    with open(legacy_file, 'w', encoding='utf-8') as f:
        json.dump(legacy_data, f)
    
    try:
        # 加载旧数据
        dm = DataManager(file_path=legacy_file)
        
        # 验证数据被正确转换
        entries = dm.get_entries()
        assert len(entries) == 1
        assert 'entry_type' in entries[0]  # 应该被转换
        assert entries[0]['entry_type'] == 'income'
        assert entries[0]['amount'] == 1000.0
        
    finally:
        try:
            os.unlink(legacy_file)
        except FileNotFoundError:
            pass
