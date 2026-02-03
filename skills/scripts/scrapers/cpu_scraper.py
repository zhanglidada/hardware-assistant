#!/usr/bin/env python3
"""
CPU数据爬虫模块
从TechPowerUp网站爬取CPU信息并返回标准格式的数据
"""

import json
import re
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
try:
    from web_scraper import HardwareScraper
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from web_scraper import HardwareScraper


class CpuScraper(HardwareScraper):
    """CPU数据爬虫 - TechPowerUp版本"""
    
    def __init__(self):
        """初始化CPU爬虫"""
        super().__init__(
            category="cpu",
            base_url="https://www.techpowerup.com",
            delay_range=(1, 2)  # TechPowerUp反爬较松
        )
        
        # TechPowerUp CPU数据库页面
        self.cpu_db_url = "/cpu-specs/"
        
        # 品牌识别
        self.brand_keywords = {
            'Intel': ['Intel', 'Core', 'Xeon', 'Pentium', 'Celeron', 'Atom'],
            'AMD': ['AMD', 'Ryzen', 'Athlon', 'Threadripper', 'EPYC', 'FX'],
            'Apple': ['Apple', 'M1', 'M2', 'M3', 'M4'],
            'Qualcomm': ['Qualcomm', 'Snapdragon'],
            'MediaTek': ['MediaTek', 'Dimensity']
        }
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        从TechPowerUp爬取CPU数据
        
        Returns:
            CPU数据列表
        """
        print("🔍 开始从TechPowerUp爬取CPU数据...")
        
        cpu_data = []
        
        # 从TechPowerUp爬取
        tp_data = self._scrape_techpowerup()
        if tp_data:
            cpu_data.extend(tp_data)
            print(f"✅ 从TechPowerUp爬取到 {len(tp_data)} 个CPU数据")
        
        # 如果数据不足，使用备用数据源
        if len(cpu_data) < 20:
            print("⚠️  爬取数据不足，使用备用数据源")
            backup_data = self._get_backup_data()
            cpu_data.extend(backup_data)
        
        # 去重
        unique_data = self._deduplicate(cpu_data)
        
        return unique_data
    
    def _scrape_techpowerup(self) -> List[Dict[str, Any]]:
        """从TechPowerUp爬取CPU数据"""
        cpu_items = []
        
        try:
            print(f"📄 获取TechPowerUp CPU数据库页面: {self.cpu_db_url}")
            
            # 获取CPU数据库页面
            html = self.fetch_page(self.cpu_db_url)
            if not html:
                print("❌ 无法获取TechPowerUp页面")
                return []
                
            soup = self.parse_html(html)
            if not soup:
                print("❌ 无法解析TechPowerUp页面")
                return []
            
            # 查找CPU数据表格
            table = soup.find('table', class_='items-desktop-table')
            if not table:
                print("❌ 未找到CPU数据表格")
                return []
            
            # 提取表头
            headers = []
            thead = table.find('thead')
            if thead:
                header_cells = thead.find_all('th')
                headers = [cell.get_text(strip=True) for cell in header_cells]
                print(f"📊 表格列: {headers}")
            
            # 提取数据行
            rows = table.find_all('tr')[1:]  # 跳过表头
            print(f"📈 找到 {len(rows)} 行CPU数据")
            
            # 解析每一行
            for i, row in enumerate(rows[:100]):  # 只取前100个
                try:
                    cpu_item = self._parse_techpowerup_row(row)
                    if cpu_item and self.validate_data(cpu_item):
                        cpu_items.append(cpu_item)
                        
                    # 显示进度
                    if (i + 1) % 20 == 0:
                        print(f"  已处理 {i + 1} 个CPU...")
                        
                except Exception as e:
                    print(f"  解析第{i+1}行失败: {e}")
                    continue
                    
                # 避免请求过快
                if (i + 1) % 10 == 0:
                    time.sleep(0.5)
            
            print(f"✅ 成功解析 {len(cpu_items)} 个CPU数据")
            
        except Exception as e:
            print(f"❌ 爬取TechPowerUp数据失败: {e}")
            import traceback
            traceback.print_exc()
        
        return cpu_items
    
    def _parse_techpowerup_row(self, row) -> Optional[Dict[str, Any]]:
        """解析TechPowerUp表格行"""
        try:
            cells = row.find_all('td')
            if len(cells) < 8:
                return None
            
            # 提取各列数据
            name_cell = cells[0]
            model = self.extract_text(name_cell).strip()
            if not model:
                return None
            
            # 从名称中提取品牌
            brand = self._extract_brand_from_model(model)
            
            # 提取代号
            codename = self.extract_text(cells[1]).strip()
            
            # 提取核心/线程数
            cores_text = self.extract_text(cells[2]).strip()
            cores_info = self._parse_cores_text(cores_text)
            
            # 提取时钟频率
            clock_text = self.extract_text(cells[3]).strip()
            clock_info = self._parse_clock_text(clock_text)
            
            # 提取插槽
            socket = self.extract_text(cells[4]).strip()
            
            # 提取制程工艺
            process = self.extract_text(cells[5]).strip()
            
            # 提取缓存
            cache_text = self.extract_text(cells[6]).strip()
            cache = self._parse_cache_text(cache_text)
            
            # 提取TDP
            tdp_text = self.extract_text(cells[7]).strip()
            tdp = self._parse_tdp_text(tdp_text)
            
            # 构建CPU数据 - 保持与现有格式兼容
            cpu_data = {
                'id': self.generate_id(model, brand),
                'model': model,
                'brand': brand,
                'releaseDate': self._estimate_release_date(model, brand),
                'price': self._estimate_price(model, brand, cores_info['cores']),
                'description': f"{brand} {model} - {codename} - {cores_info['cores']}核心{cores_info['threads']}线程",
                'cores': str(cores_info['cores']),
                'baseClock': clock_info['base'],
                'boostClock': clock_info['boost'],
                'socket': socket,
                'tdp': tdp,
                'integratedGraphics': self._has_integrated_graphics(model, brand),
                'cache': cache,
                'source': 'TechPowerUp',
                # 额外字段，保持向后兼容
                'threads': str(cores_info['threads']),
                'process': process,
                'codename': codename
            }
            
            return cpu_data
            
        except Exception as e:
            print(f"解析表格行失败: {e}")
            return None
    
    def _extract_brand_from_model(self, model: str) -> str:
        """从型号中提取品牌"""
        model_upper = model.upper()
        
        for brand, keywords in self.brand_keywords.items():
            for keyword in keywords:
                if keyword.upper() in model_upper:
                    return brand
        
        # 默认根据常见模式判断
        if 'RYZEN' in model_upper or 'ATHLON' in model_upper or 'THREADRIPPER' in model_upper:
            return 'AMD'
        elif 'CORE' in model_upper or 'XEON' in model_upper or 'PENTIUM' in model_upper or 'CELERON' in model_upper:
            return 'Intel'
        elif 'APPLE' in model_upper or model_upper.startswith('M'):
            return 'Apple'
        
        return '其他'
    
    def _parse_cores_text(self, cores_text: str) -> Dict[str, int]:
        """解析核心/线程文本"""
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
    
    def _parse_clock_text(self, clock_text: str) -> Dict[str, float]:
        """解析时钟频率文本"""
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
    
    def _parse_cache_text(self, cache_text: str) -> float:
        """解析缓存文本"""
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
    
    def _parse_tdp_text(self, tdp_text: str) -> int:
        """解析TDP文本"""
        try:
            # 提取数字
            numbers = re.findall(r'\d+', tdp_text)
            if numbers:
                return int(numbers[0])
        except:
            pass
        
        # 默认值
        return 65
    
    def _estimate_price(self, model: str, brand: str, cores: int) -> float:
        """估算价格"""
        # 根据品牌、型号和核心数估算价格
        model_lower = model.lower()
        
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
    
    def _has_integrated_graphics(self, model: str, brand: str) -> bool:
        """判断是否有集成显卡"""
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
    
    def _estimate_release_date(self, model: str, brand: str) -> str:
        """估算发布日期"""
        current_year = datetime.now().year
        
        # 尝试从型号中提取年份
        year_match = re.search(r'(\d{4})', model)
        if year_match:
            year = int(year_match.group(1))
            if 2010 <= year <= current_year:
                return f"{year}-01-01"
        
        # 根据型号特征估算
        model_lower = model.lower()
        
        if brand == 'Intel':
            if any(x in model_lower for x in ['14900', '13900', '12900']):
                return '2023-01-01'
            elif any(x in model_lower for x in ['11900', '10900']):
                return '2020-01-01'
            elif any(x in model_lower for x in ['9900', '9700']):
                return '2018-01-01'
        elif brand == 'AMD':
            if any(x in model_lower for x in ['9950', '7950', '7900']):
                return '2023-01-01'
            elif any(x in model_lower for x in ['5950', '5900', '5800']):
                return '2020-01-01'
            elif any(x in model_lower for x in ['3950', '3900', '3800']):
                return '2019-01-01'
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
    
    def _get_backup_data(self) -> List[Dict[str, Any]]:
        """获取备用数据（当爬取失败时使用）"""
        backup_cpus = [
            {
                "id": "cpu-backup-001",
                "model": "Intel Core i5-12400F",
                "brand": "Intel",
                "releaseDate": "2022-01-01",
                "price": 1199,
                "description": "Intel第12代酷睿i5处理器，6核心12线程，无集成显卡",
                "cores": "6",
                "threads": "12",
                "baseClock": 2.5,
                "boostClock": 4.4,
                "socket": "LGA1700",
                "process": "10 nm",
                "tdp": 65,
                "cache": 18,
                "integratedGraphics": False,
                "codename": "Alder Lake",
                "source": "备用数据"
            },
            {
                "id": "cpu-backup-002",
                "model": "AMD Ryzen 5 5600X",
                "brand": "AMD",
                "releaseDate": "2020-11-01",
                "price": 1499,
                "description": "AMD Ryzen 5 5600X处理器，6核心12线程，Zen 3架构",
                "cores": "6",
                "threads": "12",
                "baseClock": 3.7,
                "boostClock": 4.6,
                "socket": "AM4",
                "process": "7 nm",
                "tdp": 65,
                "cache": 32,
                "integratedGraphics": False,
                "codename": "Vermeer",
                "source": "备用数据"
            },
            {
                "id": "cpu-backup-003",
                "model": "Intel Core i7-12700K",
                "brand": "Intel",
                "releaseDate": "2021-11-01",
                "price": 2599,
                "description": "Intel第12代酷睿i7处理器，12核心20线程",
                "cores": "8P+4E",
                "threads": "20",
                "baseClock": 3.6,
                "boostClock": 5.0,
                "socket": "LGA1700",
                "process": "10 nm",
                "tdp": 125,
                "cache": 25,
                "integratedGraphics": True,
                "codename": "Alder Lake",
                "source": "备用数据"
            },
            {
                "id": "cpu-backup-004",
                "model": "AMD Ryzen 7 5800X",
                "brand": "AMD",
                "releaseDate": "2020-11-01",
                "price": 2299,
                "description": "AMD Ryzen 7 5800X处理器，8核心16线程",
                "cores": "8",
                "threads": "16",
                "baseClock": 3.8,
                "boostClock": 4.7,
                "socket": "AM4",
                "process": "7 nm",
                "tdp": 105,
                "cache": 32,
                "integratedGraphics": False,
                "codename": "Vermeer",
                "source": "备用数据"
            }
        ]
        return backup_cpus
    
    def _deduplicate(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重数据（基于ID）"""
        seen_ids = set()
        unique_data = []
        
        for item in data:
            item_id = item.get('id')
            if item_id and item_id not in seen_ids:
                seen_ids.add(item_id)
                unique_data.append(item)
        
        return unique_data
    
    def normalize_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """标准化数据格式"""
        # 这里可以添加数据清洗和标准化逻辑
        # 目前直接返回原始数据
        return raw_data


