#!/usr/bin/env python3
"""
获取近10年的CPU数据并按品牌和型号分类
"""

import json
import os
import sys
from datetime import datetime, timedelta

# 定义必要的函数
def get_recent_cpu_data_from_mock(cpu_data, years=10):
    """
    从本地mock数据中过滤出近10年的CPU数据
    """
    print(f"🔍 从本地mock数据中过滤近{years}年的CPU数据...")
    
    # 计算时间范围（使用不带时区的日期）
    today = datetime.now()
    cutoff_date = today - timedelta(days=years*365)
    
    print(f"📅 时间范围: {cutoff_date.strftime('%Y-%m-%d')} 到 {today.strftime('%Y-%m-%d')}")
    
    # 过滤出近10年的数据
    recent_cpu_data = []
    
    for cpu in cpu_data:
        try:
            # 处理不同格式的日期
            release_date_str = cpu.get('releaseDate', '')
            
            if isinstance(release_date_str, dict) and '$date' in release_date_str:
                # 处理MongoDB日期格式
                date_str = release_date_str['$date']
                # 解析ISO格式日期
                if isinstance(date_str, str):
                    # 处理ISO格式字符串
                    if date_str.endswith('Z'):
                        # 解析带时区的日期，然后转换为不带时区的日期
                        dt_with_tz = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        release_date = dt_with_tz.replace(tzinfo=None)
                    else:
                        # 直接解析
                        release_date = datetime.fromisoformat(date_str)
                else:
                    # 处理时间戳
                    release_date = datetime.fromtimestamp(date_str / 1000)
            else:
                # 处理字符串日期格式
                if isinstance(release_date_str, str):
                    # 尝试不同的日期格式
                    for fmt in ['%Y-%m-%d', '%Y-%m', '%Y']:
                        try:
                            release_date = datetime.strptime(release_date_str, fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        # 如果所有格式都失败，跳过
                        print(f"⚠️  无法解析日期: {release_date_str}")
                        continue
                else:
                    # 其他类型，跳过
                    continue
            
            # 检查是否在时间范围内
            if release_date >= cutoff_date:
                recent_cpu_data.append(cpu)
                
        except Exception as e:
            print(f"⚠️  处理CPU数据时出错: {e}")
            continue
    
    print(f"✅ 过滤出 {len(recent_cpu_data)} 个近{years}年的CPU数据")
    return recent_cpu_data

def categorize_cpu_data(cpu_data):
    """
    按品牌和型号分类CPU数据
    """
    print("📊 开始按品牌和型号分类CPU数据...")
    
    categorized_data = {}
    
    for cpu in cpu_data:
        brand = cpu.get('brand', '其他')
        
        if brand not in categorized_data:
            categorized_data[brand] = []
        
        categorized_data[brand].append(cpu)
    
    # 对每个品牌的CPU按型号排序
    for brand, cpus in categorized_data.items():
        # 按型号排序（尝试提取数字部分）
        cpus.sort(key=lambda x: extract_model_number(x.get('model', '')))
    
    # 统计每个品牌的数量
    for brand, cpus in categorized_data.items():
        print(f"   {brand}: {len(cpus)} 个")
    
    return categorized_data

def extract_model_number(model):
    """
    从型号中提取数字部分用于排序
    """
    import re
    
    # 提取数字部分
    numbers = re.findall(r'\d+', model)
    if numbers:
        # 组合所有数字
        return int(''.join(numbers))
    return 0

def save_data(data, filename):
    """
    保存数据到JSON文件
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 数据已保存到: {filename}")
    except Exception as e:
        print(f"❌ 保存数据失败: {e}")

def save_results(raw_data, categorized_data):
    """
    保存结果并生成报告
    """
    # 保存结果
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存原始数据
    raw_output_file = os.path.join(output_dir, 'recent_cpu_data_raw.json')
    save_data(raw_data, raw_output_file)
    
    # 保存分类数据
    categorized_output_file = os.path.join(output_dir, 'recent_cpu_data_categorized.json')
    save_data(categorized_data, categorized_output_file)
    
    # 生成统计报告
    generate_report(raw_data, categorized_data)
    
    print("🎉 任务执行完成！")

def generate_report(raw_data, categorized_data):
    """
    生成统计报告
    """
    print("📋 生成CPU数据统计报告...")
    
    # 计算基本统计信息
    total_count = len(raw_data)
    brand_count = len(categorized_data)
    
    print(f"\n=== 近10年CPU数据统计报告 ===")
    print(f"总CPU数量: {total_count}")
    print(f"品牌数量: {brand_count}")
    print("\n品牌分布:")
    
    for brand, cpus in sorted(categorized_data.items(), key=lambda x: len(x[1]), reverse=True):
        count = len(cpus)
        percentage = (count / total_count) * 100
        print(f"  {brand}: {count}个 ({percentage:.1f}%)")
    
    # 计算价格统计
    prices = [cpu.get('price', 0) for cpu in raw_data if cpu.get('price', 0) > 0]
    if prices:
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        print("\n价格统计:")
        print(f"  平均价格: ¥{avg_price:.0f}")
        print(f"  最低价格: ¥{min_price}")
        print(f"  最高价格: ¥{max_price}")
    
    # 计算核心数统计
    cores = []
    for cpu in raw_data:
        core_str = cpu.get('cores', '')
        try:
            # 尝试提取核心数
            if isinstance(core_str, str):
                # 处理类似 "8P+16E" 的格式
                import re
                core_nums = re.findall(r'\d+', core_str)
                if core_nums:
                    total_cores = sum(int(num) for num in core_nums)
                    cores.append(total_cores)
            elif isinstance(core_str, (int, float)):
                cores.append(int(core_str))
        except:
            pass
    
    if cores:
        avg_cores = sum(cores) / len(cores)
        min_cores = min(cores)
        max_cores = max(cores)
        
        print("\n核心数统计:")
        print(f"  平均核心数: {avg_cores:.1f}")
        print(f"  最少核心数: {min_cores}")
        print(f"  最多核心数: {max_cores}")
    
    print("\n=== 报告结束 ===")

def main():
    """
    主函数
    """
    print("🚀 开始执行获取近10年CPU数据的任务...")
    
    # 直接使用本地mock数据
    print("⚠️  使用本地mock数据作为备选")
    mock_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src', 'mock', 'cpu_data.json')
    try:
        with open(mock_data_path, 'r', encoding='utf-8') as f:
            all_cpu_data = json.load(f)
        print(f"✅ 成功加载本地mock数据: {len(all_cpu_data)}个CPU")
    except Exception as e:
        print(f"❌ 加载本地mock数据失败: {e}")
        sys.exit(1)
    
    # 处理mock数据
    recent_cpu_data = get_recent_cpu_data_from_mock(all_cpu_data)
    categorized_data = categorize_cpu_data(recent_cpu_data)
    save_results(recent_cpu_data, categorized_data)

if __name__ == "__main__":
    main()
