# coding:utf-8
"""
双均线策略示例
基于 QAStrategyCtaBase 实现的趋势跟踪策略
"""
from pydantic import BaseModel, Field
from quanda.QDStrategy.qactabase import QAStrategyCtaBase


class StrategyParams(BaseModel):
    """策略参数定义"""
    fast_period: int = Field(default=5, title="短均线周期", description="快速移动平均线周期")
    slow_period: int = Field(default=20, title="长均线周期", description="慢速移动平均线周期")
    volume: int = Field(default=1, title="交易手数", description="每次交易的手数")


class DoubleMAStrategy(QAStrategyCtaBase):
    """
    双均线策略

    策略逻辑：
    1. 短均线上穿长均线 -> 金叉 -> 买入开仓
    2. 短均线下穿长均线 -> 死叉 -> 卖出平仓

    参数说明：
    - fast_period: 短期均线周期，默认5
    - slow_period: 长期均线周期，默认20
    - volume: 每次交易的手数，默认1
    """

    # 用于 UI 自动生成参数表单
    Params = StrategyParams

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化参数
        self.params = StrategyParams(**{
            k: v for k, v in kwargs.items()
            if k in StrategyParams.model_fields
        })

        # 策略变量
        self.fast_ma = 0
        self.slow_ma = 0
        self.last_fast_ma = 0
        self.last_slow_ma = 0
        self.inited = False

    def user_init(self):
        """用户自定义初始化"""
        print(f"双均线策略初始化: fast_period={self.params.fast_period}, slow_period={self.params.slow_period}")

    def on_bar(self, bar):
        """K线回调"""
        # 获取历史数据
        if len(self._market_data) < self.params.slow_period:
            return

        # 计算均线
        close_prices = [item['close'] for item in self._market_data[-self.params.slow_period:]]

        self.last_fast_ma = self.fast_ma
        self.last_slow_ma = self.slow_ma

        self.fast_ma = sum(close_prices[-self.params.fast_period:]) / self.params.fast_period
        self.slow_ma = sum(close_prices) / self.params.slow_period

        # 记录指标值用于可视化
        self.plot('fast_ma', self.fast_ma, 'line')
        self.plot('slow_ma', self.slow_ma, 'line')

        if not self.inited:
            self.inited = True
            return

        # 获取当前持仓
        position = self.get_positions(self.get_code())

        # 金叉买入
        if self.last_fast_ma <= self.last_slow_ma and self.fast_ma > self.slow_ma:
            if position.volume_long == 0:
                self.send_order(
                    direction='BUY',
                    offset='OPEN',
                    price=bar['close'],
                    volume=self.params.volume
                )
                print(f"金叉买入: {bar['close']}")

        # 死叉卖出
        elif self.last_fast_ma >= self.last_slow_ma and self.fast_ma < self.slow_ma:
            if position.volume_long > 0:
                self.send_order(
                    direction='SELL',
                    offset='CLOSE',
                    price=bar['close'],
                    volume=position.volume_long
                )
                print(f"死叉卖出: {bar['close']}")

    def on_tick(self, tick):
        """Tick回调"""
        pass

    def on_1min_bar(self):
        """1分钟K线回调"""
        pass


if __name__ == '__main__':
    # 回测示例
    strategy = DoubleMAStrategy(
        code='rb2405',
        frequence='1min',
        strategy_id='double_ma_test',
        start='2024-01-01',
        end='2024-03-31',
        init_cash=1000000,
        fast_period=5,
        slow_period=20,
        volume=1
    )
    strategy.run_backtest()
