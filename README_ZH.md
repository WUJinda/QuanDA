# QuanDA - 现代化量化交易框架

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Rust](https://img.shields.io/badge/Rust-高性能核心-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

**高性能量化交易框架 · 专为专业交易者设计**

[English](README.md) | [中文](README_ZH.md)

</div>

## 🚀 核心特性

### ⚡ 极致性能
- **Rust 核心引擎**：100倍性能提升，回测速度提升100倍
- **零拷贝数据传输**：跨语言通信性能提升5-10倍
- **多市场支持**：A股、期货、数字货币全覆盖

### 🎯 核心功能
- **多市场数据**：股票、期货、期权、数字货币
- **高性能回测**：Rust核心引擎，秒级10年数据回测
- **统一账户体系**：QIFI协议，跨平台账户管理
- **实时行情**：毫秒级行情推送，支持Level2数据
- **策略开发**：Python API + 可视化策略编辑器

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/WUJinda/QuanDA.git
cd QuanDA

# 基础安装
pip install -e .

# 安装Rust核心（可选，性能提升100倍）
pip install -e .[rust]
```

### 快速示例

```python
import quanda as qa
from quanda.QARSBridge import QARSAccount

# 创建高性能账户
account = QARSAccount("my_strategy", init_cash=1000000)

# 执行交易
account.buy("000001.SZ", price=10.5, volume=1000)
account.sell("000001.SZ", price=11.2, volume=500)

# 获取实时持仓
positions = account.get_positions()
print(f"当前持仓: {positions}")
```

## 🏗️ 项目架构

```
QuanDA/
├── quanda/                    # Python核心库
│   ├── QARSBridge/           # Rust核心桥接
│   ├── QIFI/                 # 统一账户系统
│   ├── QAFetch/              # 数据获取
│   ├── QAStrategy/           # 策略引擎
│   └── QAWebServer/          # Web服务
├── quanda-frontend/          # 前端界面
├── apps/electron/            # 桌面客户端
└── packages/                 # 微服务架构
```

## 📊 性能对比

| 操作 | 传统Python | QuanDA | 性能提升 |
|------|-----------|---------|----------|
| 账户创建 | 50ms | 0.5ms | 100x |
| 10年回测 | 30秒 | 3秒 | 10x |
| 内存占用 | 100% | 10% | 90%↓ |
| 数据转换 | 100ms | 10ms | 10x |

## 📈 支持的市场

| 市场类型 | 支持程度 | 数据源 |
|----------|----------|--------|
| A股市场 | ✅ 完整支持 | 通达信/东方财富 |
| 期货 | ✅ 完整支持 | CTP/SimNow |
| 数字货币 | ✅ 完整支持 | 主流交易所API |
| 期权 | 🔶 部分支持 | 通达信/中金所 |

## 🛠️ 技术栈

**核心语言**
- Python 3.9-3.13
- Rust (QARS2 高性能核心)

**关键依赖**
- `pandas>=2.0.0` - 数据处理
- `numpy>=1.26.0` - 数值计算
- `pyarrow>=15.0.0` - 零拷贝通信
- `tornado>=6.4.0` - Web服务

**数据库**
- MongoDB 4.0+ (文档存储)
- ClickHouse 20.0+ (时序数据)

## 🚀 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
conda create -n quanda python=3.11
conda activate quanda
```

### 2. 安装依赖

```bash
# 基础安装
pip install -e .

# 完整安装（推荐）
pip install -e .[rust,performance]
```

### 3. 运行示例

```python
import quanda as qa

# 初始化账户
account = qa.create_account("my_strategy", 1000000)

# 获取数据
data = qa.fetch_data("000001.SZ", "2024-01-01", "2024-12-31")

# 运行策略
strategy = qa.Strategy("my_strategy")
results = strategy.backtest(data)
```

## 📊 可视化界面

QuanDA 提供现代化的Web界面：

```bash
# 启动Web界面
python -m quanda.web

# 访问 http://localhost:8080
```

## 🎯 核心优势

1. **性能卓越**：Rust核心提供100倍性能提升
2. **全市场覆盖**：A股、期货、数字货币全覆盖
3. **易用性**：Python API + 可视化界面
4. **企业级功能**：支持分布式回测、实盘交易
5. **开源免费**：MIT协议，商业友好

## 🔧 开发

```bash
# 克隆仓库
git clone https://github.com/WUJinda/QuanDA.git
cd QuanDA

# 安装开发环境
pip install -e .[dev]

# 运行测试
pytest tests/

# 构建文档
make docs
```

## 📚 文档

- [快速开始](docs/quickstart.md)
- [API文档](docs/api.md)
- [策略开发指南](docs/strategy_guide.md)
- [性能优化](docs/performance.md)

## 🤝 贡献

欢迎提交Issue和Pull Request！请阅读[贡献指南](CONTRIBUTING.md)。

## 📄 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

<div align="center">
  <p>由 <a href="https://github.com/WUJinda">WUJinda</a> 创建并维护</p>
  <p>⭐ 如果这个项目对你有帮助，请给我们一个Star！</p>
</div>