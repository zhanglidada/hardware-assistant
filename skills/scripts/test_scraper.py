#!/usr/bin/env python3
"""
测试scraper模块
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_cpu_scraper():
    """测试CPU scraper"""
    print("🔍 测试CPU scraper...")
    try:
        import scripts.scrapers.cpu as cpu_scraper
        data = cpu_scraper.run()
        print(f"✅ CPU scraper运行成功，返回{len(data)}条数据")
        print(f"第一条数据: {data[0]['model'] if data else '无数据'}")
        return True
    except Exception as e:
        print(f"❌ CPU scraper测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gpu_scraper():
    """测试GPU scraper"""
    print("🔍 测试GPU scraper...")
    try:
        import scripts.scrapers.gpu as gpu_scraper
        data = gpu_scraper.run()
        print(f"✅ GPU scraper运行成功，返回{len(data)}条数据")
        print(f"第一条数据: {data[0]['model'] if data else '无数据'}")
        return True
    except Exception as e:
        print(f"❌ GPU scraper测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phone_scraper():
    """测试Phone scraper"""
    print("🔍 测试Phone scraper...")
    try:
        import scripts.scrapers.phone as phone_scraper
        data = phone_scraper.run()
        print(f"✅ Phone scraper运行成功，返回{len(data)}条数据")
        print(f"第一条数据: {data[0]['model'] if data else '无数据'}")
        return True
    except Exception as e:
        print(f"❌ Phone scraper测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🧪 开始测试scraper模块...")
    
    results = []
    results.append(test_cpu_scraper())
    results.append(test_gpu_scraper())
    results.append(test_phone_scraper())
    
    print("\n📋 测试结果总结:")
    print(f"CPU scraper: {'✅ 通过' if results[0] else '❌ 失败'}")
    print(f"GPU scraper: {'✅ 通过' if results[1] else '❌ 失败'}")
    print(f"Phone scraper: {'✅ 通过' if results[2] else '❌ 失败'}")
    
    if all(results):
        print("🎉 所有scraper测试通过！")
        return 0
    else:
        print("⚠️ 部分scraper测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
