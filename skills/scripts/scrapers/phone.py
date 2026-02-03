#!/usr/bin/env python3
"""
手机数据采集模块 - 真正的爬虫版本
从京东等电商网站爬取手机信息并返回标准格式的数据
"""

import json
import sys
import os
from typing import List, Dict, Any

# 添加当前目录到Python路径，以便导入web_scraper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # 尝试导入爬虫模块
    import sys
    import os
    # 添加当前目录到路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    from phone_scraper import run as run_phone_scraper
    HAS_SCRAPER = True
except ImportError as e:
    print(f"⚠️  无法导入爬虫模块: {e}")
    print("⚠️  将使用备用数据")
    HAS_SCRAPER = False


def get_phone_data_from_source() -> List[Dict[str, Any]]:
    """
    从数据源获取手机数据
    
    Returns:
        手机数据列表
    """
    if HAS_SCRAPER:
        try:
            # 使用真正的爬虫获取数据
            return run_phone_scraper()
        except Exception as e:
            print(f"⚠️  爬虫运行失败: {e}")
            print("⚠️  使用备用数据")
    
    # 备用数据（当爬虫失败时使用）
    return get_backup_phone_data()


def get_backup_phone_data() -> List[Dict[str, Any]]:
    """
    获取备用手机数据
    
    Returns:
        手机数据列表
    """
    backup_phones = [
        {
            "id": "phone-backup-001",
            "model": "iPhone 15",
            "brand": "Apple",
            "releaseDate": "2023-01-01",
            "price": 5999,
            "description": "苹果iPhone 15智能手机，A16芯片，灵动岛设计",
            "processor": "A16",
            "ram": 6,
            "storage": 128,
            "screenSize": 6.1,
            "resolution": "2556x1179",
            "refreshRate": 60,
            "batteryCapacity": 3349,
            "camera": "48MP+12MP",
            "os": "iOS",
            "support5G": True,
            "source": "备用数据"
        },
        {
            "id": "phone-backup-002",
            "model": "Xiaomi 14",
            "brand": "Xiaomi",
            "releaseDate": "2023-01-01",
            "price": 3999,
            "description": "小米14智能手机，骁龙8 Gen 3，徕卡影像",
            "processor": "骁龙8 Gen 3",
            "ram": 12,
            "storage": 256,
            "screenSize": 6.36,
            "resolution": "2670x1200",
            "refreshRate": 120,
            "batteryCapacity": 4610,
            "camera": "50MP+50MP+50MP",
            "os": "Android",
            "support5G": True,
            "source": "备用数据"
        },
        {
            "id": "phone-backup-003",
            "model": "Huawei Mate 60 Pro",
            "brand": "Huawei",
            "releaseDate": "2023-01-01",
            "price": 6999,
            "description": "华为Mate 60 Pro智能手机，麒麟9000S，卫星通话",
            "processor": "麒麟9000S",
            "ram": 12,
            "storage": 512,
            "screenSize": 6.82,
            "resolution": "2720x1260",
            "refreshRate": 120,
            "batteryCapacity": 5000,
            "camera": "50MP+48MP+12MP",
            "os": "Android",
            "support5G": True,
            "source": "备用数据"
        },
        {
            "id": "phone-backup-004",
            "model": "Samsung Galaxy S24",
            "brand": "Samsung",
            "releaseDate": "2024-01-01",
            "price": 5699,
            "description": "三星Galaxy S24智能手机，骁龙8 Gen 3",
            "processor": "骁龙8 Gen 3",
            "ram": 8,
            "storage": 256,
            "screenSize": 6.2,
            "resolution": "2340x1080",
            "refreshRate": 120,
            "batteryCapacity": 4000,
            "camera": "50MP+12MP+10MP",
            "os": "Android",
            "support5G": True,
            "source": "备用数据"
        },
        {
            "id": "phone-backup-005",
            "model": "iPhone 15 Pro Max",
            "brand": "Apple",
            "releaseDate": "2023-01-01",
            "price": 9999,
            "description": "苹果iPhone 15 Pro Max，A17 Pro芯片，钛金属边框",
            "processor": "A17 Pro",
            "ram": 8,
            "storage": 256,
            "screenSize": 6.7,
            "resolution": "2796x1290",
            "refreshRate": 120,
            "batteryCapacity": 4422,
            "camera": "48MP+12MP+12MP",
            "os": "iOS",
            "support5G": True,
            "source": "备用数据"
        },
        {
            "id": "phone-backup-006",
            "model": "Xiaomi 14 Ultra",
            "brand": "Xiaomi",
            "releaseDate": "2024-01-01",
            "price": 6499,
            "description": "小米14 Ultra，徕卡四摄，骁龙8 Gen 3",
            "processor": "骁龙8 Gen 3",
            "ram": 16,
            "storage": 512,
            "screenSize": 6.73,
            "resolution": "3200x1440",
            "refreshRate": 120,
            "batteryCapacity": 5300,
            "camera": "50MP+50MP+50MP+50MP",
            "os": "Android",
            "support5G": True,
            "source": "备用数据"
        }
    ]
    return backup_phones


