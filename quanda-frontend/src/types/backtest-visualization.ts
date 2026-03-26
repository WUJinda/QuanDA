// 回测可视化相关类型定义

// K线数据
export interface BacktestKLine {
  time: string
  open: number
  high: number
  low: number
  close: number
  volume?: number
}

// 账户状态
export interface BacktestAccount {
  datetime: string
  balance: number
  available: number
  margin: number
  float_profit: number
  close_profit: number
}

// 交易信号
export interface BacktestSignal {
  time: string
  price: number
  direction: 'buy' | 'sell'
  volume?: number
}

// WebSocket 消息类型
export type WSMessageType =
  | 'status'      // 状态更新
  | 'progress'    // 进度更新
  | 'kline'       // K线数据
  | 'account'     // 账户状态
  | 'signal'      // 交易信号
  | 'completed'   // 回测完成
  | 'error'       // 错误
  | 'started'     // 回测启动

// WebSocket 消息
export interface WSMessage {
  type: WSMessageType
  data?: BacktestKLine | BacktestAccount | BacktestSignal
  progress?: number
  message?: string
  result?: BacktestResult
  timestamp?: string
}

// 回测结果
export interface BacktestResult {
  backtest_id: string
  status: string
  start_date: string
  end_date: string
  init_cash: number
  metrics: {
    profit: number
    max_drawdown: number
    sharpe_ratio: number
    win_rate: number
    total_trades: number
  }
  account_history: BacktestAccount[]
  trade_history: any[]
}

// 可视化状态
export interface VisualizationState {
  status: 'idle' | 'running' | 'completed' | 'error'
  progress: number
  message: string
  klines: BacktestKLine[]
  account: BacktestAccount | null
  signals: BacktestSignal[]
  result: BacktestResult | null
}
