/**
 * QuanDA Electron 主进程入口
 */

import { app, BrowserWindow, Menu, screen, shell, ipcMain } from 'electron'
import { join } from 'path'
import { existsSync } from 'fs'
import { createApplicationMenu } from './menu'
import { registerIpcHandlers } from './ipc'
import { ProcessManager } from './lib/process-manager'
import { getUserDataPath, getLogsPath } from './lib/paths'
import { IPC_CHANNELS } from '@quanda/shared'

let mainWindow: BrowserWindow | null = null
let processManager: ProcessManager | null = null

/**
 * 确保窗口在屏幕范围内
 */
function ensureWindowOnScreen(win: BrowserWindow): void {
  const bounds = win.getBounds()
  const displays = screen.getAllDisplays()
  const centerX = bounds.x + bounds.width / 2
  const centerY = bounds.y + bounds.height / 2
  const isOnScreen = displays.some((display) => {
    const { x, y, width, height } = display.workArea
    return centerX >= x && centerX <= x + width && centerY >= y && centerY <= y + height
  })
  if (!isOnScreen) {
    const primary = screen.getPrimaryDisplay()
    const { x, y, width, height } = primary.workArea
    win.setBounds({
      x: x + Math.round((width - bounds.width) / 2),
      y: y + Math.round((height - bounds.height) / 2),
      width: bounds.width,
      height: bounds.height,
    })
    console.log('[窗口] 窗口已重新定位到主显示器')
  }
}

function getIconPath(): string {
  const resourcesDir = join(__dirname, 'resources')
  if (process.platform === 'darwin') {
    return join(resourcesDir, 'icon.icns')
  } else if (process.platform === 'win32') {
    return join(resourcesDir, 'icon.ico')
  } else {
    return join(resourcesDir, 'icon.png')
  }
}

function createWindow(): void {
  const iconPath = getIconPath()
  const iconExists = existsSync(iconPath)

  if (!iconExists) {
    console.warn('App icon not found at:', iconPath)
  }

  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    icon: iconExists ? iconPath : undefined,
    show: false,
    webPreferences: {
      preload: join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
      webSecurity: false, // 开发模式需要
    },
    titleBarStyle: 'default',
  })

  // 加载渲染进程
  const isDev = !app.isPackaged
  if (isDev) {
    mainWindow.loadURL('http://localhost:3000')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(join(__dirname, 'renderer', 'index.html'))
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow?.show()
  })

  // 拦截外部链接
  mainWindow.webContents.on('will-navigate', (event, url) => {
    if (isDev && url.startsWith('http://localhost:')) return
    event.preventDefault()
    if (url.startsWith('http://') || url.startsWith('https://')) {
      shell.openExternal(url)
    }
  })

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http://') || url.startsWith('https://')) {
      shell.openExternal(url)
    }
    return { action: 'deny' }
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

/**
 * 初始化应用
 */
async function initializeApp() {
  console.log('[初始化] QuanDA 桌面应用启动中...')
  console.log('[初始化] 用户数据目录:', getUserDataPath())
  console.log('[初始化] 日志目录:', getLogsPath())

  // 创建进程管理器
  processManager = new ProcessManager()

  // 注册 IPC 处理器
  registerIpcHandlers(ipcMain, processManager)

  // 创建应用菜单
  const menu = createApplicationMenu()
  Menu.setApplicationMenu(menu)
}

/**
 * 启动后台服务
 */
async function startBackendServices() {
  console.log('[后台服务] 启动数据库和后端服务...')

  try {
    // 启动 MongoDB
    await processManager?.startDatabase('mongo')
    await new Promise(resolve => setTimeout(resolve, 2000))

    // 启动 ClickHouse
    await processManager?.startDatabase('clickhouse')
    await new Promise(resolve => setTimeout(resolve, 1000))

    // 启动 Redis
    await processManager?.startDatabase('redis')
    await new Promise(resolve => setTimeout(resolve, 1000))

    // 启动 Python 后端
    await processManager?.startBackend()

    console.log('[后台服务] 所有服务启动完成')
  } catch (error) {
    console.error('[后台服务] 启动失败:', error)
  }
}

/**
 * 停止后台服务
 */
async function stopBackendServices() {
  console.log('[后台服务] 停止所有服务...')
  await processManager?.stopAll()
  console.log('[后台服务] 所有服务已停止')
}

// ============================================
// 应用生命周期
// ============================================

app.whenReady().then(async () => {
  await initializeApp()
  createWindow()

  // 启动后台服务
  await startBackendServices()

  app.on('activate', () => {
    if (!mainWindow || mainWindow.isDestroyed()) {
      createWindow()
    } else {
      mainWindow.show()
      mainWindow.focus()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', async () => {
  // 停止所有后台服务
  await stopBackendServices()
})

// 导出用于测试
export { mainWindow, processManager }
