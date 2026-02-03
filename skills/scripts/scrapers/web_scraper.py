#!/usr/bin/env python3
"""
通用网页爬虫工具类
提供HTTP请求、HTML解析、数据提取等通用功能
"""

import requests
import time
import random
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
import logging
from bs4 import BeautifulSoup
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebScraper:
    """通用网页爬虫类"""
    
    def __init__(self, base_url: str = "", headers: Optional[Dict] = None, 
                 delay_range: tuple = (1, 3), max_retries: int = 3):
        """
        初始化爬虫
        
        Args:
            base_url: 基础URL
            headers: HTTP请求头
            delay_range: 请求延迟范围（秒）
            max_retries: 最大重试次数
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        self.session.headers.update(self.headers)
        self.delay_range = delay_range
        self.max_retries = max_retries
        
    def _random_delay(self):
        """随机延迟，避免被网站封禁"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
        
    def fetch_page(self, url: str, params: Optional[Dict] = None, 
                   method: str = 'GET', data: Optional[Dict] = None) -> Optional[str]:
        """
        获取网页内容
        
        Args:
            url: 目标URL
            params: 查询参数
            method: HTTP方法
            data: POST数据
            
        Returns:
            网页HTML内容或None
        """
        full_url = urljoin(self.base_url, url) if self.base_url else url
        
        for attempt in range(self.max_retries):
            try:
                self._random_delay()
                
                if method.upper() == 'GET':
                    response = self.session.get(full_url, params=params, timeout=10)
                elif method.upper() == 'POST':
                    response = self.session.post(full_url, data=data, timeout=10)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                response.raise_for_status()
                
                # 检查编码
                if response.encoding is None:
                    response.encoding = 'utf-8'
                    
                logger.info(f"成功获取页面: {full_url} (状态码: {response.status_code})")
                return response.text
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"第{attempt + 1}次尝试失败: {e}")
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    logger.info(f"等待{wait_time}秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"获取页面失败: {full_url}, 错误: {e}")
                    
        return None
    
    def parse_html(self, html: str, parser: str = 'html.parser') -> Optional[BeautifulSoup]:
        """
        解析HTML为BeautifulSoup对象
        
        Args:
            html: HTML内容
            parser: 解析器类型
            
        Returns:
            BeautifulSoup对象或None
        """
        if not html:
            return None
            
        try:
            soup = BeautifulSoup(html, parser)
            return soup
        except Exception as e:
            logger.error(f"解析HTML失败: {e}")
            return None
    
    def extract_links(self, soup: BeautifulSoup, base_url: str = None, 
                     link_selector: str = 'a', attr: str = 'href') -> List[str]:
        """
        从页面提取链接
        
        Args:
            soup: BeautifulSoup对象
            base_url: 基础URL（用于相对链接转绝对链接）
            link_selector: 链接选择器
            attr: 链接属性
            
        Returns:
            链接列表
        """
        links = []
        if not soup:
            return links
            
        for link in soup.select(link_selector):
            href = link.get(attr)
            if href:
                # 过滤掉JavaScript链接和空链接
                if href.startswith('javascript:') or href.startswith('#'):
                    continue
                    
                # 转换为绝对链接
                if base_url and not href.startswith(('http://', 'https://')):
                    href = urljoin(base_url, href)
                    
                links.append(href)
                
        return list(set(links))  # 去重
    
    def extract_text(self, soup: BeautifulSoup, selector: str = None, 
                    default: str = '') -> str:
        """
        提取文本内容
        
        Args:
            soup: BeautifulSoup对象或元素
            selector: CSS选择器
            default: 默认值
            
        Returns:
            提取的文本
        """
        if not soup:
            return default
            
        try:
            if selector:
                element = soup.select_one(selector)
                if element:
                    return element.get_text(strip=True)
                return default
            else:
                # 如果没有选择器，直接获取soup的文本
                return soup.get_text(strip=True)
        except Exception as e:
            logger.error(f"提取文本失败: {e}")
            return default
    
    def extract_attribute(self, soup: BeautifulSoup, selector: str, 
                         attr: str, default: str = '') -> str:
        """
        提取元素属性
        
        Args:
            soup: BeautifulSoup对象
            selector: CSS选择器
            attr: 属性名
            default: 默认值
            
        Returns:
            属性值
        """
        if not soup:
            return default
            
        try:
            element = soup.select_one(selector)
            if element:
                return element.get(attr, default)
            return default
        except Exception as e:
            logger.error(f"提取属性失败: {e}")
            return default
    
    def extract_json_ld(self, soup: BeautifulSoup) -> List[Dict]:
        """
        提取JSON-LD结构化数据
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            JSON-LD数据列表
        """
        json_ld_data = []
        if not soup:
            return json_ld_data
            
        try:
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    json_ld_data.append(data)
                except json.JSONDecodeError as e:
                    logger.warning(f"解析JSON-LD失败: {e}")
        except Exception as e:
            logger.error(f"提取JSON-LD失败: {e}")
            
        return json_ld_data
    
    def save_to_file(self, data: Any, filename: str):
        """
        保存数据到文件
        
        Args:
            data: 要保存的数据
            filename: 文件名
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                if isinstance(data, (dict, list)):
                    json.dump(data, f, ensure_ascii=False, indent=2)
                else:
                    f.write(str(data))
            logger.info(f"数据已保存到: {filename}")
        except Exception as e:
            logger.error(f"保存文件失败: {e}")
    
    def load_from_file(self, filename: str) -> Any:
        """
        从文件加载数据
        
        Args:
            filename: 文件名
            
        Returns:
            加载的数据
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                if filename.endswith('.json'):
                    return json.load(f)
                else:
                    return f.read()
        except Exception as e:
            logger.error(f"加载文件失败: {e}")
            return None


class HardwareScraper(WebScraper):
    """硬件数据爬虫基类"""
    
    def __init__(self, category: str, **kwargs):
        """
        初始化硬件爬虫
        
        Args:
            category: 硬件类别（cpu, gpu, phone等）
        """
        super().__init__(**kwargs)
        self.category = category
        self.data = []
        
    def scrape(self) -> List[Dict[str, Any]]:
        """
        爬取数据（子类需要实现）
        
        Returns:
            爬取的数据列表
        """
        raise NotImplementedError("子类必须实现scrape方法")
    
    def normalize_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化数据格式（子类需要实现）
        
        Args:
            raw_data: 原始数据
            
        Returns:
            标准化后的数据
        """
        raise NotImplementedError("子类必须实现normalize_data方法")
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        验证数据完整性
        
        Args:
            data: 要验证的数据
            
        Returns:
            验证结果
        """
        required_fields = ['id', 'model', 'brand', 'price', 'releaseDate', 'description']
        
        for field in required_fields:
            if field not in data or not data[field]:
                logger.warning(f"数据缺少必需字段: {field}")
                return False
                
        # 验证价格是数字
        try:
            price = float(data['price'])
            if price <= 0:
                logger.warning(f"价格无效: {price}")
                return False
        except (ValueError, TypeError):
            logger.warning(f"价格格式错误: {data['price']}")
            return False
            
        return True
    
    def generate_id(self, model: str, brand: str) -> str:
        """
        生成唯一ID
        
        Args:
            model: 型号
            brand: 品牌
            
        Returns:
            唯一ID
        """
        # 简单ID生成：类别-品牌-型号的MD5前8位
        import hashlib
        id_str = f"{self.category}-{brand}-{model}".lower().replace(' ', '-')
        id_hash = hashlib.md5(id_str.encode()).hexdigest()[:8]
        return f"{self.category}-{id_hash}"
    
    def run(self) -> List[Dict[str, Any]]:
        """
        运行爬虫
        
        Returns:
            爬取的数据列表
        """
        logger.info(f"开始爬取{self.category}数据...")
        
        try:
            self.data = self.scrape()
            
            # 验证数据
            valid_data = []
            for item in self.data:
                if self.validate_data(item):
                    valid_data.append(item)
                else:
                    logger.warning(f"数据验证失败: {item.get('model', 'unknown')}")
            
            logger.info(f"爬取完成，共获取{len(self.data)}条数据，有效{len(valid_data)}条")
            return valid_data
            
        except Exception as e:
            logger.error(f"爬取{self.category}数据失败: {e}")
            return []


if __name__ == "__main__":
    # 测试爬虫
    scraper = WebScraper()
    html = scraper.fetch_page("https://www.baidu.com")
    if html:
        soup = scraper.parse_html(html)
        if soup:
            title = scraper.extract_text(soup, 'title')
            print(f"页面标题: {title}")