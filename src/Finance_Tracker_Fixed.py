"""
Finance Tracker Application - Optimized Version
Author: Li Yujiang
Student ID: 231220013
Date: 2025/10/24
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
from matplotlib.font_manager import FontProperties

matplotlib.use('TkAgg')

# ==================== 字体设置模块优化 ====================
def setup_chinese_font() -> bool:
    """
    设置 matplotlib 中文字体支持。
    
    Returns:
        bool: 字体设置是否成功
    """
    try:
        # Windows 系统字体路径
        font_path = 'C:/Windows/Fonts/simhei.ttf'
        
        if os.path.exists(font_path):
            custom_font = FontProperties(fname=font_path)
            plt.rcParams['font.family'] = custom_font.get_name()
            return True
        
        # macOS 或 Linux 备选方案
        plt.rcParams['font.sans-serif'] = [
            'Arial Unicode MS', 'SimHei', 'Microsoft YaHei'
        ]
        plt.rcParams['axes.unicode_minus'] = False
        return False
        
    except (OSError, FileNotFoundError) as e:
        print(f"字体设置失败: {e}")
        return False

# 执行字体设置
if not setup_chinese_font():
    print("可能需要手动安装中文字体")

# ==================== MODEL LAYER ====================
@dataclass
class Entry:
    """账目实体类"""
    entry_type: str
    amount: float
    currency: str
    category: str
    date: str
    invoice: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """将 Entry 对象转换为字典。"""
        return asdict(self)


@dataclass
class Plan:
    """资金计划实体类"""
    plan_type: str
    start_date: str
    end_date: str
    spending_limit: float
    saving_goal: float

    def to_dict(self) -> Dict[str, Any]:
        """将 Plan 对象转换为字典。"""
        return asdict(self)


class DataManager:
    """数据管理类"""
    def __init__(self, file_path: str = 'finance_data.json'):
        """初始化数据管理器。"""
        self.file_path = file_path
        self.logger = self._setup_logger()

        self.data = {
            'entries': [],
            'budget': 0.0,
            'exchange_rates': {
                'USD': 7.0,
                'EUR': 8.0,
                'HKD': 0.9,
                'CNY': 1.0
            },
            'plans': []
        }
        self.load_data()

    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器。"""
        logger = logging.getLogger('FinanceTracker')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def load_data(self) -> bool:
        """从文件加载数据。"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    loaded_data = json.load(file)
                    if 'entries' in loaded_data:
                        for entry in loaded_data['entries']:
                            # 兼容性处理
                            if 'type' in entry and 'entry_type' not in entry:
                                entry['entry_type'] = entry.pop('type')
                self.data.update(loaded_data)
                self.logger.info("数据加载成功: %s", self.file_path)
                return True
            self.logger.info("未找到数据文件，使用默认数据")
            return False
        except (IOError, json.JSONDecodeError) as e:
            self.logger.error("数据加载失败: %s", str(e))
            return False

    def save_data(self) -> bool:
        """保存数据到文件。"""
        try:
            directory = os.path.dirname(self.file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump(self.data, file, indent=2, ensure_ascii=False)
            self.logger.info("数据保存成功: %s", self.file_path)
            return True
        except (IOError, PermissionError) as e:
            self.logger.error("数据保存失败: %s", str(e))
            return False

    def save_as(self, new_file_path: str) -> bool:
        """将数据另存为新文件。"""
        original_path = self.file_path
        self.file_path = new_file_path

        if self.save_data():
            return True
        self.file_path = original_path
        return False

    def import_data(self, import_file_path: str) -> bool:
        """从其他文件导入数据。"""
        try:
            with open(import_file_path, 'r', encoding='utf-8') as file:
                imported_data = json.load(file)

            if 'entries' in imported_data:
                for entry in imported_data['entries']:
                    if 'type' in entry and 'entry_type' not in entry:
                        entry['entry_type'] = entry.pop('type')

            self.data.update(imported_data)
            self.file_path = import_file_path

            if self.save_data():
                self.logger.info("数据导入成功: %s", import_file_path)
                return True
            return False
        except (IOError, json.JSONDecodeError) as e:
            self.logger.error("数据导入失败: %s", str(e))
            return False

    def add_entry(self, entry: Entry) -> None:
        """添加账目条目。"""
        self.data['entries'].append(entry.to_dict())

    def delete_entries(self, indices: List[int]) -> None:
        """删除指定索引的账目。"""
        for index in sorted(indices, reverse=True):
            if 0 <= index < len(self.data['entries']):
                del self.data['entries'][index]

    def get_entries(self) -> List[Dict[str, Any]]:
        """获取所有账目。"""
        return self.data['entries']

    def set_budget(self, budget: float) -> None:
        """设置预算。"""
        self.data['budget'] = budget

    def get_budget(self) -> float:
        """获取预算。"""
        return self.data.get('budget', 0.0)

    def set_exchange_rates(self, rates: Dict[str, float]) -> None:
        """设置汇率。"""
        self.data['exchange_rates'] = rates

    def get_exchange_rates(self) -> Dict[str, float]:
        """获取汇率。"""
        return self.data.get('exchange_rates', {})

    def add_plan(self, plan: Plan) -> None:
        """添加资金计划。"""
        self.data['plans'].append(plan.to_dict())

    def delete_plan(self, index: int) -> None:
        """删除指定索引的资金计划。"""
        if 0 <= index < len(self.data['plans']):
            del self.data['plans'][index]

    def get_plans(self) -> List[Dict[str, Any]]:
        """获取所有资金计划。"""
        return self.data.get('plans', [])


# ==================== VIEW LAYER ====================
class BaseView(ABC):
    """视图基类"""
    @abstractmethod
    def create_widgets(self):
        """创建界面组件。"""

    @abstractmethod
    def update_display(self):
        """更新显示。"""


class MainView(BaseView):
    """主视图类"""
    def __init__(self, root, controller):
        """初始化主视图。"""
        self.root = root
        self.controller = controller
        
        # 初始化所有属性
        self.entry_type_var = tk.StringVar(value="Income")
        self.amount_var = tk.DoubleVar(value=0.0)
        self.currency_var = tk.StringVar(value='CNY')
        self.category_var = tk.StringVar(value='Salary')
        self.invoice_type_var = tk.StringVar(value='none')
        self.invoice_desc_var = tk.StringVar()
        self.budget_var = tk.DoubleVar(value=0.0)
        
        # 图表相关属性
        self._fig, self._ax = plt.subplots(figsize=(6, 4), tight_layout=True)
        self._canvas = None
        self._canvas_widget = None
        
        # 界面元素
        self._date_entry = None
        self._treeview = None
        
        self.root.title("Finance Tracker")
        self.root.geometry("1200x800")
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

        self._configure_styles()
        self.create_widgets()
        if self._date_entry:
            self._date_entry.set_date(datetime.now())

    def _configure_styles(self):
        """配置界面样式。"""
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('Title.TLabel',
                       font=('Arial', 14, 'bold'), foreground='navy')
        style.configure('TEntry', padding=5)
        style.configure('TCombobox', padding=5)

    def create_widgets(self):
        """创建界面组件。"""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(1, weight=1)
        main_container.rowconfigure(2, weight=1)

        title_text = "个人记账本"
        title_label = ttk.Label(main_container, text=title_text,
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        input_frame = self._create_input_frame(main_container)
        input_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))

        chart_frame = self._create_chart_frame(main_container)
        chart_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0))

        data_frame = self._create_data_frame(main_container)
        data_frame.grid(row=2, column=0, columnspan=2,
                       sticky="nsew", pady=(10, 0))

    def _create_input_frame(self, parent) -> ttk.LabelFrame:
        """创建输入框架。"""
        frame = ttk.LabelFrame(parent, text="账目录入", padding="10")
        frame.columnconfigure(1, weight=1)
        
        self._create_input_widgets(frame)
        return frame

    def _create_input_widgets(self, frame: ttk.LabelFrame):
        """创建输入框架中的各个组件。"""
        # 账目类型
        ttk.Label(frame, text="账目类型:").grid(
            row=0, column=0, sticky="w", pady=2)
        entry_types = ["Income", "Expense"]
        combo = ttk.Combobox(frame, textvariable=self.entry_type_var,
                            values=entry_types, state="readonly")
        combo.grid(row=0, column=1, sticky="ew", pady=2)

        # 金额
        ttk.Label(frame, text="金额:").grid(
            row=1, column=0, sticky="w", pady=2)
        spinbox = ttk.Spinbox(frame, textvariable=self.amount_var,
                             from_=0, to=float('inf'), increment=1)
        spinbox.grid(row=1, column=1, sticky="ew", pady=2)

        # 货币类型
        ttk.Label(frame, text="货币类型:").grid(
            row=2, column=0, sticky="w", pady=2)
        currencies = ['CNY', 'USD', 'EUR', 'HKD']
        combo = ttk.Combobox(frame, textvariable=self.currency_var,
                            values=currencies, state="readonly")
        combo.grid(row=2, column=1, sticky="ew", pady=2)

        # 类别
        ttk.Label(frame, text="类别:").grid(
            row=3, column=0, sticky="w", pady=2)
        categories = [
            "Salary", "Food", "Housing", "Transportation",
            "Medical", "Clothes & Cosmetics", "Hobby", "Education", "Gift"
        ]
        combo = ttk.Combobox(frame, textvariable=self.category_var,
                            values=categories, state="readonly")
        combo.grid(row=3, column=1, sticky="ew", pady=2)

        # 日期
        ttk.Label(frame, text="日期:").grid(
            row=4, column=0, sticky="w", pady=2)
        self._date_entry = DateEntry(frame, date_pattern="yyyy-mm-dd")
        self._date_entry.grid(row=4, column=1, sticky="ew", pady=2)

        # 发票类型
        ttk.Label(frame, text="发票类型:").grid(
            row=5, column=0, sticky="w", pady=2)
        invoice_types = ['none', 'electronic', 'paper']
        combo = ttk.Combobox(frame, textvariable=self.invoice_type_var,
                            values=invoice_types, state="readonly")
        combo.grid(row=5, column=1, sticky="ew", pady=2)

        # 发票信息
        ttk.Label(frame, text="发票信息:").grid(
            row=6, column=0, sticky="w", pady=2)
        entry = ttk.Entry(frame, textvariable=self.invoice_desc_var)
        entry.grid(row=6, column=1, sticky="ew", pady=2)
        button = ttk.Button(frame, text="浏览",
                           command=self.controller.browse_invoice_file)
        button.grid(row=6, column=2, padx=(5, 0))

        # 按钮框架
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=10)

        add_btn = ttk.Button(button_frame, text="添加记账",
                            command=self.controller.record_entry)
        add_btn.pack(side="left", padx=(0, 5))

        delete_btn = ttk.Button(button_frame, text="删除选中",
                               command=self.controller.delete_entries)
        delete_btn.pack(side="left")

        # 月度预算
        ttk.Label(frame, text="月度预算:").grid(
            row=8, column=0, sticky="w", pady=2)
        budget_spin = ttk.Spinbox(frame, textvariable=self.budget_var,
                                 from_=0, to=float('inf'), increment=100)
        budget_spin.grid(row=8, column=1, sticky="ew", pady=2)

        set_budget_btn = ttk.Button(frame, text="设置预算",
                                   command=self.controller.set_budget)
        set_budget_btn.grid(row=9, column=0, columnspan=2, pady=5)

    def _create_chart_frame(self, parent) -> ttk.LabelFrame:
        """创建图表框架。"""
        frame = ttk.LabelFrame(parent, text="数据统计", padding="10")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=0)

        # 图表组件
        self._canvas = FigureCanvasTkAgg(self._fig, master=frame)
        self._canvas_widget = self._canvas.get_tk_widget()
        self._canvas_widget.grid(row=0, column=0, sticky="nsew")

        # 按钮框架
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=1, column=0, pady=(10, 0))

        bar_btn = ttk.Button(button_frame, text="条形图统计",
                            command=self.controller.bar_analytics)
        bar_btn.pack(side="left", padx=(0, 5))

        pie_btn = ttk.Button(button_frame, text="饼状图统计",
                            command=self.controller.pie_analytics)
        pie_btn.pack(side="left")

        return frame

    def _create_data_frame(self, parent) -> ttk.LabelFrame:
        """创建数据显示框架。"""
        frame = ttk.LabelFrame(parent, text="账目列表", padding="10")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        # 工具栏
        toolbar = ttk.Frame(frame)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        btn_texts = [
            ("导入账本", self.controller.import_data),
            ("另存为", self.controller.save_as_data),
            ("保存账本", self.controller.save_data),
            ("管理汇率", self.controller.manage_exchange_rates),
            ("资金计划", self.controller.manage_plans),
            ("保存并退出", self.controller.quit_app)
        ]

        for text, command in btn_texts:
            btn = ttk.Button(toolbar, text=text, command=command)
            btn.pack(side="left", padx=(0, 5))

        # 树形视图
        columns = ("序号", "类型", "金额", "货币", "类别", "日期", "发票信息")
        self._treeview = ttk.Treeview(frame, columns=columns,
                                     show="headings", height=12)

        for col in columns:
            self._treeview.heading(col, text=col)
            self._treeview.column(col, width=100)

        self._treeview.grid(row=1, column=0, sticky="nsew")

        # 滚动条
        scrollbar = ttk.Scrollbar(frame, orient="vertical",
                                 command=self._treeview.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self._treeview.configure(yscrollcommand=scrollbar.set)

        return frame

    def on_window_close(self):
        """窗口关闭事件处理。"""
        self.controller.quit_app()

    def update_display(self):
        """更新显示。"""
        # 实现根据需要更新显示
        pass

    def get_entry_data(self) -> Dict[str, Any]:
        """获取输入框中的数据。"""
        return {
            'type': self.entry_type_var.get().lower(),
            'amount': self.amount_var.get(),
            'currency': self.currency_var.get(),
            'category': self.category_var.get(),
            'date': self._date_entry.get() if self._date_entry else '',
            'invoice_type': self.invoice_type_var.get(),
            'invoice_info': self.invoice_desc_var.get()
        }

    def clear_entry_fields(self):
        """清空输入框。"""
        self.entry_type_var.set("Income")
        self.amount_var.set(0.0)
        self.currency_var.set('CNY')
        self.category_var.set('Salary')
        if self._date_entry:
            self._date_entry.set_date(datetime.now())
        self.invoice_type_var.set('none')
        self.invoice_desc_var.set('')

    def get_selected_entry_indices(self) -> List[int]:
        """获取选中的条目索引。"""
        selected = self._treeview.selection()
        return [self._treeview.index(item) for item in selected]

    def update_treeview(self, entries: List[Dict[str, Any]]):
        """更新树形视图。"""
        self._treeview.delete(*self._treeview.get_children())

        for i, entry in enumerate(entries):
            invoice_info = entry.get('invoice', {})
            invoice_display = "无"
            if invoice_info:
                invoice_type = invoice_info.get('type', '')
                invoice_detail = invoice_info.get('info', '')
                invoice_display = f"{invoice_type}: {invoice_detail}"

            entry_type = entry.get('entry_type', '')
            if not entry_type and 'type' in entry:
                entry_type = entry['type']

            values = (
                f"{i + 1}",
                entry_type.capitalize() if entry_type else '',
                f"{entry['amount']:.2f}",
                entry.get('currency', 'CNY'),
                entry['category'],
                entry['date'],
                invoice_display
            )
            self._treeview.insert("", "end", values=values)

    def update_chart(self, chart_type: str, data: Dict[str, Any]):
        """更新图表。"""
        self._ax.clear()

        if chart_type == 'bar':
            categories = list(data.keys())
            values = list(data.values())
            color_list = ['green', 'red', 'purple', 'blue'][:len(categories)]

            bars = self._ax.bar(categories, values, color=color_list)
            self._ax.set_ylabel('金额 (CNY)')
            self._ax.set_title('财务统计')

            for bar_item, value in zip(bars, values):
                self._ax.text(bar_item.get_x() + bar_item.get_width()/2,
                             bar_item.get_height(), f'{value:.2f}',
                             ha='center', va='bottom')

        elif chart_type == 'pie':
            filtered_data = {k: v for k, v in data.items() if v > 0}
            if not filtered_data:
                self._ax.text(0.5, 0.5, '暂无数据', ha='center', va='center',
                             transform=self._ax.transAxes, fontsize=12)
                self._ax.set_title('收入/支出占比')
            else:
                categories = list(filtered_data.keys())
                values = list(filtered_data.values())
                color_list = ['#4CAF50', '#F44336', '#FF9800',
                             '#2196F3'][:len(categories)]

                _, _, autotexts = self._ax.pie(
                    values,
                    labels=categories,
                    autopct='%1.1f%%',
                    colors=color_list,
                    startangle=90
                )
                self._ax.set_title('收入/支出占比')

                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')

        self._canvas.draw()

    def show_message(self, title: str, message: str, message_type: str = "info"):
        """显示消息对话框。"""
        if message_type == "info":
            messagebox.showinfo(title, message)
        elif message_type == "warning":
            messagebox.showwarning(title, message)
        elif message_type == "error":
            messagebox.showerror(title, message)

    def ask_confirmation(self, title: str, message: str) -> bool:
        """显示确认对话框。"""
        return messagebox.askyesno(title, message)

    def browse_file(self, title: str, filetypes: List[tuple]) -> str:
        """打开文件选择对话框。"""
        return filedialog.askopenfilename(title=title, filetypes=filetypes)

    def save_file(self, title: str, filetypes: List[tuple]) -> str:
        """打开文件保存对话框。"""
        return filedialog.asksaveasfilename(
            title=title,
            filetypes=filetypes,
            defaultextension=".json"
        )

    def ask_string(self, title: str, prompt: str) -> str:
        """显示字符串输入对话框。"""
        return simpledialog.askstring(title, prompt)


class ExchangeRateView:
    """汇率管理视图"""
    def __init__(self, parent, controller):
        """初始化汇率管理视图。"""
        self.window = tk.Toplevel(parent)
        self.controller = controller
        self.window.title("管理汇率")
        self.window.geometry("300x200")
        self.window.transient(parent)
        self.window.grab_set()

        self.rate_vars = {}
        self.create_widgets()

    def create_widgets(self):
        """创建界面组件。"""
        self.window.columnconfigure(1, weight=1)

        title = ttk.Label(self.window,
                         text="汇率管理（基准货币: CNY）",
                         style='Title.TLabel')
        title.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        row = 1
        currencies = ['USD', 'EUR', 'HKD']

        for currency in currencies:
            ttk.Label(self.window, text=f"{currency}:").grid(
                row=row, column=0, sticky="w", pady=2)
            rate_var = tk.DoubleVar()
            ttk.Entry(self.window, textvariable=rate_var).grid(
                row=row, column=1, sticky="ew", pady=2)
            self.rate_vars[currency] = rate_var
            row += 1

        button_frame = ttk.Frame(self.window)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)

        save_btn = ttk.Button(button_frame, text="保存",
                             command=self.controller.save_exchange_rates)
        save_btn.pack(side="left", padx=(0, 5))

        cancel_btn = ttk.Button(button_frame, text="取消",
                               command=self.window.destroy)
        cancel_btn.pack(side="left")

    def set_rates(self, rates: Dict[str, float]):
        """设置汇率显示。"""
        for currency, rate in rates.items():
            if currency in self.rate_vars:
                self.rate_vars[currency].set(rate)

    def get_rates(self) -> Dict[str, float]:
        """获取输入的汇率。"""
        return {currency: var.get() for currency, var in self.rate_vars.items()}

    def close(self):
        """关闭窗口。"""
        self.window.destroy()


class PlanView:
    """资金计划管理视图"""
    def __init__(self, parent, controller):
        """初始化资金计划管理视图。"""
        self.window = tk.Toplevel(parent)
        self.controller = controller
        self.window.title("资金计划管理")
        self.window.geometry("600x500")
        self.window.transient(parent)
        self.window.grab_set()

        self._create_variables()
        self._treeview = None
        self._start_date_entry = None
        self._end_date_entry = None
        self.create_widgets()

    def _create_variables(self):
        """创建界面变量。"""
        self.plan_type_var = tk.StringVar(value='monthly')
        self.spending_limit_var = tk.DoubleVar()
        self.saving_goal_var = tk.DoubleVar()

    def create_widgets(self):
        """创建界面组件。"""
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)

        columns = ("类型", "开始日期", "结束日期", "花费限额", "省钱目标")
        self._treeview = ttk.Treeview(self.window, columns=columns,
                                     show="headings", height=8)

        for col in columns:
            self._treeview.heading(col, text=col)

        self._treeview.grid(row=0, column=0, columnspan=2,
                           sticky="nsew", pady=(0, 10))

        scrollbar = ttk.Scrollbar(self.window, orient="vertical",
                                 command=self._treeview.yview)
        scrollbar.grid(row=0, column=2, sticky="ns")
        self._treeview.configure(yscrollcommand=scrollbar.set)

        form_frame = ttk.LabelFrame(self.window, text="添加新计划", padding="10")
        form_frame.grid(row=1, column=0, columnspan=2,
                       sticky="ew", pady=(0, 10))
        form_frame.columnconfigure(1, weight=1)

        row = 0

        # 计划类型
        ttk.Label(form_frame, text="计划类型:").grid(
            row=row, column=0, sticky="w", pady=2)
        combo = ttk.Combobox(form_frame, textvariable=self.plan_type_var,
                            values=['yearly', 'monthly', 'weekly'],
                            state="readonly")
        combo.grid(row=row, column=1, sticky="ew", pady=2)
        row += 1

        # 开始日期
        ttk.Label(form_frame, text="开始日期:").grid(
            row=row, column=0, sticky="w", pady=2)
        self._start_date_entry = DateEntry(form_frame, date_pattern="yyyy-mm-dd")
        self._start_date_entry.grid(row=row, column=1, sticky="ew", pady=2)
        row += 1

        # 结束日期
        ttk.Label(form_frame, text="结束日期:").grid(
            row=row, column=0, sticky="w", pady=2)
        self._end_date_entry = DateEntry(form_frame, date_pattern="yyyy-mm-dd")
        self._end_date_entry.grid(row=row, column=1, sticky="ew", pady=2)
        row += 1

        # 花费限额
        ttk.Label(form_frame, text="花费限额:").grid(
            row=row, column=0, sticky="w", pady=2)
        limit_entry = ttk.Entry(form_frame,
                               textvariable=self.spending_limit_var)
        limit_entry.grid(row=row, column=1, sticky="ew", pady=2)
        row += 1

        # 省钱目标
        ttk.Label(form_frame, text="省钱目标:").grid(
            row=row, column=0, sticky="w", pady=2)
        goal_entry = ttk.Entry(form_frame, textvariable=self.saving_goal_var)
        goal_entry.grid(row=row, column=1, sticky="ew", pady=2)
        row += 1

        # 按钮框架
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=5)

        add_btn = ttk.Button(button_frame, text="添加计划",
                            command=self.controller.add_plan)
        add_btn.pack(side="left", padx=(0, 5))

        delete_btn = ttk.Button(button_frame, text="删除选中计划",
                               command=self.controller.delete_plan)
        delete_btn.pack(side="left")

    def get_plan_data(self) -> Dict[str, Any]:
        """获取表单中的计划数据。"""
        return {
            'plan_type': self.plan_type_var.get(),
            'start_date': self._start_date_entry.get() if self._start_date_entry else '',
            'end_date': self._end_date_entry.get() if self._end_date_entry else '',
            'spending_limit': self.spending_limit_var.get(),
            'saving_goal': self.saving_goal_var.get()
        }

    def clear_form(self):
        """清空表单。"""
        self.plan_type_var.set('monthly')
        if self._start_date_entry:
            self._start_date_entry.set_date(datetime.now())
        if self._end_date_entry:
            self._end_date_entry.set_date(datetime.now())
        self.spending_limit_var.set(0.0)
        self.saving_goal_var.set(0.0)

    def update_plans(self, plans: List[Dict[str, Any]]):
        """更新计划列表。"""
        self._treeview.delete(*self._treeview.get_children())

        for plan in plans:
            values = (
                plan['plan_type'],
                plan['start_date'],
                plan['end_date'],
                f"{plan['spending_limit']:.2f}",
                f"{plan['saving_goal']:.2f}"
            )
            self._treeview.insert("", "end", values=values)

    def get_selected_plan_index(self) -> int:
        """获取选中的计划索引。"""
        selected = self._treeview.selection()
        if selected:
            return self._treeview.index(selected[0])
        return -1

    def close(self):
        """关闭窗口。"""
        self.window.destroy()


# ==================== CONTROLLER LAYER ====================
class FinanceController:
    """财务控制器"""
    def __init__(self):
        """初始化控制器。"""
        self.root = tk.Tk()
        self.data_manager = DataManager()
        self.rate_view = None
        self.plan_view = None

        self.main_view = MainView(self.root, self)
        self.update_display()

    def run(self):
        """运行应用程序。"""
        try:
            self.root.mainloop()
        except (tk.TclError, RuntimeError) as e:
            logging.error("应用运行错误: %s", str(e))
            messagebox.showerror("错误", f"应用运行错误: {str(e)}")

    def record_entry(self):
        """记录账目条目。"""
        try:
            data = self.main_view.get_entry_data()

            if not self._validate_entry_data(data):
                return

            invoice_data = None
            if data['invoice_type'] != 'none':
                invoice_data = {
                    'type': data['invoice_type'],
                    'info': data['invoice_info']
                }

            entry = Entry(
                entry_type=data['type'],
                amount=float(data['amount']),
                currency=data['currency'],
                category=data['category'],
                date=data['date'],
                invoice=invoice_data
            )

            self.data_manager.add_entry(entry)
            if self.data_manager.save_data():
                self.update_display()
                self.main_view.clear_entry_fields()
                self.main_view.show_message("成功", "账目记录成功")
            else:
                self.main_view.show_message("错误", "保存失败", "error")

        except ValueError as e:
            error_msg = f"输入数据无效: {str(e)}"
            self.main_view.show_message("错误", error_msg, "error")
        except (IOError, PermissionError) as e:
            logging.error("记录失败: %s", str(e))
            self.main_view.show_message("错误", f"记录失败: {str(e)}", "error")

    def _validate_entry_data(self, data: Dict[str, Any]) -> bool:
        """验证账目数据。"""
        try:
            amount = float(data['amount'])
            if amount <= 0:
                self.main_view.show_message("错误", "金额必须大于0", "error")
                return False
        except ValueError:
            self.main_view.show_message("错误", "金额必须是有效数字", "error")
            return False

        try:
            datetime.strptime(data['date'], '%Y-%m-%d')
        except ValueError:
            self.main_view.show_message("错误", "日期格式必须为 YYYY-MM-DD", "error")
            return False

        if data['invoice_type'] != 'none' and not data['invoice_info']:
            self.main_view.show_message("错误", "请提供发票信息", "error")
            return False

        if 'type' not in data or not data['type']:
            self.main_view.show_message("错误", "账目类型不能为空", "error")
            return False

        return True

    def delete_entries(self):
        """删除选中的账目条目。"""
        indices = self.main_view.get_selected_entry_indices()

        if not indices:
            self.main_view.show_message("警告", "请先选择要删除的账目", "warning")
            return

        confirm_msg = "确定要删除选中的账目吗？"
        if self.main_view.ask_confirmation("确认删除", confirm_msg):
            self.data_manager.delete_entries(indices)
            if self.data_manager.save_data():
                self.update_display()
                self.main_view.show_message("成功", "账目删除成功")
            else:
                self.main_view.show_message("错误", "删除失败", "error")

    def set_budget(self):
        """设置预算。"""
        try:
            budget = self.main_view.budget_var.get()
            if budget < 0:
                self.main_view.show_message("错误", "预算不能为负数", "error")
                return

            self.data_manager.set_budget(budget)
            if self.data_manager.save_data():
                self.main_view.show_message("成功", "预算设置成功")
            else:
                self.main_view.show_message("错误", "保存失败", "error")

        except ValueError:
            self.main_view.show_message("错误", "请输入有效的预算金额", "error")

    def import_data(self):
        """导入数据。"""
        file_path = self.main_view.browse_file(
            "选择要导入的账本文件", [("JSON files", "*.json")]
        )

        if file_path:
            if self.data_manager.import_data(file_path):
                self.update_display()
                self.main_view.show_message("成功", "数据导入成功")
            else:
                self.main_view.show_message("错误", "数据导入失败", "error")

    def save_as_data(self):
        """另存数据。"""
        file_path = self.main_view.save_file(
            "另存为", [("JSON files", "*.json")]
        )

        if file_path:
            if self.data_manager.save_as(file_path):
                self.main_view.show_message("成功", f"账本已保存到: {file_path}")
            else:
                self.main_view.show_message("错误", "保存失败", "error")

    def save_data(self):
        """保存数据。"""
        if self.data_manager.save_data():
            self.main_view.show_message("成功", "账本保存成功")
        else:
            self.main_view.show_message("错误", "保存失败", "error")

    def manage_exchange_rates(self):
        """管理汇率。"""
        self.rate_view = ExchangeRateView(self.root, self)
        current_rates = self.data_manager.get_exchange_rates()
        self.rate_view.set_rates(current_rates)

    def save_exchange_rates(self):
        """保存汇率。"""
        try:
            new_rates = self.rate_view.get_rates()

            for currency, rate in new_rates.items():
                if rate <= 0:
                    msg = f"{currency}汇率必须大于0"
                    self.main_view.show_message("错误", msg, "error")
                    return

            current_rates = self.data_manager.get_exchange_rates()
            current_rates.update(new_rates)
            self.data_manager.set_exchange_rates(current_rates)

            if self.data_manager.save_data():
                self.rate_view.close()
                self.main_view.show_message("成功", "汇率更新成功")
            else:
                self.main_view.show_message("错误", "保存失败", "error")

        except ValueError:
            self.main_view.show_message("错误", "请输入有效的汇率数字", "error")

    def manage_plans(self):
        """管理资金计划。"""
        self.plan_view = PlanView(self.root, self)
        current_plans = self.data_manager.get_plans()
        self.plan_view.update_plans(current_plans)

    def add_plan(self):
        """添加资金计划。"""
        try:
            data = self.plan_view.get_plan_data()

            if data['spending_limit'] < 0 or data['saving_goal'] < 0:
                msg = "花费限额和省钱目标不能为负数"
                self.main_view.show_message("错误", msg, "error")
                return

            plan = Plan(
                plan_type=data['plan_type'],
                start_date=data['start_date'],
                end_date=data['end_date'],
                spending_limit=float(data['spending_limit']),
                saving_goal=float(data['saving_goal'])
            )

            self.data_manager.add_plan(plan)
            if self.data_manager.save_data():
                current_plans = self.data_manager.get_plans()
                self.plan_view.update_plans(current_plans)
                self.plan_view.clear_form()
                self.main_view.show_message("成功", "计划添加成功")
            else:
                self.main_view.show_message("错误", "保存失败", "error")

        except ValueError:
            self.main_view.show_message("错误", "请输入有效的数字", "error")

    def delete_plan(self):
        """删除资金计划。"""
        index = self.plan_view.get_selected_plan_index()

        if index == -1:
            self.main_view.show_message("警告", "请先选择要删除的计划", "warning")
            return

        confirm_msg = "确定要删除选中的计划吗？"
        if self.main_view.ask_confirmation("确认删除", confirm_msg):
            self.data_manager.delete_plan(index)
            if self.data_manager.save_data():
                current_plans = self.data_manager.get_plans()
                self.plan_view.update_plans(current_plans)
                self.main_view.show_message("成功", "计划删除成功")
            else:
                self.main_view.show_message("错误", "删除失败", "error")

    def browse_invoice_file(self):
        """浏览发票文件。"""
        invoice_type = self.main_view.invoice_type_var.get()

        if invoice_type == 'electronic':
            file_path = self.main_view.browse_file(
                "选择电子发票文件", [("All files", "*.*")]
            )
            if file_path:
                self.main_view.invoice_desc_var.set(file_path)
        elif invoice_type == 'paper':
            desc = self.main_view.ask_string("纸质发票描述", "请输入发票描述:")
            if desc:
                self.main_view.invoice_desc_var.set(desc)

    def bar_analytics(self):
        """生成条形图分析。"""
        try:
            totals = self.calculate_totals()

            data = {
                '总收入': totals['total_income'],
                '总支出': totals['total_expenses'],
                '预算': totals['budget'],
                '净收入': totals['net_income']
            }

            self.main_view.update_chart('bar', data)
        except (ValueError, KeyError, TypeError) as e:
            error_msg = f"生成条形图失败: {str(e)}"
            self.main_view.show_message("错误", error_msg, "error")

    def pie_analytics(self):
        """生成饼状图分析。"""
        try:
            totals = self.calculate_totals()

            data = {
                '收入': totals['total_income'],
                '支出': totals['total_expenses']
            }

            if totals['net_income'] < 0:
                data['赤字'] = abs(totals['net_income'])
            elif totals['net_income'] > 0:
                data['结余'] = totals['net_income']

            self.main_view.update_chart('pie', data)
        except (ValueError, KeyError, TypeError) as e:
            error_msg = f"生成饼状图失败: {str(e)}"
            self.main_view.show_message("错误", error_msg, "error")

    def calculate_totals(self) -> Dict[str, float]:
        """计算财务统计。"""
        entries = self.data_manager.get_entries()
        exchange_rates = self.data_manager.get_exchange_rates()
        budget = self.data_manager.get_budget()

        total_income = 0.0
        total_expenses = 0.0

        for entry in entries:
            amount = entry['amount']
            currency = entry.get('currency', 'CNY')

            rate = exchange_rates.get(currency, 1.0)
            converted_amount = amount * rate

            entry_type = entry.get('entry_type', '')
            if not entry_type and 'type' in entry:
                entry_type = entry['type']

            if entry_type == 'income':
                total_income += converted_amount
            else:
                total_expenses += converted_amount

        net_income = total_income - total_expenses - budget

        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'budget': budget,
            'net_income': net_income
        }

    def update_display(self):
        """更新显示。"""
        entries = self.data_manager.get_entries()
        self.main_view.update_treeview(entries)

        budget = self.data_manager.get_budget()
        self.main_view.budget_var.set(budget)

    def quit_app(self):
        """退出应用程序。"""
        if self.main_view.ask_confirmation("确认退出", "是否保存并退出？"):
            self.data_manager.save_data()
            self.root.quit()
            self.root.destroy()


def main():
    """主函数。"""
    try:
        logging.basicConfig(level=logging.INFO)
        app = FinanceController()
        app.run()
    except (ImportError, AttributeError) as e:
        logging.error("应用启动失败: %s", str(e))
        messagebox.showerror("错误", f"应用启动失败: {str(e)}")


if __name__ == '__main__':
    main()
