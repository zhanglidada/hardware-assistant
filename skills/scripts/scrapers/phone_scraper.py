#!/usr/bin/env python3
"""
手机数据爬虫模块
从京东等电商网站爬取手机信息并返回标准格式的数据
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


class PhoneScraper(HardwareScraper):
    """手机数据爬虫"""
    
    def __init__(self):
        """初始化手机爬虫"""
        super().__init__(
            category="phone",
            base_url="https://search.jd.com",
            delay_range=(2, 5)
        )
        
        # 手机搜索关键词
        self.search_keywords = [
            "智能手机",
            "5G手机",
            "iPhone",
            "小米手机",
            "华为手机",
            "三星手机",
            "OPPO手机",
            "vivo手机",
            "荣耀手机"
        ]
        
        # 品牌映射
        self.brand_mapping = {
            'apple': 'Apple',
            'iphone': 'Apple',
            '苹果': 'Apple',
            'xiaomi': 'Xiaomi',
            '小米': 'Xiaomi',
            'redmi': 'Xiaomi',
            '红米': 'Xiaomi',
            'huawei': 'Huawei',
            '华为': 'Huawei',
            'samsung': 'Samsung',
            '三星': 'Samsung',
            'oppo': '其他',
            'vivo': '其他',
            'realme': '其他',
            '真我': '其他',
            'oneplus': '其他',
            '一加': '其他',
            'honor': '其他',
            '荣耀': '其他'
        }
        
        # 型号解析正则
        self.model_patterns = [
            r'(iPhone\s*[\d]+\s*[A-Za-z]*)',  # iPhone系列
            r'(小米\s*[\d]+\s*[A-Za-z]*)',  # 小米系列
            r'(Redmi\s*[\d]+\s*[A-Za-z]*)',  # Redmi系列
            r'(华为\s*[A-Za-z\d\s]+)',  # 华为系列
            r'(Mate\s*[\d]+\s*[A-Za-z]*)',  # 华为Mate
            r'(P\d+\s*[A-Za-z]*)',  # 华为P系列
            r'(三星\s*[A-Za-z\d\s]+)',  # 三星系列
            r'(Galaxy\s*[A-Za-z\d\s]+)',  # 三星Galaxy
            r'([A-Za-z]+\s*[\d]+\s*[A-Za-z]*\s*手机)',  # 通用手机模式
        ]
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        爬取手机数据
        
        Returns:
            手机数据列表
        """
        phone_data = []
        
        # 尝试从京东爬取
        jd_data = self._scrape_jd()
        if jd_data:
            phone_data.extend(jd_data)
            print(f"✅ 从京东爬取到 {len(jd_data)} 个手机数据")
        
        # 如果数据不足，使用备用数据源
        if len(phone_data) < 8:
            print("⚠️  爬取数据不足，使用备用数据源")
            backup_data = self._get_backup_data()
            phone_data.extend(backup_data)
        
        # 去重
        unique_data = self._deduplicate(phone_data)
        
        return unique_data
    
    def _scrape_jd(self) -> List[Dict[str, Any]]:
        """从京东爬取手机数据"""
        phone_items = []
        
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
                        phone_item = self._parse_jd_item(item)
                        if phone_item and self.validate_data(phone_item):
                            phone_items.append(phone_item)
                    except Exception as e:
                        print(f"  解析商品失败: {e}")
                        continue
                        
                # 避免请求过快
                time.sleep(3)
                
            except Exception as e:
                print(f"搜索 {keyword} 失败: {e}")
                continue
        
        return phone_items
    
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
            
            # 从标题中提取手机信息
            phone_info = self._extract_phone_info_from_title(title)
            if not phone_info:
                return None
            
            # 构建手机数据
            phone_data = {
                'id': self.generate_id(phone_info['model'], phone_info['brand']),
                'model': phone_info['model'],
                'brand': phone_info['brand'],
                'releaseDate': self._estimate_release_date(phone_info['model'], phone_info['brand']),
                'price': self._parse_price(price),
                'description': title,
                'processor': phone_info.get('processor', ''),
                'ram': phone_info.get('ram', 0),
                'storage': phone_info.get('storage', 0),
                'screenSize': phone_info.get('screenSize', 0),
                'resolution': phone_info.get('resolution', ''),
                'refreshRate': phone_info.get('refreshRate', 0),
                'batteryCapacity': phone_info.get('batteryCapacity', 0),
                'camera': phone_info.get('camera', ''),
                'os': phone_info.get('os', ''),
                'support5G': phone_info.get('support5G', True),
                'source': '京东',
                'url': link
            }
            
            return phone_data
            
        except Exception as e:
            print(f"解析商品项失败: {e}")
            return None
    
    def _extract_phone_info_from_title(self, title: str) -> Optional[Dict[str, Any]]:
        """从标题中提取手机信息"""
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
            if '手机' in title or 'phone' in title_lower:
                # 提取可能包含型号的部分
                words = title.split()
                for word in words:
                    if re.search(r'[\d]+[A-Za-z]*', word) and len(word) > 3:
                        model = word
                        break
        
        if not model:
            return None
        
        # 提取处理器
        processor = self._extract_processor(title)
        
        # 提取内存
        ram = self._extract_ram(title)
        
        # 提取存储
        storage = self._extract_storage(title)
        
        # 提取屏幕尺寸
        screen_size = self._extract_screen_size(title)
        
        # 提取分辨率
        resolution = self._extract_resolution(title)
        
        # 提取刷新率
        refresh_rate = self._extract_refresh_rate(title)
        
        # 提取电池容量
        battery_capacity = self._extract_battery_capacity(title)
        
        # 提取摄像头信息
        camera = self._extract_camera(title)
        
        # 确定操作系统
        os = self._determine_os(brand)
        
        # 是否支持5G
        support_5g = self._has_5g_support(title)
        
        return {
            'model': model,
            'brand': brand,
            'processor': processor,
            'ram': ram,
            'storage': storage,
            'screenSize': screen_size,
            'resolution': resolution,
            'refreshRate': refresh_rate,
            'batteryCapacity': battery_capacity,
            'camera': camera,
            'os': os,
            'support5G': support_5g
        }
    
    def _extract_processor(self, title: str) -> str:
        """从标题中提取处理器信息"""
        # 常见处理器关键词
        processor_keywords = [
            '骁龙', 'Snapdragon', '天玑', 'Dimensity', '麒麟', 'Kirin',
            'A系列', 'A\d+', 'Tensor', 'Exynos', '联发科', 'MediaTek'
        ]
        
        for keyword in processor_keywords:
            pattern = rf'({keyword}\s*[\dA-Za-z\+]*)'
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # 根据品牌估算
        title_lower = title.lower()
        if 'iphone' in title_lower:
            return 'A系列芯片'
        elif any(x in title_lower for x in ['小米', '红米', 'redmi']):
            return '骁龙处理器'
        elif '华为' in title_lower or 'huawei' in title_lower:
            return '麒麟处理器'
        elif '三星' in title_lower or 'samsung' in title_lower:
            return 'Exynos处理器'
        
        return '骁龙处理器'  # 默认
    
    def _extract_ram(self, title: str) -> int:
        """从标题中提取内存大小(GB)"""
        # 查找 GB 内存
        ram_patterns = [
            r'(\d+)\s*[Gg][Bb]\s*内存',
            r'(\d+)\s*[Gg][Bb]\s*[Rr][Aa][Mm]',
            r'内存\s*(\d+)\s*[Gg]',
            r'(\d+)[Gg]\s*运存'
        ]
        
        for pattern in ram_patterns:
            match = re.search(pattern, title)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        
        # 根据型号估算
        title_lower = title.lower()
        if any(x in title_lower for x in ['pro', 'ultra', 'max', 'plus']):
            return 12  # 高端机型
        elif any(x in title_lower for x in ['iphone 15', 'mate 60', 's24']):
            return 8   # 旗舰机型
        else:
            return 6   # 中端机型
    
    def _extract_storage(self, title: str) -> int:
        """从标题中提取存储大小(GB)"""
        # 查找 GB 存储
        storage_patterns = [
            r'(\d+)\s*[Gg][Bb]\s*存储',
            r'(\d+)\s*[Gg][Bb]\s*[Ss][Tt][Oo][Rr][Aa][Gg][Ee]',
            r'存储\s*(\d+)\s*[Gg]',
            r'(\d+)[Gg]\s*内存'
        ]
        
        for pattern in storage_patterns:
            match = re.search(pattern, title)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        
        # 根据型号估算
        title_lower = title.lower()
        if any(x in title_lower for x in ['pro', 'ultra', 'max', 'plus']):
            return 256  # 高端机型
        elif any(x in title_lower for x in ['iphone 15', 'mate 60', 's24']):
            return 128  # 旗舰机型
        else:
            return 128  # 中端机型
    
    def _extract_screen_size(self, title: str) -> float:
        """从标题中提取屏幕尺寸(英寸)"""
        # 查找英寸尺寸
        size_patterns = [
            r'(\d+\.?\d*)\s*英寸',
            r'(\d+\.?\d*)\s*寸',
            r'屏幕\s*(\d+\.?\d*)\s*[Ii]nch'
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, title)
            if match:
                try:
                    return float(match.group(1))
                except:
                    pass
        
        # 根据型号估算
        title_lower = title.lower()
        if any(x in title_lower for x in ['max', 'ultra', 'pro max']):
            return 6.7  # 大屏机型
        elif any(x in title_lower for x in ['mini', 'se']):
            return 5.4  # 小屏机型
        else:
            return 6.1  # 标准机型
    
    def _extract_resolution(self, title: str) -> str:
        """从标题中提取分辨率"""
        # 查找分辨率
        res_patterns = [
            r'(\d+[xX*]\d+)\s*分辨率',
            r'分辨率\s*(\d+[xX*]\d+)',
            r'(\d+K)\s*屏幕'
        ]
        
        for pattern in res_patterns:
            match = re.search(pattern, title)
            if match:
                return match.group(1)
        
        return '1080x2400'  # 默认FHD+
    
    def _extract_refresh_rate(self, title: str) -> int:
        """从标题中提取刷新率(Hz)"""
        # 查找刷新率
        refresh_patterns = [
            r'(\d+)\s*[Hh]z\s*刷新',
            r'刷新率\s*(\d+)\s*[Hh]z',
            r'(\d+)[Hh]z\s*高刷'
        ]
        
        for pattern in refresh_patterns:
            match = re.search(pattern, title)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        
        # 根据型号估算
        title_lower = title.lower()
        if any(x in title_lower for x in ['pro', 'ultra', 'gaming', '游戏']):
            return 120  # 高端机型
        elif 'iphone' in title_lower:
            if 'pro' in title_lower:
                return 120
            else:
                return 60   # 标准iPhone
        else:
            return 90   # 中端机型
    
    def _extract_battery_capacity(self, title: str) -> int:
        """从标题中提取电池容量(mAh)"""
        # 查找电池容量
        battery_patterns = [
            r'(\d+)\s*[Mm][Aa][Hh]\s*电池',
            r'电池\s*(\d+)\s*[Mm][Aa][Hh]',
            r'(\d+)[Mm][Aa][Hh]\s*大电池'
        ]
        
        for pattern in battery_patterns:
            match = re.search(pattern, title)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        
        # 根据型号估算
        title_lower = title.lower()
        if any(x in title_lower for x in ['pro', 'ultra', 'max']):
            return 5000  # 大电池机型
        elif 'iphone' in title_lower:
            return 3500  # iPhone
        else:
            return 4500  # 标准机型
    
    def _extract_camera(self, title: str) -> str:
        """从标题中提取摄像头信息"""
        # 查找摄像头配置
        camera_patterns = [
            r'(\d+[MmPp]\s*[+\dMmPp]*)\s*摄像头',
            r'摄像头\s*(\d+[MmPp]\s*[+\dMmPp]*)',
            r'(\d+[MmPp]\s*[+\dMmPp]*)\s*相机'
        ]
        
        for pattern in camera_patterns:
            match = re.search(pattern, title)
            if match:
                return match.group(1)
        
        # 根据型号估算
        title_lower = title.lower()
        if any(x in title_lower for x in ['pro', 'ultra', '摄影', '影像']):
            return '50MP+12MP+12MP'
        else:
            return '48MP+8MP+2MP'  # 标准配置
    
    def _determine_os(self, brand: str) -> str:
        """确定操作系统"""
        if brand == 'Apple':
            return 'iOS'
        elif brand in ['Xiaomi', 'Huawei', 'Samsung', '其他']:
            return 'Android'
        else:
            return 'Android'  # 默认
    
    def _has_5g_support(self, title: str) -> bool:
        """判断是否支持5G"""
        title_lower = title.lower()
        # 现代手机基本都支持5G
        if any(x in title_lower for x in ['4g', '3g', '2g']):
            return False
        # 默认支持5G
        return True
    
    def _estimate_release_date(self, model: str, brand: str) -> str:
        """估算发布日期"""
        # 简单估算：根据型号中的数字
        year_match = re.search(r'(\d{4})', model)
        if year_match:
            year = year_match.group(1)
            if len(year) == 4 and 2020 <= int(year) <= 2025:
                return f"{year}-01-01"
        
        # 根据品牌和系列估算
        model_lower = model.lower()
        current_year = datetime.now().year
        
        if brand == 'Apple':
            if '15' in model_lower:
                return '2023-01-01'
            elif '14' in model_lower:
                return '2022-01-01'
            elif '13' in model_lower:
                return '2021-01-01'
            elif '12' in model_lower:
                return '2020-01-01'
        elif brand == 'Xiaomi':
            if '14' in model_lower:
                return '2023-01-01'
            elif '13' in model_lower:
                return '2022-01-01'
            elif '12' in model_lower:
                return '2021-01-01'
        elif brand == 'Huawei':
            if '60' in model_lower:
                return '2023-01-01'
            elif '50' in model_lower:
                return '2022-01-01'
            elif '40' in model_lower:
                return '2021-01-01'
        elif brand == 'Samsung':
            if '24' in model_lower:
                return '2024-01-01'
            elif '23' in model_lower:
                return '2023-01-01'
            elif '22' in model_lower:
                return '2022-01-01'
        
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
        return 2999.0
    
    def _generate_pvid(self) -> str:
        """生成京东PVID参数"""
        import uuid
        return str(uuid.uuid4()).replace('-', '')[:32]
    
    def _get_backup_data(self) -> List[Dict[str, Any]]:
        """获取备用数据（当爬取失败时使用）"""
        backup_phones = [
            {
                "id": "phone-backup-001",
                "model": "iPhone 15",
                "brand": "Apple",
                "releaseDate": "2023-01-01",
                "price": 5999,
                "description": "苹果iPhone 15智能手机，A16芯片，灵动岛设计",
                "processor": "A16",
                "ram": 6,
                "storage": 128,
                "screenSize": 6.1,
                "resolution": "2556x1179",
                "refreshRate": 60,
                "batteryCapacity": 3349,
                "camera": "48MP+12MP",
                "os": "iOS",
                "support5G": True,
                "source": "备用数据"
            },
            {
                "id": "phone-backup-002",
                "model": "Xiaomi 14",
                "brand": "Xiaomi",
                "releaseDate": "2023-01-01",
                "price": 3999,
                "description": "小米14智能手机，骁龙8 Gen 3，徕卡影像",
                "processor": "骁龙8 Gen 3",
                "ram": 12,
                "storage": 256,
                "screenSize": 6.36,
                "resolution": "2670x1200",
                "refreshRate": 120,
                "batteryCapacity": 4610,
                "camera": "50MP+50MP+50MP",
                "os": "Android",
                "support5G": True,
                "source": "备用数据"
            },
            {
                "id": "phone-backup-003",
                "model": "Huawei Mate 60 Pro",
                "brand": "Huawei",
                "releaseDate": "2023-01-01",
                "price": 6999,
                "description": "华为Mate 60 Pro智能手机，麒麟9000S，卫星通话",
                "processor": "麒麟9000S",
                "ram": 12,
                "storage": 512,
                "screenSize": 6.82,
                "resolution": "2720x1260",
                "refreshRate": 120,
                "batteryCapacity": 5000,
                "camera": "50MP+48MP+12MP",
                "os": "Android",
                "support5G": True,
                "source": "备用数据"
            },
            {
                "id": "phone-backup-004",
                "model": "Samsung Galaxy S24",
                "brand": "Samsung",
                "releaseDate": "2024-01-01",
                "price": 5699,
                "description": "三星Galaxy S24智能手机，骁龙8 Gen 3",
                "processor": "骁龙8 Gen 3",
                "ram": 8,
                "storage": 256,
                "screenSize": 6.2,
                "resolution": "2340x1080",
                "refreshRate": 120,
                "batteryCapacity": 4000,
                "camera": "50MP+12MP+10MP",
                "os": "Android",
                "support5G": True,
                "source": "备用数据"
            }
        ]
        return backup_phones
    
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
    运行手机数据爬取
    
    Returns:
        手机数据列表
    """
    print("🔍 开始爬取手机数据...")
    
    scraper = PhoneScraper()
    phone_data = scraper.run()
    
    # 数据统计
    brand_stats = {}
    for p in phone_data:
        brand = p['brand']
        brand_stats[brand] = brand_stats.get(brand, 0) + 1
    
    print(f"✅ 手机数据爬取完成，共{len(phone_data)}个手机")
    for brand, count in sorted(brand_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"   {brand}: {count} 个 ({count/len(phone_data)*100:.1f}%)")
    
    # 价格统计
    if phone_data:
        prices = [p['price'] for p in phone_data]
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        print(f"   平均价格: ¥{avg_price:.0f}")
        print(f"   价格区间: ¥{min_price}-¥{max_price}")
        
        # 5G支持统计
        g5_count = len([p for p in phone_data if p['support5G']])
        print(f"   5G支持: {g5_count} 个 ({g5_count/len(phone_data)*100:.1f}%)")
        
        # 显示数据来源
        sources = {}
        for p in phone_data:
            source = p.get('source', '未知')
            sources[source] = sources.get(source, 0) + 1
        
        print(f"   数据来源:")
        for source, count in sources.items():
            print(f"     - {source}: {count} 个")
    
    return phone_data


if __name__ == "__main__":
    # 测试运行
    data = run()
    print(f"爬取到{len(data)}个手机数据")
    if data:
        print("第一个手机:", json.dumps(data[0], ensure_ascii=False, indent=2))
