export interface Strategy {
  id: number
  name: string
  type: 'trend' | 'mean_reversion' | 'arbitrage' | 'hft'
  status: 'running' | 'stopped'
  createTime: string
  profit: number
  description: string
  code?: string
  filePath?: string  // 策略文件路径
  backtestHistory?: BacktestSummary[]  // 回测历史
}

export interface StrategyConfig {
  name: string
  type: string
  description: string
  parameters: Record<string, any>
  filePath?: string
}

export interface BacktestSummary {
  id: number
  name: string
  date: string
  profit: number
  sharpeRatio: number
  maxDrawdown: number
  status: string
}
