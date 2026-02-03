# 数据更新脚本说明

## 📋 概述

本目录包含硬件参数小助手的数据采集和更新脚本，用于维护 CPU、GPU 和手机的硬件参数数据库。

**数据规模**: 80+ 硬件产品数据（CPU 30+, GPU 25+, Phone 25+）

## 🏗️ 架构设计

### 系统架构
```
scripts/
├── config.py          # ⚙️ 配置管理（路径、数据源、验证规则等）
├── utils.py           # 🛠️ 工具模块（日志、验证、备份、对比）
├── update_db.py       # 🎯 主控制器（orchestrator）
├── test_scraper.py    # 🧪 测试工具
├── scrapers/          # 📦 数据采集器
│   ├── cpu.py         # CPU数据采集器 (30+)
│   ├── gpu.py         # GPU数据采集器 (25+)
│   └── phone.py       # 手机数据采集器 (25+)
├── backups/           # 💾 数据备份（按日期组织）
└── logs/              # 📄 日志文件
```

### 核心模块

#### 1. config.py - 配置管理
集中管理所有配置选项：
- **PATHS**: 项目路径、数据目录、备份目录
- **TARGET_FILES**: 目标JSON文件映射
- **SCRAPER_MODULES**: 采集器模块配置
- **DATA_SOURCE_CONFIG**: 数据源模式（local/api/hybrid）
- **VALIDATION_CONFIG**: 数据验证规则
- **BACKUP_CONFIG**: 备份策略（保留天数、自动清理）
- **LOG_CONFIG**: 日志配置

#### 2. utils.py - 工具集
提供通用功能支持：
- **Logger**: 单例日志管理器
  - 控制台输出（INFO级别）
  - 文件输出（DEBUG级别）
  - 统一格式化
- **DataValidator**: 数据验证器
  - 必需字段检查
  - 数据类型验证
  - 重复ID检测
  - 价格范围验证
- **BackupManager**: 备份管理器
  - 自动按日期备份
  - 智能清理过期备份
- **DataComparator**: 数据对比器
  - 新增/删除/更新统计
  - 详细变更报告

#### 3. update_db.py - 主控制器
六步骤数据更新流程：
1. **备份** - 创建当前数据备份
2. **加载** - 读取现有数据
3. **采集** - 运行数据采集器
4. **验证** - 完整性检查
5. **对比** - 分析数据变化
6. **保存** - 写入新数据

特性：
- 动态模块导入
- 完整错误处理
- 详细进度反馈
- 自动备份恢复

## 🚀 使用方法

### 快速开始

在项目根目录执行：
```bash
python3 skills/scripts/update_db.py
```

### 预期输出示例

```
╔════════════════════════════════════════════════════════════╗
║   硬件参数小助手 - 数据更新控制器                         ║
╚════════════════════════════════════════════════════════════╝
📁 项目根目录: /path/to/hardware-assistant/skills
📁 Mock数据目录: /path/to/hardware-assistant/skills/src/mock
📁 备份目录: /path/to/hardware-assistant/skills/scripts/backups

============================================================
📝 开始更新 CPU 数据
============================================================
🔒 步骤1: 创建数据备份...
✅ 备份创建成功: backups/20260201/cpu_data_20260201_223800.json
📂 步骤2: 加载现有数据...
   现有数据: 30个项目
🔍 步骤3: 获取最新数据...
📦 导入模块: scrapers.cpu
🚀 运行CPU数据采集器...
✅ CPU采集完成: 30个项目
✓ 步骤4: 验证数据完整性...
   验证通过: 30个项目
📊 步骤5: 分析数据变化...
   总计项目: 30 (之前: 30)
   新增项目: 0
   删除项目: 0
   更新项目: 0
   未变项目: 30
💾 步骤6: 保存新数据...
✅ 数据保存成功
✅ CPU数据更新成功！

[GPU和Phone的更新流程类似...]

============================================================
📋 数据更新总结报告
============================================================
   CPU      : ✅ 成功
   GPU      : ✅ 成功
   PHONE    : ✅ 成功

   总计: 3/3 成功

🎉 所有数据更新成功！
```

## 📊 数据采集器详情

### CPU采集器 (cpu.py)
- **数据量**: 30个CPU
- **品牌**: Intel (15) + AMD (15)
- **覆盖范围**: 
  - Intel: Core i3/i5/i7/i9系列
  - AMD: Ryzen 3/5/7/9系列
- **字段**: id, model, brand, releaseDate, price, cores, baseClock, boostClock, socket, tdp, cache等

### GPU采集器 (gpu.py)
- **数据量**: 25个GPU
- **品牌**: NVIDIA (14) + AMD (11)
- **覆盖范围**:
  - NVIDIA: RTX 4090/4080/4070系列, RTX 3000系列
  - AMD: RX 7900/7800/7700系列, RX 6000系列
