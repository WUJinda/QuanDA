export interface BacktestTask {
  id: number
  name: string
  strategy: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  startDate: string
  endDate: string
  profit: number
  createTime: string
}

export interface BacktestResult {
  taskId: number
  totalReturn: number
  annualReturn: number
  sharpeRatio: number
  maxDrawdown: number
  winRate: number
  trades: number
}

export interface BacktestConfig {
  name: string
  strategyPath: string
  dateRange: [string, string]
  initCash: number
  commission: number
}
