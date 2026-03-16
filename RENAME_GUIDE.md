# QuanDA 模块重命名指南

## 概述

本文档说明如何将 QuanDA 项目中的所有子模块从 `QA` 前缀重命名为 `QD` 前缀。

## 重命名范围

### 需要重命名的目录（17个）

| 原目录名 | 新目录名 | 说明 |
|---------|---------|------|
| QAAnalysis | QDAnalysis | 分析模块 |
| QACmd | QDCmd | 命令行模块 |
| QAData | QDData | 数据模块 |
| QADataBridge | QDDataBridge | 数据桥接模块 |
| QAEngine | QDEngine | 引擎模块 |
| QAFactor | QDFactor | 因子模块 |
| QAFetch | QDFetch | 数据获取模块 |
| QAIndicator | QDIndicator | 指标模块 |
| QAMarket | QDMarket | 市场模块 |
| QAPubSub | QDPubSub | 发布订阅模块 |
| QARSBridge | QDRSBridge | Rust桥接模块 |
| QASchedule | QDSchedule | 调度模块 |
| QASetting | QDSetting | 设置模块 |
| QAStrategy | QDStrategy | 策略模块 |
| QASU | QDSU | 存储工具模块 |
| QAUtil | QDUtil | 工具模块 |
| QAWebServer | QDWebServer | Web服务器模块 |

### 保持不变的目录

| 目录名 | 说明 |
|-------|------|
| QIFI | QIFI协议模块（特殊模块，保持不变） |

## 执行方法

### 方法一：使用 Python 脚本（推荐）

**这是最安全和推荐的方法，适用于所有平台（Windows/Linux/Mac）。**

```bash
# 在项目根目录执行
python rename_qa_to_qd.py
```

脚本会自动完成：
1. ✅ 使用 `git mv` 重命名目录（保持 git 历史）
2. ✅ 更新所有 Python 文件中的导入语句
3. ✅ 更新 setup.py 配置文件
4. ✅ 更新 README.md 中的引用

### 方法二：使用 Bash 脚本（Linux/Mac）

```bash
# 在项目根目录执行
bash rename_qa_to_qd.sh
```

### 方法三：使用批处理脚本（Windows）

```cmd
# 在项目根目录执行
rename_qa_to_qd.bat
```

## 受影响的文件

### 主要文件
- `quanda/__init__.py` - 主模块导入
- `setup.py` - 包配置
- `README.md` - 文档

### Python 文件数量
约 **119 个文件** 需要更新导入语句，包括：
- quanda 包下的所有子模块
- scripts 目录下的示例脚本
- 测试文件

## 导入语句变化示例

```python
# 旧导入
from quanda.QAAnalysis import QAAnalysis_signal
from quanda.QAData import QA_DataStruct_Day
from quanda.QAFetch import QA_fetch_get_stock_day
from quanda.QAUtil import QA_util_code_tolist

# 新导入
from quanda.QDAnalysis import QAAnalysis_signal
from quanda.QDData import QA_DataStruct_Day
from quanda.QDFetch import QA_fetch_get_stock_day
from quanda.QDUtil import QA_util_code_tolist
```

## 执行前检查清单

- [ ] 确认工作区是干净的（无未提交的更改）
  ```bash
  git status
  ```
- [ ] 确保在正确的分支上
  ```bash
  git branch
  ```
- [ ] 备份重要数据（如果需要）
- [ ] 关闭所有正在运行的 QuanDA 进程

## 执行步骤

1. **检查当前状态**
   ```bash
   cd D:\Workbench\QuanDA
   git status
   ```

2. **执行重命名脚本**
   ```bash
   python rename_qa_to_qd.py
   ```

3. **验证更改**
   ```bash
   # 查看重命名的目录
   ls quanda/

   # 查看 git 状态
   git status

   # 查看具体更改
   git diff
   ```

4. **提交更改**
   ```bash
   git add -A
   git commit -m "重命名模块: QA 前缀改为 QD 前缀

   - 重命名 17 个模块目录从 QA 到 QD 前缀
   - 更新所有 Python 文件中的导入语句
   - 更新 setup.py 和 README.md
   - 保持 git 历史完整性"
   ```

