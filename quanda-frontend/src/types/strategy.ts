export interface Strategy {
  id: string
  name: string
  type: string  // 'trend' | 'mean_reversion' | 'arbitrage' | 'hft' | 'custom'
  description: string
  file_path: string
  code?: string
  status: 'running' | 'stopped'
  parameters: Record<string, any>
  tags: string[]
  profit: number
  sharpe_ratio: number
  max_drawdown: number
  create_time: string
  update_time: string
  start_time?: string
  stop_time?: string
}

export interface StrategyConfig {
  name: string
  type: string
  description: string
  code?: string
  parameters?: Record<string, any>
  tags?: string[]
}

export interface StrategyAnalysis {
  parameters: StrategyParameter[]
  strategy_class: string | null
}

export interface StrategyParameter {
  name: string
  type: 'int' | 'float' | 'str' | 'bool'
  default: any
  title: string
  description?: string
}

export interface BacktestSummary {
  backtest_id: string
  strategy_path: string
  start_date: string
  end_date: string
  profit: number
  sharpe_ratio: number
  max_drawdown: number
  status: string
  create_time: string
}

// 策略类型选项
export const STRATEGY_TYPES = [
  { value: 'trend', label: '趋势跟踪' },
  { value: 'mean_reversion', label: '均值回归' },
  { value: 'arbitrage', label: '套利策略' },
  { value: 'hft', label: '高频交易' },
  { value: 'custom', label: '自定义策略' },
]

// 策略状态选项
export const STRATEGY_STATUS = [
  { value: 'running', label: '运行中', type: 'success' },
  { value: 'stopped', label: '已停止', type: 'info' },
]
