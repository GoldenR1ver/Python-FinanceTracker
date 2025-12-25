"""
Entry实体类的单元测试。
目标：测试Entry的创建、序列化、边界条件等。
"""

import pytest
from dataclasses import asdict

def test_entry_creation(sample_entry_data):
    """测试Entry对象创建。"""
    import importlib.util
    import sys
    import os
    
    main_file_path = os.path.join(os.path.dirname(__file__), '..', 'Finance_Tracker_Fixed.py')
    spec = importlib.util.spec_from_file_location("finance_tracker", main_file_path)
    finance_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(finance_module)
    sys.modules['finance_tracker'] = finance_module
    
    # 创建Entry实例
    entry = finance_module.Entry(**sample_entry_data)
    
    # 验证属性
    assert entry.entry_type == 'income'
    assert entry.amount == 1000.0
    assert entry.currency == 'CNY'
    assert entry.category == 'Salary'
    assert entry.date == '2024-01-15'
    assert entry.invoice is None

def test_entry_with_invoice():
    """测试创建带发票信息的Entry。"""
    import importlib.util
    import sys
    import os
    
    main_file_path = os.path.join(os.path.dirname(__file__), '..', 'Finance_Tracker_Fixed.py')
    spec = importlib.util.spec_from_file_location("finance_tracker", main_file_path)
    finance_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(finance_module)
    sys.modules['finance_tracker'] = finance_module
    
    invoice_data = {'type': 'electronic', 'info': '发票编号12345'}
    entry = finance_module.Entry(
        entry_type='expense',
        amount=88.0,
        currency='USD',
        category='Food',
        date='2024-01-16',
        invoice=invoice_data
    )
    
    assert entry.invoice == invoice_data
    assert entry.invoice['type'] == 'electronic'
    assert entry.invoice['info'] == '发票编号12345'

def test_entry_to_dict(sample_entry_data):
    """测试to_dict方法。"""
    import importlib.util
    import sys
    import os
    
    main_file_path = os.path.join(os.path.dirname(__file__), '..', 'Finance_Tracker_Fixed.py')
    spec = importlib.util.spec_from_file_location("finance_tracker", main_file_path)
    finance_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(finance_module)
    sys.modules['finance_tracker'] = finance_module
    
    entry = finance_module.Entry(**sample_entry_data)
    entry_dict = entry.to_dict()
    
    # 验证字典结构
    assert isinstance(entry_dict, dict)
    assert entry_dict['entry_type'] == 'income'
    assert entry_dict['amount'] == 1000.0
    assert entry_dict['currency'] == 'CNY'
    assert entry_dict['category'] == 'Salary'
    assert entry_dict['date'] == '2024-01-15'
    assert entry_dict['invoice'] is None
    
    # 验证to_dict使用dataclasses.asdict
    assert entry_dict == asdict(entry)

def test_entry_with_negative_amount():
    """测试负金额的Entry（可能表示退款）。"""
    import importlib.util
    import sys
    import os
    
    main_file_path = os.path.join(os.path.dirname(__file__), '..', 'Finance_Tracker_Fixed.py')
    spec = importlib.util.spec_from_file_location("finance_tracker", main_file_path)
    finance_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(finance_module)
    sys.modules['finance_tracker'] = finance_module
    
    # 负金额可能是退款或调整
    entry = finance_module.Entry(
        entry_type='income',  # 负的收入可能是退款支出
        amount=-50.0,
        currency='CNY',
        category='Adjustment',
        date='2024-01-18'
    )
    
    assert entry.amount == -50.0

def test_entry_with_zero_amount():
    """测试零金额的Entry（边界情况）。"""
    import importlib.util
    import sys
    import os
    
    main_file_path = os.path.join(os.path.dirname(__file__), '..', 'Finance_Tracker_Fixed.py')
    spec = importlib.util.spec_from_file_location("finance_tracker", main_file_path)
    finance_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(finance_module)
    sys.modules['finance_tracker'] = finance_module
    
    entry = finance_module.Entry(
        entry_type='expense',
        amount=0.0,
        currency='CNY',
        category='Free',
        date='2024-01-19'
    )
    
    assert entry.amount == 0.0

def test_entry_with_large_amount():
    """测试大金额的Entry（边界情况）。"""
    import importlib.util
    import sys
    import os
    
    main_file_path = os.path.join(os.path.dirname(__file__), '..', 'Finance_Tracker_Fixed.py')
    spec = importlib.util.spec_from_file_location("finance_tracker", main_file_path)
    finance_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(finance_module)
    sys.modules['finance_tracker'] = finance_module
    
    large_amount = 10_000_000.0
    entry = finance_module.Entry(
        entry_type='income',
        amount=large_amount,
        currency='CNY',
        category='Lottery',
        date='2024-01-20'
    )
    
    assert entry.amount == large_amount

def test_entry_date_format_variations():
    """测试不同日期格式（Entry不验证格式，只存储字符串）。"""
    import importlib.util
    import sys
    import os
    
    main_file_path = os.path.join(os.path.dirname(__file__), '..', 'Finance_Tracker_Fixed.py')
    spec = importlib.util.spec_from_file_location("finance_tracker", main_file_path)
    finance_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(finance_module)
    sys.modules['finance_tracker'] = finance_module
    
    test_cases = [
        '2024-01-15',      # 标准格式
        '2024/01/15',      # 斜杠格式
        '2024.01.15',      # 点格式
        '15-01-2024',      # 日-月-年
        'January 15, 2024' # 文本格式
    ]
    
    for date_str in test_cases:
        entry = finance_module.Entry(
            entry_type='expense',
            amount=10.0,
            currency='CNY',
            category='Test',
            date=date_str
        )
        assert entry.date == date_str