## 潜在问题与解决方案

### 问题1: git mv 失败

**症状**: `git mv` 命令执行失败

**原因**: 目标目录已存在或文件被占用

**解决方案**:
```bash
# 检查目标目录是否存在
ls quanda/QDAnalysis

# 如果存在，先删除
rm -rf quanda/QDAnalysis

# 然后重新执行 git mv
git mv quanda/QAAnalysis quanda/QDAnalysis
```

### 问题2: 导入语句未完全更新

**症状**: 某些文件仍使用旧的导入语句

**解决方案**:
```bash
# 手动查找遗漏的文件
grep -r "from quanda\.QA" quanda/
grep -r "import quanda\.QA" quanda/

# 手动替换
sed -i 's/from quanda\.QA\([A-Z]\)/from quanda.QD\1/g' filename.py
```

### 问题3: 类名不一致

**症状**: 某些类名仍使用 QA 前缀

**注意**: 本次重命名仅针对**模块名**（目录名），**类名保持不变**。

例如：
- 模块: `QAAnalysis` → `QDAnalysis`
- 类名: `QAAnalysis_signal` → `QAAnalysis_signal`（保持不变）

这是正确的设计，因为类名使用 QA 前缀表示 "Quantitative Analysis" 的含义。

### 问题4: 第三方依赖

**症状**: 外部项目引用了旧模块名

**解决方案**: 通知相关项目更新导入语句，或提供兼容层：

```python
# 在 quanda/__init__.py 中添加兼容层（临时）
try:
    from quanda.QDAnalysis import *
except ImportError:
    from quanda.QAAnalysis import *
```

## 验证测试

重命名完成后，建议进行以下测试：

1. **导入测试**
   ```python
   import quanda
   from quanda.QDData import QA_DataStruct_Day
   from quanda.QDFetch import QA_fetch_get_stock_day
   print("导入成功!")
   ```

2. **功能测试**
   ```bash
   # 运行测试脚本
   python scripts/auto_init_data.py
   ```

3. **Web 服务器测试**
   ```bash
   # 启动 Web 服务器
   python quanda/QDWebServer/server.py
   ```

## 回滚方案

如果重命名后发现问题需要回滚：

```bash
# 方法1: 使用 git reset（如果还未提交）
git reset --hard HEAD

# 方法2: 创建反向重命名脚本
# 将所有 QD 改回 QA
```

## 后续工作

1. **更新文档**
   - 更新开发者文档
   - 更新 API 文档
   - 更新示例代码

2. **通知用户**
   - 发布版本更新说明
   - 提供迁移指南
   - 说明 breaking changes

3. **清理临时文件**
   ```bash
   # 删除重命名脚本（可选）
   rm rename_qa_to_qd.py
   rm rename_qa_to_qd.sh
   rm rename_qa_to_qd.bat
   rm RENAME_GUIDE.md
   ```

## 技术细节

### 为什么使用 git mv

使用 `git mv` 而不是普通 `mv` 的原因：
- ✅ 保持 git 历史记录
- ✅ Git 能正确识别这是重命名而非删除+新增
- ✅ 便于代码审查和历史追溯
- ✅ 减少 git 仓库大小

### 正则替换规则

```python
# 替换规则
from quanda.QA[A-Z] → from quanda.QD[A-Z]
import quanda.QA[A-Z] → import quanda.QD[A-Z]
from .QA[A-Z] → from .QD[A-Z]

# 不替换
QA_xxx 函数名/类名（保留 QA 前缀）
QIFI 模块名（特殊模块）
```

## 参考资料

- [Git 重命名文档](https://git-scm.com/docs/git-mv)
- [PEP 8 编码规范](https://www.python.org/dev/peps/pep-0008/)
- QuanDA 项目规范: `CLAUDE.md`

## 联系方式

如有问题，请参考：
- 项目文档: `README.md`
- 工作日志: `CLAUDE.md`
- 项目记忆: `memory/MEMORY.md`

---

**文档创建**: 2025-03-16
**作者**: Claude AI
**版本**: 1.0
