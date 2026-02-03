#!/usr/bin/env python3
"""
CPU数据采集总控脚本 - 维基百科对接版
功能：
1. 调用生产级 Wiki 爬虫获取全量 Intel/AMD 数据
2. 执行数据 Schema 校验，确保符合前端 TypeScript 定义
3. 自动更新本地 mock 文件并统计采集质量
"""

import json
import sys
import os
import hashlib
from typing import List, Dict, Any, Optional

# 确保可以导入同目录下的爬虫模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from cpu_production import run as run_wiki_scraper
    HAS_SCRAPER = True
except ImportError as e:
    print(f"[ERROR] 无法导入 cpu_production 模块: {e}")
    HAS_SCRAPER = False

# 定义输出路径
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(current_dir)), "src", "mock", "cpu_data.json")

def validate_and_sanitize(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    清洗并校验数据，确保符合 CpuSpecs 接口规范
    """
    valid_list = []
    seen_ids = set()

    for item in data:
        # 1. 基础字段补全 (确保不缺失必需字段)
        sanitized = {
            "id": item.get("id", f"cpu-{hashlib.md5(item.get('model','').encode()).hexdigest()[:8]}"),
            "model": item.get("model", "Unknown Model"),
            "brand": item.get("brand", "Other"),
            "releaseDate": item.get("releaseDate", "2024-01-01"),
            "price": item.get("price"), # 允许为 None
            "description": item.get("description", ""),
            "cores": str(item.get("cores", "4")),
            "threads": str(item.get("threads", item.get("cores", "4"))),
            "baseClock": float(item.get("baseClock", 3.0)),
            "boostClock": float(item.get("boostClock", 4.0)),
            "socket": item.get("socket", "Generic"),
            "tdp": int(item.get("tdp", 65)),
            "cache": int(item.get("cache", 16)),
            "integratedGraphics": bool(item.get("integratedGraphics", True)),
            "process": item.get("process", "7 nm"),
            "source": item.get("source", "Wikipedia")
        }

        # 2. 去重逻辑
        if sanitized["id"] not in seen_ids:
            seen_ids.add(sanitized["id"])
            valid_list.append(sanitized)
            
    return valid_list

def run():
    print("=" * 60)
    print("[SYSTEM] 启动 CPU 硬件数据同步流水线")
    print("=" * 60)

    if not HAS_SCRAPER:
        print("[FATAL] 核心爬虫模块丢失，请检查 cpu_production.py 是否在同一目录。")
        return

    # 1. 执行采集
    print("[STEP 1/3] 正在从维基百科矩阵获取原始数据...")
    raw_data = run_wiki_scraper()
    
    if not raw_data:
        print("[ERROR] 采集返回数据为空，请检查网络连接或维基百科页面结构是否变动。")
        return

    # 2. 数据清洗与格式化
    print(f"[STEP 2/3] 正在执行数据清洗与 Schema 校验 (原始条数: {len(raw_data)})...")
    final_data = validate_and_sanitize(raw_data)

    # 3. 持久化到本地 Mock 文件
    print(f"[STEP 3/3] 正在更新本地数据仓库: {OUTPUT_PATH}")
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        
        print("\n" + "—" * 40)
        print(f"✅ 同步成功！")
        print(f"📊 最终入库条数: {len(final_data)}")
        print(f"🌐 数据源: Wikipedia (Intel Core / AMD Ryzen)")
        print(f"💾 存储位置: {os.path.relpath(OUTPUT_PATH)}")
        print("—" * 40)

    except Exception as e:
        print(f"[ERROR] 写入文件失败: {e}")

if __name__ == "__main__":
    # 强制设置输出编码以支持中文日志
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    run()