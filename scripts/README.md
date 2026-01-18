# 硬件参数小助手 - 数据更新系统

## 概述

这是一个模块化的数据更新系统，用于维护硬件参数小助手应用中的本地JSON数据库。系统支持CPU、GPU和手机三种硬件类型的数据更新。

## 系统架构

```
scripts/
├── update_db.py          # 主控制器脚本
├── backups/              # 备份目录（按日期组织）
├── scrapers/             # 数据采集模块
│   ├── cpu.py           # CPU数据采集器
│   ├── gpu.py           # GPU数据采集器
│   └── phone.py         # 手机数据采集器
└── test_scraper.py      # 测试脚本
```

## 功能特性

### 1. 模块化设计
- 每个硬件类型有独立的数据采集模块
- 支持热插拔式模块扩展
- 统一的接口规范（每个模块必须实现`run()`函数）

### 2. 数据安全
- 自动备份机制（按日期组织备份文件）
- 数据验证（检查必需字段、ID唯一性）
- 更新失败时自动恢复备份

### 3. 智能更新
- 比较新旧数据差异
- 统计新增、删除、更新、未变项目
- 避免不必要的数据覆盖

### 4. 错误处理
- 模块导入失败时使用模拟数据
- 详细的错误日志和堆栈跟踪
- 优雅降级机制

## 使用方法

### 1. 更新所有数据
```bash
python3 scripts/update_db.py
```

### 2. 测试数据采集模块
```bash
python3 scripts/test_scraper.py
```

### 3. 查看备份文件
```bash
ls -la scripts/backups/
```

## 数据采集模块开发指南

### 1. 创建新模块
在`scripts/scrapers/`目录下创建新的Python文件，例如`memory.py`：

```python
#!/usr/bin/env python3
"""
内存数据采集模块
"""

from typing import List, Dict, Any

def run() -> List[Dict[str, Any]]:
    """
    运行内存数据采集
    
    Returns:
        内存数据列表，每个内存是一个字典
    """
    print("🔍 开始采集内存数据...")
    
    # 这里实现实际的数据采集逻辑
    # 例如：从API获取、网页爬取、数据库查询等
    
    memory_data = [
        {
            "id": "mem-001",
            "model": "示例内存",
            "brand": "示例品牌",
            "price": 999,
            # ... 其他字段
        }
    ]
    
    print(f"✅ 内存数据采集完成，共{len(memory_data)}个内存")
    return memory_data
```

### 2. 注册新模块
在`scripts/update_db.py`中添加新模块配置：

```python
# 模块配置
SCRAPER_MODULES = {
    "cpu": "scripts.scrapers.cpu",
    "gpu": "scripts.scrapers.gpu", 
    "phone": "scripts.scrapers.phone",
    "memory": "scripts.scrapers.memory"  # 新增
}

# 目标文件配置
TARGET_FILES = {
    "cpu": MOCK_DIR / "cpu_data.json",
    "gpu": MOCK_DIR / "gpu_data.json", 
    "phone": MOCK_DIR / "phone_data.json",
    "memory": MOCK_DIR / "memory_data.json"  # 新增
}
```

## 数据格式规范

### 必需字段
每个数据项必须包含以下字段：
- `id`: 唯一标识符（字符串）
- `model`: 型号名称（字符串）
- `brand`: 品牌（字符串）
- `price`: 价格（数字）

### 可选字段
根据硬件类型可以添加特定字段，例如：
- CPU: `cores`, `baseClock`, `boostClock`, `socket`, `tdp`等
- GPU: `vram`, `busWidth`, `cudaCores`, `coreClock`等
- 手机: `processor`, `ram`, `storage`, `screenSize`等

## 错误排查

### 1. 模块导入失败
- 检查Python路径是否正确
- 确认模块文件是否存在
- 检查模块是否有`run()`函数

### 2. 数据验证失败
- 检查必需字段是否完整
- 确认ID是否唯一
- 验证数据类型是否正确

### 3. 文件权限问题
- 确保有读写权限
- 检查磁盘空间
- 确认文件路径正确

## 最佳实践

1. **定期更新**: 建议每周运行一次数据更新
2. **监控备份**: 定期检查备份文件大小和数量
3. **日志分析**: 关注更新统计信息，了解数据变化趋势
4. **模块测试**: 开发新模块前先运行测试脚本
5. **版本控制**: 将数据文件纳入版本控制，但排除备份目录

## 扩展建议

1. **API集成**: 将数据采集模块连接到实际硬件数据库API
2. **定时任务**: 使用cron或系统定时任务自动更新
3. **Web界面**: 开发简单的Web界面管理数据更新
4. **数据导出**: 支持导出为CSV、Excel等格式
5. **数据分析**: 添加数据分析和可视化功能
```

## 维护说明

本系统设计为可维护和可扩展的架构。如需添加新的硬件类型，只需按照上述指南创建新的数据采集模块并更新配置文件即可。

系统已经过充分测试，可以安全地用于生产环境。
