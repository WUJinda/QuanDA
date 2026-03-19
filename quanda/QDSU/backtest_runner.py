# coding:utf-8
"""
回测执行器模块
基于 QAStrategyCtaBase 实现回测执行功能
"""
import asyncio
import copy
import importlib.util
import json
import os
import sys
import threading
import traceback
import uuid
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional, Any

import pandas as pd
import pymongo
from qaenv import mongo_ip

from quanda.QDSU.risk_metrics import calculate_backtest_metrics
from quanda.QIFI.QifiAccount import QIFI_Account, ORDER_DIRECTION
from quanda.QDMarket.market_preset import MARKET_PRESET
import quanda as QA


# 全局数据库连接池 (复用连接)
_db_client = None
_db_instance = None


def get_database():
    """获取数据库连接（单例模式）"""
    global _db_client, _db_instance
    if _db_client is None:
        _db_client = pymongo.MongoClient(mongo_ip)
        _db_instance = _db_client.quanda
    return _db_instance


class BacktestRunner:
    """回测执行器"""

    def __init__(self, backtest_id: str, strategy_path: str, strategy_class_name: str = None,
                 start_date: str = None, end_date: str = None, init_cash: float = 1000000,
                 code: str = None, frequence: str = '1min',
                 progress_callback: Callable[[int, str], None] = None):
        """
        初始化回测执行器

        Args:
            backtest_id: 回测任务ID
            strategy_path: 策略文件路径
            strategy_class_name: 策略类名（如果为None，则使用文件中继承自QAStrategyCtaBase的类）
            start_date: 回测开始日期
            end_date: 回测结束日期
            init_cash: 初始资金
            code: 回测标的
            frequence: 回测频率
            progress_callback: 进度回调函数
        """
        self.backtest_id = backtest_id
        self.strategy_path = strategy_path
        self.strategy_class_name = strategy_class_name
        self.start_date = start_date
        self.end_date = end_date
        self.init_cash = init_cash
        self.code = code
        self.frequence = frequence
        self.progress_callback = progress_callback

        # 回测状态
        self.status = 'pending'
        self.progress = 0
        self.message = ''
        self.is_running = False

        # 结果数据
        self.account_history = []
        self.trade_history = []
        self.result = None

        # 使用全局数据库连接
        self.database = get_database()

    def report_progress(self, progress: int, message: str):
        """报告进度"""
        self.progress = progress
        self.message = message
        if self.progress_callback:
            self.progress_callback(progress, message)

    def load_strategy_class(self):
        """动态加载策略类"""
        if not os.path.exists(self.strategy_path):
            raise FileNotFoundError(f"策略文件不存在: {self.strategy_path}")

        # 动态导入策略模块
        spec = importlib.util.spec_from_file_location("strategy_module", self.strategy_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["strategy_module"] = module
        spec.loader.exec_module(module)

        # 查找策略类
        from quanda.QDStrategy.qactabase import QAStrategyCtaBase

        if self.strategy_class_name:
            strategy_class = getattr(module, self.strategy_class_name, None)
            if strategy_class is None:
                raise ValueError(f"未找到策略类: {self.strategy_class_name}")
        else:
            # 自动查找继承自 QAStrategyCtaBase 的类
            strategy_class = None
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and issubclass(obj, QAStrategyCtaBase) and obj != QAStrategyCtaBase:
                    strategy_class = obj
                    break

            if strategy_class is None:
                raise ValueError("未找到有效的策略类")

        return strategy_class

    def run(self) -> Dict:
        """执行回测"""
        self.is_running = True
        self.status = 'running'
        self.report_progress(0, "开始回测...")

        try:
            # 加载策略
            self.report_progress(5, "加载策略...")
            strategy_class = self.load_strategy_class()

            # 创建策略实例
            self.report_progress(10, "初始化策略...")
            strategy = strategy_class(
                code=self.code,
                frequence=self.frequence,
                strategy_id=self.backtest_id,
                start=self.start_date,
                end=self.end_date,
                init_cash=self.init_cash
            )

            # 获取数据量用于进度计算
            self.report_progress(15, "加载数据...")
            data = QA.QA_quotation(
                self.code.upper() if self.code else strategy.code.upper(),
                self.start_date,
                self.end_date,
                source=QA.DATASOURCE.MONGO,
                frequence=self.frequence,
                market=strategy.market_type,
                output=QA.OUTPUT_FORMAT.DATASTRUCT
            )

            if data is None or data.data.empty:
                raise ValueError("无法获取回测数据")

            total_bars = len(data.data)

            if total_bars == 0:
                raise ValueError("回测数据为空")

            # 执行回测
            self.report_progress(20, f"开始回测，共 {total_bars} 根K线...")

            # 初始化账户历史记录
            self.account_history = []
            self.trade_history = []

            # 自定义处理函数
            bar_count = 0
            progress_interval = max(1, total_bars // 100)  # 动态调整进度更新频率

            def custom_bar_handler(item):
                nonlocal bar_count
                bar_count += 1

                # 更新进度
                if bar_count % progress_interval == 0 or bar_count == total_bars:
                    progress = 20 + int((bar_count / total_bars) * 60)
                    self.report_progress(progress, f"处理中 {bar_count}/{total_bars}...")

                # 记录账户状态
                try:
                    acc_msg = strategy.acc.account_msg
                    self.account_history.append({
                        'datetime': str(item.name[0]),
                        'balance': acc_msg.get('balance', self.init_cash),
                        'available': acc_msg.get('available', self.init_cash),
                        'margin': acc_msg.get('margin', 0),
                        'float_profit': acc_msg.get('float_profit', 0),
                        'close_profit': acc_msg.get('close_profit', 0),
                    })
                except Exception as e:
                    pass

                # 调用原始处理函数
                strategy.x1(item)

            # 替换处理函数
            data.data.apply(custom_bar_handler, axis=1)

            # 收集交易记录
            self.report_progress(85, "收集交易记录...")
            if hasattr(strategy.acc, 'trades'):
                self.trade_history = [
                    {
                        'trade_id': trade.get('trade_id', ''),
                        'code': trade.get('instrument_id', ''),
                        'direction': trade.get('direction', ''),
                        'offset': trade.get('offset', ''),
                        'price': trade.get('price', 0),
                        'volume': trade.get('volume', 0),
                        'trade_time': trade.get('trade_time', ''),
                        'commission': trade.get('commission', 0),
                    }
                    for trade in strategy.acc.trades.values()
                ]

            # 计算风险指标
            self.report_progress(90, "计算风险指标...")
            metrics = calculate_backtest_metrics(
                self.account_history,
                self.trade_history,
                self.init_cash
            )

            # 构建结果
            self.report_progress(95, "保存结果...")
            self.result = {
                'backtest_id': self.backtest_id,
                'strategy_path': self.strategy_path,
                'start_date': self.start_date,
                'end_date': self.end_date,
                'init_cash': self.init_cash,
                'code': self.code,
                'frequence': self.frequence,
                'status': 'completed',
                'complete_time': datetime.now().isoformat(),
                'metrics': metrics,
                'account_history': self.account_history,
                'trade_history': self.trade_history,
            }

            # 保存到数据库
            self.save_result()

            self.report_progress(100, "回测完成!")
            self.status = 'completed'

            return self.result

        except Exception as e:
            self.status = 'failed'
            self.message = str(e)
            traceback.print_exc()
            self.report_progress(0, f"回测失败: {e}")
            return {
                'backtest_id': self.backtest_id,
                'status': 'failed',
                'error': str(e),
                'traceback': traceback.format_exc()
            }

        finally:
            self.is_running = False

    def save_result(self):
        """保存回测结果到数据库"""
        if self.result:
            self.database.backtest_results.update_one(
                {'backtest_id': self.backtest_id},
                {'$set': self.result},
                upsert=True
            )

    def run_async(self) -> threading.Thread:
        """异步执行回测"""
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread


class BacktestManager:
    """回测任务管理器"""

    def __init__(self):
        self.runners: Dict[str, BacktestRunner] = {}
        self._lock = threading.Lock()  # 线程安全锁
        self.database = get_database()

    def create_backtest(self, strategy_path: str, strategy_class_name: str = None,
                        start_date: str = None, end_date: str = None,
                        init_cash: float = 1000000, code: str = None,
                        frequence: str = '1min') -> str:
        """
        创建回测任务

        Returns:
            回测任务ID
        """
        backtest_id = str(uuid.uuid4())

        # 创建任务记录
        task = {
            'backtest_id': backtest_id,
            'strategy_path': strategy_path,
            'strategy_class_name': strategy_class_name,
            'start_date': start_date,
            'end_date': end_date,
            'init_cash': init_cash,
            'code': code,
            'frequence': frequence,
            'status': 'pending',
            'progress': 0,
            'message': '任务已创建',
            'create_time': datetime.now().isoformat(),
        }

        self.database.backtest_tasks.update_one(
            {'backtest_id': backtest_id},
            {'$set': task},
            upsert=True
        )

        return backtest_id

    def start_backtest(self, backtest_id: str,
                       progress_callback: Callable[[int, str], None] = None) -> BacktestRunner:
        """
        启动回测任务

        Args:
            backtest_id: 回测任务ID
            progress_callback: 进度回调函数

        Returns:
            BacktestRunner 实例
        """
        # 获取任务信息
        task = self.database.backtest_tasks.find_one({'backtest_id': backtest_id})
        if not task:
            raise ValueError(f"回测任务不存在: {backtest_id}")

        # 更新任务状态
        self.database.backtest_tasks.update_one(
            {'backtest_id': backtest_id},
            {'$set': {'status': 'running', 'start_time': datetime.now().isoformat()}}
        )

        # 创建回测执行器
        runner = BacktestRunner(
            backtest_id=backtest_id,
            strategy_path=task['strategy_path'],
            strategy_class_name=task.get('strategy_class_name'),
            start_date=task['start_date'],
            end_date=task['end_date'],
            init_cash=task['init_cash'],
            code=task.get('code'),
            frequence=task.get('frequence', '1min'),
            progress_callback=progress_callback
        )

        with self._lock:
            self.runners[backtest_id] = runner
        return runner

    def get_backtest_status(self, backtest_id: str) -> Dict:
        """获取回测任务状态"""
        task = self.database.backtest_tasks.find_one({'backtest_id': backtest_id})
        if not task:
            return None

        # 如果任务正在运行，获取最新进度
        with self._lock:
            if backtest_id in self.runners:
                runner = self.runners[backtest_id]
                task['progress'] = runner.progress
                task['message'] = runner.message
                task['status'] = runner.status

        return task

    def get_backtest_result(self, backtest_id: str) -> Dict:
        """获取回测结果"""
        return self.database.backtest_results.find_one(
            {'backtest_id': backtest_id},
            {'_id': 0}
        )

    def list_backtests(self, skip: int = 0, limit: int = 20) -> List[Dict]:
        """获取回测任务列表"""
        tasks = list(self.database.backtest_tasks.find(
            {},
            {'_id': 0}
        ).sort('create_time', -1).skip(skip).limit(limit))

        return tasks

    def count_backtests(self) -> int:
        """获取回测任务总数"""
        return self.database.backtest_tasks.count_documents({})

    def delete_backtest(self, backtest_id: str) -> bool:
        """删除回测任务"""
        # 检查任务是否正在运行
        with self._lock:
            if backtest_id in self.runners:
                runner = self.runners[backtest_id]
                if runner.is_running:
                    return False  # 不能删除正在运行的任务

        # 删除任务记录
        self.database.backtest_tasks.delete_one({'backtest_id': backtest_id})
        # 删除结果记录
        self.database.backtest_results.delete_one({'backtest_id': backtest_id})
        # 从运行器中移除
        with self._lock:
            if backtest_id in self.runners:
                del self.runners[backtest_id]

        return True


# 全局回测管理器实例
backtest_manager = BacktestManager()


if __name__ == '__main__':
    # 测试代码
    def progress_callback(progress: int, message: str):
        print(f"[{progress}%] {message}")

    # 示例：创建并运行回测
    # backtest_id = backtest_manager.create_backtest(
    #     strategy_path='/path/to/strategy.py',
    #     start_date='2024-01-01',
    #     end_date='2024-12-31',
    #     init_cash=1000000,
    #     code='rb2405',
    #     frequence='1min'
    # )
    #
    # runner = backtest_manager.start_backtest(backtest_id, progress_callback)
    # result = runner.run()
    # print("回测结果:", result['metrics'])
    pass
