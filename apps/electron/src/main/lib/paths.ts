/**
 * 用户数据路径管理
 */

import { app } from 'electron'
import { join } from 'path'

/**
 * 获取用户数据目录
 */
export function getUserDataPath(): string {
  const path = app.getPath('userData')
  console.log(`[路径] 用户数据目录: ${path}`)
  return path
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
 * 获取数据库可执行文件路径
 * 在开发环境使用系统安装的版本，在生产环境使用打包的绿色版
 */
export function getDatabaseExecutable(type: 'mongo' | 'clickhouse' | 'redis'): string | null {
  const isDev = !app.isPackaged

  console.log(`[路径] 查找数据库可执行文件: ${type}`)
  console.log(`[路径] app.isPackaged: ${app.isPackaged}`)
  console.log(`[路径] process.resourcesPath: ${process.resourcesPath}`)

  if (isDev) {
    // 开发环境：假设系统已安装数据库，返回 null（使用系统路径）
    console.log(`[路径] 开发环境，使用系统安装的数据库`)
    return null
  }

  // 生产环境：使用打包的绿色版
  const resourcesPath = join(process.resourcesPath, 'databases')
  console.log(`[路径] 生产环境，数据库资源目录: ${resourcesPath}`)

  const fs = require('fs')

  switch (type) {
    case 'mongo': {
      // MongoDB: 查找 mongodb-win32-* 目录下的 bin/mongod.exe
      const mongodbDir = join(resourcesPath, 'mongodb')
      console.log(`[路径] MongoDB 目录: ${mongodbDir}`)
      console.log(`[路径] MongoDB 目录是否存在: ${fs.existsSync(mongodbDir)}`)
      if (fs.existsSync(mongodbDir)) {
        const dirs = fs.readdirSync(mongodbDir)
        console.log(`[路径] MongoDB 目录内容:`, dirs)
        const mongoVersionDir = dirs.find((dir: string) => dir.startsWith('mongodb-win32-'))
        console.log(`[路径] 找到 MongoDB 版本目录: ${mongoVersionDir}`)
        if (mongoVersionDir) {
          const execPath = join(mongodbDir, mongoVersionDir, 'bin', 'mongod.exe')
          console.log(`[路径] MongoDB 可执行文件路径: ${execPath}`)
          console.log(`[路径] MongoDB 可执行文件是否存在: ${fs.existsSync(execPath)}`)
          if (fs.existsSync(execPath)) {
            return execPath
          }
        }
      }
      console.log(`[路径] MongoDB 可执行文件未找到`)
      return null
    }
    case 'clickhouse':
      // ClickHouse: clickhouse-server.exe
      const clickhousePath = join(resourcesPath, 'clickhouse', 'clickhouse-server.exe')
      console.log(`[路径] ClickHouse 可执行文件路径: ${clickhousePath}`)
      console.log(`[路径] ClickHouse 可执行文件是否存在: ${fs.existsSync(clickhousePath)}`)
      return clickhousePath
    case 'redis':
      // Redis: redis-server.exe
      const redisPath = join(resourcesPath, 'redis', 'redis-server.exe')
      console.log(`[路径] Redis 可执行文件路径: ${redisPath}`)
      console.log(`[路径] Redis 可执行文件是否存在: ${fs.existsSync(redisPath)}`)
      return redisPath
    default:
      return null
  }
}

/**
 * 获取数据库配置文件路径
 */
export function getDatabaseConfigPath(type: 'mongo' | 'clickhouse' | 'redis'): string {
  return join(getConfigPath(), `${type}.conf`)
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

/**
 * 验证数据库资源文件
 */
export function validateDatabaseResources(): Record<string, { found: boolean; path: string }> {
  console.log('[验证] 验证数据库资源文件...')
  const result: Record<string, { found: boolean; path: string }> = {}

  const types: Array<'mongo' | 'clickhouse' | 'redis'> = ['mongo', 'clickhouse', 'redis']
  for (const type of types) {
    const execPath = getDatabaseExecutable(type)
    result[type] = {
      found: execPath !== null,
      path: execPath || '未找到'
    }
  }

  console.log('[验证] 数据库资源验证结果:', result)
  return result
}
