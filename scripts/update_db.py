#!/usr/bin/env python3
"""
硬件参数小助手 - 主数据更新控制器
用于更新本地JSON数据库（cpu_data.json, gpu_data.json, phone_data.json）
"""

import os
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
MOCK_DIR = PROJECT_ROOT / "src" / "mock"
BACKUP_DIR = PROJECT_ROOT / "scripts" / "backups"
SCRAPERS_DIR = PROJECT_ROOT / "scripts" / "scrapers"

# 目标文件配置
TARGET_FILES = {
    "cpu": MOCK_DIR / "cpu_data.json",
    "gpu": MOCK_DIR / "gpu_data.json", 
    "phone": MOCK_DIR / "phone_data.json"
}

# 模块配置（假设的scraper模块）
SCRAPER_MODULES = {
    "cpu": "scripts.scrapers.cpu",
    "gpu": "scripts.scrapers.gpu",
    "phone": "scripts.scrapers.phone"
}


def ensure_directories() -> None:
    """确保必要的目录存在"""
    MOCK_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    SCRAPERS_DIR.mkdir(parents=True, exist_ok=True)


def create_backup(file_path: Path) -> Optional[Path]:
    """
    创建文件备份
    
    Args:
        file_path: 要备份的文件路径
        
    Returns:
        备份文件路径，如果文件不存在则返回None
    """
    if not file_path.exists():
        print(f"⚠️  文件不存在，跳过备份: {file_path}")
        return None
    
    # 创建备份目录（按日期）
    today = datetime.now().strftime("%Y%m%d")
    backup_date_dir = BACKUP_DIR / today
    backup_date_dir.mkdir(exist_ok=True)
    
    # 生成备份文件名
    backup_name = f"{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    backup_path = backup_date_dir / backup_name
    
    try:
        shutil.copy2(file_path, backup_path)
        print(f"✅  备份创建成功: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌  备份创建失败: {e}")
        return None


def validate_data(data: List[Dict[str, Any]], data_type: str) -> bool:
    """
    验证数据完整性
    
    Args:
        data: 要验证的数据列表
        data_type: 数据类型标识
        
    Returns:
        验证是否通过
    """
    if not data:
        print(f"❌  {data_type.upper()}数据为空")
        return False
    
    if not isinstance(data, list):
        print(f"❌  {data_type.upper()}数据不是列表类型")
        return False
    
    # 检查每个项目的基本字段
    required_fields = ["id", "model", "brand", "price"]
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            print(f"❌  第{i+1}个项目不是字典类型")
            return False
        
        for field in required_fields:
            if field not in item:
                print(f"❌  第{i+1}个项目缺少必需字段: {field}")
                return False
        
        # 检查ID唯一性
        if len([d for d in data if d.get("id") == item["id"]]) > 1:
            print(f"❌  发现重复ID: {item['id']}")
            return False
    
    print(f"✅  {data_type.upper()}数据验证通过: {len(data)}个项目")
    return True


def save_json(data: List[Dict[str, Any]], file_path: Path) -> bool:
    """
    保存数据到JSON文件
    
    Args:
        data: 要保存的数据
        file_path: 目标文件路径
        
    Returns:
        保存是否成功
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅  数据保存成功: {file_path}")
        return True
    except Exception as e:
        print(f"❌  数据保存失败: {e}")
        return False


def load_existing_data(file_path: Path) -> List[Dict[str, Any]]:
    """
    加载现有的JSON数据
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        加载的数据列表，如果文件不存在或解析失败则返回空列表
    """
    if not file_path.exists():
        print(f"⚠️  文件不存在: {file_path}")
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            print(f"📂  加载现有数据: {file_path} ({len(data)}个项目)")
            return data
        else:
            print(f"❌  文件格式错误，期望列表类型: {file_path}")
            return []
    except json.JSONDecodeError as e:
        print(f"❌  JSON解析失败: {file_path} - {e}")
        return []
    except Exception as e:
        print(f"❌  文件读取失败: {file_path} - {e}")
        return []


def compare_data(new_data: List[Dict[str, Any]], old_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    比较新旧数据
    
    Args:
        new_data: 新数据
        old_data: 旧数据
        
    Returns:
        比较结果统计
    """
    old_ids = {item["id"] for item in old_data}
    new_ids = {item["id"] for item in new_data}
    
    added_ids = new_ids - old_ids
    removed_ids = old_ids - new_ids
    common_ids = old_ids & new_ids
    
    # 检查是否有更新的项目
    updated_items = []
    for new_item in new_data:
        if new_item["id"] in common_ids:
            old_item = next(item for item in old_data if item["id"] == new_item["id"])
            if new_item != old_item:
                updated_items.append(new_item["id"])
    
    return {
        "total_new": len(new_data),
        "total_old": len(old_data),
        "added": len(added_ids),
        "removed": len(removed_ids),
        "updated": len(updated_items),
        "unchanged": len(common_ids) - len(updated_items)
    }


