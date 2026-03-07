export interface Strategy {
  id: number
  name: string
  type: 'trend' | 'mean_reversion' | 'arbitrage' | 'hft'
  status: 'running' | 'stopped'
  createTime: string
  profit: number
  description: string
  code?: string
}

export interface StrategyConfig {
  name: string
  type: string
  description: string
  parameters: Record<string, any>
}