def validate_phone_data(data: List[Dict[str, Any]]) -> bool:
    """
    验证手机数据的完整性和正确性
    
    Args:
        data: 手机数据列表
        
    Returns:
        验证是否通过
    """
    if not data:
        print("⚠️  数据为空")
        return False
    
    required_fields = ['id', 'model', 'brand', 'processor', 'ram', 'storage',
                      'screenSize', 'resolution', 'refreshRate', 'batteryCapacity',
                      'camera', 'os', 'support5G', 'price', 'releaseDate']
    
    for item in data:
        # 检查必需字段
        for field in required_fields:
            if field not in item:
                print(f"⚠️  数据项 {item.get('id', 'unknown')} 缺少字段: {field}")
                return False
        
        # 检查数据类型
        if not isinstance(item['ram'], int):
            print(f"⚠️  {item['id']} 的 ram 类型错误")
            return False
    
    return True


def run() -> List[Dict[str, Any]]:
    """
    运行手机数据采集
    
    Returns:
        手机数据列表
    """
    print("=" * 60)
    print("🔍 手机数据采集系统")
    print("=" * 60)
    
    if HAS_SCRAPER:
        print("✅ 检测到爬虫模块，将尝试从京东等网站爬取实时数据")
        print("⚠️  注意：爬取过程可能需要一些时间，请耐心等待...")
    else:
        print("⚠️  未检测到爬虫模块，将使用备用数据")
    
    print("\n📊 开始采集手机数据...")
    
    # 获取数据
    phone_data = get_phone_data_from_source()
    
    # 验证数据
    if not validate_phone_data(phone_data):
        print("⚠️  数据验证失败，但仍返回数据")
    
    # 数据统计
    brand_stats = {}
    for p in phone_data:
        brand = p['brand']
        brand_stats[brand] = brand_stats.get(brand, 0) + 1
    
    print(f"\n✅ 手机数据采集完成，共{len(phone_data)}个手机")
    for brand, count in sorted(brand_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"   {brand}: {count} 个 ({count/len(phone_data)*100:.1f}%)")
    
    # 价格统计
    if phone_data:
        prices = [p['price'] for p in phone_data]
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        print(f"   平均价格: ¥{avg_price:.0f}")
        print(f"   价格区间: ¥{min_price}-¥{max_price}")
        
        # 5G支持统计
        g5_count = len([p for p in phone_data if p['support5G']])
        print(f"   5G支持: {g5_count} 个 ({g5_count/len(phone_data)*100:.1f}%)")
        
        # 显示数据来源
        sources = {}
        for p in phone_data:
            source = p.get('source', '未知')
            sources[source] = sources.get(source, 0) + 1
        
        print(f"   数据来源:")
        for source, count in sources.items():
            print(f"     - {source}: {count} 个")
    
    print("\n" + "=" * 60)
    
    return phone_data


if __name__ == "__main__":
    # 测试运行
    print("🚀 启动手机数据采集测试...")
    data = run()
    print(f"\n📋 采集结果: 共获取{len(data)}个手机数据")
    
    if data:
        print("\n📄 前3个手机数据示例:")
        for i, phone in enumerate(data[:3], 1):
            print(f"\n{i}. {phone['brand']} {phone['model']}")
            print(f"   价格: ¥{phone['price']}")
            print(f"   内存: {phone['ram']}GB RAM + {phone['storage']}GB 存储")
            print(f"   屏幕: {phone['screenSize']}英寸, {phone['resolution']}")
            print(f"   处理器: {phone['processor']}")
            print(f"   来源: {phone.get('source', '未知')}")
    
    print("\n✅ 手机数据采集测试完成")