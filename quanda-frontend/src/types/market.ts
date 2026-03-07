export interface FutureData {
  date: string
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