def test_entry_currency_codes():
    """测试不同货币代码。"""
    import importlib.util
    import sys
    import os
    
    main_file_path = os.path.join(os.path.dirname(__file__), '..', 'Finance_Tracker_Fixed.py')
    spec = importlib.util.spec_from_file_location("finance_tracker", main_file_path)
    finance_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(finance_module)
    sys.modules['finance_tracker'] = finance_module
    
    currencies = ['CNY', 'USD', 'EUR', 'JPY', 'GBP', 'CAD', 'AUD', 'HKD']
    
    for currency in currencies:
        entry = finance_module.Entry(
            entry_type='income',
            amount=100.0,
            currency=currency,
            category='Test',
            date='2024-01-15'
        )
        assert entry.currency == currency

def test_entry_category_types():
    """测试不同类别。"""
    import importlib.util
    import sys
    import os
    
    main_file_path = os.path.join(os.path.dirname(__file__), '..', 'Finance_Tracker_Fixed.py')
    spec = importlib.util.spec_from_file_location("finance_tracker", main_file_path)
    finance_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(finance_module)
    sys.modules['finance_tracker'] = finance_module
    
    categories = [
        'Salary', 'Food', 'Housing', 'Transportation',
        'Medical', 'Clothes & Cosmetics', 'Hobby', 'Education', 'Gift',
        'Other', 'Investment', 'Entertainment'
    ]
    
    for category in categories:
        entry = finance_module.Entry(
            entry_type='expense',
            amount=50.0,
            currency='CNY',
            category=category,
            date='2024-01-15'
        )
        assert entry.category == category

def test_entry_comparison():
    """测试Entry对象的比较（基于值而非引用）。"""
    import importlib.util
    import sys
    import os
    
    main_file_path = os.path.join(os.path.dirname(__file__), '..', 'Finance_Tracker_Fixed.py')
    spec = importlib.util.spec_from_file_location("finance_tracker", main_file_path)
    finance_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(finance_module)
    sys.modules['finance_tracker'] = finance_module
    
    # 创建两个相同的Entry
    entry1 = finance_module.Entry(
        entry_type='income',
        amount=100.0,
        currency='CNY',
        category='Salary',
        date='2024-01-15'
    )
    
    entry2 = finance_module.Entry(
        entry_type='income',
        amount=100.0,
        currency='CNY',
        category='Salary',
        date='2024-01-15'
    )
    
    # 验证它们的字典表示相同
    assert entry1.to_dict() == entry2.to_dict()
    
    # 但对象本身不同（除非实现__eq__方法）
    # 大多数dataclass会自动实现__eq__
    assert entry1 == entry2

def test_entry_default_values():
    """测试Entry的默认值。"""
    import importlib.util
    import sys
    import os
    
    main_file_path = os.path.join(os.path.dirname(__file__), '..', 'Finance_Tracker_Fixed.py')
    spec = importlib.util.spec_from_file_location("finance_tracker", main_file_path)
    finance_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(finance_module)
    sys.modules['finance_tracker'] = finance_module
    
    # 测试不提供invoice参数（应使用默认值None）
    entry = finance_module.Entry(
        entry_type='expense',
        amount=100.0,
        currency='CNY',
        category='Food',
        date='2024-01-15'
        # 不提供invoice
    )
    
    assert entry.invoice is None

def test_entry_invoice_types():
    """测试不同类型的发票。"""
    import importlib.util
    import sys
    import os
    
    main_file_path = os.path.join(os.path.dirname(__file__), '..', 'Finance_Tracker_Fixed.py')
    spec = importlib.util.spec_from_file_location("finance_tracker", main_file_path)
    finance_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(finance_module)
    sys.modules['finance_tracker'] = finance_module
    
    invoice_cases = [
        None,  # 无发票
        {'type': 'electronic', 'info': '电子发票123'},  # 电子发票
        {'type': 'paper', 'info': '纸质发票收据'},  # 纸质发票
        {'type': 'other', 'info': '其他类型凭证'},  # 其他类型
        {'type': 'electronic', 'info': '', 'number': 'INV-001'},  # 复杂结构
    ]
    
    for invoice in invoice_cases:
        entry = finance_module.Entry(
            entry_type='expense',
            amount=100.0,
            currency='CNY',
            category='Test',
            date='2024-01-15',
            invoice=invoice
        )
        
        assert entry.invoice == invoice

@pytest.mark.parametrize("entry_type,amount,currency,category,date", [
    ('income', 100.0, 'CNY', 'Salary', '2024-01-01'),
    ('expense', 50.0, 'USD', 'Food', '2024-01-02'),
    ('income', 0.01, 'EUR', 'Gift', '2024-12-31'),
    ('expense', 999999.99, 'JPY', 'Housing', '2024-06-15'),
])
def test_entry_parametrized(entry_type, amount, currency, category, date):
    """参数化测试Entry的不同组合。"""
    import importlib.util
    import sys
    import os
    
    main_file_path = os.path.join(os.path.dirname(__file__), '..', 'Finance_Tracker_Fixed.py')
    spec = importlib.util.spec_from_file_location("finance_tracker", main_file_path)
    finance_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(finance_module)
    sys.modules['finance_tracker'] = finance_module
    
    entry = finance_module.Entry(
        entry_type=entry_type,
        amount=amount,
        currency=currency,
        category=category,
        date=date
    )
    
    assert entry.entry_type == entry_type
    assert entry.amount == amount
    assert entry.currency == currency
    assert entry.category == category
    assert entry.date == date
