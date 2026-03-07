# QuanDA 脚本工具

本目录包含 QuanDA 项目的实用脚本工具。

## 📁 脚本列表

### 1. test_api.py - API 测试脚本

测试 QuanDA 后端 API 接口是否正常工作。

**使用方法**:
```bash
python scripts/test_api.py
```

**功能**:
- 测试根路径
- 测试期货列表接口
- 测试期货日线数据接口
- 测试 QIFI 账户接口

**要求**:
- 后端服务已启动（http://localhost:8010）
- 安装 requests 库：`pip install requests`

---

### 2. init_data.py - 数据初始化脚本

初始化和更新 MongoDB 中的市场数据。

**使用方法**:

```bash
# 初始化数据（首次使用）
python scripts/init_data.py

# 更新最近7天数据
python scripts/init_data.py update

# 更新最近30天数据
python scripts/init_data.py update 30
```

**功能**:
- 保存期货列表到 MongoDB
- 保存期货日线数据（最近一年）
- 可选：保存期货分钟数据

**要求**:
- MongoDB 已启动
- QuanDA 已安装
- 网络连接正常（用于从 TDX 获取数据）

**数据量说明**:
- 期货列表：< 1MB
- 期货日线（一年）：约 100-500MB
- 期货分钟数据：数据量很大（GB级别），建议按需保存

---

## 🚀 快速开始

### 首次使用

1. **启动 MongoDB**:
```bash
# Windows
net start MongoDB

# Linux/Mac
sudo systemctl start mongod
```

2. **初始化数据**:
```bash
python scripts/init_data.py
```

3. **测试 API**:
```bash
# 启动后端
python -m QuanDA.QAWebServer.server

# 新终端测试
python scripts/test_api.py
```

---

## 📝 定时任务

### Windows 任务计划程序

每天 18:00 更新数据：
```bash
schtasks /create /tn "QuanDA数据更新" /tr "python C:\path\to\scripts\init_data.py update" /sc daily /st 18:00
```

### Linux Crontab

每天 18:00 更新数据：
```bash
# 编辑 crontab
crontab -e

# 添加以下行
0 18 * * * cd /path/to/QuanDA && python scripts/init_data.py update
```

---

## 🔧 故障排查

### 问题 1: ModuleNotFoundError

**错误**: `ModuleNotFoundError: No module named 'QuanDA'`

**解决**:
```bash
# 安装 QuanDA
pip install -e .
```

### 问题 2: MongoDB 连接失败

**错误**: `pymongo.errors.ServerSelectionTimeoutError`

**解决**:
```bash
# 检查 MongoDB 状态
mongo --eval "db.adminCommand('ping')"

# 启动 MongoDB
# Windows: net start MongoDB
# Linux: sudo systemctl start mongod
```

### 问题 3: 数据初始化很慢

**原因**: 从 TDX 服务器获取数据需要时间

**建议**:
- 首次初始化可能需要 10-30 分钟
- 确保网络连接稳定
- 可以先只初始化期货列表，按需获取其他数据

---

## 📊 数据存储位置

### MongoDB 数据库

- 数据库名：`quanda`
- 集合：
  - `future_list` - 期货列表
  - `future_day` - 期货日线数据
  - `future_min` - 期货分钟数据

### 查看数据

```bash
# 进入 MongoDB Shell
mongo

# 切换到 quanda 数据库
use quanda

# 查看期货列表
db.future_list.find().limit(10)

# 查看期货日线数据
db.future_day.find({code: 'IF2512'}).limit(10)

# 统计数据量
db.future_day.count()
```

---

## 🎯 最佳实践

1. **首次使用**:
   - 先初始化期货列表
   - 再初始化最近一年的日线数据
   - 按需初始化分钟数据

2. **日常维护**:
   - 每天更新最近7天的数据
   - 每周完整更新一次
   - 定期清理过期数据

3. **性能优化**:
   - 使用 MongoDB 索引
   - 限制查询时间范围
   - 使用数据分页

---

## 📞 获取帮助

- [数据初始化指南](../quanda-frontend/docs/DATA_INIT.md)
- [故障排查指南](../quanda-frontend/docs/TROUBLESHOOTING.md)
- [QuanDA 文档](https://github.com/QuanDA/QuanDA)

---

**维护者**: QuanDA Team
**最后更新**: 2024
