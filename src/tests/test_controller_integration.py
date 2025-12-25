"""
FinanceController的集成测试。
测试Controller与DataManager、View模拟的交互。
"""

import pytest
import tempfile
import json
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 动态导入主模块
import importlib.util
main_file_path = os.path.join(os.path.dirname(__file__), '..', 'Finance_Tracker_Fixed.py')
spec = importlib.util.spec_from_file_location("finance_tracker", main_file_path)
finance_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(finance_module)
sys.modules['finance_tracker'] = finance_module

from Finance_Tracker_Fixed import FinanceController, DataManager, Entry, Plan


class TestControllerIntegration:
    """FinanceController集成测试类"""
    
    @pytest.fixture
    def temp_json_file(self):
        """创建临时JSON文件。"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            # 写入初始测试数据
            test_data = {
                'entries': [],
                'budget': 0.0,
                'exchange_rates': {'USD': 7.0, 'EUR': 8.0, 'CNY': 1.0},
                'plans': []
            }
            json.dump(test_data, f, ensure_ascii=False, indent=2)
            temp_path = f.name
        
        yield temp_path
        
        # 清理
        try:
            os.unlink(temp_path)
        except FileNotFoundError:
            pass
    
    @pytest.fixture
    def mock_view(self):
        """模拟MainView组件。"""
        mock_view = Mock()
        mock_view.get_entry_data.return_value = {
            'type': 'income',
            'amount': 1000.0,
            'currency': 'CNY',
            'category': 'Salary',
            'date': '2024-01-15',
            'invoice_type': 'none',
            'invoice_info': ''
        }
        mock_view.entry_type_var = Mock()
        mock_view.amount_var = Mock()
        mock_view.currency_var = Mock()
        mock_view.category_var = Mock()
        mock_view.invoice_type_var = Mock()
        mock_view.invoice_desc_var = Mock()
        mock_view.budget_var = Mock()
        mock_view._date_entry = Mock()
        mock_view._treeview = Mock()
        mock_view.show_message = Mock()
        mock_view.clear_entry_fields = Mock()
        mock_view.update_treeview = Mock()
        mock_view.ask_confirmation = Mock(return_value=True)
        return mock_view
    
    def test_controller_record_entry_integration(self, temp_json_file, mock_view):
        """测试控制器记录条目的完整流程。"""
        # 创建控制器，但跳过GUI初始化
        with patch('Finance_Tracker_Fixed.tk.Tk'), \
             patch('Finance_Tracker_Fixed.MainView', return_value=mock_view):
            
            # 首先创建一个使用临时文件的DataManager实例
            data_manager = DataManager(file_path=temp_json_file)
            # 模拟DataManager的初始化，使其返回我们创建的实例
            with patch('Finance_Tracker_Fixed.DataManager', return_value=data_manager):
                # 创建控制器实例，此时它的data_manager将使用临时文件
                controller = FinanceController()
                # 注意：此时控制器的data_manager已经是我们创建的实例，不需要再替换

            # 重置update_treeview的调用计数，忽略初始化时的调用
            mock_view.update_treeview.reset_mock()

            # 模拟输入数据
            input_data = {
                'type': 'income',
                'amount': 1000.0,
                'currency': 'CNY',
                'category': 'Salary',
                'date': '2024-01-15',
                'invoice_type': 'none',
                'invoice_info': ''
            }
            mock_view.get_entry_data.return_value = input_data

            # 初始条目数（临时文件初始为空）
            initial_count = len(controller.data_manager.get_entries())

            # 执行记录条目操作
            controller.record_entry()

            # 验证结果
            entries = controller.data_manager.get_entries()
            assert len(entries) == initial_count + 1

            # 验证新条目的属性
            new_entry = entries[-1]
            assert new_entry['entry_type'] == 'income'
            assert new_entry['amount'] == 1000.0
            assert new_entry['currency'] == 'CNY'
            assert new_entry['category'] == 'Salary'
            assert new_entry['date'] == '2024-01-15'

            # 验证视图方法被调用
            mock_view.show_message.assert_called_with("成功", "账目记录成功")
            mock_view.clear_entry_fields.assert_called_once()
            # 现在，update_treeview应该只被调用了一次（在record_entry中）
            mock_view.update_treeview.assert_called_once()
            # 并且检查调用参数
            call_args = mock_view.update_treeview.call_args
            # 检查参数中的条目列表长度是否为1（只有新添加的条目）
            assert len(call_args[0][0]) == 1
            assert call_args[0][0][0]['entry_type'] == 'income'

    
    def test_controller_budget_management_integration(self, temp_json_file, mock_view):
        """测试控制器预算管理流程。"""
        with patch('Finance_Tracker_Fixed.tk.Tk'), \
             patch('Finance_Tracker_Fixed.MainView', return_value=mock_view):
            
            controller = FinanceController()
            controller.data_manager = DataManager(file_path=temp_json_file)
            
            # 设置预算
            mock_view.budget_var.get.return_value = 5000.0
            controller.set_budget()
            
            # 验证预算设置成功
            assert controller.data_manager.get_budget() == 5000.0
            mock_view.show_message.assert_called_with("成功", "预算设置成功")
    
    def test_controller_delete_entries_integration(self, temp_json_file, mock_view):
        """测试控制器删除条目的流程。"""
        with patch('Finance_Tracker_Fixed.tk.Tk'), \
             patch('Finance_Tracker_Fixed.MainView', return_value=mock_view):
            
            controller = FinanceController()
            controller.data_manager = DataManager(file_path=temp_json_file)
            
            # 先添加几个测试条目
            entry1 = Entry(
                entry_type='income',
                amount=1000.0,
                currency='CNY',
                category='Salary',
                date='2024-01-15'
            )
            entry2 = Entry(
                entry_type='expense',
                amount=200.0,
                currency='CNY',
                category='Food',
                date='2024-01-16'
            )
            controller.data_manager.add_entry(entry1)
            controller.data_manager.add_entry(entry2)
            controller.data_manager.save_data()
            
            # 模拟选择第一个条目
            mock_view.get_selected_entry_indices.return_value = [0]
            
            # 执行删除
            controller.delete_entries()
            
            # 验证删除结果
            entries = controller.data_manager.get_entries()
            assert len(entries) == 1  # 应该只剩下一个条目
            assert entries[0]['entry_type'] == 'expense'  # 第一个income被删除
    
    def test_controller_calculate_totals_integration(self, temp_json_file, mock_view):
        """测试控制器财务计算功能。"""
        with patch('Finance_Tracker_Fixed.tk.Tk'), \
             patch('Finance_Tracker_Fixed.MainView', return_value=mock_view):
            
            controller = FinanceController()
            controller.data_manager = DataManager(file_path=temp_json_file)
            
            # 添加测试数据
            controller.data_manager.add_entry(Entry(
                entry_type='income',
                amount=5000.0,
                currency='CNY',
                category='Salary',
                date='2024-01-01'
            ))
            controller.data_manager.add_entry(Entry(
                entry_type='expense',
                amount=1000.0,
                currency='USD',
                category='Food',
                date='2024-01-02'
            ))
            controller.data_manager.set_budget(2000.0)
            
            # 计算统计
            totals = controller.calculate_totals()
            
            # 验证计算结果
            assert 'total_income' in totals
            assert 'total_expenses' in totals
            assert 'budget' in totals
            assert 'net_income' in totals
            
            # 具体验证（USD转换为CNY的汇率是7.0）
            # total_income = 5000 CNY
            # total_expenses = 1000 USD * 7.0 = 7000 CNY
            # budget = 2000 CNY
            # net_income = 5000 - 7000 - 2000 = -4000 CNY
            assert totals['total_income'] == 5000.0
            assert totals['total_expenses'] == 7000.0
            assert totals['budget'] == 2000.0
            assert totals['net_income'] == -4000.0


def test_finance_analytics_integration():
    """测试财务分析功能集成。"""
    # 这里可以测试条形图和饼状图的分析功能
    pass


def test_plan_management_integration():
    """测试资金计划管理集成。"""
    # 测试计划的添加、删除和显示
    pass
