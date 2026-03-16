# QuanDA 模块重命名快速参考

## 一键执行（推荐）

```bash
python rename_qa_to_qd.py
```

## 重命名映射表

```
QAAnalysis     → QDAnalysis      (分析模块)
QACmd          → QDCmd           (命令行模块)
QAData         → QDData          (数据模块)
QADataBridge   → QDDataBridge    (数据桥接)
QAEngine       → QDEngine        (引擎模块)
QAFactor       → QDFactor        (因子模块)
QAFetch        → QDFetch         (数据获取)
QAIndicator    → QDIndicator     (指标模块)
QAMarket       → QDMarket        (市场模块)
QAPubSub       → QDPubSub        (发布订阅)
QARSBridge     → QDRSBridge      (Rust桥接)
QASchedule     → QDSchedule      (调度模块)
QASetting      → QDSetting       (设置模块)
QAStrategy     → QDStrategy      (策略模块)
QASU           → QDSU            (存储工具)
QAUtil         → QDUtil          (工具模块)
QAWebServer    → QDWebServer     (Web服务器)
QIFI           → QIFI            (保持不变)
```

## 导入语句变化

```python
# 之前
from quanda.QAData import QA_DataStruct_Day
from quanda.QAFetch import QA_fetch_get_stock_day
from quanda.QAUtil import QA_util_code_tolist

# 之后
from quanda.QDData import QA_DataStruct_Day
from quanda.QDFetch import QA_fetch_get_stock_day
from quanda.QDUtil import QA_util_code_tolist
```

## 影响统计

- 📁 重命名目录: 17 个
- 📝 更新文件: ~119 个 Python 文件
- 🔄 导入语句: 数百条导入语句
- 📄 配置文件: setup.py, README.md

## 执行流程

```
1. 检查 git status (确保工作区干净)
   ↓
2. 执行 python rename_qa_to_qd.py
   ↓
3. 验证 git diff
   ↓
4. 提交 git commit
```

## 重要提示

⚠️ **类名/函数名不变**: 只重命名模块目录，类名和函数名仍使用 QA 前缀
✅ **Git 历史保留**: 使用 git mv 保持完整的版本历史
🔍 **自动更新**: 脚本会自动查找并更新所有导入语句

## 验证命令

```bash
# 查看重命名的目录
ls quanda/ | grep QD

# 查找未更新的导入（应该为空）
grep -r "from quanda\.QA" quanda/ | grep -v "QIFI"

# 测试导入
python -c "from quanda.QDData import QA_DataStruct_Day; print('✓ 成功')"
```

## 完成后清理

```bash
# 删除临时脚本和文档（可选）
rm rename_qa_to_qd.py
rm rename_qa_to_qd.sh
rm rename_qa_to_qd.bat
rm RENAME_GUIDE.md
rm RENAME_QUICK_REFERENCE.md
```

---

**需要帮助?** 查看详细指南: `RENAME_GUIDE.md`