def run_scraper(module_name: str) -> Optional[List[Dict[str, Any]]]:
    """
    运行指定的scraper模块
    
    Args:
        module_name: 模块名称
        
    Returns:
        scraper返回的数据，如果失败则返回None
    """
    try:
        # 动态导入模块
        module_parts = module_name.split(".")
        if len(module_parts) != 3:
            print(f"❌  模块名称格式错误: {module_name}")
            return None
        
        # 添加项目根目录到Python路径
        if str(PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT))
        
        # 尝试导入模块
        import importlib
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as e:
            print(f"⚠️  模块未找到: {module_name}，错误: {e}")
            print(f"📁  尝试从当前目录导入...")
            # 尝试从当前目录导入
            try:
                # 添加scripts目录到Python路径
                scripts_dir = PROJECT_ROOT / "scripts"
                if str(scripts_dir) not in sys.path:
                    sys.path.insert(0, str(scripts_dir))
                
                # 重新尝试导入
                module = importlib.import_module(module_name)
                print(f"✅  模块导入成功（从scripts目录）")
            except ModuleNotFoundError as e2:
                print(f"❌  仍然无法导入模块: {e2}")
                print(f"📁  当前Python路径: {sys.path}")
                print(f"📁  Scrapers目录: {SCRAPERS_DIR}")
                return generate_mock_data(module_parts[2])
        
        # 检查是否有run函数
        if not hasattr(module, "run"):
            print(f"❌  模块没有run函数: {module_name}")
            return generate_mock_data(module_parts[2])
        
        # 运行scraper
        print(f"🚀  运行scraper: {module_name}")
        data = module.run()
        
        if not data:
            print(f"⚠️  scraper返回空数据，使用模拟数据")
            return generate_mock_data(module_parts[2])
        
        return data
        
    except Exception as e:
        print(f"❌  scraper运行失败: {e}")
        import traceback
        traceback.print_exc()
        return generate_mock_data(module_parts[2] if len(module_parts) > 2 else "unknown")


def generate_mock_data(data_type: str) -> List[Dict[str, Any]]:
    """
    生成模拟数据（当scraper不可用时）
    
    Args:
        data_type: 数据类型
        
    Returns:
        模拟数据
    """
    print(f"📝  生成{data_type.upper()}模拟数据")
    
    if data_type == "cpu":
        return [
            {
                "id": "cpu-001",
                "model": "Intel Core i9-14900KS",
                "brand": "Intel",
                "releaseDate": "2024-03-14",
                "price": 5999,
                "description": "Intel第14代酷睿旗舰特别版，6.2GHz睿频",
                "cores": "8P+16E",
                "baseClock": 3.2,
                "boostClock": 6.2,
                "socket": "LGA1700",
                "tdp": 150,
                "integratedGraphics": True,
                "cache": 36
            }
        ]
    elif data_type == "gpu":
        return [
            {
                "id": "gpu-001",
                "model": "NVIDIA GeForce RTX 4090",
                "brand": "NVIDIA",
                "releaseDate": "2024-01-10",
                "price": 12999,
                "description": "NVIDIA Ada Lovelace架构旗舰显卡",
                "vram": 24,
                "busWidth": 384,
                "cudaCores": 16384,
                "coreClock": 2235,
                "memoryClock": 21000,
                "powerConsumption": 450,
                "rayTracing": True,
                "upscalingTech": "DLSS"
            }
        ]
    elif data_type == "phone":
        return [
            {
                "id": "phone-001",
                "model": "iPhone 15 Pro Max",
                "brand": "Apple",
                "releaseDate": "2024-09-22",
                "price": 9999,
                "description": "苹果旗舰手机，A17 Pro芯片",
                "processor": "A17 Pro",
                "ram": 8,
                "storage": 256,
                "screenSize": 6.7,
                "resolution": "2796x1290",
                "refreshRate": 120,
                "batteryCapacity": 4422,
                "camera": "48MP+12MP+12MP",
                "os": "iOS",
                "support5G": True
            }
        ]
    else:
        return []


