export interface BacktestTask {
  backtest_id: string
  strategy_path: string
  strategy_class_name?: string
  start_date: string
  end_date: string
  init_cash: number
  code?: string
  frequence: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  message: string
  create_time: string
  start_time?: string
  complete_time?: string
}

export interface BacktestResult {
  backtest_id: string
  strategy_path: string
  start_date: string
  end_date: string
  init_cash: number
  code?: string
  frequence: string
  status: 'completed' | 'failed'
  complete_time: string
  metrics: BacktestMetrics
  account_history: AccountHistoryItem[]
  trade_history: TradeRecord[]
  error?: string
  traceback?: string
}

export interface BacktestMetrics {
  profit: number           // 总收益率 %
  annual_return: number    // 年化收益率 %
  sharpe_ratio: number     // 夏普比率
  max_drawdown: number     // 最大回撤 %
  win_rate: number         // 胜率 %
  profit_loss_ratio: number // 盈亏比
  volatility: number       // 年化波动率 %
  trade_count: number      // 交易次数
  avg_profit_per_trade: number // 每笔交易平均利润
  max_consecutive_wins: number  // 最大连续盈利次数
  max_consecutive_losses: number // 最大连续亏损次数
}

export interface BacktestConfig {
  strategy_path: string
  strategy_class_name?: string
  start_date: string
  end_date: string
  init_cash: number
  code?: string
  frequence?: string
}

export interface AccountHistoryItem {
  datetime: string
  balance: number
  available: number
  margin: number
  float_profit: number
  close_profit: number
}

export interface TradeRecord {
  trade_id: string
  code: string
  direction: string  // 'BUY' | 'SELL'
  offset: string     // 'OPEN' | 'CLOSE' | 'CLOSETODAY'
  price: number
  volume: number
  trade_time: string
  commission: number
  close_profit?: number
}

// 前端列表展示用
export interface BacktestListItem {
  id: string
  name: string
  strategy: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  startDate: string
  endDate: string
  profit: number
  progress: number
  message: string
  createTime: string
}
