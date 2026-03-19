# coding:utf-8
"""
风险指标计算模块
用于计算回测结果的各项风险指标
"""
import copy
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class RiskMetrics:
    """风险指标计算器"""

    def __init__(self, account_history: List[Dict], trade_history: List[Dict], init_cash: float):
        """
        初始化风险指标计算器

        Args:
            account_history: 账户历史记录列表，每条记录包含 datetime, balance, available 等
            trade_history: 交易历史记录列表
            init_cash: 初始资金
        """
        self.account_history = account_history or []
        self.trade_history = trade_history or []
        self.init_cash = init_cash if init_cash and init_cash > 0 else 1  # 防止除零

        # 转换为 DataFrame 便于计算 (使用副本避免修改原始数据)
        if self.account_history:
            self.account_df = pd.DataFrame(self.account_history).copy()
            if 'datetime' in self.account_df.columns:
                self.account_df['datetime'] = pd.to_datetime(self.account_df['datetime'])
                self.account_df = self.account_df.sort_values('datetime').reset_index(drop=True)
        else:
            self.account_df = pd.DataFrame()

        if self.trade_history:
            self.trade_df = pd.DataFrame(self.trade_history).copy()
        else:
            self.trade_df = pd.DataFrame()

    def calculate_all(self) -> Dict:
        """计算所有风险指标"""
        return {
            'profit': self.total_profit(),
            'annual_return': self.annual_return(),
            'sharpe_ratio': self.sharpe_ratio(),
            'max_drawdown': self.max_drawdown(),
            'win_rate': self.win_rate(),
            'profit_loss_ratio': self.profit_loss_ratio(),
            'volatility': self.volatility(),
            'trade_count': self.trade_count(),
            'avg_profit_per_trade': self.avg_profit_per_trade(),
            'max_consecutive_wins': self.max_consecutive_wins(),
            'max_consecutive_losses': self.max_consecutive_losses(),
        }

    def total_profit(self) -> float:
        """计算总收益率"""
        if self.account_df.empty:
            return 0.0

        final_balance = self.account_df['balance'].iloc[-1]
        return round((final_balance - self.init_cash) / self.init_cash * 100, 2)

    def annual_return(self) -> float:
        """计算年化收益率"""
        if self.account_df.empty or len(self.account_df) < 2:
            return 0.0

        start_date = self.account_df['datetime'].iloc[0]
        end_date = self.account_df['datetime'].iloc[-1]

        # 计算交易天数
        days = (end_date - start_date).days
        if days <= 0:
            return 0.0

        # 计算年化收益率
        total_return = self.total_profit() / 100
        annual_return = (1 + total_return) ** (365 / days) - 1

        return round(annual_return * 100, 2)

    def sharpe_ratio(self, risk_free_rate: float = 0.03) -> float:
        """
        计算夏普比率
        Sharpe Ratio = (年化收益率 - 无风险利率) / 年化波动率

        Args:
            risk_free_rate: 无风险利率，默认3%
        """
        if self.account_df.empty or len(self.account_df) < 2:
            return 0.0

        # 计算日收益率 (使用本地变量，不修改 self.account_df)
        balance_series = self.account_df['balance']
        daily_return = balance_series.pct_change()

        # 计算年化波动率
        daily_vol = daily_return.std()
        annual_vol = daily_vol * np.sqrt(252) if not np.isnan(daily_vol) and daily_vol != 0 else 0

        if annual_vol == 0:
            return 0.0

        annual_ret = self.annual_return() / 100
        sharpe = (annual_ret - risk_free_rate) / annual_vol

        return round(sharpe, 2)

    def max_drawdown(self) -> float:
        """
        计算最大回撤
        Max Drawdown = (peak - trough) / peak
        """
        if self.account_df.empty:
            return 0.0

        balance_series = self.account_df['balance']

        # 计算累计最高点
        cumulative_max = balance_series.expanding().max()

        # 计算回撤
        drawdown = (balance_series - cumulative_max) / cumulative_max

        # 获取最大回撤
        max_dd = drawdown.min() * 100

        return round(max_dd, 2)

    def win_rate(self) -> float:
        """计算胜率"""
        if self.trade_df.empty:
            return 0.0

        # 过滤平仓交易（有 close_profit 的交易）
        if 'close_profit' not in self.trade_df.columns:
            return 0.0

        closed_trades = self.trade_df[self.trade_df['close_profit'].notna()]

        if len(closed_trades) == 0:
            return 0.0

        # 计算盈利交易数量
        winning_trades = (closed_trades['close_profit'] > 0).sum()
        total_trades = len(closed_trades)

        if total_trades == 0:
            return 0.0

        return round(winning_trades / total_trades * 100, 2)

    def profit_loss_ratio(self) -> float:
        """计算盈亏比"""
        if self.trade_df.empty:
            return 0.0

        # 过滤平仓交易
        if 'close_profit' not in self.trade_df.columns:
            return 0.0

        closed_trades = self.trade_df[self.trade_df['close_profit'].notna()]

        if len(closed_trades) == 0:
            return 0.0

        winning_trades = closed_trades[closed_trades['close_profit'] > 0]
        losing_trades = closed_trades[closed_trades['close_profit'] < 0]

        if len(winning_trades) == 0 or len(losing_trades) == 0:
            return 0.0

        avg_profit = winning_trades['close_profit'].mean()
        avg_loss = abs(losing_trades['close_profit'].mean())

        if avg_loss == 0 or np.isnan(avg_loss):
            return 0.0

        return round(avg_profit / avg_loss, 2)

    def volatility(self) -> float:
        """计算年化波动率"""
        if self.account_df.empty or len(self.account_df) < 2:
            return 0.0

        # 使用本地变量计算，不修改 self.account_df
        daily_return = self.account_df['balance'].pct_change()
        daily_vol = daily_return.std()
        annual_vol = daily_vol * np.sqrt(252) * 100 if not np.isnan(daily_vol) else 0

        return round(annual_vol, 2)

    def trade_count(self) -> int:
        """获取交易次数"""
        if self.trade_df.empty:
            return 0
        return len(self.trade_df)

    def avg_profit_per_trade(self) -> float:
        """计算每笔交易平均利润"""
        if self.trade_df.empty:
            return 0.0

        if 'close_profit' in self.trade_df.columns:
            total_profit = self.trade_df['close_profit'].sum()
        else:
            total_profit = 0

        trade_count = len(self.trade_df)

        if trade_count == 0:
            return 0.0

        return round(total_profit / trade_count, 2)

    def max_consecutive_wins(self) -> int:
        """计算最大连续盈利次数"""
        if self.trade_df.empty:
            return 0

        if 'close_profit' not in self.trade_df.columns:
            return 0

        closed_trades = self.trade_df[self.trade_df['close_profit'].notna()]

        if len(closed_trades) == 0:
            return 0

        profits = (closed_trades['close_profit'] > 0).astype(int)

        max_wins = 0
        current_wins = 0

        for p in profits:
            if p == 1:
                current_wins += 1
                max_wins = max(max_wins, current_wins)
            else:
                current_wins = 0

        return max_wins

    def max_consecutive_losses(self) -> int:
        """计算最大连续亏损次数"""
        if self.trade_df.empty:
            return 0

        if 'close_profit' not in self.trade_df.columns:
            return 0

        closed_trades = self.trade_df[self.trade_df['close_profit'].notna()]

        if len(closed_trades) == 0:
            return 0

        profits = (closed_trades['close_profit'] < 0).astype(int)

        max_losses = 0
        current_losses = 0

        for p in profits:
            if p == 1:
                current_losses += 1
                max_losses = max(max_losses, current_losses)
            else:
                current_losses = 0

        return max_losses


