#!/usr/bin/env python3
"""
从网上获取CPU硬件信息并按品牌和型号分类
数据源：TechPowerUp CPU数据库
"""

import json
import os
import sys
import time
import random
import ssl
import gzip
from io import BytesIO
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser

# 创建一个不验证SSL证书的上下文
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# 自定义HTML解析器来处理表格数据
class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_thead = False
        self.in_row = False
        self.in_cell = False
        self.current_row = []
        self.headers = []
        self.rows = []
        self.current_cell = ""
    
    def handle_starttag(self, tag, attrs):
        if tag == 'table' and any(attr[0] == 'class' and 'items-desktop-table' in attr[1] for attr in attrs):
            self.in_table = True
        elif self.in_table and tag == 'thead':
            self.in_thead = True
        elif self.in_table and tag == 'tr':
            self.in_row = True
            self.current_row = []
        elif (self.in_table and self.in_row) and tag == 'th':
            self.in_cell = True
            self.current_cell = ""
        elif (self.in_table and self.in_row) and tag == 'td':
            self.in_cell = True
            self.current_cell = ""
    
    def handle_endtag(self, tag):
        if tag == 'table':
            self.in_table = False
        elif tag == 'thead':
            self.in_thead = False
        elif tag == 'tr':
            self.in_row = False
            if self.current_row:
                if self.in_thead:
                    self.headers = self.current_row
                else:
                    self.rows.append(self.current_row)
        elif tag == 'th' or tag == 'td':
            self.in_cell = False
            if self.current_cell:
                self.current_row.append(self.current_cell.strip())
                self.current_cell = ""
    
    def handle_data(self, data):
        if self.in_cell:
            self.current_cell += data
    
    def get_table_data(self):
        return self.headers, self.rows

