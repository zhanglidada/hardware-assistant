#!/usr/bin/env python3
"""
AMD Ryzen 处理器数据抓取脚本
从维基百科提取 AMD Ryzen 处理器表格数据

数据源: https://en.wikipedia.org/wiki/List_of_AMD_Ryzen_processors
"""

import pandas as pd
import json
import os
import ssl
import urllib.request
from io import StringIO
from datetime import datetime
from typing import List, Dict, Any


def fetch_ryzen_tables(url: str) -> List[pd.DataFrame]:
    """
    从维基百科获取所有表格
    
    Args:
        url: 维基百科页面URL
        
    Returns:
        表格列表
    """
    print(f"📡 正在获取数据: {url}")
    try:
        # 禁用 SSL 证书验证（仅用于开发环境）
        ssl._create_default_https_context = ssl._create_unverified_context
        
        # 设置 User-Agent 避免被维基百科拒绝
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        req = urllib.request.Request(url, headers=headers)
        
        # 先获取HTML内容
        with urllib.request.urlopen(req) as response:
            html_content = response.read().decode('utf-8')
        
        # 从HTML内容中解析表格
        tables = pd.read_html(StringIO(html_content))
        print(f"✅ 成功获取 {len(tables)} 个表格")
        return tables
    except Exception as e:
        print(f"❌ 获取表格失败: {e}")
        return []


def analyze_tables(tables: List[pd.DataFrame]) -> None:
    """
    分析表格结构，帮助识别目标表格
    
    Args:
        tables: 表格列表
    """
    print("\n" + "="*80)
    print("📊 表格结构分析")
    print("="*80)
    
    for idx, table in enumerate(tables):
        print(f"\n表格 #{idx}")
        print(f"  行数: {len(table)}")
        print(f"  列数: {len(table.columns)}")
        print(f"  列名: {list(table.columns[:5])}{'...' if len(table.columns) > 5 else ''}")
        
        # 显示前2行数据示例
        if len(table) > 0:
            print(f"  示例数据:")
            print(table.head(2).to_string(max_cols=5, index=False))


def extract_ryzen_data(tables: List[pd.DataFrame]) -> List[Dict[str, Any]]:
    """
    从表格中提取 Ryzen 处理器数据
    
    Args:
        tables: 表格列表
        
    Returns:
        处理器数据列表
    """
    all_processors = []
    
    for idx, table in enumerate(tables):
        # 跳过太小的表格（可能不是处理器数据）
        if len(table) < 3 or len(table.columns) < 5:
            continue
        
        # 检查是否包含处理器相关列
        columns_lower = [str(col).lower() for col in table.columns]
        
        # 常见的处理器表格列名关键词
        keywords = ['model', 'core', 'thread', 'frequency', 'tdp', 'cache', 'socket']
        has_keywords = any(keyword in ' '.join(columns_lower) for keyword in keywords)
        
        if not has_keywords:
            continue
        
        print(f"\n🔍 处理表格 #{idx} (共 {len(table)} 行)")
        
        # 转换为字典列表
        try:
            records = table.to_dict('records')
            
            for record in records:
                # 清理数据：移除 NaN 值，并将元组键转换为字符串
                cleaned_record = {}
                for k, v in record.items():
                    # 将元组键转换为字符串
                    if isinstance(k, tuple):
                        key = ' - '.join(str(x) for x in k if str(x).strip())
                    else:
                        key = str(k)
                    
                    # 移除 NaN 值
                    if pd.notna(v):
                        cleaned_record[key] = v
                    else:
                        cleaned_record[key] = None
                
                all_processors.append({
                    'source_table': idx,
                    'data': cleaned_record
                })
            
            print(f"  ✅ 提取 {len(records)} 条记录")
            
        except Exception as e:
            print(f"  ⚠️  处理失败: {e}")
    
    return all_processors


def save_data(data: List[Dict[str, Any]], output_dir: str = "output") -> None:
    """
    保存数据到文件
    
    Args:
        data: 处理器数据
        output_dir: 输出目录
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存原始数据（包含表格索引）
    raw_file = os.path.join(output_dir, f"ryzen_raw_{timestamp}.json")
    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n💾 原始数据已保存: {raw_file}")
    
    # 保存简化数据（仅数据部分）
    simplified_data = [item['data'] for item in data]
    simple_file = os.path.join(output_dir, f"ryzen_simplified_{timestamp}.json")
    with open(simple_file, 'w', encoding='utf-8') as f:
        json.dump(simplified_data, f, ensure_ascii=False, indent=2)
    print(f"💾 简化数据已保存: {simple_file}")
    
    # 保存汇总信息
    summary = {
        'total_records': len(data),
        'tables_count': len(set(item['source_table'] for item in data)),
        'timestamp': timestamp,
        'source_url': 'https://en.wikipedia.org/wiki/List_of_AMD_Ryzen_processors'
    }
    
    summary_file = os.path.join(output_dir, f"ryzen_summary_{timestamp}.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"💾 汇总信息已保存: {summary_file}")


def main():
    """主函数"""
    url = "https://en.wikipedia.org/wiki/List_of_AMD_Ryzen_processors"
    
    print("🚀 AMD Ryzen 处理器数据抓取")
    print("="*80)
    
    # 1. 获取表格
    tables = fetch_ryzen_tables(url)
    if not tables:
        print("❌ 未能获取任何表格，程序退出")
        return
    
    # 2. 分析表格结构（可选，用于调试）
    analyze_tables(tables)
    
    # 3. 提取数据
    print("\n" + "="*80)
    print("📥 提取处理器数据")
    print("="*80)
    processors = extract_ryzen_data(tables)
    
    if not processors:
        print("⚠️  未提取到任何处理器数据")
        return
    
    # 4. 保存数据
    print("\n" + "="*80)
    print(f"✨ 总共提取 {len(processors)} 条处理器记录")
    print("="*80)
    save_data(processors)
    
    print("\n✅ 数据抓取完成!")


if __name__ == "__main__":
    main()
