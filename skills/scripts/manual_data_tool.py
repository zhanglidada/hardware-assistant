#!/usr/bin/env python3
"""
手动数据添加工具
安全、可控地添加新的硬件数据
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 数据模板
CPU_TEMPLATE = {
    "id": "",  # 自动生成
    "model": "Intel Core i9-14900KS",
    "brand": "Intel",
    "releaseDate": "2024-03-14",
    "price": 5999,
    "description": "Intel第14代酷睿旗舰特别版",
    "cores": "8P+16E",
    "threads": "32",
    "baseClock": 3.2,
    "boostClock": 6.2,
    "socket": "LGA1700",
    "tdp": 150,
    "integratedGraphics": True,
    "cache": 36,
    "codename": "Raptor Lake Refresh",
    "process": "Intel 7",
    "source": "手动添加"
}

GPU_TEMPLATE = {
    "id": "",  # 自动生成
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
    "rayTracing": True,
    "upscalingTech": "DLSS",
    "source": "手动添加"
}

PHONE_TEMPLATE = {
    "id": "",  # 自动生成
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
    "support5G": True,
    "source": "手动添加"
}


def generate_id(data_type: str, model: str, brand: str) -> str:
    """生成唯一ID"""
    import hashlib
    unique_str = f"{brand}_{model}_{datetime.now().timestamp()}"
    hash_val = hashlib.md5(unique_str.encode()).hexdigest()[:8]
    return f"{data_type}-{hash_val}"


def load_data(file_path: Path):
    """加载现有数据"""
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_data(data, file_path: Path):
    """保存数据"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_cpu_interactive():
    """交互式添加CPU"""
    print("\n" + "="*60)
    print("📝 添加新的 CPU 数据")
    print("="*60)
    
    cpu = CPU_TEMPLATE.copy()
    
    print("\n请输入CPU信息（直接回车使用默认值）：")
    
    model = input(f"型号 [{cpu['model']}]: ").strip()
    if model: cpu['model'] = model
    
    brand = input(f"品牌 [{cpu['brand']}]: ").strip()
    if brand: cpu['brand'] = brand
    
    price = input(f"价格 (元) [{cpu['price']}]: ").strip()
    if price: cpu['price'] = float(price)
    
    cores = input(f"核心数 [{cpu['cores']}]: ").strip()
    if cores: cpu['cores'] = cores
    
    threads = input(f"线程数 [{cpu['threads']}]: ").strip()
    if threads: cpu['threads'] = threads
    
    base_clock = input(f"基础频率 (GHz) [{cpu['baseClock']}]: ").strip()
    if base_clock: cpu['baseClock'] = float(base_clock)
    
    boost_clock = input(f"加速频率 (GHz) [{cpu['boostClock']}]: ").strip()
    if boost_clock: cpu['boostClock'] = float(boost_clock)
    
    socket = input(f"插槽 [{cpu['socket']}]: ").strip()
    if socket: cpu['socket'] = socket
    
    tdp = input(f"TDP (W) [{cpu['tdp']}]: ").strip()
    if tdp: cpu['tdp'] = int(tdp)
    
    cache = input(f"缓存 (MB) [{cpu['cache']}]: ").strip()
    if cache: cpu['cache'] = float(cache)
    
    # 生成ID
    cpu['id'] = generate_id('cpu', cpu['model'], cpu['brand'])
    cpu['releaseDate'] = datetime.now().strftime('%Y-%m-%d')
    
    return cpu


def main():
    """主函数"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║         硬件数据手动添加工具 - 安全可靠               ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    print("\n选择数据类型：")
    print("  1. CPU")
    print("  2. GPU")
    print("  3. 手机")
    print("  4. 查看模板")
    print("  0. 退出")
    
    choice = input("\n请选择 [1-4, 0]: ").strip()
    
    if choice == '1':
        new_cpu = add_cpu_interactive()
        
        print("\n" + "="*60)
        print("📊 确认新增数据：")
        print("="*60)
        print(json.dumps(new_cpu, ensure_ascii=False, indent=2))
        
        confirm = input("\n确认添加? [y/N]: ").strip().lower()
        if confirm == 'y':
            # 加载现有数据
            data_file = Path(__file__).parent.parent.parent / "src" / "mock" / "cpu_data.json"
            data = load_data(data_file)
            
            # 添加新数据
            data.append(new_cpu)
            
            # 保存
            save_data(data, data_file)
            
            print(f"\n✅ 成功添加！当前共有 {len(data)} 条 CPU 数据")
        else:
            print("\n❌ 已取消")
    
    elif choice == '4':
        print("\n" + "="*60)
        print("📋 CPU 数据模板：")
        print("="*60)
        print(json.dumps(CPU_TEMPLATE, ensure_ascii=False, indent=2))
        
        print("\n" + "="*60)
        print("📋 GPU 数据模板：")
        print("="*60)
        print(json.dumps(GPU_TEMPLATE, ensure_ascii=False, indent=2))
        
        print("\n" + "="*60)
        print("📋 手机数据模板：")
        print("="*60)
        print(json.dumps(PHONE_TEMPLATE, ensure_ascii=False, indent=2))
    
    elif choice == '0':
        print("\n👋 再见！")
    
    else:
        print("\n⚠️  无效选择")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 操作已取消")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
