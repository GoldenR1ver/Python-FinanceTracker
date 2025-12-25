#!/usr/bin/env python3
"""
运行测试的脚本。
"""

import subprocess
import sys
import os

def run_tests():
    """运行所有测试。"""
    # 切换到项目根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("=" * 60)
    print("运行测试套件")
    print("=" * 60)
    
    # 运行简单测试
    print("\n1. 运行基础测试...")
    result1 = subprocess.run([sys.executable, "-m", "pytest", "tests/helloworld_test.py", "-v"])
    
    # 运行DataManager测试
    print("\n2. 运行DataManager测试...")
    result2 = subprocess.run([sys.executable, "-m", "pytest", "tests/test_datamanager.py", "-v"])
    
    # 运行Entry测试
    print("\n3. 运行Entry测试...")
    result3 = subprocess.run([sys.executable, "-m", "pytest", "tests/test_entry.py", "-v"])
    
    # 运行集成测试
    print("\n4. 运行集成测试...")
    result4 = subprocess.run([sys.executable, "-m", "pytest", "tests/test_controller_integration.py", "-v"])
    
    # 运行所有测试并生成覆盖率报告
    print("\n5. 运行所有测试并生成覆盖率报告...")
    result5 = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=Finance_Tracker_Fixed.py",
        "--cov-report=term-missing",
        "--cov-report=html"
    ])
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    # 返回综合结果
    return all([result1.returncode == 0, 
                result2.returncode == 0, 
                result3.returncode == 0,
                result4.returncode == 0,
                result5.returncode == 0])

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
