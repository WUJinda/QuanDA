/**
 * QuanDA 应用菜单
 */

import { app, Menu, shell, BrowserWindow } from 'electron'

/**
 * 创建应用菜单
 */
export function createApplicationMenu(): Menu {
  const template: Electron.MenuItemConstructorOptions[] = [
    {
      label: '文件',
      submenu: [
        {
          label: '新建策略',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            // TODO: 实现新建策略功能
            console.log('新建策略')
          }
        },
        {
          label: '打开',
          accelerator: 'CmdOrCtrl+O',
          click: () => {
            // TODO: 实现打开功能
            console.log('打开')
          }
        },
        { type: 'separator' },
        {
          label: '设置',
          accelerator: 'CmdOrCtrl+,',
          click: () => {
            // TODO: 打开设置页面
            console.log('设置')
          }
        },
        { type: 'separator' },
        { role: 'quit', label: '退出' }
      ]
    },
    {
      label: '编辑',
      submenu: [
        { role: 'undo', label: '撤销' },
        { role: 'redo', label: '重做' },
        { type: 'separator' },
        { role: 'cut', label: '剪切' },
        { role: 'copy', label: '复制' },
        { role: 'paste', label: '粘贴' },
        { role: 'selectall', label: '全选' }
      ]
    },
    {
      label: '视图',
      submenu: [
        { role: 'reload', label: '重新加载' },
        { role: 'forceReload', label: '强制重新加载' },
        { role: 'toggleDevTools', label: '开发者工具' },
        { type: 'separator' },
        { role: 'resetZoom', label: '重置缩放' },
        { role: 'zoomIn', label: '放大' },
        { role: 'zoomOut', label: '缩小' },
        { type: 'separator' },
        { role: 'togglefullscreen', label: '全屏' }
      ]
    },
    {
      label: '窗口',
      submenu: [
        { role: 'minimize', label: '最小化' },
        { role: 'close', label: '关闭' },
        { type: 'separator' },
        { role: 'front', label: '全部置于顶层' }
      ]
    },
    {
      label: '帮助',
      submenu: [
        {
          label: '文档',
          click: () => {
            shell.openExternal('https://github.com/WUJinda/QuanDA')
          }
        },
        {
          label: '报告问题',
          click: () => {
            shell.openExternal('https://github.com/WUJinda/QuanDA/issues')
          }
        },
        { type: 'separator' },
        {
          label: '关于 QuanDA',
          click: () => {
            // TODO: 显示关于对话框
            console.log('关于 QuanDA')
          }
        }
      ]
    }
  ]

  // macOS 特殊菜单
  if (process.platform === 'darwin') {
    template.unshift({
      label: app.getName(),
      submenu: [
        { role: 'about', label: '关于 QuanDA' },
        { type: 'separator' },
        { role: 'services', label: '服务' },
        { type: 'separator' },
        { role: 'hide', label: '隐藏 QuanDA' },
        { role: 'hideOthers', label: '隐藏其他' },
        { role: 'unhide', label: '显示全部' },
        { type: 'separator' },
        { role: 'quit', label: '退出 QuanDA' }
      ]
    })
  }

  return Menu.buildFromTemplate(template)
}
