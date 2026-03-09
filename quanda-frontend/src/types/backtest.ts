export interface BacktestTask {
  id: number
  name: string
  strategy: string
  strategyId?: string  // 关联的策略ID
  status: 'pending' | 'running' | 'completed' | 'failed'
  startDate: string
  endDate: string
  profit: number
  createTime: string
  config?: BacktestConfig
  result?: BacktestResult
}

export interface BacktestResult {
  taskId: number
  totalReturn: number
  annualReturn: number
  sharpeRatio: number
  maxDrawdown: number
  winRate: number
  trades: number
  profitCurve?: number[]  // 收益曲线
  drawdownCurve?: number[]  // 回撤曲线
  tradeList?: TradeRecord[]  // 交易记录
}

export interface BacktestConfig {
  name: string
  strategyPath: string
  strategyId?: string
  dateRange: [string, string]
  initCash: number
  commission: number
  slippage?: number
  code?: string
  frequence?: string
}

export interface TradeRecord {
  time: string
  code: string
  direction: 'buy' | 'sell'
  offset: 'open' | 'close'
  price: number
  volume: number
  profit?: number
}
