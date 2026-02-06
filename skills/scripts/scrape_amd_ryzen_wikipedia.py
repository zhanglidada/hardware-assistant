#!/usr/bin/env python3
"""
从维基百科页面获取AMD Ryzen处理器信息并分类存储为JSON文件
数据源：https://en.wikipedia.org/wiki/List_of_AMD_Ryzen_processors
"""

import json
import os
import sys
import ssl
import re
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser

# 创建一个不验证SSL证书的上下文
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

class WikipediaTableParser(HTMLParser):
    """维基百科表格解析器"""
    
    def __init__(self):
        super().__init__()
        self.in_h2 = False
        self.in_h3 = False
        self.in_table = False
        self.in_tr = False
        self.in_th = False
        self.in_td = False
        self.current_section = ""
        self.current_subsection = ""
        self.current_header = ""
        self.current_cell = ""
        self.headers = []
        self.rows = []
        self.current_row = []
        self.sections = []
        self.tables = []
        self.table_count = 0
        self.row_count = 0
    
    def handle_starttag(self, tag, attrs):
        if tag == 'h2':
            self.in_h2 = True
            self.in_h3 = False
            # 重置当前部分，避免标题合并
            self.current_section = ""
            self.current_subsection = ""
        elif tag == 'h3':
            self.in_h3 = True
            # 重置当前子部分
            self.current_subsection = ""
        elif tag == 'table':
            # 简化表格检测，不依赖class属性
            self.in_table = True
            self.headers = []
            self.rows = []
            self.row_count = 0
            self.table_count += 1
            print(f"📋 检测到表格 #{self.table_count}")
        elif self.in_table and tag == 'tr':
            self.in_tr = True
            self.current_row = []
            self.row_count += 1
        elif self.in_table and self.in_tr and tag == 'th':
            self.in_th = True
            self.current_header = ""
        elif self.in_table and self.in_tr and tag == 'td':
            self.in_td = True
            self.current_cell = ""
    
    def handle_endtag(self, tag):
        if tag == 'h2':
            self.in_h2 = False
            self.current_section = self.current_section.strip()
            # 过滤掉不需要的部分
            if self.current_section and not self.current_section.startswith('Contents') and not self.current_section in ['See also', 'References']:
                self.sections.append(self.current_section)
                print(f"✅ 找到部分: {self.current_section}")
        elif tag == 'h3':
            self.in_h3 = False
            self.current_subsection = self.current_subsection.strip()
            if self.current_subsection:
                print(f"✅ 找到子部分: {self.current_subsection}")
        elif tag == 'table':
            self.in_table = False
            if self.headers and self.rows:
                # 只添加有数据的表格
                # 构建完整的部分路径
                full_section = self.current_section
                if self.current_subsection:
                    full_section += f" - {self.current_subsection}"
                
                table_info = {
                    'section': full_section,
                    'headers': self.headers,
                    'rows': self.rows
                }
                self.tables.append(table_info)
                print(f"✅ 保存表格: {full_section} - {len(self.rows)} 行数据")
            else:
                print(f"⚠️  表格为空或无表头，跳过")
        elif tag == 'tr':
            self.in_tr = False
            if self.current_row:
                # 保留所有单元格，包括空单元格，以保持与表头长度一致
                cleaned_row = [cell.strip() for cell in self.current_row]
                if cleaned_row:
                    # 如果是第一行，且没有表头，则将其作为表头
                    if not self.headers and self.row_count == 1:
                        self.headers = cleaned_row
                        print(f"  📊 表头: {self.headers}")
                    else:
                        # 否则作为数据行
                        self.rows.append(cleaned_row)
                        if self.row_count <= 3:  # 只打印前3行作为示例
                            print(f"  📈 行 {self.row_count}: {cleaned_row[:3]}...")  # 只显示前3列
        elif tag == 'th':
            self.in_th = False
            if self.current_header:
                self.current_row.append(self.current_header.strip())
        elif tag == 'td':
            self.in_td = False
            if self.current_cell:
                self.current_row.append(self.current_cell.strip())
    
    def handle_data(self, data):
        if self.in_h2:
            self.current_section += data
        elif self.in_h3:
            self.current_subsection += data
        elif self.in_th:
            self.current_header += data
        elif self.in_td:
            self.current_cell += data
    
    def handle_entityref(self, name):
        """处理HTML实体引用"""
        entity_map = {
            'amp': '&',
            'lt': '<',
            'gt': '>',
            'quot': '"',
            'apos': "'"
        }
        if self.in_h2:
            self.current_section += entity_map.get(name, f'&{name};')
        elif self.in_th:
            self.current_header += entity_map.get(name, f'&{name};')
        elif self.in_td:
            self.current_cell += entity_map.get(name, f'&{name};')
    
    def handle_charref(self, name):
        """处理HTML字符引用"""
        try:
            if name.startswith('x'):
                char = chr(int(name[1:], 16))
            else:
                char = chr(int(name))
            if self.in_h2:
                self.current_section += char
            elif self.in_th:
                self.current_header += char
            elif self.in_td:
                self.current_cell += char
        except ValueError:
            pass