def update_data(data_type: str, target_file: Path) -> bool:
    """
    更新指定类型的数据
    
    Args:
        data_type: 数据类型
        target_file: 目标文件路径
        
    Returns:
        更新是否成功
    """
    print(f"\n{'='*60}")
    print(f"更新 {data_type.upper()} 数据")
    print(f"{'='*60}")
    
    # 1. 创建备份
    backup_path = create_backup(target_file)
    
    # 2. 加载现有数据
    old_data = load_existing_data(target_file)
    
    # 3. 运行scraper获取新数据
    module_name = SCRAPER_MODULES.get(data_type)
    if not module_name:
        print(f"❌  未找到{data_type}的scraper配置")
        return False
    
    new_data = run_scraper(module_name)
    if not new_data:
        print(f"❌  无法获取{data_type}数据")
        return False
    
    # 4. 验证新数据
    if not validate_data(new_data, data_type):
        print(f"❌  {data_type}数据验证失败")
        return False
    
    # 5. 比较数据变化
    stats = compare_data(new_data, old_data)
    
    # 6. 保存新数据
    if not save_json(new_data, target_file):
        # 如果保存失败，尝试恢复备份
        if backup_path and backup_path.exists():
            print(f"🔄  尝试恢复备份...")
            try:
                shutil.copy2(backup_path, target_file)
                print(f"✅  备份恢复成功")
            except Exception as e:
                print(f"❌  备份恢复失败: {e}")
        return False
    
    # 7. 打印统计信息
    print(f"\n📊  {data_type.upper()}数据更新统计:")
    print(f"   总计项目: {stats['total_new']} (之前: {stats['total_old']})")
    print(f"   新增项目: {stats['added']}")
    print(f"   删除项目: {stats['removed']}")
    print(f"   更新项目: {stats['updated']}")
    print(f"   未变项目: {stats['unchanged']}")
    
    return True


def main():
    """主函数"""
    print("🔄  硬件参数小助手 - 数据更新控制器")
    print(f"📁  项目根目录: {PROJECT_ROOT}")
    print(f"📁  Mock数据目录: {MOCK_DIR}")
    print(f"📁  备份目录: {BACKUP_DIR}")
    
    # 确保目录存在
    ensure_directories()
    
    # 更新所有类型的数据
    success_count = 0
    total_count = len(TARGET_FILES)
    
    for data_type, target_file in TARGET_FILES.items():
        try:
            if update_data(data_type, target_file):
                success_count += 1
        except Exception as e:
            print(f"❌  {data_type.upper()}更新过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
    
    # 总结
    print(f"\n{'='*60}")
    print("📋  更新完成总结")
    print(f"{'='*60}")
    print(f"✅  成功更新: {success_count}/{total_count}")
    print(f"❌  失败更新: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉  所有数据更新成功！")
        return 0
    elif success_count > 0:
        print("⚠️  部分数据更新成功")
        return 1
    else:
        print("❌  所有数据更新失败")
        return 2


if __name__ == "__main__":
    sys.exit(main())
