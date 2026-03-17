# QuanDA - Modern Quantitative Trading Framework

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Rust](https://img.shields.io/badge/Rust-High%20Performance%20Core-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

**High-Performance Quantitative Trading Framework for Professional Traders**

[中文](README_ZH.md) | [English](README_EN.md)

</div>

## 🚀 Core Features

### ⚡ Extreme Performance
- **Rust Core Engine**: 100x performance improvement
- **Zero-Copy Data Transfer**: 5-10x faster cross-language communication
- **Multi-Market Support**: A-shares, futures, cryptocurrencies

### 🎯 Key Capabilities
- **Multi-Market Data**: Stocks, futures, options, cryptocurrencies
- **High-Performance Backtesting**: Rust core engine, second-level backtesting for 10-year data
- **Unified Account System**: QIFI protocol, cross-platform account management
- **Real-time Market Data**: Millisecond-level data streaming with Level2 support
- **Strategy Development**: Python API + Visual Strategy Editor

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/WUJinda/QuanDA.git
cd QuanDA

# Basic installation
pip install -e .

# Full installation with Rust core (recommended)
pip install -e .[rust]
```

### Quick Example

```python
import quanda as qa
from quanda.QARSBridge import QARSAccount

# Create high-performance account
account = QARSAccount("my_strategy", init_cash=1000000)

# Execute trades
account.buy("000001.SZ", price=10.5, volume=1000)
account.sell("000001.SZ", price=11.2, volume=500)

# Get real-time positions
positions = account.get_positions()
print(f"Current positions: {positions}")
```

## 🏗️ Architecture

```
QuanDA/
├── quanda/                    # Python core library
│   ├── QARSBridge/           # Rust core bridge
│   ├── QIFI/                 # Unified account system
│   ├── QAFetch/              # Data fetching
│   ├── QAStrategy/           # Strategy engine
│   └── QAWebServer/          # Web services
├── quanda-frontend/          # Frontend interface
├── apps/electron/            # Desktop client
└── packages/                 # Microservices architecture
```

## 📊 Performance Comparison

| Operation | Traditional Python | QuanDA | Improvement |
|-----------|-------------------|---------|-------------|
| Account Creation | 50ms | 0.5ms | 100x |
| 10-Year Backtest | 30s | 3s | 10x |
| Memory Usage | 100% | 10% | 90% ↓ |
| Data Conversion | 100ms | 10ms | 10x |

## 📊 Supported Markets

| Market | Support Level | Data Sources |
|--------|---------------|--------------|
| A-Shares | ✅ Full Support | TDX/EastMoney |
| Futures | ✅ Full Support | CTP/SimNow |
| Cryptocurrencies | ✅ Full Support | Major Exchange APIs |
| Options | ⚠️ Partial Support | TDX/CFFEX |

## 🛠️ Tech Stack

**Core Languages**
- Python 3.9-3.13
- Rust (QARS2 High-Performance Core)

**Key Dependencies**
- `pandas>=2.0.0` - Data processing
- `numpy>=1.26.0` - Numerical computing
- `pyarrow>=15.0.0` - Zero-copy communication
- `tornado>=6.4.0` - Web services

**Databases**
- MongoDB 4.0+ (Document storage)
- ClickHouse 20.0+ (Time-series data)

## 🚀 Getting Started

1. **Environment Setup**
```bash
# Create virtual environment
conda create -n quanda python=3.11
conda activate quanda
```

2. **Install Dependencies**
```bash
# Basic installation
pip install -e .

# Full installation (recommended)
pip install -e .[rust,performance]
```

3. **Run Example**
```python
import quanda as qa

# Initialize account
account = qa.create_account("my_strategy", 1000000)

# Fetch market data
data = qa.fetch_data("000001.SZ", "2024-01-01", "2024-12-31")

# Run strategy
strategy = qa.Strategy("my_strategy")
results = strategy.backtest(data)
```

## 📈 Web Interface

QuanDA provides a modern web interface:

```bash
# Start web interface
python -m quanda.web

# Access at http://localhost:8080
```

## 🎯 Key Advantages

1. **Exceptional Performance**: Rust core provides 100x performance boost
2. **Full Market Coverage**: A-shares, futures, cryptocurrencies
3. **Easy to Use**: Python API + Visual interface
4. **Enterprise Ready**: Distributed backtesting, live trading support
5. **Open Source**: MIT license, business-friendly

## 🔧 Development

```bash
# Clone repository
git clone https://github.com/WUJinda/QuanDA.git
cd QuanDA

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest tests/

# Build documentation
make docs
```

## 📚 Documentation

- [Quick Start](docs/quickstart.md)
- [API Documentation](docs/api.md)
- [Strategy Development Guide](docs/strategy_guide.md)
- [Performance Optimization](docs/performance.md)

## 🤝 Contributing

Issues and PRs are welcome! Please read the [Contributing Guide](CONTRIBUTING.md).

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

<div align="center">
  <p>Created and maintained by <a href="https://github.com/WUJinda">WUJinda</a></p>
  <p>⭐ If you find this project helpful, please give it a Star!</p>
</div>