def calculate_backtest_metrics(account_history: List[Dict], trade_history: List[Dict],
                                init_cash: float) -> Dict:
    """
    计算回测指标的便捷函数

    Args:
        account_history: 账户历史记录
        trade_history: 交易历史记录
        init_cash: 初始资金

    Returns:
        包含所有风险指标的字典
    """
    metrics = RiskMetrics(account_history, trade_history, init_cash)
    return metrics.calculate_all()


if __name__ == '__main__':
    # 测试数据
    account_history = [
        {'datetime': '2024-01-01', 'balance': 100000, 'available': 100000},
        {'datetime': '2024-01-02', 'balance': 102000, 'available': 95000},
        {'datetime': '2024-01-03', 'balance': 101000, 'available': 96000},
        {'datetime': '2024-01-04', 'balance': 105000, 'available': 98000},
        {'datetime': '2024-01-05', 'balance': 103000, 'available': 97000},
    ]

    trade_history = [
        {'trade_id': '1', 'code': 'rb2405', 'close_profit': 2000},
        {'trade_id': '2', 'code': 'rb2405', 'close_profit': -1000},
        {'trade_id': '3', 'code': 'rb2405', 'close_profit': 3000},
        {'trade_id': '4', 'code': 'rb2405', 'close_profit': 500},
    ]

    metrics = calculate_backtest_metrics(account_history, trade_history, 100000)
    print("风险指标:", metrics)
