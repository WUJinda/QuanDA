import { defineStore } from 'pinia'
import { ref } from 'vue'
import { accountApi } from '@/api/account'
import type { AccountHistory, MonthProfit, TradeRecord, AccountInfo } from '@/types/account'

export const useAccountStore = defineStore('account', () => {
  const accountList = ref<string[]>([])
  const currentAccount = ref<string>('')
  const accountHistory = ref<AccountHistory>({})
  const monthProfit = ref<MonthProfit>({})
  const tradeRecords = ref<TradeRecord[]>([])
  const accountInfo = ref<AccountInfo | null>(null)

  const fetchAccountList = async () => {
    try {
      const data = await accountApi.getAccountList()
      accountList.value = data
      if (data.length > 0) {
        currentAccount.value = data[0]
      }
    } catch (error) {
      console.error('获取账户列表失败:', error)
    }
  }

  const fetchAccountHistory = async (accountCookie: string) => {
    try {
      const data = await accountApi.getAccountHistory(accountCookie)
      accountHistory.value = data
      return data
    } catch (error) {
      console.error('获取账户历史失败:', error)
      return {}
    }
  }

  const fetchMonthProfit = async (accountCookie: string) => {
    try {
      const data = await accountApi.getMonthProfit(accountCookie)
      monthProfit.value = data
      return data
    } catch (error) {
      console.error('获取月度收益失败:', error)
      return {}
    }
  }

  const fetchTradeRecords = async (accountCookie: string) => {
    try {
      const data = await accountApi.getTradeRecords(accountCookie)
      tradeRecords.value = data
      return data
    } catch (error) {
      console.error('获取交易记录失败:', error)
      return []
    }
  }

  return {
    accountList,
    currentAccount,
    accountHistory,
    monthProfit,
    tradeRecords,
    accountInfo,
    fetchAccountList,
    fetchAccountHistory,
    fetchMonthProfit,
    fetchTradeRecords
  }
})
