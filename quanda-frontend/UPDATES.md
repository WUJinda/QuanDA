# 🔧 问题修复：404 错误

## 问题描述

前端报错：
```
Failed to load resource: the server responded with a status of 404 (Not Found)
/api/future/list:1
```

## 根本原因

1. **后端缺少 API 接口**: QuanDA 原本只提供 Python 函数，没有 RESTful API
2. **前端调用不存在的接口**: 前端尝试调用 `/future/list` 等接口，但后端未实现

## 解决方案

### ✅ 已完成的修复

#### 1. 创建数据接口 Handler

新建文件 `QuanDA/QAWebServer/datahandler.py`:

```python
# 提供以下接口:
- QAFutureListHandler      # 期货列表
- QAFutureDayHandler       # 期货日线数据
- QAFutureMinHandler       # 期货分钟数据
- QAFutureRealtimeHandler  # 期货实时数据
```

#### 2. 注册路由

修改 `QuanDA/QAWebServer/server.py`:

```python
handlers = [
    # ... 原有路由
    (r"/future/list", QAFutureListHandler),
    (r"/future/day", QAFutureDayHandler),
    (r"/future/min", QAFutureMinHandler),
    (r"/future/realtime", QAFutureRealtimeHandler)
]
```

#### 3. 配置数据源

使用 `tdx`（通达信）数据源，**无需预先下载数据**，实时获取。

---

## 使用方法

### 1. 启动后端服务

```bash
cd QuanDA
python -m QuanDA.QAWebServer.server
```

### 2. 测试 API（可选）

```bash
# 使用测试脚本
python test_api.py

# 或手动测试
curl http://localhost:8010/future/list
```

### 3. 启动前端

```bash
cd quantaxis-frontend
npm run dev
```

### 4. 访问应用

打开浏览器访问 http://localhost:3000

---

## API 接口文档

### 1. 获取期货列表

```
GET /future/list
```

**响应**:
```json
{
  "status": 200,
  "res": ["IF2512", "IC2512", "IH2512", ...]
}
```

### 2. 获取期货日线数据

```
GET /future/day?code=IF2512&start=2024-01-01&end=2024-12-31&frequence=day
```

**参数**:
- `code`: 期货代码
- `start`: 开始日期
- `end`: 结束日期
- `frequence`: 周期（day/week/month）

**响应**:
```json
{
  "status": 200,
  "res": [
    {
      "date": "2024-01-01",
      "open": 4500.0,
      "high": 4520.0,
      "low": 4480.0,
      "close": 4510.0,
      "volume": 125000
    },
    ...
  ]
}
```

### 3. 获取期货分钟数据

```
GET /future/min?code=IF2512&start=2024-01-01&end=2024-01-31&frequence=5min
```

**参数**:
- `code`: 期货代码
- `start`: 开始日期
- `end`: 结束日期
- `frequence`: 周期（1min/5min/15min/30min/60min）

### 4. 获取期货实时数据

```
GET /future/realtime?code=IF2512
```

**参数**:
- `code`: 期货代码

---

## 数据说明

### 数据源：TDX（通达信）

**优点**:
- ✅ 无需预先下载数据
- ✅ 实时从服务器获取
- ✅ 支持多种市场（期货、股票、指数）
- ✅ 免费使用

**注意事项**:
- ⚠️ 需要网络连接
- ⚠️ 首次查询可能较慢（3-10秒）
- ⚠️ 建议查询时间范围不要太大

### 可选：使用 MongoDB 缓存

如需更快的查询速度，可以将数据保存到 MongoDB：

```python
import QuanDA as QA

# 保存期货列表
QA.QA_SU_save_future_list()

# 保存期货日线数据
QA.QA_SU_save_future_day()
```

详见 [数据初始化指南](./docs/DATA_INIT.md)

---

## 故障排查

### 问题 1: 后端启动失败

**错误**: `ModuleNotFoundError: No module named 'QuanDA.QAWebServer.datahandler'`

**解决**:
```bash
# 重新安装 QuanDA
cd QuanDA
pip install -e .
```

### 问题 2: 期货列表为空

**原因**: TDX 服务器连接失败

**解决**:
1. 检查网络连接
2. 重启后端服务
3. 查看后端控制台错误信息

### 问题 3: 数据加载很慢

**原因**: 首次从 TDX 获取数据需要时间

**解决**:
1. 减小查询日期范围
2. 使用 MongoDB 缓存数据
3. 使用更大的周期（日线而非分钟线）

---

## 测试清单

- [x] 后端 API 接口创建
- [x] 路由注册
- [x] 数据源配置（TDX）
- [x] 错误处理
- [x] CORS 配置
- [x] 测试脚本
- [x] 文档更新

---

## 相关文档

- [数据初始化指南](./docs/DATA_INIT.md) - 如何初始化数据
- [故障排查指南](./docs/TROUBLESHOOTING.md) - 常见问题解决
- [快速开始](./docs/QUICKSTART.md) - 快速上手指南

---

## 总结

✅ **问题已解决**！

现在可以：
1. 启动后端服务
2. 启动前端应用
3. 正常使用所有功能

数据会实时从通达信服务器获取，无需预先下载！

---

**更新时间**: 2024
**状态**: ✅ 已修复
