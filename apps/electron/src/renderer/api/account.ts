import request from './request'
import type { AccountHistory, MonthProfit, TradeRecord } from '@/types/account'

export const accountApi = {
  // 获取账户列表
  getAccountList: async () => {
    const response = await request.get('/qifis', {
      params: { action: 'accountlist' }
    })
    return response || []
  },

  // 获取账户历史资产
  getAccountHistory: async (accountCookie: string) => {
    const response = await request.get('/qifi', {
      params: { action: 'acchistory', account_cookie: accountCookie }
    })
    return response?.data || {}
  },

  // 获取月度收益
  getMonthProfit: async (accountCookie: string) => {
    const response = await request.get('/qifi', {
      params: { action: 'monthprofit', account_cookie: accountCookie }
    })
    return response?.data || {}
  },

  // 获取历史交易记录
  getTradeRecords: async (accountCookie: string) => {
    const response = await request.get('/qifi', {
      params: { action: 'historytrade', account_cookie: accountCookie }
    })
    return response?.data || []
  },

  // 获取持仓面板
  getHoldingPanel: (accountCookie: string, tradingDay: string) => {
    return request.get('/qifi', {
      params: { action: 'holdingpanel', account_cookie: accountCookie, trading_day: tradingDay }
    })
  },

  // 删除账户
  dropAccount: (accountCookie: string) => {
    return request.post('/qifis', null, {
      params: { action: 'drop_account', account_cookie: accountCookie }
    })
  }
}
