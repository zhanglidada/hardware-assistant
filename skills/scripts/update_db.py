#!/usr/bin/env python3
"""
硬件参数小助手 - 主数据更新控制器
用于更新本地JSON数据库（cpu_data.json, gpu_data.json, phone_data.json）

使用配置化、模块化设计，提供完整的备份、验证和日志功能
"""

import sys
import importlib
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.config import PATHS, TARGET_FILES, SCRAPER_MODULES
from scripts.utils import (
    logger, DataValidator, BackupManager, DataComparator,
    save_json, load_json
)


def ensure_directories() -> None:
    """确保必要的目录存在"""
    PATHS["MOCK_DIR"].mkdir(parents=True, exist_ok=True)
    PATHS["BACKUP_DIR"].mkdir(parents=True, exist_ok=True)
    PATHS["SCRAPERS_DIR"].mkdir(parents=True, exist_ok=True)
    logger.info(f"📁 目录初始化完成")


def run_scraper(module_name: str, data_type: str) -> Optional[List[Dict[str, Any]]]:
    """
    动态导入并运行scraper模块
    
    Args:
        module_name: 模块名称 (如: "scripts.scrapers.cpu")
        data_type: 数据类型 (如: "cpu")
        
    Returns:
        采集的数据列表，失败返回None
    """
    try:
        # 添加scripts目录到路径
        scripts_dir = PATHS["PROJECT_ROOT"] / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        
        # 动态导入模块
        logger.info(f"📦 导入模块: {module_name}")
        module = importlib.import_module(module_name)
        
        # 检查run函数
        if not hasattr(module, "run"):
            logger.error(f"模块缺少run()函数: {module_name}")
            return None
        
        # 运行scraper
        logger.info(f"🚀 运行{data_type.upper()}数据采集器...")
        data = module.run()
        
        if not data:
            logger.warning(f"{data_type.upper()}采集器返回空数据")
            return None
        
        logger.info(f"✅ {data_type.upper()}采集完成: {len(data)}个项目")
        return data
        
    except ModuleNotFoundError as e:
        logger.error(f"模块未找到: {module_name} - {e}")
        return None
    except Exception as e:
        logger.error(f"Scraper运行失败: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return None


def update_single_data(data_type: str, target_file: Path) -> bool:
    """
    更新单个类型的数据
    
    Args:
        data_type: 数据类型 (cpu/gpu/phone)
        target_file: 目标JSON文件路径
        
    Returns:
        更新是否成功
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"📝 开始更新 {data_type.upper()} 数据")
    logger.info(f"{'='*60}")
    
    # 步骤1: 创建备份
    logger.info("🔒 步骤1: 创建数据备份...")
    BackupManager.create_backup(target_file, PATHS["BACKUP_DIR"])
    
    # 步骤2: 加载现有数据
    logger.info("📂 步骤2: 加载现有数据...")
    old_data = load_json(target_file) or []
    if old_data:
        logger.info(f"   现有数据: {len(old_data)}个项目")
    else:
        logger.info(f"   无现有数据，将创建新文件")
    
    # 步骤3: 运行scraper获取新数据
    logger.info("🔍 步骤3: 获取最新数据...")
    module_name = SCRAPER_MODULES.get(data_type)
    if not module_name:
        logger.error(f"未找到{data_type}的scraper配置")
        return False
    
    new_data = run_scraper(module_name, data_type)
    if not new_data:
        logger.error(f"无法获取{data_type}数据")
        return False
    
    # 步骤4: 验证新数据
    logger.info("✓ 步骤4: 验证数据完整性...")
    is_valid, errors = DataValidator.validate_data_list(new_data, data_type)
    if not is_valid:
        logger.error(f"数据验证失败:")
        for error in errors[:5]:  # 只显示前5个错误
            logger.error(f"  - {error}")
        if len(errors) > 5:
            logger.error(f"  ... 还有 {len(errors) - 5} 个错误")
        return False
    
    logger.info(f"   验证通过: {len(new_data)}个项目")
    
    # 步骤5: 对比数据变化
    logger.info("📊 步骤5: 分析数据变化...")
    stats = DataComparator.compare_data(old_data, new_data)
    DataComparator.print_comparison(data_type, stats)
    
    # 步骤6: 保存新数据
    logger.info("💾 步骤6: 保存新数据...")
    if not save_json(new_data, target_file):
        logger.error(f"数据保存失败")
        return False
    
    logger.info(f"✅ {data_type.upper()}数据更新成功！\n")
    return True


def main():
    """主函数 - 执行所有数据更新任务"""
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║   硬件参数小助手 - 数据更新控制器                         ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info(f"📁 项目根目录: {PATHS['PROJECT_ROOT']}")
    logger.info(f"📁 Mock数据目录: {PATHS['MOCK_DIR']}")
    logger.info(f"📁 备份目录: {PATHS['BACKUP_DIR']}")
    logger.info("")
    
    # 初始化目录
    ensure_directories()
    
    # 清理旧备份
    logger.info("🗑️  清理过期备份...")
    BackupManager.cleanup_old_backups(PATHS["BACKUP_DIR"])
    logger.info("")
    
    # 更新所有类型的数据
    success_results = {}
    
    for data_type, target_file in TARGET_FILES.items():
        try:
            success = update_single_data(data_type, target_file)
            success_results[data_type] = success
        except Exception as e:
            logger.error(f"❌ {data_type.upper()}更新过程中发生异常: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            success_results[data_type] = False
    
    # 生成总结报告
    logger.info(f"\n{'='*60}")
    logger.info("📋 数据更新总结报告")
    logger.info(f"{'='*60}")
    
    success_count = sum(1 for v in success_results.values() if v)
    total_count = len(success_results)
    
    for data_type, success in success_results.items():
        status = "✅ 成功" if success else "❌ 失败"
        logger.info(f"   {data_type.upper():8} : {status}")
    
    logger.info(f"\n   总计: {success_count}/{total_count} 成功")
    
    # 返回状态码
    if success_count == total_count:
        logger.info("\n🎉 所有数据更新成功！")
        return 0
    elif success_count > 0:
        logger.info("\n⚠️  部分数据更新成功")
        return 1
    else:
        logger.info("\n❌ 所有数据更新失败")
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
