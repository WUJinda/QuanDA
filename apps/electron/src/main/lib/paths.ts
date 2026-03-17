/**
 * 用户数据路径管理
 */

import { app } from 'electron'
import { join } from 'path'

/**
 * 获取用户数据目录
 */
export function getUserDataPath(): string {
  return app.getPath('userData')
}

/**
 * 获取数据目录
 */
export function getDataPath(): string {
  return join(getUserDataPath(), 'data')
}

/**
 * 获取日志目录
 */
export function getLogsPath(): string {
  return join(getUserDataPath(), 'logs')
}

/**
 * 获取配置目录
 */
export function getConfigPath(): string {
  return join(getUserDataPath(), 'config')
}

/**
 * 获取数据库数据目录
 */
export function getDatabasePath(type: 'mongo' | 'clickhouse' | 'redis'): string {
  return join(getDataPath(), type)
}

/**
 * 确保所有必需目录存在
 */
export function ensureDirectories(): void {
  const fs = require('fs')
  const paths = [
    getUserDataPath(),
    getDataPath(),
    getLogsPath(),
    getConfigPath(),
    getDatabasePath('mongo'),
    getDatabasePath('clickhouse'),
    getDatabasePath('redis'),
  ]

  for (const path of paths) {
    if (!fs.existsSync(path)) {
      fs.mkdirSync(path, { recursive: true })
      console.log('[目录] 创建目录:', path)
    }
  }
}