class AmdRyzenScraper:
    """AMD Ryzen处理器维基百科页面爬虫"""
    
    def __init__(self):
        """初始化爬虫"""
        self.url = "https://en.wikipedia.org/wiki/List_of_AMD_Ryzen_processors"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        self.cpu_data = []
    
    def fetch_page(self):
        """
        获取维基百科页面内容
        
        Returns:
            页面内容
        """
        print(f"📄 获取页面: {self.url}")
        
        try:
            request = Request(self.url, headers=self.headers)
            with urlopen(request, timeout=30, context=ssl_context) as response:
                content = response.read()
                
                # 检查是否是gzip压缩内容
                content_encoding = response.info().get('Content-Encoding', '')
                if 'gzip' in content_encoding:
                    # 解压缩gzip内容
                    import gzip
                    from io import BytesIO
                    buffer = BytesIO(content)
                    with gzip.GzipFile(fileobj=buffer, mode='rb') as f:
                        content = f.read()
                
                # 解码内容
                encoding = response.info().get_content_charset('utf-8')
                return content.decode(encoding)
                
        except HTTPError as e:
            print(f"❌ HTTP错误: {e.code} - {e.reason}")
            return None
        except URLError as e:
            print(f"❌ URL错误: {e.reason}")
            return None
        except Exception as e:
            print(f"❌ 处理页面时出错: {e}")
            return None
    
    def parse_page(self, html_content):
        """
        解析页面内容，提取CPU信息
        
        Args:
            html_content: 页面HTML内容
        """
        print("🔍 开始解析页面内容...")
        
        try:
            parser = WikipediaTableParser()
            parser.feed(html_content)
            
            # 调试信息：打印找到的部分
            print(f"📋 找到的部分: {parser.sections}")
            print(f"📊 找到的表格数量: {len(parser.tables)}")
            
            # 处理解析结果
            for i, table in enumerate(parser.tables):
                section_title = table['section']
                headers = table['headers']
                rows = table['rows']
                
                print(f"\n📋 表格 {i+1}:")
                print(f"  部分: {section_title}")
                print(f"  表头: {headers}")
                print(f"  行数: {len(rows)}")
                
                if not headers or not rows:
                    print(f"  ⚠️  表格为空，跳过")
                    continue
                
                print(f"  ✅ 处理表格")
                
                # 解析每一行
                for j, row in enumerate(rows):
                    try:
                        cpu_item = self._parse_cpu_row(row, headers, section_title)
                        if cpu_item:
                            self.cpu_data.append(cpu_item)
                            print(f"    ✅ 解析成功: {cpu_item.get('model', 'Unknown')}")
                        else:
                            print(f"    ⚠️  解析失败: 无法提取CPU信息")
                    except Exception as e:
                        print(f"    ❌ 解析第{j+1}行失败: {e}")
                        # 打印失败的行数据
                        print(f"    行数据: {row}")
                        continue
            
            # 最终调试信息
            print(f"\n📊 解析完成:")
            print(f"  找到的CPU数据数量: {len(self.cpu_data)}")
            
        except Exception as e:
            print(f"❌ 解析页面失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _parse_cpu_row(self, row, headers, section_title):
        """
        解析CPU表格行
        
        Args:
            row: 表格行数据列表
            headers: 表头列表
            section_title: 所属部分标题
            
        Returns:
            CPU数据字典
        """
        # 过滤掉表头行和空行
        if not row:
            return None
        
        # 过滤掉明显是表头的行
        first_cell = row[0].strip()
        if first_cell in ['Model', 'Cores(threads)', 'Base', 'Boost', 'Processorbranding', 'Series', 'Desktop processors', 'Mobile processors']:
            return None
        
        # 过滤掉包含表头关键字的行
        header_keywords = ['clock', 'rate', 'ghz', 'cache', 'tdp', 'release', 'date', 'price', 'socket', 'memory', 'pcie', 'gpu', 'graphics']
        if any(keyword in first_cell.lower() for keyword in header_keywords):
            return None
        
        # 创建CPU数据字典
        cpu_data = {
            'id': self._generate_id(row, section_title),
            'series': section_title,
            'source': 'Wikipedia'
        }
        
        # 解析每个单元格，确保只处理行和表头都有的部分
        min_length = min(len(row), len(headers))
        for i in range(min_length):
            header = headers[i]
            cell_value = row[i]
            value = cell_value.strip()
            
            # 跳过空值
            if not value:
                continue
            
            # 根据表头处理不同字段
            normalized_header = header.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_').replace('-', '_').replace('\n', '_').replace('\t', '_')
            
            # 特殊字段处理
            if 'branding_and_model' in normalized_header or 'model' in normalized_header:
                # 过滤掉非型号值
                if not any(keyword in value.lower() for keyword in ['ryzen', 'threadripper']):
                    continue
                cpu_data['model'] = value
            elif 'cores' in normalized_header and 'threads' in normalized_header:
                # 处理核心数和线程数
                core_thread_match = value.strip('()')
                if '(' in core_thread_match:
                    parts = core_thread_match.split('(')
                    cores = parts[0].strip()
                    threads = parts[1].strip(')')
                    # 确保是数字
                    if cores.isdigit() or cores.replace('.', '').isdigit():
                        cpu_data['cores'] = cores
                    if threads.isdigit() or threads.replace('.', '').isdigit():
                        cpu_data['threads'] = threads
            elif 'clock_rate' in normalized_header or 'clock' in normalized_header:
                # 处理时钟频率
                clock_values = value.split('\n')
                if clock_values:
                    base_clock = clock_values[0].strip()
                    # 确保包含频率单位
                    if any(unit in base_clock for unit in ['ghz', 'mhz', 'g hz']):
                        cpu_data['base_clock'] = base_clock
                    if len(clock_values) > 1:
                        boost_clock = clock_values[1].strip()
                        if any(unit in boost_clock for unit in ['ghz', 'mhz', 'g hz']):
                            cpu_data['boost_clock'] = boost_clock
            elif 'l3_cache' in normalized_header or 'cache' in normalized_header:
                # 确保包含缓存单位
                if any(unit in value for unit in ['mb', 'kb', 'gb']):
                    cpu_data['cache'] = value
            elif 'tdp' in normalized_header:
                # 确保包含TDP单位
                if any(unit in value for unit in ['w', 'watts']):
                    cpu_data['tdp'] = value
            elif 'released' in normalized_header or 'release' in normalized_header:
                # 尝试识别日期格式
                if any(char in value for char in ['20', '19', '-', '/', '.']):
                    cpu_data['release_date'] = value
            elif 'price' in normalized_header:
                # 确保包含价格单位或格式
                if any(unit in value for unit in ['$', 'usd', 'eur', 'cny', 'jpy']):
                    cpu_data['price'] = value
            elif 'socket' in normalized_header:
                cpu_data['socket'] = value
            elif 'memory' in normalized_header:
                cpu_data['memory'] = value
            elif 'pcie' in normalized_header:
                cpu_data['pcie'] = value
            elif 'gpu' in normalized_header or 'graphics' in normalized_header:
                cpu_data['gpu'] = value
            else:
                # 其他字段直接添加
                cpu_data[normalized_header] = value
        
        # 确保至少有model字段
        if not cpu_data.get('model') and row:
            # 尝试从第一列获取型号
            first_cell = row[0].strip()
            # 过滤掉非型号值
            if any(keyword in first_cell.lower() for keyword in ['ryzen', 'threadripper']):
                cpu_data['model'] = first_cell
        
        # 过滤掉没有有效字段的行
        if len(cpu_data) <= 3:  # 只包含id, series, source
            return None
        
        return cpu_data if cpu_data.get('model') else None
    
    def _generate_id(self, row, section_title):
        """
        生成唯一ID
        
        Args:
            row: 表格行数据列表
            section_title: 所属部分标题
            
        Returns:
            唯一ID
        """
        import hashlib
        
        # 尝试从行中提取型号信息
        model = ''
        if row:
            # 通常第一列是型号
            model = row[0].strip()
        
        # 使用部分标题和型号生成MD5哈希作为ID
        hash_input = f"AMD-{section_title}-{model}".encode('utf-8')
        hash_value = hashlib.md5(hash_input).hexdigest()
        return f"amd-{hash_value[:8]}"
    
    def categorize_cpu_data(self):
        """
        对CPU数据进行分类
        """
        print("🔍 开始对CPU数据进行分类...")
        
        categorized_data = {}
        
        for cpu in self.cpu_data:
            series = cpu.get('series', 'Unknown')
            if series not in categorized_data:
                categorized_data[series] = []
            categorized_data[series].append(cpu)
        
        # 统计每个系列的数量
        print("📈 CPU系列分类:")
        for series, cpus in categorized_data.items():
            print(f"  {series}: {len(cpus)} 个")
        
        return categorized_data
    
    def save_to_json(self, output_file):
        """
        将数据保存到JSON文件
        
        Args:
            output_file: 输出文件路径
        """
        print(f"💾 开始保存数据到 {output_file}...")
        
        try:
            # 创建输出目录
            output_dir = os.path.dirname(output_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # 对CPU数据进行分类
            categorized_data = self.categorize_cpu_data()
            
            # 构建最终数据结构
            final_data = {
                'total_cpus': len(self.cpu_data),
                'categories': categorized_data,
                'all_cpus': self.cpu_data,
                'source': 'https://en.wikipedia.org/wiki/List_of_AMD_Ryzen_processors',
                'scraped_at': self._get_current_time()
            }
            
            # 保存数据
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, ensure_ascii=False, indent=2)
            
            print(f"  ✅ 成功保存 {len(self.cpu_data)} 条CPU数据到 {output_file}")
            
        except Exception as e:
            print(f"  ❌ 保存数据失败: {e}")
    
    def _get_current_time(self):
        """
        获取当前时间
        
        Returns:
            当前时间字符串
        """
        from datetime import datetime
        return datetime.now().isoformat()
    
    def run(self):
        """
        运行整个数据获取和处理流程
        """
        print("🚀 开始从维基百科获取AMD Ryzen处理器数据...")
        
        # 获取页面内容
        html_content = self.fetch_page()
        if not html_content:
            print("❌ 未能获取页面内容，任务失败")
            return
        
        # 解析页面
        self.parse_page(html_content)
        
        if not self.cpu_data:
            print("❌ 未能提取CPU数据，任务失败")
            return
        
        # 保存数据
        output_file = os.path.join(os.path.dirname(__file__), 'output', 'amd_ryzen_processors.json')
        self.save_to_json(output_file)
        
        print("🎉 任务执行完成！")

if __name__ == "__main__":
    scraper = AmdRyzenScraper()
    scraper.run()