- **特性**: 84%支持光线追踪
- **字段**: id, model, brand, vram, cudaCores, coreClock, powerConsumption, rayTracing等

### 手机采集器 (phone.py)
- **数据量**: 25个手机
- **品牌**: Apple, Xiaomi, Huawei, Samsung等
- **覆盖范围**: 各品牌旗舰和热门机型
- **5G支持**: 100%
- **字段**: id, model, brand, processor, ram, storage, screenSize, camera, battery等

## ⚙️ 配置选项

### 修改数据源模式

编辑 `config.py`:
```python
DATA_SOURCE_CONFIG = {
    "mode": "local",  # 改为 "api" 或 "hybrid"
    "cache_enabled": True,
    "cache_ttl_hours": 24
}
```

### 调整验证规则

编辑 `config.py`:
```python
VALIDATION_CONFIG = {
    "required_fields": ["id", "model", "brand", "price"],
    "check_duplicates": True,
    "check_price_range": True,
    "min_price": 50,
    "max_price": 50000
}
```

### 配置备份策略

编辑 `config.py`:
```python
BACKUP_CONFIG = {
    "enabled": True,
    "keep_days": 7,  # 保留7天内的备份
    "auto_cleanup": True
}
```

## 🧪 测试

### 测试单个采集器
```bash
cd skills/scripts
python3 test_scraper.py
```

### 测试数据验证
```python
from scripts.utils import DataValidator

data = [{"id": "cpu-001", "model": "i9-14900K", "brand": "Intel", "price": 5999}]
is_valid, errors = DataValidator.validate_data_list(data, "cpu")
```

## 📝 数据格式

### CPU数据结构
```json
{
  "id": "cpu-001",
  "model": "Intel Core i9-14900K",
  "brand": "Intel",
  "releaseDate": "2024-10-17",
  "price": 4699,
  "description": "Intel第14代酷睿旗舰处理器",
  "cores": "8P+16E",
  "baseClock": 3.2,
  "boostClock": 6.0,
  "socket": "LGA1700",
  "tdp": 125,
  "integratedGraphics": true,
  "cache": 36
}
```

### GPU数据结构
```json
{
  "id": "gpu-001",
  "model": "NVIDIA GeForce RTX 4090",
  "brand": "NVIDIA",
  "releaseDate": "2022-10-12",
  "price": 14999,
  "description": "NVIDIA Ada Lovelace架构旗舰显卡",
  "vram": 24,
  "busWidth": 384,
  "cudaCores": 16384,
  "coreClock": 2235,
  "memoryClock": 21000,
  "powerConsumption": 450,
  "rayTracing": true,
  "upscalingTech": "DLSS"
}
```

### Phone数据结构
```json
{
  "id": "phone-001",
  "model": "iPhone 16 Pro Max",
  "brand": "Apple",
  "releaseDate": "2024-09-20",
  "price": 13999,
  "description": "苹果2024年旗舰手机",
  "processor": "A18 Pro",
  "ram": 8,
  "storage": 256,
  "screenSize": 6.9,
  "resolution": "2868x1320",
  "refreshRate": 120,
  "batteryCapacity": 4685,
  "camera": "48MP+48MP+12MP",
  "os": "iOS",
  "support5G": true
}
```

## 🔧 开发指南

### 添加新的数据采集器

1. 在 `scrapers/` 目录创建新文件（如 `tablet.py`）
2. 实现 `run()` 函数返回数据列表
3. 在 `config.py` 中注册：
```python
TARGET_FILES["tablet"] = MOCK_DIR / "tablet_data.json"
SCRAPER_MODULES["tablet"] = "scrapers.tablet"
```

### 添加自定义验证规则

在 `utils.py` 的 `DataValidator.validate_item()` 中添加：
```python
# 自定义验证逻辑
if data_type == "cpu" and item.get("cores"):
    # 验证CPU核心数格式
    pass
```

## 📌 注意事项

1. **备份机制**: 每次更新前自动备份，保留7天
2. **数据验证**: 严格的字段和格式检查，确保数据质量
3. **错误恢复**: 保存失败时自动尝试恢复备份
4. **日志记录**: 所有操作记录到 `logs/update.log`
5. **模块化设计**: 易于扩展新的数据源和验证规则

## 🐛 故障排除

### 模块导入失败
```
❌ 模块未找到: scrapers.cpu
```
**解决**: 确保从项目根目录运行脚本

### 数据验证失败
```
❌ 数据验证失败: 缺少必需字段: price
```
**解决**: 检查采集器返回的数据结构是否符合要求

### 备份目录权限问题
```
FileNotFoundError: backups/20260201/
```
**解决**: 确保 `scripts/backups/` 目录可写

## 📞 维护者

如果您在使用过程中遇到问题或有改进建议，请查看项目文档或提交issue。

---

**最后更新**: 2026-02-01  
**版本**: 2.0.0（配置化重构版）
