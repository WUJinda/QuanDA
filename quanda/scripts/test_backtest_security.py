# coding:utf-8
"""
回测系统安全性测试脚本
测试路径遍历、代码注入等安全漏洞
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from quanda.QDSU.backtest_runner import BacktestRunner
from quanda.QDWebServer.handlers.strategyhandler import validate_strategy_path


def test_path_traversal():
    """测试路径遍历攻击防护"""
    print("=" * 60)
    print("测试 1: 路径遍历攻击防护")
    print("=" * 60)
    
    dangerous_paths = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "/etc/passwd",
        "C:\\Windows\\System32\\config\\sam",
        "strategy/../../../secret.py",
    ]
    
    for path in dangerous_paths:
        result = validate_strategy_path(path)
        status = "✅ 已拦截" if not result else "❌ 未拦截"
        print(f"{status}: {path}")
    
    print()


def test_code_injection():
    """测试代码注入防护"""
    print("=" * 60)
    print("测试 2: 代码注入防护")
    print("=" * 60)
    
    # 创建测试策略文件
    test_dir = os.path.join(os.path.dirname(__file__), 'test_strategies')
    os.makedirs(test_dir, exist_ok=True)
    
    # 危险代码示例
    dangerous_code = """
import os
import sys

class DangerousStrategy:
    def __init__(self):
        # 尝试执行系统命令
        os.system('echo "Dangerous operation"')
        eval('print("Code injection")')
    """
    
    test_file = os.path.join(test_dir, 'dangerous_strategy.py')
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(dangerous_code)
    
    try:
        runner = BacktestRunner(
            backtest_id='test-001',
            strategy_path=test_file,
            start_date='2024-01-01',
            end_date='2024-01-31',
            init_cash=100000
        )
        
        # 尝试加载策略
        runner.load_strategy_class()
        print("❌ 危险代码未被检测")
    except Exception as e:
        print(f"✅ 危险代码已检测: {e}")
    
    # 清理测试文件
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print()


def test_timeout():
    """测试超时控制"""
    print("=" * 60)
    print("测试 3: 超时控制")
    print("=" * 60)
    
    # 创建一个简单的测试策略
    test_dir = os.path.join(os.path.dirname(__file__), 'test_strategies')
    os.makedirs(test_dir, exist_ok=True)
    
    simple_strategy = """
from quanda.QDStrategy.qactabase import QAStrategyCtaBase

class SimpleStrategy(QAStrategyCtaBase):
    def on_bar(self, bar):
        pass
    """
    
    test_file = os.path.join(test_dir, 'simple_strategy.py')
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(simple_strategy)
    
    try:
        runner = BacktestRunner(
            backtest_id='test-timeout',
            strategy_path=test_file,
            start_date='2024-01-01',
            end_date='2024-01-02',
            init_cash=100000,
            timeout=1  # 1秒超时
        )
        
        print("✅ 超时参数已设置: 1秒")
        print(f"   回测超时时间: {runner.timeout}秒")
    except Exception as e:
        print(f"❌ 超时设置失败: {e}")
    
    # 清理测试文件
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print()


def test_parameter_validation():
    """测试参数验证"""
    print("=" * 60)
    print("测试 4: 参数验证")
    print("=" * 60)
    
    from quanda.QDSU.backtest_models import BacktestConfig
    from pydantic import ValidationError
    
    # 测试无效日期格式
    try:
        config = BacktestConfig(
            strategy_path='test.py',
            start_date='2024/01/01',  # 错误格式
            end_date='2024-12-31',
            init_cash=100000
        )
        print("❌ 日期格式验证失败")
    except ValidationError as e:
        print(f"✅ 日期格式验证成功: {e.errors()[0]['msg']}")
    
    # 测试日期范围错误
    try:
        config = BacktestConfig(
            strategy_path='test.py',
            start_date='2024-12-31',
            end_date='2024-01-01',  # 结束日期早于开始日期
            init_cash=100000
        )
        print("❌ 日期范围验证失败")
    except ValidationError as e:
        print(f"✅ 日期范围验证成功: {e.errors()[0]['msg']}")
    
    # 测试无效初始资金
    try:
        config = BacktestConfig(
            strategy_path='test.py',
            start_date='2024-01-01',
            end_date='2024-12-31',
            init_cash=-100000  # 负数
        )
        print("❌ 初始资金验证失败")
    except ValidationError as e:
        print(f"✅ 初始资金验证成功: {e.errors()[0]['msg']}")
    
    # 测试无效K线周期
    try:
        config = BacktestConfig(
            strategy_path='test.py',
            start_date='2024-01-01',
            end_date='2024-12-31',
            init_cash=100000,
            frequence='invalid'  # 无效周期
        )
        print("❌ K线周期验证失败")
    except ValidationError as e:
        print(f"✅ K线周期验证成功: {e.errors()[0]['msg']}")
    
    print()


def main():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "回测系统安全性测试" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    test_path_traversal()
    test_code_injection()
    test_timeout()
    test_parameter_validation()
    
    print("=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()
