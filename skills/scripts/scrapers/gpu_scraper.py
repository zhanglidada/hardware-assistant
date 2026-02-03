#!/usr/bin/env python3
"""
GPU数据爬虫模块
从京东等电商网站爬取显卡信息并返回标准格式的数据
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


class GpuScraper(HardwareScraper):
    """GPU数据爬虫"""
    
    def __init__(self):
        """初始化GPU爬虫"""
        super().__init__(
            category="gpu",
            base_url="https://search.jd.com",
            delay_range=(2, 5)
        )
        
        # GPU搜索关键词
        self.search_keywords = [
            "NVIDIA 显卡",
            "AMD 显卡",
            "RTX 显卡",
            "RX 显卡",
            "GeForce RTX",
            "Radeon RX",
            "游戏显卡",
            "独立显卡"
        ]
        
        # 品牌映射
        self.brand_mapping = {
            'nvidia': 'NVIDIA',
            '英伟达': 'NVIDIA',
            'amd': 'AMD',
            'radeon': 'AMD',
            '华硕': '其他',
            '技嘉': '其他',
            '微星': '其他',
            '七彩虹': '其他',
            '影驰': '其他',
            '索泰': '其他'
        }
        
        # 型号解析正则
        self.model_patterns = [
            r'(RTX\s*[\d]+\s*[A-Za-z]*)',  # NVIDIA RTX系列
            r'(GTX\s*[\d]+\s*[A-Za-z]*)',  # NVIDIA GTX系列
            r'(RX\s*[\d]+\s*[A-Za-z]*)',  # AMD RX系列
            r'(Radeon\s*[A-Za-z\d\s]+)',  # AMD Radeon
            r'(GeForce\s*[A-Za-z\d\s]+)',  # NVIDIA GeForce
            r'([A-Za-z]+\s*[\d]+\s*[A-Za-z]*\s*显卡)',  # 通用显卡模式
        ]
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        爬取GPU数据
        
        Returns:
            GPU数据列表
        """
        gpu_data = []
        
        # 尝试从京东爬取
        jd_data = self._scrape_jd()
        if jd_data:
            gpu_data.extend(jd_data)
            print(f"✅ 从京东爬取到 {len(jd_data)} 个GPU数据")
        
        # 如果数据不足，使用备用数据源
        if len(gpu_data) < 8:
            print("⚠️  爬取数据不足，使用备用数据源")
            backup_data = self._get_backup_data()
            gpu_data.extend(backup_data)
        
        # 去重
        unique_data = self._deduplicate(gpu_data)
        
        return unique_data
    
    def _scrape_jd(self) -> List[Dict[str, Any]]:
        """从京东爬取GPU数据"""
        gpu_items = []
        
        for keyword in self.search_keywords[:3]:  # 先试前三个关键词
            try:
                print(f"🔍 正在搜索京东: {keyword}")
                
                # 构建搜索URL
                params = {
                    'keyword': keyword,
                    'enc': 'utf-8',
                    'wq': keyword,
                    'pvid': self._generate_pvid()
                }
                
                # 获取搜索页面
                html = self.fetch_page("/Search", params=params)
                if not html:
                    continue
                    
                soup = self.parse_html(html)
                if not soup:
                    continue
                
                # 提取商品列表
                items = soup.select('.gl-item')
                print(f"  找到 {len(items)} 个商品")
                
                for item in items[:15]:  # 每个关键词最多处理15个商品
                    try:
                        gpu_item = self._parse_jd_item(item)
                        if gpu_item and self.validate_data(gpu_item):
                            gpu_items.append(gpu_item)
                    except Exception as e:
                        print(f"  解析商品失败: {e}")
                        continue
                        
                # 避免请求过快
                time.sleep(3)
                
            except Exception as e:
                print(f"搜索 {keyword} 失败: {e}")
                continue
        
        return gpu_items
    
    def _parse_jd_item(self, item) -> Optional[Dict[str, Any]]:
        """解析京东商品项"""
        try:
            # 提取商品标题
            title_elem = item.select_one('.p-name a em')
            if not title_elem:
                title_elem = item.select_one('.p-name-type-2 a em')
            
            title = self.extract_text(title_elem) if title_elem else ""
            if not title:
                return None
            
            # 提取价格
            price_elem = item.select_one('.p-price strong i')
            price = self.extract_text(price_elem) if price_elem else "0"
            
            # 提取商品链接
            link_elem = item.select_one('.p-name a')
            link = self.extract_attribute(link_elem, 'href') if link_elem else ""
            if link and not link.startswith('http'):
                link = f"https:{link}"
            
            # 从标题中提取GPU信息
            gpu_info = self._extract_gpu_info_from_title(title)
            if not gpu_info:
                return None
            
            # 构建GPU数据
            gpu_data = {
                'id': self.generate_id(gpu_info['model'], gpu_info['brand']),
                'model': gpu_info['model'],
                'brand': gpu_info['brand'],
                'releaseDate': self._estimate_release_date(gpu_info['model'], gpu_info['brand']),
                'price': self._parse_price(price),
                'description': title,
                'vram': gpu_info.get('vram', 0),
                'busWidth': gpu_info.get('busWidth', 0),
                'cudaCores': gpu_info.get('cudaCores', 0),
                'coreClock': gpu_info.get('coreClock', 0),
                'memoryClock': gpu_info.get('memoryClock', 0),
                'powerConsumption': gpu_info.get('powerConsumption', 0),
                'rayTracing': gpu_info.get('rayTracing', False),
                'upscalingTech': gpu_info.get('upscalingTech', ''),
                'source': '京东',
                'url': link
            }
            
            return gpu_data
            
        except Exception as e:
            print(f"解析商品项失败: {e}")
            return None
    
    def _extract_gpu_info_from_title(self, title: str) -> Optional[Dict[str, Any]]:
        """从标题中提取GPU信息"""
        title_lower = title.lower()
        
        # 确定品牌
        brand = '其他'
        for key, value in self.brand_mapping.items():
            if key in title_lower:
                brand = value
                break
        
        # 提取型号
        model = ''
        for pattern in self.model_patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                model = match.group(1).strip()
                break
        
        if not model:
            # 尝试其他模式
            if '显卡' in title or 'gpu' in title_lower:
                # 提取可能包含型号的部分
                words = title.split()
                for word in words:
                    if re.search(r'[\d]+[A-Za-z]*', word) and len(word) > 3:
                        model = word
                        break
        
        if not model:
            return None
        
        # 提取显存
        vram = self._extract_vram(title)
        
        # 提取核心频率
        core_clock = self._extract_core_clock(title)
        
        # 提取显存频率
        memory_clock = self._extract_memory_clock(title)
        
        # 估算位宽
        bus_width = self._estimate_bus_width(model, brand, vram)
        
        # 估算CUDA核心数
        cuda_cores = self._estimate_cuda_cores(model, brand)
        
        # 估算功耗
        power_consumption = self._estimate_power_consumption(model, brand)
        
        # 是否支持光追
        ray_tracing = self._has_ray_tracing(model, brand)
        
        # 超采样技术
        upscaling_tech = self._get_upscaling_tech(model, brand)
        
        return {
            'model': model,
            'brand': brand,
            'vram': vram,
            'busWidth': bus_width,
            'cudaCores': cuda_cores,
            'coreClock': core_clock,
            'memoryClock': memory_clock,
            'powerConsumption': power_consumption,
            'rayTracing': ray_tracing,
            'upscalingTech': upscaling_tech
        }
    
    def _extract_vram(self, title: str) -> int:
        """从标题中提取显存大小(GB)"""
        # 查找 GB 显存
        gb_patterns = [
            r'(\d+)\s*[Gg][Bb]\s*显存',
            r'(\d+)\s*[Gg][Bb]\s*[GgDd][Dd][Rr]',
            r'显存\s*(\d+)\s*[Gg]',
            r'(\d+)[Gg]\s*显存'
        ]
        
        for pattern in gb_patterns:
            match = re.search(pattern, title)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        
        # 根据型号估算
        title_lower = title.lower()
        if 'rtx 4090' in title_lower:
            return 24
        elif 'rtx 4080' in title_lower:
            return 16
        elif 'rtx 4070' in title_lower:
            return 12
        elif 'rtx 4060' in title_lower:
            return 8
        elif 'rx 7900' in title_lower:
            return 20
        elif 'rx 7800' in title_lower:
            return 16
        elif 'rx 7700' in title_lower:
            return 12
        elif 'rx 7600' in title_lower:
            return 8
        
        return 8  # 默认8GB
    
    def _extract_core_clock(self, title: str) -> int:
        """从标题中提取核心频率(MHz)"""
        # 查找 GHz 或 MHz 频率
        clock_patterns = [
            r'(\d+)\s*[Gg][Hh]z\s*核心',
            r'核心频率\s*(\d+)\s*[Mm]?[Hh]z',
            r'(\d+)\s*[Gg][Hh]z',
            r'(\d+)\s*[Mm][Hh]z'
        ]
        
        for pattern in clock_patterns:
            match = re.search(pattern, title)
            if match:
                try:
                    clock = int(match.group(1))
                    if 'ghz' in pattern.lower():
                        return clock * 1000  # GHz转MHz
                    return clock
                except:
                    pass
        
        # 根据型号估算
        title_lower = title.lower()
        if any(x in title_lower for x in ['rtx 40', 'rx 7000']):
            return 2500  # 新一代显卡
        elif any(x in title_lower for x in ['rtx 30', 'rx 6000']):
            return 1800  # 上一代显卡
        elif any(x in title_lower for x in ['rtx 20', 'rx 5000']):
            return 1500  # 上上代显卡
        
        return 1500  # 默认1500MHz
    
    def _extract_memory_clock(self, title: str) -> int:
        """从标题中提取显存频率(MHz)"""
        # 查找显存频率
        memory_patterns = [
            r'显存频率\s*(\d+)\s*[Mm]?[Hh]z',
            r'(\d+)\s*[Gg][Bb]/[Ss]\s*显存',
            r'GDDR\d+\s*(\d+)'
        ]
        
        for pattern in memory_patterns:
            match = re.search(pattern, title)
            if match:
                try:
                    clock = int(match.group(1))
                    if clock < 100:  # 可能是GHz
                        return clock * 1000
                    return clock
                except:
                    pass
        
        # 根据型号估算
        title_lower = title.lower()
        if any(x in title_lower for x in ['rtx 40', 'rx 7000']):
            return 21000  # GDDR6X/GDDR6
        elif any(x in title_lower for x in ['rtx 30', 'rx 6000']):
            return 19000  # GDDR6
        elif any(x in title_lower for x in ['rtx 20', 'rx 5000']):
            return 14000  # GDDR6
        
        return 16000  # 默认16000MHz
    
    def _estimate_bus_width(self, model: str, brand: str, vram: int) -> int:
        """估算位宽"""
        model_lower = model.lower()
        
        if brand == 'NVIDIA':
            if '4090' in model_lower:
                return 384
            elif '4080' in model_lower:
                return 256
            elif '4070' in model_lower:
                return 192
            elif '4060' in model_lower:
                return 128
        elif brand == 'AMD':
            if '7900' in model_lower:
                return 384
            elif '7800' in model_lower:
                return 256
            elif '7700' in model_lower:
                return 192
            elif '7600' in model_lower:
                return 128
        
        # 根据显存估算
        if vram >= 16:
            return 256
        elif vram >= 12:
            return 192
        elif vram >= 8:
            return 128
        else:
            return 64
    
    def _estimate_cuda_cores(self, model: str, brand: str) -> int:
        """估算CUDA核心数"""
        model_lower = model.lower()
        
        if brand == 'NVIDIA':
            if '4090' in model_lower:
                return 16384
            elif '4080' in model_lower:
                return 9728
            elif '4070' in model_lower:
                return 5888
            elif '4060' in model_lower:
                return 3072
            elif '3090' in model_lower:
                return 10496
            elif '3080' in model_lower:
                return 8704
            elif '3070' in model_lower:
                return 5888
            elif '3060' in model_lower:
                return 3584
        elif brand == 'AMD':
            if '7900' in model_lower:
                return 5376
            elif '7800' in model_lower:
                return 3840
            elif '7700' in model_lower:
                return 3456
            elif '7600' in model_lower:
                return 2048
        
        return 2048  # 默认2048
    
    def _estimate_power_consumption(self, model: str, brand: str) -> int:
        """估算功耗(W)"""
        model_lower = model.lower()
        
        if brand == 'NVIDIA':
            if '4090' in model_lower:
                return 450
            elif '4080' in model_lower:
                return 320
            elif '4070' in model_lower:
                return 200
            elif '4060' in model_lower:
                return 115
        elif brand == 'AMD':
            if '7900' in model_lower:
                return 355
            elif '7800' in model_lower:
                return 263
            elif '7700' in model_lower:
                return 245
            elif '7600' in model_lower:
                return 165
        
        return 200  # 默认200W
    
    def _has_ray_tracing(self, model: str, brand: str) -> bool:
        """判断是否支持光追"""
        model_lower = model.lower()
        
        if brand == 'NVIDIA':
            # NVIDIA RTX系列都支持光追
            return 'rtx' in model_lower
        elif brand == 'AMD':
            # AMD RX 6000/7000系列支持光追
            return any(x in model_lower for x in ['rx 6', 'rx 7', 'rx 6000', 'rx 7000'])
        
        return False
    
    def _get_upscaling_tech(self, model: str, brand: str) -> str:
        """获取超采样技术"""
        model_lower = model.lower()
        
        if brand == 'NVIDIA':
            if 'rtx' in model_lower:
                return 'DLSS'
            else:
                return '无'
        elif brand == 'AMD':
            if any(x in model_lower for x in ['rx 6', 'rx 7', 'rx 6000', 'rx 7000']):
                return 'FSR'
            else:
                return '无'
        
        return '无'
    
    def _estimate_release_date(self, model: str, brand: str) -> str:
        """估算发布日期"""
        # 简单估算：根据型号中的数字
        year_match = re.search(r'(\d{4})', model)
        if year_match:
            year = year_match.group(1)
            if len(year) == 4 and 2018 <= int(year) <= 2025:
                return f"{year}-01-01"
        
        # 根据品牌和系列估算
        model_lower = model.lower()
        current_year = datetime.now().year
        
        if brand == 'NVIDIA':
            if '4090' in model_lower:
                return '2022-01-01'
            elif '4080' in model_lower:
                return '2022-01-01'
            elif '4070' in model_lower:
                return '2022-01-01'
            elif '4060' in model_lower:
                return '2023-01-01'
            elif '3090' in model_lower:
                return '2020-01-01'
            elif '3080' in model_lower:
                return '2020-01-01'
            elif '3070' in model_lower:
                return '2020-01-01'
            elif '3060' in model_lower:
                return '2021-01-01'
        elif brand == 'AMD':
            if '7900' in model_lower:
                return '2022-01-01'
            elif '7800' in model_lower:
                return '2023-01-01'
            elif '7700' in model_lower:
                return '2023-01-01'
            elif '7600' in model_lower:
                return '2023-01-01'
            elif '6900' in model_lower:
                return '2020-01-01'
            elif '6800' in model_lower:
                return '2020-01-01'
            elif '6700' in model_lower:
                return '2021-01-01'
            elif '6600' in model_lower:
                return '2021-01-01'
        
        # 默认返回当前年份
        return f"{current_year}-01-01"
    
    def _parse_price(self, price_str: str) -> float:
        """解析价格字符串"""
        try:
            # 移除非数字字符
            clean_price = re.sub(r'[^\d.]', '', price_str)
            if clean_price:
                return float(clean_price)
        except:
            pass
        
        # 默认价格
        return 1999.0
    
    def _generate_pvid(self) -> str:
        """生成京东PVID参数"""
        import uuid
        return str(uuid.uuid4()).replace('-', '')[:32]
    
    def _get_backup_data(self) -> List[Dict[str, Any]]:
        """获取备用数据（当爬取失败时使用）"""
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
            }
        ]
        return backup_gpus
    
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
    运行GPU数据爬取
    
    Returns:
        GPU数据列表
    """
    print("🔍 开始爬取GPU数据...")
    
    scraper = GpuScraper()
    gpu_data = scraper.run()
    
    # 数据统计
    nvidia_count = len([g for g in gpu_data if g['brand'] == 'NVIDIA'])
    amd_count = len([g for g in gpu_data if g['brand'] == 'AMD'])
    other_count = len(gpu_data) - nvidia_count - amd_count
    rt_count = len([g for g in gpu_data if g['rayTracing']])
    
    print(f"✅ GPU数据爬取完成，共{len(gpu_data)}个显卡")
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
    
    return gpu_data


if __name__ == "__main__":
    # 测试运行
    data = run()
    print(f"爬取到{len(data)}个GPU数据")
    if data:
        print("第一个GPU:", json.dumps(data[0], ensure_ascii=False, indent=2))
