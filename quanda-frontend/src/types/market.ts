export interface FutureData {
  date?: string
  datetime?: string
  code: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  amount?: number
}

export interface RealtimeData {
  code: string
  name: string
  price: number
  open: number
  high: number
  low: number
  volume: number
  amount: number
  time: string
  bid: number[]
  ask: number[]
  change: number
  changePercent: number
}

export interface KLineData {
  time: string
  open: number
  close: number
  high: number
  low: number
  volume: number
}

// 品种信息
export interface FutureProduct {
  code: string    // 品种代码：RB
  name: string    // 中文名称：螺纹钢
}

// 交易所分类
export interface FutureCategory {
  exchange: string          // 交易所代码：SHFE
  name: string              // 交易所名称：上期所
  products: FutureProduct[] // 品种列表
}
