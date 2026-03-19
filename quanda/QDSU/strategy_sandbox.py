# coding:utf-8
"""
策略沙箱执行器
在隔离环境中安全执行策略代码
"""
import argparse
import json
import sys
import os
import traceback
from typing import Dict, Any


def validate_strategy_code(code: str) -> bool:
    """
    验证策略代码安全性
    检测危险操作
    """
    dangerous_patterns = [
        'import os',
        'import sys',
        'import subprocess',
        'import socket',
        '__import__',
        'eval(',
        'exec(',
        'compile(',
        'open(',
        'file(',
        '__builtins__',
    ]
    
    for pattern in dangerous_patterns:
        if pattern in code:
            raise ValueError(f"策略代码包含危险操作: {pattern}")
    
    return True


def run_strategy_in_sandbox(strategy_path: str, config: Dict[str, Any]) -> Dict:
    """
    在沙箱中运行策略
    
    Args:
        strategy_path: 策略文件路径
        config: 回测配置
    
    Returns:
        回测结果
    """
    try:
        # 验证路径安全性
        if not os.path.exists(strategy_path):
            raise FileNotFoundError(f"策略文件不存在: {strategy_path}")
        
        if '..' in strategy_path or not strategy_path.endswith('.py'):
            raise ValueError("非法的策略文件路径")
        
        # 读取策略代码
        with open(strategy_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # 验证代码安全性
        validate_strategy_code(code)
        
        # 导入回测执行器
        from quanda.QDSU.backtest_runner import BacktestRunner
        
        # 创建回测执行器
        runner = BacktestRunner(
            backtest_id=config['backtest_id'],
            strategy_path=strategy_path,
            strategy_class_name=config.get('strategy_class_name'),
            start_date=config['start_date'],
            end_date=config['end_date'],
            init_cash=config['init_cash'],
            code=config.get('code'),
            frequence=config.get('frequence', '1min')
        )
        
        # 执行回测
        result = runner.run()
        
        return result
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e),
            'traceback': traceback.format_exc()
        }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='策略沙箱执行器')
    parser.add_argument('--strategy', required=True, help='策略文件路径')
    parser.add_argument('--config', required=True, help='回测配置 JSON')
    
    args = parser.parse_args()
    
    try:
        config = json.loads(args.config)
        result = run_strategy_in_sandbox(args.strategy, config)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        error_result = {
            'status': 'failed',
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        print(json.dumps(error_result, ensure_ascii=False))
        sys.exit(1)