class CpuWebScraper:
    """CPU网络爬虫"""
    
    def __init__(self):
        """初始化爬虫"""
        self.base_url = "https://www.techpowerup.com"
        self.cpu_db_url = f"{self.base_url}/cpu-specs/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
    
    def get_cpu_data(self):
        """
        从TechPowerUp获取CPU数据
        
        Returns:
            CPU数据列表
        """
        print("🔍 开始从TechPowerUp获取CPU数据...")
        
        try:
            # 发送请求
            print(f"📄 获取页面: {self.cpu_db_url}")
            request = Request(self.cpu_db_url, headers=self.headers)
            
            # 设置超时并使用SSL上下文
            with urlopen(request, timeout=30, context=ssl_context) as response:
                content = response.read()
                
                # 检查是否是gzip压缩内容
                content_encoding = response.info().get('Content-Encoding', '')
                if 'gzip' in content_encoding:
                    # 解压缩gzip内容
                    buffer = BytesIO(content)
                    with gzip.GzipFile(fileobj=buffer, mode='rb') as f:
                        content = f.read()
                
                # 解码内容
                encoding = response.info().get_content_charset('utf-8')
                html_content = content.decode(encoding)
            
            # 解析页面
            parser = TableParser()
            parser.feed(html_content)
            
            # 获取表格数据
            headers, rows = parser.get_table_data()
            
            if not rows:
                print("❌ 未找到CPU数据表格")
                return []
            
            print(f"📊 表格列: {headers}")
            print(f"📈 找到 {len(rows)} 行CPU数据")
            
            cpu_data = []
            
            # 解析每一行
            for i, row in enumerate(rows):  # 处理所有行数据
                try:
                    cpu_item = self._parse_cpu_row(row)
                    if cpu_item:
                        cpu_data.append(cpu_item)
                        print(f"  ✅ 解析成功: {cpu_item['model']}")
                    else:
                        print(f"  ⚠️  解析失败: 无法提取CPU信息")
                    
                    # 显示进度
                    if (i + 1) % 10 == 0:
                        print(f"  已处理 {i + 1} 个CPU...")
                    
                    # 避免请求过快，添加随机延迟
                    time.sleep(random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    print(f"  ❌ 解析第{i+1}行失败: {e}")
                    continue
            
            print(f"✅ 成功获取 {len(cpu_data)} 个CPU数据")
            return cpu_data
            
        except HTTPError as e:
            print(f"❌ HTTP错误: {e.code} - {e.reason}")
            return []
        except URLError as e:
            print(f"❌ URL错误: {e.reason}")
            return []
        except Exception as e:
            print(f"❌ 处理数据时出错: {e}")
            return []
    
    def _parse_cpu_row(self, row):
        """
        解析CPU表格行
        
        Args:
            row: 表格行数据列表
            
        Returns:
            CPU数据字典
        """
        if len(row) < 8:
            return None
        
        # 提取各列数据
        model = row[0]
        if not model:
            return None
        
        # 从名称中提取品牌
        brand = self._extract_brand(model)
        
        # 提取代号
        codename = row[1]
        
        # 提取核心/线程数
        cores_text = row[2]
        cores_info = self._parse_cores(cores_text)
        
        # 提取时钟频率
        clock_text = row[3]
        clock_info = self._parse_clock(clock_text)
        
        # 提取插槽
        socket = row[4]
        
        # 提取制程工艺
        process = row[5]
        
        # 提取缓存
        cache_text = row[6]
        cache = self._parse_cache(cache_text)
        
        # 提取TDP
        tdp_text = row[7]
        tdp = self._parse_tdp(tdp_text)
        
        # 构建CPU数据
        cpu_data = {
            'id': self._generate_id(model, brand),
            'model': model,
            'brand': brand,
            'releaseDate': self._estimate_release_date(model, brand),
            'price': self._estimate_price(model, brand, cores_info['cores']),
            'description': f"{brand} {model} - {codename} - {cores_info['cores']}核心{cores_info['threads']}线程",
            'cores': str(cores_info['cores']),
            'threads': str(cores_info['threads']),
            'baseClock': clock_info['base'],
            'boostClock': clock_info['boost'],
            'socket': socket,
            'process': process,
            'tdp': tdp,
            'cache': cache,
            'integratedGraphics': self._has_integrated_graphics(model, brand),
            'codename': codename,
            'source': 'TechPowerUp'
        }
        
        return cpu_data
    
    def _extract_brand(self, model):
        """
        从型号中提取品牌
        
        Args:
            model: CPU型号字符串
            
        Returns:
            品牌名称
        """
        model_upper = model.upper()
        
        brand_keywords = {
            'Intel': ['INTEL', 'CORE', 'XEON', 'PENTIUM', 'CELERON', 'ATOM'],
            'AMD': ['AMD', 'RYZEN', 'ATHLON', 'THREADRIPPER', 'EPYC', 'FX'],
            'Apple': ['APPLE', 'M1', 'M2', 'M3', 'M4'],
            'Qualcomm': ['QUALCOMM', 'SNAPDRAGON'],
            'MediaTek': ['MEDIATEK', 'DIMENSITY']
        }
        
        for brand, keywords in brand_keywords.items():
            for keyword in keywords:
                if keyword in model_upper:
                    return brand
        
        return '其他'
    
    def _parse_cores(self, cores_text):
        """
        解析核心/线程数
        
        Args:
            cores_text: 核心/线程数文本
            
        Returns:
            核心和线程数字典
        """
        import re
        
        # 格式: "6 / 12" 或 "8 / 16"
        try:
            if '/' in cores_text:
                parts = cores_text.split('/')
                cores = int(parts[0].strip())
                threads = int(parts[1].strip())
            else:
                # 尝试提取数字
                numbers = re.findall(r'\d+', cores_text)
                if len(numbers) >= 2:
                    cores = int(numbers[0])
                    threads = int(numbers[1])
                elif len(numbers) == 1:
                    cores = int(numbers[0])
                    threads = cores * 2  # 假设超线程
                else:
                    cores = 4
                    threads = 8
        except:
            cores = 4
            threads = 8
        
        return {'cores': cores, 'threads': threads}
    
    def _parse_clock(self, clock_text):
        """
        解析时钟频率
        
        Args:
            clock_text: 时钟频率文本
            
        Returns:
            基础和 boost 频率字典
        """
        import re
        
        # 格式: "3.4 to 4.6 GHz" 或 "3.6-4.2 GHz"
        try:
            # 提取所有数字
            numbers = re.findall(r'\d+\.?\d*', clock_text)
            if len(numbers) >= 2:
                base = float(numbers[0])
                boost = float(numbers[1])
            elif len(numbers) == 1:
                base = float(numbers[0])
                boost = base * 1.2  # 估算睿频
            else:
                base = 3.0
                boost = 4.0
            
            # 检查单位
            if 'MHZ' in clock_text.upper():
                base = base / 1000
                boost = boost / 1000
                
        except:
            base = 3.0
            boost = 4.0
        
        return {'base': base, 'boost': boost}
    
    def _parse_cache(self, cache_text):
        """
        解析缓存
        
        Args:
            cache_text: 缓存文本
            
        Returns:
            缓存大小（MB）
        """
        import re
        
        try:
            # 提取数字
            numbers = re.findall(r'\d+\.?\d*', cache_text)
            if numbers:
                cache = float(numbers[0])
                # 检查单位
                if 'KB' in cache_text.upper():
                    cache = cache / 1024  # KB转MB
                elif 'GB' in cache_text.upper():
                    cache = cache * 1024  # GB转MB
                return cache
        except:
            pass
        
        # 默认值
        return 8.0
    
    def _parse_tdp(self, tdp_text):
        """
        解析TDP
        
        Args:
            tdp_text: TDP文本
            
        Returns:
            TDP值（W）
        """
        import re
        
        try:
            # 提取数字
            numbers = re.findall(r'\d+', tdp_text)
            if numbers:
                return int(numbers[0])
        except:
            pass
        
        # 默认值
        return 65
    
    def _estimate_release_date(self, model, brand):
        """
        估算发布日期
        
        Args:
            model: CPU型号
            brand: CPU品牌
            
        Returns:
            发布日期字符串
        """
        current_year = datetime.now().year
        
        # 尝试从型号中提取年份
        import re
        year_match = re.search(r'(20\d{2})', model)
        if year_match:
            year = int(year_match.group(1))
            if 2010 <= year <= current_year:
                return f"{year}-01-01"
        
        # 根据品牌和型号特征估算
        model_lower = model.lower()
        
        if brand == 'Intel':
            if any(x in model_lower for x in ['14900', '13900', '12900']):
                return '2023-01-01'
            elif any(x in model_lower for x in ['11900', '10900']):
                return '2020-01-01'
            elif any(x in model_lower for x in ['9900', '9700']):
                return '2018-01-01'
        elif brand == 'AMD':
            if any(x in model_lower for x in ['9950x', '7950x', '5950x']):
                return '2022-01-01'
            elif any(x in model_lower for x in ['3950x', '3900x']):
                return '2019-01-01'
            elif any(x in model_lower for x in ['1800x', '1700x']):
                return '2017-01-01'
        elif brand == 'Apple':
            if 'm4' in model_lower:
                return '2024-01-01'
            elif 'm3' in model_lower:
                return '2023-01-01'
            elif 'm2' in model_lower:
                return '2022-01-01'
            elif 'm1' in model_lower:
                return '2020-01-01'
        
        # 默认返回当前年份
        return f"{current_year}-01-01"
    
    def _estimate_price(self, model, brand, cores):
        """
        估算价格
        
        Args:
            model: CPU型号
            brand: CPU品牌
            cores: 核心数
            
        Returns:
            价格（元）
        """
        base_price = 1000  # 基础价格
        
        # 品牌加成
        if brand == 'Intel':
            base_price *= 1.1
        elif brand == 'AMD':
            base_price *= 0.9
        elif brand == 'Apple':
            base_price *= 1.5
        
        # 核心数加成
        core_multiplier = 1 + (cores - 4) * 0.2  # 每多一个核心增加20%
        base_price *= core_multiplier
        
        # 型号系列加成
        model_lower = model.lower()
        if brand == 'Intel':
            if 'i9' in model_lower:
                base_price *= 1.8
            elif 'i7' in model_lower:
                base_price *= 1.5
            elif 'i5' in model_lower:
                base_price *= 1.2
            elif 'xeon' in model_lower:
                base_price *= 2.0
        elif brand == 'AMD':
            if 'ryzen 9' in model_lower or 'threadripper' in model_lower:
                base_price *= 1.8
            elif 'ryzen 7' in model_lower:
                base_price *= 1.5
            elif 'ryzen 5' in model_lower:
                base_price *= 1.2
            elif 'epyc' in model_lower:
                base_price *= 3.0
        
        return round(base_price, -2)  # 取整到百位
    
    def _has_integrated_graphics(self, model, brand):
        """
        判断是否有集成显卡
        
        Args:
            model: CPU型号
            brand: CPU品牌
            
        Returns:
            是否有集成显卡
        """
        model_lower = model.lower()
        
        if brand == 'Intel':
            # Intel F系列没有集成显卡
            if 'f' in model_lower:
                return False
            # 大多数Intel CPU有集成显卡
            return True
        elif brand == 'AMD':
            # AMD G系列有集成显卡
            if 'g' in model_lower:
                return True
            # 大多数AMD CPU没有集成显卡
            return False
        elif brand == 'Apple':
            # Apple Silicon都有集成显卡
            return True
        
        return False
    
    def _generate_id(self, model, brand):
        """
        生成唯一ID
        
        Args:
            model: CPU型号
            brand: CPU品牌
            
        Returns:
            唯一ID
        """
        import hashlib
        
        # 使用品牌和型号生成MD5哈希作为ID
        hash_input = f"{brand}-{model}".encode('utf-8')
        hash_value = hashlib.md5(hash_input).hexdigest()
        
        # 提取前8位作为ID
        return f"cpu-{hash_value[:8]}"

def get_recent_cpu_data(cpu_data, years=10):
    """
    过滤出近10年的CPU数据
    
    Args:
        cpu_data: CPU数据列表
        years: 年份范围
        
    Returns:
        近10年的CPU数据列表
    """
    print(f"🔍 过滤近{years}年的CPU数据...")
    
    # 计算时间范围
    today = datetime.now()
    cutoff_date = today - timedelta(days=years*365)
    
    print(f"📅 时间范围: {cutoff_date.strftime('%Y-%m-%d')} 到 {today.strftime('%Y-%m-%d')}")
    
    # 过滤出近10年的数据
    recent_cpu_data = []
    
    for cpu in cpu_data:
        try:
            # 解析发布日期
            release_date_str = cpu.get('releaseDate', '')
            release_date = datetime.strptime(release_date_str, '%Y-%m-%d')
            
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
    
    Args:
        cpu_data: CPU数据列表
        
    Returns:
        按品牌分类的CPU数据字典
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
    
    Args:
        model: CPU型号字符串
        
    Returns:
        用于排序的键值
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
    
    Args:
        data: 要保存的数据
        filename: 文件名
    """
    try:
        output_dir = os.path.dirname(filename)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 数据已保存到: {filename}")
    except Exception as e:
        print(f"❌ 保存数据失败: {e}")

def generate_report(raw_data, categorized_data):
    """
    生成统计报告
    
    Args:
        raw_data: 原始数据列表
        categorized_data: 分类数据字典
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
            if isinstance(core_str, str):
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
    print("🚀 开始从网上获取CPU数据...")
    
    # 初始化爬虫
    scraper = CpuWebScraper()
    
    # 获取CPU数据
    cpu_data = scraper.get_cpu_data()
    
    if not cpu_data:
        print("❌ 未获取到CPU数据")
        sys.exit(1)
    
    # 过滤近10年的数据
    recent_cpu_data = get_recent_cpu_data(cpu_data)
    
    if not recent_cpu_data:
        print("❌ 未过滤出近10年的CPU数据")
        sys.exit(1)
    
    # 按品牌分类
    categorized_data = categorize_cpu_data(recent_cpu_data)
    
    # 保存结果
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存原始数据
    raw_output_file = os.path.join(output_dir, 'web_cpu_data_raw.json')
    save_data(recent_cpu_data, raw_output_file)
    
    # 保存分类数据
    categorized_output_file = os.path.join(output_dir, 'web_cpu_data_categorized.json')
    save_data(categorized_data, categorized_output_file)
    
    # 生成统计报告
    generate_report(recent_cpu_data, categorized_data)
    
    print("🎉 任务执行完成！")

if __name__ == "__main__":
    main()
