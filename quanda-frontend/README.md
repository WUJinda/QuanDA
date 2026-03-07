# QuanDA Frontend

Vue 3 + TypeScript 可视化前端项目，用于展示期货行情数据和技术分析。

## 🚀 快速开始

### 前置要求

- Node.js 16+
- npm 或 yarn
- QuanDA 后端服务运行中

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

## 📁 项目结构

```
quantaxis-frontend/
├── src/
│   ├── components/        # 组件库
│   │   ├── Layout/       # 布局组件
│   │   ├── Charts/       # 图表组件（K线图、BOLL等）
│   │   ├── Market/       # 市场组件
│   │   ├── Account/      # 账户组件
│   │   └── Common/       # 通用组件
│   ├── views/            # 页面视图
│   │   ├── Dashboard/    # 仪表盘
│   │   ├── Market/       # 市场行情
│   │   ├── Futures/      # 期货交易
│   │   ├── Account/      # 账户管理
│   │   ├── Backtest/     # 回测系统
│   │   └── Strategy/     # 策略管理
│   ├── stores/           # Pinia 状态管理
│   ├── api/              # API 接口层
│   ├── types/            # TypeScript 类型定义
│   └── router/           # 路由配置
├── docs/                 # 项目文档
└── public/              # 静态资源
```

## ✨ 核心功能

### 1. K线图表
- 实时期货K线展示
- 支持多种周期切换（1分钟-日线）
- 自定义周期设置

### 2. BOLL 指标
- 布林带三轨显示（上轨、中轨、下轨）
- 可切换显示/隐藏
- 20周期，2倍标准差

### 3. 技术指标
- MA5/MA10/MA20 移动平均线
- MACD 指标
- KDJ 指标

### 4. 实时行情
- 最新价、涨跌幅
- 开盘价、最高价、最低价
- 成交量数据

## 🔧 配置说明

### 环境变量

`.env.development`:
```env
VITE_API_BASE_URL=http://localhost:8010
```

`.env.production`:
```env
VITE_API_BASE_URL=https://your-production-api.com
```

### API 接口

后端接口地址：`http://localhost:8010`

主要接口：
- `GET /future/list` - 获取期货列表
- `GET /future/day` - 获取日线数据
- `GET /future/min` - 获取分钟数据
- `GET /future/realtime` - 获取实时数据

## 📚 文档

详细文档请查看 [docs/](./docs/) 目录：

- [快速开始](./docs/QUICKSTART.md)
- [功能特性](./docs/FEATURES.md)
- [数据初始化](./docs/DATA_INIT.md)
- [故障排查](./docs/TROUBLESHOOTING.md)
- [部署指南](./docs/DEPLOYMENT.md)

## 🛠️ 技术栈

- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI 库**: Element Plus
- **图表库**: ECharts
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP 客户端**: Axios

## 📝 开发指南

### 添加新页面

1. 在 `src/views/` 创建页面组件
2. 在 `src/router/index.ts` 添加路由
3. 在侧边栏菜单中添加入口

### 添加新组件

1. 在 `src/components/` 对应目录创建组件
2. 在 `src/components/index.ts` 导出组件
3. 在需要的地方导入使用

### API 调用

```typescript
import { useMarketStore } from '@/stores/market'

const marketStore = useMarketStore()
const data = await marketStore.fetchFutureData(code, start, end)
```

## 🐛 故障排查

### 问题：404 错误

确保后端服务已启动：
```bash
cd QuanDA
python -m QuanDA.QAWebServer.server
```

### 问题：依赖安装失败

清除缓存重新安装：
```bash
rm -rf node_modules package-lock.json
npm install
```

### 问题：TypeScript 错误

检查类型定义文件是否完整：
```bash
npm run type-check
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**维护者**: QuanDA Team  
**最后更新**: 2024
