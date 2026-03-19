/**
 * 配置 API
 * 用于管理应用配置信息
 */

import request from './request'

export interface AppConfig {
  // MongoDB 配置
  mongodb: {
    host: string
    port: number
    enabled: boolean
  }
  // Python 配置
  python: {
    path: string
  }
  // 后端配置
  backend: {
    host: string
    port: number
  }
  // 演示模式
  demoMode: boolean
}

// 默认配置
export const defaultConfig: AppConfig = {
  mongodb: {
    host: 'localhost',
    port: 27017,
    enabled: false
  },
  python: {
    path: 'D:\\Programs\\Python\\Python313\\python.exe'
  },
  backend: {
    host: 'localhost',
    port: 8010
  },
  demoMode: true
}

/**
 * 获取配置
 */
export async function getConfig(): Promise<AppConfig> {
  try {
    const stored = localStorage.getItem('quanda_config')
    if (stored) {
      return JSON.parse(stored)
    }
  } catch (error) {
    console.error('[Config] 获取配置失败:', error)
  }
  return { ...defaultConfig }
}

/**
 * 保存配置
 */
export async function saveConfig(config: Partial<AppConfig>): Promise<void> {
  try {
    const current = await getConfig()
    const merged = { ...current, ...config }
    localStorage.setItem('quanda_config', JSON.stringify(merged))
  } catch (error) {
    console.error('[Config] 保存配置失败:', error)
    throw error
  }
}

/**
 * 重置配置为默认值
 */
export async function resetConfig(): Promise<void> {
  localStorage.removeItem('quanda_config')
}

export const configApi = {
  getConfig,
  saveConfig,
  resetConfig
}
