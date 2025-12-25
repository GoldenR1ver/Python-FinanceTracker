"""
Finance Tracker Application - Fixed Version
修复了"记录失败：type"错误
Author: Li Yujiang
Student ID: 231220013
Date: 2025/10/24
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')

# ==================== matplotlib 中文支持 ====================
from matplotlib.font_manager import FontProperties
try:
    # Windows 系统字体路径
    font_path = 'C:/Windows/Fonts/simhei.ttf'
    if os.path.exists(font_path):
        custom_font = FontProperties(fname=font_path)
        plt.rcParams['font.family'] = custom_font.get_name()
    else:
        # macOS 或 Linux 备选方案
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'Microsoft YaHei']
    
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
except:
    print("字体设置失败，可能需要手动安装中文字体")



# ==================== MODEL LAYER ====================

@dataclass
class Entry:
    """账目实体类"""
    type: str  # 修复：统一使用 'type' 而不是 'entry_type'
    amount: float
    currency: str
    category: str
    date: str
    invoice: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
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
        return asdict(self)

class DataManager:
    """数据管理类"""
    
    def __init__(self, file_path: str = 'finance_data.json'):
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
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    loaded_data = json.load(file)
                    
                    # 修复：处理旧数据中的字段名问题
                    if 'entries' in loaded_data:
                        for entry in loaded_data['entries']:
                            # 如果存在 entry_type 字段，转换为 type 字段
                            if 'entry_type' in entry:
                                entry['type'] = entry.pop('entry_type')
                    
                    self.data.update(loaded_data)
                self.logger.info(f"数据加载成功: {self.file_path}")
                return True
            else:
                self.logger.info("未找到数据文件，使用默认数据")
                return False
        except Exception as e:
            self.logger.error(f"数据加载失败: {str(e)}")
            return False
    
    def save_data(self) -> bool:
        try:
            directory = os.path.dirname(self.file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump(self.data, file, indent=2, ensure_ascii=False)
            
            self.logger.info(f"数据保存成功: {self.file_path}")
            return True
        except Exception as e:
            self.logger.error(f"数据保存失败: {str(e)}")
            return False
    
    def save_as(self, new_file_path: str) -> bool:
        original_path = self.file_path
        self.file_path = new_file_path
        
        if self.save_data():
            return True
        else:
            self.file_path = original_path
            return False
    
    def import_data(self, import_file_path: str) -> bool:
        try:
            with open(import_file_path, 'r', encoding='utf-8') as file:
                imported_data = json.load(file)
            
            # 修复：导入时也处理字段名问题
            if 'entries' in imported_data:
                for entry in imported_data['entries']:
                    if 'entry_type' in entry:
                        entry['type'] = entry.pop('entry_type')
            
            self.data.update(imported_data)
            self.file_path = import_file_path
            
            if self.save_data():
                self.logger.info(f"数据导入成功: {import_file_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"数据导入失败: {str(e)}")
            return False
    
    def add_entry(self, entry: Entry) -> None:
        self.data['entries'].append(entry.to_dict())
    
    def delete_entries(self, indices: List[int]) -> None:
        for index in sorted(indices, reverse=True):
            if 0 <= index < len(self.data['entries']):
                del self.data['entries'][index]
    
    def get_entries(self) -> List[Dict[str, Any]]:
        return self.data['entries']
    
    def set_budget(self, budget: float) -> None:
        self.data['budget'] = budget
    
    def get_budget(self) -> float:
        return self.data.get('budget', 0.0)
    
    def set_exchange_rates(self, rates: Dict[str, float]) -> None:
        self.data['exchange_rates'] = rates
    
    def get_exchange_rates(self) -> Dict[str, float]:
        return self.data.get('exchange_rates', {})
    
    def add_plan(self, plan: Plan) -> None:
        self.data['plans'].append(plan.to_dict())
    
    def delete_plan(self, index: int) -> None:
        if 0 <= index < len(self.data['plans']):
            del self.data['plans'][index]
    
    def get_plans(self) -> List[Dict[str, Any]]:
        return self.data.get('plans', [])

# ==================== VIEW LAYER ====================

class BaseView(ABC):
    @abstractmethod
    def create_widgets(self):
        pass
    
    @abstractmethod
    def update_display(self):
        pass

class MainView(BaseView):
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("Finance Tracker")
        self.root.geometry("1200x800")
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        self._configure_styles()
        self._create_variables()
        self.create_widgets()
        
        self.date_entry.set_date(datetime.now())
    
    def _configure_styles(self):
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'), foreground='navy')
        style.configure('TEntry', padding=5)
        style.configure('TCombobox', padding=5)
    
    def _create_variables(self):
        self.entry_type_var = tk.StringVar(value="Income")
        self.amount_var = tk.DoubleVar(value=0.0)
        self.currency_var = tk.StringVar(value='CNY')
        self.category_var = tk.StringVar(value='Salary')
        self.invoice_type_var = tk.StringVar(value='none')
        self.invoice_desc_var = tk.StringVar()
        self.budget_var = tk.DoubleVar(value=0.0)
    
    def create_widgets(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky="nsew")
        
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(1, weight=1)
        main_container.rowconfigure(2, weight=1)
        
        title_label = ttk.Label(main_container, text="个人记账本", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        input_frame = self._create_input_frame(main_container)
        input_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        
        chart_frame = self._create_chart_frame(main_container)
        chart_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        
        data_frame = self._create_data_frame(main_container)
        data_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
    
    def _create_input_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="账目录入", padding="10")
        frame.columnconfigure(1, weight=1)
        
        row = 0
        
        ttk.Label(frame, text="账目类型:").grid(row=row, column=0, sticky="w", pady=2)
        entry_types = ["Income", "Expense"]
        ttk.Combobox(frame, textvariable=self.entry_type_var, values=entry_types, state="readonly").grid(row=row, column=1, sticky="ew", pady=2)
        row += 1
        
        ttk.Label(frame, text="金额:").grid(row=row, column=0, sticky="w", pady=2)
        ttk.Spinbox(frame, textvariable=self.amount_var, from_=0, to=float('inf'), increment=1).grid(row=row, column=1, sticky="ew", pady=2)
        row += 1
        
        ttk.Label(frame, text="货币类型:").grid(row=row, column=0, sticky="w", pady=2)
        currencies = ['CNY', 'USD', 'EUR', 'HKD']
        ttk.Combobox(frame, textvariable=self.currency_var, values=currencies, state="readonly").grid(row=row, column=1, sticky="ew", pady=2)
        row += 1
        
        ttk.Label(frame, text="类别:").grid(row=row, column=0, sticky="w", pady=2)
        categories = ["Salary", "Food", "Housing", "Transportation", "Medical", "Clothes & Cosmetics", "Hobby", "Education", "Gift"]
        ttk.Combobox(frame, textvariable=self.category_var, values=categories, state="readonly").grid(row=row, column=1, sticky="ew", pady=2)
        row += 1
        
        ttk.Label(frame, text="日期:").grid(row=row, column=0, sticky="w", pady=2)
        self.date_entry = DateEntry(frame, date_pattern="yyyy-mm-dd")
        self.date_entry.grid(row=row, column=1, sticky="ew", pady=2)
        row += 1
        
        ttk.Label(frame, text="发票类型:").grid(row=row, column=0, sticky="w", pady=2)
        invoice_types = ['none', 'electronic', 'paper']
        ttk.Combobox(frame, textvariable=self.invoice_type_var, values=invoice_types, state="readonly").grid(row=row, column=1, sticky="ew", pady=2)
        row += 1
        
        ttk.Label(frame, text="发票信息:").grid(row=row, column=0, sticky="w", pady=2)
        ttk.Entry(frame, textvariable=self.invoice_desc_var).grid(row=row, column=1, sticky="ew", pady=2)
        ttk.Button(frame, text="浏览", command=self.controller.browse_invoice_file).grid(row=row, column=2, padx=(5, 0))
        row += 1
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="添加记账", command=self.controller.record_entry).pack(side="left", padx=(0, 5))
        ttk.Button(button_frame, text="删除选中", command=self.controller.delete_entries).pack(side="left")
        row += 1
        
        ttk.Label(frame, text="月度预算:").grid(row=row, column=0, sticky="w", pady=2)
        ttk.Spinbox(frame, textvariable=self.budget_var, from_=0, to=float('inf'), increment=100).grid(row=row, column=1, sticky="ew", pady=2)
        row += 1
        
        ttk.Button(frame, text="设置预算", command=self.controller.set_budget).grid(row=row, column=0, columnspan=2, pady=5)
        
        return frame
    
    def _create_chart_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="数据统计", padding="10")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=0)
        
        self.fig, self.ax = plt.subplots(figsize=(6, 4), tight_layout=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew")
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=1, column=0, pady=(10, 0))
        
        ttk.Button(button_frame, text="条形图统计", command=self.controller.bar_analytics).pack(side="left", padx=(0, 5))
        ttk.Button(button_frame, text="饼状图统计", command=self.controller.pie_analytics).pack(side="left")
        
        return frame
    
    def _create_data_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="账目列表", padding="10")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        toolbar = ttk.Frame(frame)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Button(toolbar, text="导入账本", command=self.controller.import_data).pack(side="left", padx=(0, 5))
        ttk.Button(toolbar, text="另存为", command=self.controller.save_as_data).pack(side="left", padx=(0, 5))
        ttk.Button(toolbar, text="保存账本", command=self.controller.save_data).pack(side="left", padx=(0, 5))
        ttk.Button(toolbar, text="管理汇率", command=self.controller.manage_exchange_rates).pack(side="left", padx=(0, 5))
        ttk.Button(toolbar, text="资金计划", command=self.controller.manage_plans).pack(side="left", padx=(0, 5))
        ttk.Button(toolbar, text="保存并退出", command=self.controller.quit_app).pack(side="left")
        
        columns = ("序号", "类型", "金额", "货币", "类别", "日期", "发票信息")
        self.treeview = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        
        for col in columns:
            self.treeview.heading(col, text=col)
            self.treeview.column(col, width=100)
        
        self.treeview.grid(row=1, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.treeview.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.treeview.configure(yscrollcommand=scrollbar.set)
        
        return frame
    
    def on_window_close(self):
        """窗口关闭事件处理"""
        self.controller.quit_app()
    
    def update_display(self):
        pass
    
    def get_entry_data(self) -> Dict[str, Any]:
        # 修复：确保类型转换正确
        entry_type = self.entry_type_var.get().lower()
        return {
            'type': entry_type,  # 修复：统一使用 'type'
            'amount': self.amount_var.get(),
            'currency': self.currency_var.get(),
            'category': self.category_var.get(),
            'date': self.date_entry.get(),
            'invoice_type': self.invoice_type_var.get(),
            'invoice_info': self.invoice_desc_var.get()
        }
    
    def clear_entry_fields(self):
        self.entry_type_var.set("Income")
        self.amount_var.set(0.0)
        self.currency_var.set('CNY')
        self.category_var.set('Salary')
        self.date_entry.set_date(datetime.now())
        self.invoice_type_var.set('none')
        self.invoice_desc_var.set('')
    
    def get_selected_entry_indices(self) -> List[int]:
        selected = self.treeview.selection()
        return [self.treeview.index(item) for item in selected]
    
    def update_treeview(self, entries: List[Dict[str, Any]]):
        self.treeview.delete(*self.treeview.get_children())
        
        for i, entry in enumerate(entries):
            invoice_info = entry.get('invoice', {})
            invoice_display = "无"
            if invoice_info:
                invoice_display = f"{invoice_info.get('type', '')}: {invoice_info.get('info', '')}"
            
            # 修复：统一使用 'type' 字段
            entry_type = entry.get('type', '')
            if not entry_type and 'entry_type' in entry:
                entry_type = entry['entry_type']  # 向后兼容
            
            values = (
                f"{i + 1}",
                entry_type.capitalize() if entry_type else '',
                f"{entry['amount']:.2f}",
                entry.get('currency', 'CNY'),
                entry['category'],
                entry['date'],
                invoice_display
            )
            self.treeview.insert("", "end", values=values)
    
    def update_chart(self, chart_type: str, data: Dict[str, Any]):
        self.ax.clear()
        
        if chart_type == 'bar':
            categories = list(data.keys())
            values = list(data.values())
            colors = ['green', 'red', 'purple', 'blue'][:len(categories)]
            
            bars = self.ax.bar(categories, values, color=colors)
            self.ax.set_ylabel('金额 (CNY)')
            self.ax.set_title('财务统计')
            
            for bar, value in zip(bars, values):
                self.ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), 
                           f'{value:.2f}', ha='center', va='bottom')
            
        elif chart_type == 'pie':
            filtered_data = {k: v for k, v in data.items() if v > 0}
            if not filtered_data:
                self.ax.text(0.5, 0.5, '暂无数据', ha='center', va='center', 
                           transform=self.ax.transAxes, fontsize=12)
                self.ax.set_title('收入/支出占比')
            else:
                categories = list(filtered_data.keys())
                values = list(filtered_data.values())
                colors = ['#4CAF50', '#F44336', '#FF9800', '#2196F3'][:len(categories)]
                
                wedges, texts, autotexts = self.ax.pie(
                    values, 
                    labels=categories, 
                    autopct='%1.1f%%',
                    colors=colors,
                    startangle=90
                )
                self.ax.set_title('收入/支出占比')
                
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
        
        self.canvas.draw()
    
    def show_message(self, title: str, message: str, message_type: str = "info"):
        if message_type == "info":
            messagebox.showinfo(title, message)
        elif message_type == "warning":
            messagebox.showwarning(title, message)
        elif message_type == "error":
            messagebox.showerror(title, message)
    
    def ask_confirmation(self, title: str, message: str) -> bool:
        return messagebox.askyesno(title, message)
    
    def browse_file(self, title: str, filetypes: List[tuple]) -> str:
        return filedialog.askopenfilename(title=title, filetypes=filetypes)
    
    def save_file(self, title: str, filetypes: List[tuple]) -> str:
        return filedialog.asksaveasfilename(
            title=title, 
            filetypes=filetypes, 
            defaultextension=".json"
        )
    
    def ask_string(self, title: str, prompt: str) -> str:
        return simpledialog.askstring(title, prompt)

class ExchangeRateView:
    def __init__(self, parent, controller):
        self.window = tk.Toplevel(parent)
        self.controller = controller
        self.window.title("管理汇率")
        self.window.geometry("300x200")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.rate_vars = {}
        self.create_widgets()
    
    def create_widgets(self):
        self.window.columnconfigure(1, weight=1)
        
        ttk.Label(self.window, text="汇率管理（基准货币: CNY）", style='Title.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        row = 1
        currencies = ['USD', 'EUR', 'HKD']
        
        for currency in currencies:
            ttk.Label(self.window, text=f"{currency}:").grid(row=row, column=0, sticky="w", pady=2)
            rate_var = tk.DoubleVar()
            ttk.Entry(self.window, textvariable=rate_var).grid(row=row, column=1, sticky="ew", pady=2)
            self.rate_vars[currency] = rate_var
            row += 1
        
        button_frame = ttk.Frame(self.window)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="保存", command=self.controller.save_exchange_rates).pack(side="left", padx=(0, 5))
        ttk.Button(button_frame, text="取消", command=self.window.destroy).pack(side="left")
    
    def set_rates(self, rates: Dict[str, float]):
        for currency, rate in rates.items():
            if currency in self.rate_vars:
                self.rate_vars[currency].set(rate)
    
    def get_rates(self) -> Dict[str, float]:
        return {currency: var.get() for currency, var in self.rate_vars.items()}
    
    def close(self):
        self.window.destroy()

class PlanView:
    def __init__(self, parent, controller):
        self.window = tk.Toplevel(parent)
        self.controller = controller
        self.window.title("资金计划管理")
        self.window.geometry("600x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        
        columns = ("类型", "开始日期", "结束日期", "花费限额", "省钱目标")
        self.treeview = ttk.Treeview(self.window, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.treeview.heading(col, text=col)
        
        self.treeview.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.treeview.yview)
        scrollbar.grid(row=0, column=2, sticky="ns")
        self.treeview.configure(yscrollcommand=scrollbar.set)
        
        form_frame = ttk.LabelFrame(self.window, text="添加新计划", padding="10")
        form_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        form_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        ttk.Label(form_frame, text="计划类型:").grid(row=row, column=0, sticky="w", pady=2)
        self.plan_type_var = tk.StringVar(value='monthly')
        ttk.Combobox(form_frame, textvariable=self.plan_type_var, values=['yearly', 'monthly', 'weekly'], state="readonly").grid(row=row, column=1, sticky="ew", pady=2)
        row += 1
        
        ttk.Label(form_frame, text="开始日期:").grid(row=row, column=0, sticky="w", pady=2)
        self.start_date_entry = DateEntry(form_frame, date_pattern="yyyy-mm-dd")
        self.start_date_entry.grid(row=row, column=1, sticky="ew", pady=2)
        row += 1
        
        ttk.Label(form_frame, text="结束日期:").grid(row=row, column=0, sticky="w", pady=2)
        self.end_date_entry = DateEntry(form_frame, date_pattern="yyyy-mm-dd")
        self.end_date_entry.grid(row=row, column=1, sticky="ew", pady=2)
        row += 1
        
        ttk.Label(form_frame, text="花费限额:").grid(row=row, column=0, sticky="w", pady=2)
        self.spending_limit_var = tk.DoubleVar()
        ttk.Entry(form_frame, textvariable=self.spending_limit_var).grid(row=row, column=1, sticky="ew", pady=2)
        row += 1
        
        ttk.Label(form_frame, text="省钱目标:").grid(row=row, column=0, sticky="w", pady=2)
        self.saving_goal_var = tk.DoubleVar()
        ttk.Entry(form_frame, textvariable=self.saving_goal_var).grid(row=row, column=1, sticky="ew", pady=2)
        row += 1
        
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=5)
        
        ttk.Button(button_frame, text="添加计划", command=self.controller.add_plan).pack(side="left", padx=(0, 5))
        ttk.Button(button_frame, text="删除选中计划", command=self.controller.delete_plan).pack(side="left")
    
    def get_plan_data(self) -> Dict[str, Any]:
        return {
            'plan_type': self.plan_type_var.get(),
            'start_date': self.start_date_entry.get(),
            'end_date': self.end_date_entry.get(),
            'spending_limit': self.spending_limit_var.get(),
            'saving_goal': self.saving_goal_var.get()
        }
    
    def clear_form(self):
        self.plan_type_var.set('monthly')
        self.start_date_entry.set_date(datetime.now())
        self.end_date_entry.set_date(datetime.now())
        self.spending_limit_var.set(0.0)
        self.saving_goal_var.set(0.0)
    
    def update_plans(self, plans: List[Dict[str, Any]]):
        self.treeview.delete(*self.treeview.get_children())
        
        for plan in plans:
            values = (
                plan['plan_type'],
                plan['start_date'],
                plan['end_date'],
                f"{plan['spending_limit']:.2f}",
                f"{plan['saving_goal']:.2f}"
            )
            self.treeview.insert("", "end", values=values)
    
    def get_selected_plan_index(self) -> int:
        selected = self.treeview.selection()
        if selected:
            return self.treeview.index(selected[0])
        return -1
    
    def close(self):
        self.window.destroy()

# ==================== CONTROLLER LAYER ====================

class FinanceController:
    def __init__(self):
        self.root = tk.Tk()
        self.data_manager = DataManager()
        
        # 创建视图时传入控制器实例
        self.main_view = MainView(self.root, self)
        
        self.update_display()
    
    def run(self):
        try:
            self.root.mainloop()
        except Exception as e:
            logging.error(f"应用运行错误: {str(e)}")
            messagebox.showerror("错误", f"应用运行错误: {str(e)}")
    
    def record_entry(self):
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
            
            # 修复：统一使用 'type' 字段
            entry = Entry(
                type=data['type'],  # 修复：使用 'type' 而不是 'entry_type'
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
            self.main_view.show_message("错误", f"输入数据无效: {str(e)}", "error")
        except Exception as e:
            # 修复：提供更详细的错误信息
            import traceback
            error_details = traceback.format_exc()
            logging.error(f"记录失败: {str(e)}\n{error_details}")
            self.main_view.show_message("错误", f"记录失败: {str(e)}", "error")
    
    def _validate_entry_data(self, data: Dict[str, Any]) -> bool:
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
        
        # 修复：验证类型字段
        if 'type' not in data or not data['type']:
            self.main_view.show_message("错误", "账目类型不能为空", "error")
            return False
        
        return True
    
    def delete_entries(self):
        indices = self.main_view.get_selected_entry_indices()
        
        if not indices:
            self.main_view.show_message("警告", "请先选择要删除的账目", "warning")
            return
        
        if self.main_view.ask_confirmation("确认删除", "确定要删除选中的账目吗？"):
            self.data_manager.delete_entries(indices)
            if self.data_manager.save_data():
                self.update_display()
                self.main_view.show_message("成功", "账目删除成功")
            else:
                self.main_view.show_message("错误", "删除失败", "error")
    
    def set_budget(self):
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
        file_path = self.main_view.browse_file("选择要导入的账本文件", [("JSON files", "*.json")])
        
        if file_path:
            if self.data_manager.import_data(file_path):
                self.update_display()
                self.main_view.show_message("成功", "数据导入成功")
            else:
                self.main_view.show_message("错误", "数据导入失败", "error")
    
    def save_as_data(self):
        file_path = self.main_view.save_file("另存为", [("JSON files", "*.json")])
        
        if file_path:
            if self.data_manager.save_as(file_path):
                self.main_view.show_message("成功", f"账本已保存到: {file_path}")
            else:
                self.main_view.show_message("错误", "保存失败", "error")
    
    def save_data(self):
        if self.data_manager.save_data():
            self.main_view.show_message("成功", "账本保存成功")
        else:
            self.main_view.show_message("错误", "保存失败", "error")
    
    def manage_exchange_rates(self):
        self.rate_view = ExchangeRateView(self.root, self)
        current_rates = self.data_manager.get_exchange_rates()
        self.rate_view.set_rates(current_rates)
    
    def save_exchange_rates(self):
        try:
            new_rates = self.rate_view.get_rates()
            
            for currency, rate in new_rates.items():
                if rate <= 0:
                    self.main_view.show_message("错误", f"{currency}汇率必须大于0", "error")
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
        self.plan_view = PlanView(self.root, self)
        current_plans = self.data_manager.get_plans()
        self.plan_view.update_plans(current_plans)
    
    def add_plan(self):
        try:
            data = self.plan_view.get_plan_data()
            
            if data['spending_limit'] < 0 or data['saving_goal'] < 0:
                self.main_view.show_message("错误", "花费限额和省钱目标不能为负数", "error")
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
        index = self.plan_view.get_selected_plan_index()
        
        if index == -1:
            self.main_view.show_message("警告", "请先选择要删除的计划", "warning")
            return
        
        if self.main_view.ask_confirmation("确认删除", "确定要删除选中的计划吗？"):
            self.data_manager.delete_plan(index)
            if self.data_manager.save_data():
                current_plans = self.data_manager.get_plans()
                self.plan_view.update_plans(current_plans)
                self.main_view.show_message("成功", "计划删除成功")
            else:
                self.main_view.show_message("错误", "删除失败", "error")
    
    def browse_invoice_file(self):
        invoice_type = self.main_view.invoice_type_var.get()
        
        if invoice_type == 'electronic':
            file_path = self.main_view.browse_file("选择电子发票文件", [("All files", "*.*")])
            if file_path:
                self.main_view.invoice_desc_var.set(file_path)
        elif invoice_type == 'paper':
            desc = self.main_view.ask_string("纸质发票描述", "请输入发票描述:")
            if desc:
                self.main_view.invoice_desc_var.set(desc)
    
    def bar_analytics(self):
        try:
            totals = self.calculate_totals()
            
            data = {
                '总收入': totals['total_income'],
                '总支出': totals['total_expenses'],
                '预算': totals['budget'],
                '净收入': totals['net_income']
            }
            
            self.main_view.update_chart('bar', data)
        except Exception as e:
            self.main_view.show_message("错误", f"生成条形图失败: {str(e)}", "error")
    
    def pie_analytics(self):
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
        except Exception as e:
            self.main_view.show_message("错误", f"生成饼状图失败: {str(e)}", "error")
    
    def calculate_totals(self) -> Dict[str, float]:
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
            

            entry_type = entry.get('type', '')
            if not entry_type and 'entry_type' in entry:
                entry_type = entry['entry_type']
            
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
        entries = self.data_manager.get_entries()
        self.main_view.update_treeview(entries)
        
        budget = self.data_manager.get_budget()
        self.main_view.budget_var.set(budget)
    
    def quit_app(self):
        if self.main_view.ask_confirmation("确认退出", "是否保存并退出？"):
            self.data_manager.save_data()
            self.root.quit()
            self.root.destroy()

def main():
    try:
        logging.basicConfig(level=logging.INFO)
        app = FinanceController()
        app.run()
    except Exception as e:
        logging.error(f"应用启动失败: {str(e)}")
        messagebox.showerror("错误", f"应用启动失败: {str(e)}")

if __name__ == '__main__':
    main()
