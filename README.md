<div align="center">

# QuanDA

**现代化量化交易框架 · 高性能 · 易扩展**

[Python 3.9+](https://www.python.org/) · [MIT License](./LICENSE)

[![GitHub stars](https://img.shields.io/github/stars/WUJinda/QuanDA?style=social)](https://github.com/WUJinda/QuanDA/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/WUJinda/QuanDA?style=social)](https://github.com/WUJinda/QuanDA/network/members)

---

*Built with passion by [WUJinda](https://github.com/WUJinda)*

</div>

---

##  What is QuanDA?

QuanDA 是一个现代化的量化交易框架，专为专业交易者和开发者设计。它整合了 Rust 高性能核心与 Python 易用性，提供从数据获取、策略开发到回测交易的完整解决方案。

---

##  核心优势

| 特性 | 描述 | 性能提升 |
|------|------|---------|
|  **Rust 核心加速** | QARS2 高性能账户与回测引擎 | **100x** |
|  **零拷贝数据传输** | QADataSwap 跨语言通信 | **5-10x** |
|  **现代化技术栈** | Python 3.9-3.12 + 最新依赖 | 稳定可靠 |
|  **统一账户体系** | QIFI 协议兼容多语言 | 跨平台 |
|  **完整数据支持** | 股票/期货/期权/数字货币 | 全市场 |

---

##  快速开始

### 安装

```bash
git clone https://github.com/WUJinda/QuanDA.git
cd QuanDA

# 基础安装
pip install -e .

# 包含 Rust 组件（推荐）
pip install -e .[rust]
```

### 第一个策略

```python
import quanda as QA
from quanda.QARSBridge import QARSAccount

# 创建账户
account = QARSAccount("my_strategy", init_cash=1000000)

# 股票交易
account.buy("000001", 10.5, "2025-01-15", 1000)
account.sell("000001", 10.8, "2025-01-16", 500)

# 查询持仓
print(account.get_positions())
```

---

##  功能模块

### 数据层

```
QAFetch/      多市场数据获取
  ├── 股票行情
  ├── 期货行情
  ├── 期权行情
  └── 数字货币
```

### 账户层

```
QIFI/         统一账户协议
  ├── QARSAccount      Rust 高性能账户
  ├── QIFI Account     标准账户
  └── Position         仓位管理
```

### 策略层

```
QAStrategy/   策略回测
  ├── CTA 策略
  ├── 套利策略
  └── 自定义策略
```

### 数据存储

```
QASU/         数据管理
  ├── MongoDB      文档存储
  └── ClickHouse   列式存储
```

### 工具层

```
QAUtil/       工具函数
  ├── 交易日历
  ├── 时间处理
  └── 数据转换
```

### Web 服务

```
QAWebServer/  RESTful API
  ├── 行情服务
  ├── 账户管理
  └── 策略执行
```

---

##  性能对比

| 操作 | 传统 Python | QuanDA | 提升 |
|------|------------|----------------|------|
| 账户创建 | 50ms | 0.5ms | **100x** |
| 10年回测 | 30s | 3s | **10x** |
| 内存占用 | 100% | 10% | **90%↓** |
| 数据转换 | 100ms | 10ms | **10x** |

---

##  系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    应用层                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  策略    │  │  回测    │  │  实盘    │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    核心层                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ QIFI账户 │  │ 仓位管理 │  │ 订单管理 │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    加速层                                │
│  ┌──────────────────────────────────────────┐           │
│  │        QARS2 Rust 核心引擎               │           │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐ │           │
│  │  │ 账户系统 │  │ 回测引擎 │  │ 数据桥接 │ │           │
│  │  └─────────┘  └─────────┘  └─────────┘ │           │
│  └──────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    数据层                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ MongoDB  │  │ClickHouse│  │ 文件系统 │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
```

---

##  支持的市场

| 市场类型 | 支持程度 | 数据源 |
|---------|---------|--------|
| 中国 A股 | ✅ 完整支持 | 通达信/东方财富 |
| 股指期货 | ✅ 完整支持 | 通达信 |
| 商品期货 | ✅ 完整支持 | 通达信 |
| 期权 | ✅ 部分支持 | 通达信 |
| 数字货币 | ✅ 完整支持 | 主流交易所API |

---

##  技术栈

**核心语言**
- Python 3.9-3.12
- Rust (QARS2)

**关键依赖**
```
pandas      ≥2.0.0    # 数据处理
pymongo     ≥4.10.0   # MongoDB
pyarrow     ≥15.0.0   # 零拷贝数据
tornado     ≥6.4.0    # Web服务
```

**数据库**
- MongoDB 4.0+
- ClickHouse 20.0+ (可选)

---

##  项目结构

```
QuanDA/
├── quanda/
│   ├── QARSBridge/      # Rust 桥接层
│   ├── QADataBridge/    # 数据桥接
│   ├── QAFetch/         # 数据获取
│   ├── QIFI/            # 账户系统
│   ├── QAStrategy/      # 策略回测
│   ├── QAWebServer/     # Web服务
│   └── ...
├── quantaxis-frontend/  # 前端界面
├── scripts/             # 工具脚本
└── README.md
```

---

##  路线图

- [x] QARS2 Rust 核心集成
- [x] 零拷贝数据传输
- [x] Python 3.9-3.12 支持
- [ ] 完整期权支持
- [ ] 实时行情推送
- [ ] 分布式回测
- [ ] 前端交易界面

---

##  许可证

MIT License - 详见 [LICENSE](./LICENSE)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给一个 Star！**

Made with ❤️ by [WUJinda](https://github.com/WUJinda)

</div>