def run() -> List[Dict[str, Any]]:
    """
    运行CPU数据爬取
    
    Returns:
        CPU数据列表，每个CPU是一个字典
    """
    print("🔍 开始爬取CPU数据...")
    
    scraper = CpuScraper()
    cpu_data = scraper.run()
    
    # 数据统计
    intel_count = len([c for c in cpu_data if c['brand'] == 'Intel'])
    amd_count = len([c for c in cpu_data if c['brand'] == 'AMD'])
    other_count = len(cpu_data) - intel_count - amd_count
    
    print(f"✅ CPU数据爬取完成，共{len(cpu_data)}个CPU")
    print(f"   Intel: {intel_count} 个 ({intel_count/len(cpu_data)*100:.1f}%)")
    print(f"   AMD: {amd_count} 个 ({amd_count/len(cpu_data)*100:.1f}%)")
    if other_count > 0:
        print(f"   其他: {other_count} 个 ({other_count/len(cpu_data)*100:.1f}%)")
    
    # 价格统计
    if cpu_data:
        prices = [c['price'] for c in cpu_data]
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        print(f"   平均价格: ¥{avg_price:.0f}")
        print(f"   价格区间: ¥{min_price}-¥{max_price}")
        
        # 显示数据来源
        sources = {}
        for c in cpu_data:
            source = c.get('source', '未知')
            sources[source] = sources.get(source, 0) + 1
        
        print(f"   数据来源:")
        for source, count in sources.items():
            print(f"     - {source}: {count} 个")
    
    return cpu_data


if __name__ == "__main__":
    # 测试运行
    data = run()
    print(f"爬取到{len(data)}个CPU数据")
    if data:
        print("第一个CPU:", json.dumps(data[0], ensure_ascii=False, indent=2))
