#!/usr/bin/env python3
"""
数据管道工具函数
提供日志、验证、备份等通用功能
"""

import os
import json
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

from config import LOG_CONFIG, BACKUP_CONFIG, VALIDATION_CONFIG


class Logger:
    """统一的日志管理器"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """初始化日志系统"""
        self.logger = logging.getLogger('DataPipeline')
        self.logger.setLevel(getattr(logging, LOG_CONFIG["level"]))
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器（如果启用）
        if LOG_CONFIG["enabled"]:
            # 确保日志目录存在
            log_file = Path(LOG_CONFIG["file"])
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(
                LOG_CONFIG["file"], 
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        """记录信息日志"""
        self.logger.info(message)
    
    def debug(self, message: str):
        """记录调试日志"""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """记录警告日志"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """记录错误日志"""
        self.logger.error(message)


# 全局日志实例
logger = Logger()


class DataValidator:
    """数据验证器"""
    
    @staticmethod
    def validate_item(item: Dict[str, Any], data_type: str) -> tuple[bool, Optional[str]]:
        """
        验证单个数据项
        
        Args:
            item: 数据项
            data_type: 数据类型（cpu/gpu/phone）
            
        Returns:
            (是否通过, 错误信息)
        """
        # 检查必需字段
        for field in VALIDATION_CONFIG["required_fields"]:
            if field not in item:
                return False, f"缺少必需字段: {field}"
        
        # 检查ID格式
        if not isinstance(item.get("id"), str) or not item["id"]:
            return False, "ID必须是非空字符串"
        
        # 检查价格范围
        if VALIDATION_CONFIG["check_price_range"]:
            price = item.get("price", 0)
            if not isinstance(price, (int, float)):
                return False, "价格必须是数字"
            if price < VALIDATION_CONFIG["min_price"] or price > VALIDATION_CONFIG["max_price"]:
                return False, f"价格超出合理范围: {price}"
        
        return True, None
    
    @staticmethod
    def validate_data_list(data: List[Dict[str, Any]], data_type: str) -> tuple[bool, List[str]]:
        """
        验证数据列表
        
        Args:
            data: 数据列表
            data_type: 数据类型
            
        Returns:
            (是否全部通过, 错误列表)
        """
        if not data:
            return False, ["数据列表为空"]
        
        errors = []
        ids_seen = set()
        
        for i, item in enumerate(data):
            # 验证单个项目
            is_valid, error = DataValidator.validate_item(item, data_type)
            if not is_valid:
                errors.append(f"第{i+1}项: {error}")
                continue
            
            # 检查ID唯一性
            if VALIDATION_CONFIG["check_duplicates"]:
                item_id = item["id"]
                if item_id in ids_seen:
                    errors.append(f"第{i+1}项: 重复的ID: {item_id}")
                ids_seen.add(item_id)
        
        return len(errors) == 0, errors


class BackupManager:
    """备份管理器"""
    
    @staticmethod
    def create_backup(file_path: Path, backup_dir: Path) -> Optional[Path]:
        """
        创建文件备份
        
        Args:
            file_path: 源文件路径
            backup_dir: 备份目录
            
        Returns:
            备份文件路径
        """
        if not BACKUP_CONFIG["enabled"]:
            return None
        
        if not file_path.exists():
            logger.warning(f"文件不存在，跳过备份: {file_path}")
            return None
        
        # 创建日期目录
        today = datetime.now().strftime("%Y%m%d")
        backup_date_dir = backup_dir / today
        backup_date_dir.mkdir(exist_ok=True)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}.json"
        backup_path = backup_date_dir / backup_name
        
        try:
            shutil.copy2(file_path, backup_path)
            logger.info(f"✅ 备份创建成功: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"❌ 备份创建失败: {e}")
            return None
    
    @staticmethod
    def cleanup_old_backups(backup_dir: Path):
        """
        清理过期备份
        
        Args:
            backup_dir: 备份目录
        """
        if not BACKUP_CONFIG["auto_cleanup"]:
            return
        
        cutoff_date = datetime.now() - timedelta(days=BACKUP_CONFIG["keep_days"])
        cutoff_str = cutoff_date.strftime("%Y%m%d")
        
        try:
            for date_dir in backup_dir.iterdir():
                if date_dir.is_dir() and date_dir.name.isdigit():
                    if date_dir.name < cutoff_str:
                        shutil.rmtree(date_dir)
                        logger.info(f"🗑️  清理过期备份: {date_dir}")
        except Exception as e:
            logger.error(f"⚠️  清理备份失败: {e}")


class DataComparator:
    """数据对比器"""
    
    @staticmethod
    def compare_data(old_data: List[Dict], new_data: List[Dict]) -> Dict[str, Any]:
        """
        对比新旧数据，生成变更统计
        
        Args:
            old_data: 旧数据列表
            new_data: 新数据列表
            
        Returns:
            变更统计字典
        """
        old_ids = {item["id"]: item for item in old_data}
        new_ids = {item["id"]: item for item in new_data}
        
        old_id_set = set(old_ids.keys())
        new_id_set = set(new_ids.keys())
        
        # 计算变更
        added = new_id_set - old_id_set
        removed = old_id_set - new_id_set
        common = old_id_set & new_id_set
        
        # 检查更新的项目
        updated = set()
        for item_id in common:
            if old_ids[item_id] != new_ids[item_id]:
                updated.add(item_id)
        
        unchanged = common - updated
        
        return {
            "total_new": len(new_data),
            "total_old": len(old_data),
            "added": len(added),
            "removed": len(removed),
            "updated": len(updated),
            "unchanged": len(unchanged),
            "added_ids": list(added),
            "removed_ids": list(removed),
            "updated_ids": list(updated)
        }
    
    @staticmethod
    def print_comparison(data_type: str, stats: Dict[str, Any]):
        """
        打印对比统计信息
        
        Args:
            data_type: 数据类型
            stats: 统计数据
        """
        logger.info(f"\n📊  {data_type.upper()}数据更新统计:")
        logger.info(f"   总计项目: {stats['total_new']} (之前: {stats['total_old']})")
        logger.info(f"   新增项目: {stats['added']}")
        logger.info(f"   删除项目: {stats['removed']}")
        logger.info(f"   更新项目: {stats['updated']}")
        logger.info(f"   未变项目: {stats['unchanged']}")
        
        if stats['added'] > 0 and stats['added_ids']:
            logger.debug(f"   新增ID: {', '.join(stats['added_ids'][:5])}...")
        if stats['removed'] > 0 and stats['removed_ids']:
            logger.debug(f"   删除ID: {', '.join(stats['removed_ids'][:5])}...")


def save_json(data: List[Dict], file_path: Path) -> bool:
    """
    保存数据到JSON文件
    
    Args:
        data: 数据列表
        file_path: 文件路径
        
    Returns:
        是否成功
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ 数据保存成功: {file_path}")
        return True
    except Exception as e:
        logger.error(f"❌ 数据保存失败: {e}")
        return False


def load_json(file_path: Path) -> Optional[List[Dict]]:
    """
    从JSON文件加载数据
    
    Args:
        file_path: 文件路径
        
    Returns:
        数据列表或None
    """
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"❌ 数据加载失败: {e}")
        return None
