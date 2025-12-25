"""
FinanceController的集成测试 - 完整版
测试Controller与DataManager、View模拟的交互，覆盖所有主要功能。
"""

import pytest
import tempfile
import json
import sys
import os
from unittest.mock import Mock, patch, MagicMock, call

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 动态导入主模块
import importlib.util
main_file_path = os.path.join(os.path.dirname(__file__), '..', 'Finance_Tracker_Fixed.py')
spec = importlib.util.spec_from_file_location("finance_tracker", main_file_path)
finance_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(finance_module)
sys.modules['finance_tracker'] = finance_module

from Finance_Tracker_Fixed import FinanceController, DataManager, Entry, Plan, MainView


class TestControllerIntegrationComplete:
    """FinanceController完整集成测试类"""
    
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
        mock_view = Mock(spec=MainView)
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
        mock_view.update_chart = Mock()
        mock_view.ask_confirmation = Mock(return_value=True)
        mock_view.browse_file = Mock(return_value=None)
        mock_view.save_file = Mock(return_value=None)
        mock_view.ask_string = Mock(return_value="测试发票描述")
        mock_view.get_selected_entry_indices = Mock(return_value=[])
        return mock_view
    
    @pytest.fixture
    def mock_rate_view(self):
        """模拟ExchangeRateView组件。"""
        mock_view = Mock()
        mock_view.get_rates.return_value = {'USD': 7.5, 'EUR': 8.5, 'HKD': 0.95}
        mock_view.set_rates = Mock()
        mock_view.close = Mock()
        return mock_view
    
    @pytest.fixture
    def mock_plan_view(self):
        """模拟PlanView组件。"""
        mock_view = Mock()
        mock_view.get_plan_data.return_value = {
            'plan_type': 'monthly',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'spending_limit': 2000.0,
            'saving_goal': 1000.0
        }
        mock_view.get_selected_plan_index = Mock(return_value=0)
        mock_view.update_plans = Mock()
        mock_view.clear_form = Mock()
        mock_view.close = Mock()
        return mock_view

    # ==================== 核心功能测试 ====================

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

    # ==================== 完善待完成的测试 ====================

    def test_finance_analytics_integration(self, temp_json_file, mock_view):
        """测试财务分析功能集成（条形图和饼状图）。"""
        with patch('Finance_Tracker_Fixed.tk.Tk'), \
             patch('Finance_Tracker_Fixed.MainView', return_value=mock_view):
            
            controller = FinanceController()
            controller.data_manager = DataManager(file_path=temp_json_file)
            
            # 添加测试数据
            controller.data_manager.add_entry(Entry(
                entry_type='income',
                amount=3000.0,
                currency='CNY',
                category='Salary',
                date='2024-01-01'
            ))
            controller.data_manager.add_entry(Entry(
                entry_type='expense',
                amount=1000.0,
                currency='CNY',
                category='Food',
                date='2024-01-02'
            ))
            controller.data_manager.set_budget(500.0)
            
            # 测试条形图分析
            controller.bar_analytics()
            
            # 验证update_chart被调用，且参数正确
            mock_view.update_chart.assert_called_with('bar', {
                '总收入': 3000.0,
                '总支出': 1000.0,
                '预算': 500.0,
                '净收入': 1500.0  # 3000 - 1000 - 500 = 1500
            })
            
            # 重置mock，测试饼状图
            mock_view.update_chart.reset_mock()
            
            # 测试饼状图分析
            controller.pie_analytics()
            
            # 验证饼状图调用（应包含收入和支出）
            call_args = mock_view.update_chart.call_args
            assert call_args[0][0] == 'pie'
            chart_data = call_args[0][1]
            assert '收入' in chart_data
            assert '支出' in chart_data
            assert chart_data['收入'] == 3000.0
            assert chart_data['支出'] == 1000.0
    
    def test_plan_management_integration(self, temp_json_file, mock_view, mock_plan_view):
        """测试资金计划管理集成。"""
        with patch('Finance_Tracker_Fixed.tk.Tk'), \
             patch('Finance_Tracker_Fixed.MainView', return_value=mock_view), \
             patch('Finance_Tracker_Fixed.PlanView', return_value=mock_plan_view):
            
            controller = FinanceController()
            controller.data_manager = DataManager(file_path=temp_json_file)
            
            # 模拟打开计划管理窗口
            controller.manage_plans()
            
            # 验证PlanView被创建且初始数据已加载
            finance_module.PlanView.assert_called_once()
            mock_plan_view.update_plans.assert_called_once()
            
            # 测试添加计划
            controller.add_plan()
            
            # 验证计划被添加到DataManager
            plans = controller.data_manager.get_plans()
            assert len(plans) == 1
            assert plans[0]['plan_type'] == 'monthly'
            assert plans[0]['spending_limit'] == 2000.0
            assert plans[0]['saving_goal'] == 1000.0
            
            # 验证相关方法被调用
            mock_plan_view.update_plans.assert_called()  # 至少调用两次
            mock_plan_view.clear_form.assert_called_once()
            mock_view.show_message.assert_called_with("成功", "计划添加成功")
            
            # 测试删除计划
            controller.delete_plan()
            
            # 验证计划被删除
            plans = controller.data_manager.get_plans()
            assert len(plans) == 0
            mock_view.show_message.assert_called_with("成功", "计划删除成功")

    # ==================== 新增重要集成测试 ====================

    def test_exchange_rate_management_integration(self, temp_json_file, mock_view, mock_rate_view):
        """测试汇率管理功能集成。"""
        with patch('Finance_Tracker_Fixed.tk.Tk'), \
             patch('Finance_Tracker_Fixed.MainView', return_value=mock_view), \
             patch('Finance_Tracker_Fixed.ExchangeRateView', return_value=mock_rate_view):
            
            controller = FinanceController()
            controller.data_manager = DataManager(file_path=temp_json_file)
            
            # 模拟打开汇率管理窗口
            controller.manage_exchange_rates()
            
            # 验证ExchangeRateView被创建且初始数据已加载
            finance_module.ExchangeRateView.assert_called_once()
            mock_rate_view.set_rates.assert_called_with({'USD': 7.0, 'EUR': 8.0, 'CNY': 1.0})
            
            # 测试保存汇率
            controller.save_exchange_rates()
            
            # 验证汇率被更新
            rates = controller.data_manager.get_exchange_rates()
            assert rates['USD'] == 7.5
            assert rates['EUR'] == 8.5
            assert rates['HKD'] == 0.95
            
            # 验证相关方法被调用
            mock_rate_view.close.assert_called_once()
            mock_view.show_message.assert_called_with("成功", "汇率更新成功")
    
    def test_data_import_export_integration(self, temp_json_file, mock_view):
        """测试数据导入导出功能集成。"""
        with patch('Finance_Tracker_Fixed.tk.Tk'), \
             patch('Finance_Tracker_Fixed.MainView', return_value=mock_view):
            
            controller = FinanceController()
            controller.data_manager = DataManager(file_path=temp_json_file)
            
            # 创建一个临时导入文件
            import_data = {
                'entries': [
                    {
                        'entry_type': 'income',
                        'amount': 5000.0,
                        'currency': 'CNY',
                        'category': 'Salary',
                        'date': '2024-02-01'
                    }
                ],
                'budget': 3000.0,
                'exchange_rates': {'USD': 7.2, 'EUR': 8.2},
                'plans': []
            }
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(import_data, f, ensure_ascii=False, indent=2)
                import_path = f.name
            
            try:
                # 模拟文件选择对话框返回导入文件路径
                mock_view.browse_file.return_value = import_path
                
                # 执行导入
                controller.import_data()
                
                # 验证数据被正确导入
                entries = controller.data_manager.get_entries()
                assert len(entries) == 1
                assert entries[0]['entry_type'] == 'income'
                assert entries[0]['amount'] == 5000.0
                
                budget = controller.data_manager.get_budget()
                assert budget == 3000.0
                
                rates = controller.data_manager.get_exchange_rates()
                assert rates['USD'] == 7.2
                
                # 验证成功消息
                mock_view.show_message.assert_called_with("成功", "数据导入成功")
                
            finally:
                # 清理临时文件
                try:
                    os.unlink(import_path)
                except FileNotFoundError:
                    pass
    
    def test_data_save_as_integration(self, temp_json_file, mock_view):
        """测试另存为功能集成。"""
        with patch('Finance_Tracker_Fixed.tk.Tk'), \
             patch('Finance_Tracker_Fixed.MainView', return_value=mock_view):
            
            controller = FinanceController()
            controller.data_manager = DataManager(file_path=temp_json_file)
            
            # 添加一些测试数据
            controller.data_manager.add_entry(Entry(
                entry_type='income',
                amount=1000.0,
                currency='CNY',
                category='Salary',
                date='2024-01-01'
            ))
            
            # 创建临时目标文件路径
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
                save_path = f.name
            
            try:
                # 模拟文件保存对话框返回目标路径
                mock_view.save_file.return_value = save_path
                
                # 执行另存为
                controller.save_as_data()
                
                # 验证文件被创建且包含正确数据
                assert os.path.exists(save_path)
                
                with open(save_path, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                
                assert 'entries' in saved_data
                assert len(saved_data['entries']) == 1
                assert saved_data['entries'][0]['amount'] == 1000.0
                
                # 验证成功消息
                mock_view.show_message.assert_called()
                call_args = mock_view.show_message.call_args
                assert call_args[0][0] == "成功"
                assert "账本已保存到:" in call_args[0][1]
                
            finally:
                # 清理临时文件
                try:
                    os.unlink(save_path)
                except FileNotFoundError:
                    pass
    
    def test_entry_validation_integration(self, temp_json_file, mock_view):
        """测试账目数据验证功能集成。"""
        with patch('Finance_Tracker_Fixed.tk.Tk'), \
             patch('Finance_Tracker_Fixed.MainView', return_value=mock_view):
            
            controller = FinanceController()
            controller.data_manager = DataManager(file_path=temp_json_file)
            
            # 测试1: 无效金额（负数）
            mock_view.get_entry_data.return_value = {
                'type': 'income',
                'amount': -100.0,  # 无效金额
                'currency': 'CNY',
                'category': 'Salary',
                'date': '2024-01-15',
                'invoice_type': 'none',
                'invoice_info': ''
            }
            
            controller.record_entry()
            mock_view.show_message.assert_called_with("错误", "金额必须大于0", "error")
            
            # 测试2: 无效日期格式
            mock_view.show_message.reset_mock()
            mock_view.get_entry_data.return_value = {
                'type': 'income',
                'amount': 100.0,
                'currency': 'CNY',
                'category': 'Salary',
                'date': '2024/01/15',  # 无效格式
                'invoice_type': 'none',
                'invoice_info': ''
            }
            
            controller.record_entry()
            mock_view.show_message.assert_called_with("错误", "日期格式必须为 YYYY-MM-DD", "error")
            
            # 测试3: 有发票类型但无发票信息
            mock_view.show_message.reset_mock()
            mock_view.get_entry_data.return_value = {
                'type': 'expense',
                'amount': 100.0,
                'currency': 'CNY',
                'category': 'Food',
                'date': '2024-01-15',
                'invoice_type': 'electronic',  # 有发票类型
                'invoice_info': ''  # 但无发票信息
            }
            
            controller.record_entry()
            mock_view.show_message.assert_called_with("错误", "请提供发票信息", "error")
    
    def test_invoice_management_integration(self, temp_json_file, mock_view):
        """测试发票管理功能集成。"""
        with patch('Finance_Tracker_Fixed.tk.Tk'), \
             patch('Finance_Tracker_Fixed.MainView', return_value=mock_view):
            
            controller = FinanceController()
            controller.data_manager = DataManager(file_path=temp_json_file)
            
            # 测试电子发票浏览
            mock_view.invoice_type_var.get.return_value = 'electronic'
            mock_view.browse_file.return_value = '/path/to/invoice.pdf'
            
            controller.browse_invoice_file()
            
            mock_view.browse_file.assert_called_with(
                "选择电子发票文件", [("All files", "*.*")]
            )
            mock_view.invoice_desc_var.set.assert_called_with('/path/to/invoice.pdf')
            
            # 测试纸质发票描述输入
            mock_view.invoice_type_var.get.return_value = 'paper'
            mock_view.ask_string.return_value = '纸质发票编号: 20240115001'
            
            controller.browse_invoice_file()
            
            mock_view.ask_string.assert_called_with("纸质发票描述", "请输入发票描述:")
            mock_view.invoice_desc_var.set.assert_called_with('纸质发票编号: 20240115001')
    
    def test_error_handling_integration(self, temp_json_file, mock_view):
        """测试错误处理场景集成。"""
        with patch('Finance_Tracker_Fixed.tk.Tk'), \
             patch('Finance_Tracker_Fixed.MainView', return_value=mock_view):
            
            controller = FinanceController()
            controller.data_manager = DataManager(file_path=temp_json_file)
            
            # 模拟文件保存失败
            with patch.object(controller.data_manager, 'save_data', return_value=False):
                # 测试记录条目时保存失败
                mock_view.get_entry_data.return_value = {
                    'type': 'income',
                    'amount': 1000.0,
                    'currency': 'CNY',
                    'category': 'Salary',
                    'date': '2024-01-15',
                    'invoice_type': 'none',
                    'invoice_info': ''
                }
                
                controller.record_entry()
                mock_view.show_message.assert_called_with("错误", "保存失败", "error")
            
            # 模拟删除时无选中条目
            mock_view.get_selected_entry_indices.return_value = []
            controller.delete_entries()
            mock_view.show_message.assert_called_with("警告", "请先选择要删除的账目", "warning")


def test_comprehensive_mvc_integration():
    """全面的MVC集成测试，模拟完整用户工作流。"""
    # 这个测试可以模拟一个完整的用户操作流程
    pass


if __name__ == "__main__":
    # 可以直接运行此文件进行集成测试
    pytest.main([__file__, "-v"])
