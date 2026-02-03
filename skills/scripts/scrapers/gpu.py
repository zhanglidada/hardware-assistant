#!/usr/bin/env python3
"""
GPU数据采集模块 - 真正的爬虫版本
从京东等电商网站爬取显卡信息并返回标准格式的数据
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
    
    from gpu_scraper import run as run_gpu_scraper
    HAS_SCRAPER = True
except ImportError as e:
    print(f"⚠️  无法导入爬虫模块: {e}")
    print("⚠️  将使用备用数据")
    HAS_SCRAPER = False


def get_gpu_data_from_source() -> List[Dict[str, Any]]:
    """
    从数据源获取GPU数据
    
    Returns:
        GPU数据列表
    """
    if HAS_SCRAPER:
        try:
            # 使用真正的爬虫获取数据
            return run_gpu_scraper()
        except Exception as e:
            print(f"⚠️  爬虫运行失败: {e}")
            print("⚠️  使用备用数据")
    
    # 备用数据（当爬虫失败时使用）
    return get_backup_gpu_data()


def get_backup_gpu_data() -> List[Dict[str, Any]]:
    """
    获取备用GPU数据
    
    Returns:
        GPU数据列表
    """
    backup_gpus = [
        {
            "id": "gpu-backup-001",
            "model": "NVIDIA GeForce RTX 4060",
            "brand": "NVIDIA",
            "releaseDate": "2023-01-01",
            "price": 2499,
            "description": "NVIDIA GeForce RTX 4060显卡，8GB显存，DLSS3支持",
            "vram": 8,
            "busWidth": 128,
            "cudaCores": 3072,
            "coreClock": 1830,
            "memoryClock": 17000,
            "powerConsumption": 115,
            "rayTracing": True,
            "upscalingTech": "DLSS",
            "source": "备用数据"
        },
        {
            "id": "gpu-backup-002",
            "model": "AMD Radeon RX 7600",
            "brand": "AMD",
            "releaseDate": "2023-01-01",
            "price": 2099,
            "description": "AMD Radeon RX 7600显卡，8GB显存，FSR支持",
            "vram": 8,
            "busWidth": 128,
            "cudaCores": 2048,
            "coreClock": 1720,
            "memoryClock": 18000,
            "powerConsumption": 165,
            "rayTracing": True,
            "upscalingTech": "FSR",
            "source": "备用数据"
        },
        {
            "id": "gpu-backup-003",
            "model": "NVIDIA GeForce RTX 4070",
            "brand": "NVIDIA",
            "releaseDate": "2023-01-01",
            "price": 4799,
            "description": "NVIDIA GeForce RTX 4070显卡，12GB显存",
            "vram": 12,
            "busWidth": 192,
            "cudaCores": 5888,
            "coreClock": 1920,
            "memoryClock": 21000,
            "powerConsumption": 200,
            "rayTracing": True,
            "upscalingTech": "DLSS",
            "source": "备用数据"
        },
        {
            "id": "gpu-backup-004",
            "model": "AMD Radeon RX 7800 XT",
            "brand": "AMD",
            "releaseDate": "2023-01-01",
            "price": 4599,
            "description": "AMD Radeon RX 7800 XT显卡，16GB显存",
            "vram": 16,
            "busWidth": 256,
            "cudaCores": 3840,
            "coreClock": 2124,
            "memoryClock": 19500,
            "powerConsumption": 263,
            "rayTracing": True,
            "upscalingTech": "FSR",
            "source": "备用数据"
        },
        {
            "id": "gpu-backup-005",
            "model": "NVIDIA GeForce RTX 4090",
            "brand": "NVIDIA",
            "releaseDate": "2022-01-01",
            "price": 12999,
            "description": "NVIDIA GeForce RTX 4090显卡，24GB显存，性能旗舰",
            "vram": 24,
            "busWidth": 384,
            "cudaCores": 16384,
            "coreClock": 2235,
            "memoryClock": 21000,
            "powerConsumption": 450,
            "rayTracing": True,
            "upscalingTech": "DLSS",
            "source": "备用数据"
        },
        {
            "id": "gpu-backup-006",
            "model": "AMD Radeon RX 7900 XTX",
            "brand": "AMD",
            "releaseDate": "2022-01-01",
            "price": 7999,
            "description": "AMD Radeon RX 7900 XTX显卡，24GB显存，AMD旗舰",
            "vram": 24,
            "busWidth": 384,
            "cudaCores": 6144,
            "coreClock": 2300,
            "memoryClock": 20000,
            "powerConsumption": 355,
            "rayTracing": True,
            "upscalingTech": "FSR",
            "source": "备用数据"
        }
    ]
    return backup_gpus


def validate_gpu_data(data: List[Dict[str, Any]]) -> bool:
    """
    验证GPU数据的完整性和正确性
    
    Args:
        data: GPU数据列表
        
    Returns:
        验证是否通过
    """
    if not data:
        print("⚠️  数据为空")
        return False
    
    required_fields = ['id', 'model', 'brand', 'vram', 'busWidth', 'cudaCores',
                      'coreClock', 'memoryClock', 'powerConsumption', 'rayTracing',
                      'upscalingTech', 'price', 'releaseDate']
    
    for item in data:
        # 检查必需字段
        for field in required_fields:
            if field not in item:
                print(f"⚠️  数据项 {item.get('id', 'unknown')} 缺少字段: {field}")
                return False
        
        # 检查数据类型
        if not isinstance(item['vram'], int):
            print(f"⚠️  {item['id']} 的 vram 类型错误")
            return False
    
    return True


def run() -> List[Dict[str, Any]]:
    """
    运行GPU数据采集
    
    Returns:
        GPU数据列表
    """
    print("=" * 60)
    print("🔍 GPU数据采集系统")
    print("=" * 60)
    
    if HAS_SCRAPER:
        print("✅ 检测到爬虫模块，将尝试从京东等网站爬取实时数据")
        print("⚠️  注意：爬取过程可能需要一些时间，请耐心等待...")
    else:
        print("⚠️  未检测到爬虫模块，将使用备用数据")
    
    print("\n📊 开始采集GPU数据...")
    
    # 获取数据
    gpu_data = get_gpu_data_from_source()
    
    # 验证数据
    if not validate_gpu_data(gpu_data):
        print("⚠️  数据验证失败，但仍返回数据")
    
    # 数据统计
    nvidia_count = len([g for g in gpu_data if g['brand'] == 'NVIDIA'])
    amd_count = len([g for g in gpu_data if g['brand'] == 'AMD'])
    other_count = len(gpu_data) - nvidia_count - amd_count
    rt_count = len([g for g in gpu_data if g['rayTracing']])
    
    print(f"\n✅ GPU数据采集完成，共{len(gpu_data)}个显卡")
    print(f"   NVIDIA: {nvidia_count} 个 ({nvidia_count/len(gpu_data)*100:.1f}%)")
    print(f"   AMD: {amd_count} 个 ({amd_count/len(gpu_data)*100:.1f}%)")
    if other_count > 0:
        print(f"   其他: {other_count} 个 ({other_count/len(gpu_data)*100:.1f}%)")
    print(f"   支持光追: {rt_count} 个 ({rt_count/len(gpu_data)*100:.1f}%)")
    
    # 价格统计
    if gpu_data:
        prices = [g['price'] for g in gpu_data]
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        print(f"   平均价格: ¥{avg_price:.0f}")
        print(f"   价格区间: ¥{min_price}-¥{max_price}")
        
        # 显示数据来源
        sources = {}
        for g in gpu_data:
            source = g.get('source', '未知')
            sources[source] = sources.get(source, 0) + 1
        
        print(f"   数据来源:")
        for source, count in sources.items():
            print(f"     - {source}: {count} 个")
    
    print("\n" + "=" * 60)
    
    return gpu_data


if __name__ == "__main__":
    # 测试运行
    print("🚀 启动GPU数据采集测试...")
    data = run()
    print(f"\n📋 采集结果: 共获取{len(data)}个GPU数据")
    
    if data:
        print("\n📄 前3个GPU数据示例:")
        for i, gpu in enumerate(data[:3], 1):
            print(f"\n{i}. {gpu['brand']} {gpu['model']}")
            print(f"   价格: ¥{gpu['price']}")
            print(f"   显存: {gpu['vram']}GB")
            print(f"   核心频率: {gpu['coreClock']}MHz")
            print(f"   光追: {'支持' if gpu['rayTracing'] else '不支持'}")
            print(f"   来源: {gpu.get('source', '未知')}")
    
    print("\n✅ GPU数据采集测试完成")