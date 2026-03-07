export interface AccountHistory {
  [date: string]: number
}

export interface MonthProfit {
  [month: string]: number
}

export interface TradeRecord {
  commission: number
  direction: 'BUY' | 'SELL'
  offset: 'OPEN' | 'CLOSE'
  price: number
  trade_date_time: number
  volume: number
  code: string
  datetime: string
}

export interface AccountInfo {
  account_cookie: string
  balance: number
  available: number
  frozen: number
  profit: number
  risk_ratio: number
}

export interface Position {
  code: string
  volume: number
  price: number
  direction: 'LONG' | 'SHORT'
  profit: number
}
