#!/usr/bin/env python3
"""
数据管道配置文件
统一管理所有脚本的配置选项
"""

from pathlib import Path

# 项目路径配置
PROJECT_ROOT = Path(__file__).parent.parent
MOCK_DIR = PROJECT_ROOT / "src" / "mock"
BACKUP_DIR = Path(__file__).parent / "backups"
SCRAPERS_DIR = Path(__file__).parent / "scrapers"
CACHE_DIR = Path(__file__).parent / ".cache"

# 目录路径字典
PATHS = {
    "PROJECT_ROOT": PROJECT_ROOT,
    "MOCK_DIR": MOCK_DIR,
    "BACKUP_DIR": BACKUP_DIR,
    "SCRAPERS_DIR": SCRAPERS_DIR,
    "CACHE_DIR": CACHE_DIR
}

# 目标文件配置
TARGET_FILES = {
    "cpu": MOCK_DIR / "cpu_data.json",
    "gpu": MOCK_DIR / "gpu_data.json",
    "phone": MOCK_DIR / "phone_data.json"
}

# 采集器模块配置
SCRAPER_MODULES = {
    "cpu": "scrapers.cpu",
    "gpu": "scrapers.gpu",
    "phone": "scrapers.phone"
}

# 数据源配置
DATA_SOURCE_CONFIG = {
    "mode": "local",  # local | api | hybrid
    "cache_enabled": True,
    "cache_ttl_hours": 24,
    "api_endpoints": {
        "cpu": None,  # 预留CPU API
        "gpu": None,  # 预留GPU API
        "phone": None  # 预留手机 API
    },
    "retry_times": 3,  # 重试次数
    "timeout": 30  # 超时时间（秒）
}

# 数据验证配置
VALIDATION_CONFIG = {
    "required_fields": ["id", "model", "brand", "price"],
    "check_duplicates": True,
    "check_price_range": True,
    "min_price": 50,
    "max_price": 50000
}

# 备份配置
BACKUP_CONFIG = {
    "enabled": True,
    "keep_days": 30,  # 保留30天的备份
    "auto_cleanup": True
}

# 日志配置
LOG_CONFIG = {
    "enabled": True,
    "level": "INFO",  # DEBUG | INFO | WARNING | ERROR
    "file": Path(__file__).parent / "logs" / "update.log",
    "max_size_mb": 10,
    "backup_count": 5
}

def ensure_directories():
    """确保所有必需的目录存在"""
    MOCK_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    SCRAPERS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if LOG_CONFIG["enabled"]:
        LOG_CONFIG["file"].parent.mkdir(parents=True, exist_ok=True)
