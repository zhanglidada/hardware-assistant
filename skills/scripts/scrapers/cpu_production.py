#!/usr/bin/env python3
"""
CPU数据采集模块 - 维基百科生产级对接版
功能：
1. 抓取维基百科规范化表格
2. 自动清洗引用符、单位符
3. 动态转换频率、缓存、核心数
4. 对接云数据库导入格式
"""

import pandas as pd
import re
import json
import os
import hashlib
import requests

from datetime import datetime
from typing import List, Dict, Any, Optional



class WikiCpuProductionScraper:
    def __init__(self):
        self.exchange_rate = 7.2
        # 扩展目标 URL，覆盖更全的型号
        self.targets = [
            {"brand": "Intel", "url": "https://en.wikipedia.org/wiki/List_of_Intel_Core_i9_processors", "type": "Core i9"},
            {"brand": "Intel", "url": "https://en.wikipedia.org/wiki/List_of_Intel_Core_i7_processors", "type": "Core i7"},
            {"brand": "Intel", "url": "https://en.wikipedia.org/wiki/List_of_Intel_Core_i5_processors", "type": "Core i5"},
            {"brand": "AMD", "url": "https://en.wikipedia.org/wiki/List_of_AMD_Ryzen_processors", "type": "Ryzen"}
        ]

    def _clean(self, val: Any) -> str:
        """深度清洗：去除引用 [1]、换行符和多余空格"""
        if pd.isna(val): return ""
        s = str(val)
        s = re.sub(r'\[.*?\]', '', s) # 去掉维基百科引用
        return s.replace('\n', ' ').strip()

    def _parse_numeric(self, s: str) -> float:
        """从复杂字符串提取第一个数字（处理频率 GHz、缓存 MB 等）"""
        match = re.search(r'(\d+\.?\d*)', self._clean(s))
        return float(match.group(1)) if match else 0.0
    
    def _parse_cores_threads(self, s: str) -> tuple:
        """解析核心/线程数，格式如 '2 (2)' 或 '4/8'"""
        cleaned = self._clean(s)
        # 尝试匹配格式如 "2 (2)" 或 "4/8"
        match = re.search(r'(\d+)\s*[/(]\s*(\d+)', cleaned)
        if match:
            return int(match.group(1)), int(match.group(2))
        
        # 尝试匹配单个数字
        match = re.search(r'(\d+)', cleaned)
        if match:
            cores = int(match.group(1))
            # 对于现代CPU，线程数通常是核心数的2倍（超线程）
            threads = cores * 2 if cores <= 16 else cores
            return cores, threads
        
        return 4, 8  # 默认值

    def parse_price(self, price_str: str) -> Optional[float]:
        s = self._clean(price_str)
        match = re.search(r'\$\s*([\d,]+)', s)
        if match:
            return round(float(match.group(1).replace(',', '')) * self.exchange_rate, 2)
        return None

    def fetch_all(self) -> List[Dict]:
        all_results = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        
        for target in self.targets:
            try:
                print(f"[FETCH] 正在获取 {target['brand']} {target['type']} ...")
                
                # 1. 使用 requests 获取 HTML，绕过 403
                response = requests.get(target['url'], headers=headers, timeout=30)
                response.raise_for_status() 
                
                # 2. 将 HTML 字符串传给 pandas（修复FutureWarning）
                from io import StringIO
                tables = pd.read_html(StringIO(response.text))
                
                for df in tables:
                    # 跳过太小的表格
                    if df.shape[0] < 5 or df.shape[1] < 3:
                        continue
                    
                    # 尝试查找包含CPU数据的行
                    for _, row in df.iterrows():
                        # 检查行中是否包含CPU型号关键词
                        row_str = " ".join(str(cell) for cell in row)
                        if not any(keyword in row_str for keyword in ['Core i', 'Ryzen', 'Processor', 'CPU', 'Model']):
                            continue
                        
                        # 尝试从行中提取模型名称
                        model = None
                        for cell in row:
                            cell_str = self._clean(cell)
                            if (len(cell_str) >= 3 and 
                                any(keyword in cell_str for keyword in ['Core i', 'Ryzen', 'Xeon', 'Athlon', 'Celeron', 'Pentium']) and
                                not any(exclude in cell_str for exclude in ['Model', 'Processor', 'Name'])):
                                model = cell_str
                                break
                        
                        if not model:
                            continue
                        
                        # 解析核心/线程数（从行中查找数字）
                        cores, threads = 4, 8
                        for cell in row:
                            cell_str = self._clean(cell)
                            if any(keyword in cell_str for keyword in ['core', 'Core', 'thread', 'Thread']):
                                cores, threads = self._parse_cores_threads(cell_str)
                                break
                        
                        # 构建CPU对象
                        cpu = {
                            'id': f"cpu-{hashlib.md5(model.encode()).hexdigest()[:8]}",
                            'model': model,
                            'brand': target['brand'],
                            'releaseDate': self._parse_date_from_row(row),
                            'price': self.parse_price_from_row(row),
                            'description': f"{target['brand']} {target['type']} {model}",
                            'cores': str(cores),
                            'threads': str(threads),
                            'baseClock': self._parse_clock_from_row(row, 'base'),
                            'boostClock': self._parse_clock_from_row(row, 'boost'),
                            'socket': self._parse_socket_from_row(row),
                            'tdp': int(self._parse_numeric_from_row(row, 'tdp')),
                            'cache': int(self._parse_numeric_from_row(row, 'cache')),
                            'integratedGraphics': self._parse_graphics_from_row(row),
                            'process': self._parse_process_from_row(row),
                            'source': 'Wikipedia'
                        }
                        
                        all_results.append(cpu)
                        
            except Exception as e:
                print(f"[WARN] 处理 {target['type']} 时出错: {e}")
        
        return all_results

    def _parse_date_from_row(self, row) -> str:
        """从行中解析发布日期"""
        for cell in row:
            cell_str = self._clean(cell)
            match = re.search(r'(20\d{2})', cell_str)
            if match:
                return f"{match.group(1)}-01-01"
        return "2024-01-01"
    
    def parse_price_from_row(self, row) -> Optional[float]:
        """从行中解析价格"""
        for cell in row:
            cell_str = self._clean(cell)
            match = re.search(r'\$\s*([\d,]+)', cell_str)
            if match:
                return round(float(match.group(1).replace(',', '')) * self.exchange_rate, 2)
        return None
    
    def _parse_clock_from_row(self, row, clock_type: str) -> float:
        """从行中解析时钟频率"""
        for cell in row:
            cell_str = self._clean(cell)
            if 'GHz' in cell_str or 'MHz' in cell_str:
                match = re.search(r'(\d+\.?\d*)\s*(?:GHz|MHz)', cell_str)
                if match:
                    value = float(match.group(1))
                    if 'MHz' in cell_str:
                        value = value / 1000  # 转换为GHz
                    return value
        return 3.0 if clock_type == 'base' else 4.0
    
    def _parse_socket_from_row(self, row) -> str:
        """从行中解析插槽类型"""
        for cell in row:
            cell_str = self._clean(cell)
            if any(socket in cell_str for socket in ['LGA', 'Socket', 'AM', 'FM', 'sTR']):
                return cell_str
        return "Unknown"
    
    def _parse_numeric_from_row(self, row, field_type: str) -> float:
        """从行中解析数字字段（TDP、缓存等）"""
        for cell in row:
            cell_str = self._clean(cell)
            if field_type == 'tdp' and ('W' in cell_str or 'TDP' in cell_str):
                match = re.search(r'(\d+)\s*W', cell_str)
                if match:
                    return float(match.group(1))
            elif field_type == 'cache' and ('MB' in cell_str or 'Cache' in cell_str):
                match = re.search(r'(\d+)\s*MB', cell_str)
                if match:
                    return float(match.group(1))
        return 65.0 if field_type == 'tdp' else 16.0
    
    def _parse_graphics_from_row(self, row) -> bool:
        """从行中解析是否集成显卡"""
        for cell in row:
            cell_str = self._clean(cell)
            if any(keyword in cell_str for keyword in ['Graphics', 'GPU', 'iGPU', 'Vega', 'Iris', 'UHD']):
                return True
        return False
    
    def _parse_process_from_row(self, row) -> str:
        """从行中解析制程工艺"""
        for cell in row:
            cell_str = self._clean(cell)
            if any(keyword in cell_str for keyword in ['nm', 'process', 'Process', 'lithography']):
                match = re.search(r'(\d+)\s*nm', cell_str)
                if match:
                    return f"{match.group(1)} nm"
        return "7 nm"

    def run(self):
        # 1. 采集
        raw_data = self.fetch_all()
        
        # 2. 去重
        unique_data = {item['id']: item for item in raw_data}.values()
        
        print(f"\n[OK] 采集清洗完成: 共 {len(unique_data)} 条记录")
        return list(unique_data)

def run():
    scraper = WikiCpuProductionScraper()
    return scraper.run()

if __name__ == "__main__":
    import sys
    # 强制UTF-8编码
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    print("[TEST] 测试维基百科CPU爬虫...")
    data = run()
    
    if data:
        print(f"\n[RESULT] 成功获取 {len(data)} 条CPU数据")
        print("\n[EXAMPLE] 前3条数据示例:")
        for i, cpu in enumerate(data[:3], 1):
            print(f"\n{i}. {cpu['brand']} {cpu['model']}")
            print(f"   价格: {cpu['price'] if cpu['price'] else 'N/A'}")
            print(f"   发布日期: {cpu['releaseDate']}")
            print(f"   核心/线程: {cpu['cores']}/{cpu.get('threads', 'N/A')}")
            print(f"   频率: {cpu['baseClock']}-{cpu['boostClock']}GHz")
            print(f"   插槽: {cpu['socket']}")
            print(f"   来源: {cpu.get('source', '未知')}")
    else:
        print("\n[ERROR] 未获取到任何数据")
    
    print("\n[OK] 测试完成")
