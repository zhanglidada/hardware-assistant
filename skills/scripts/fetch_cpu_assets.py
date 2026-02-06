#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CPU 徽标资源下载脚本

功能：
1. 根据预定义的目标清单搜索 CPU 徽标图片
2. 使用 icrawler 库从多个搜索引擎获取图片
3. 自动转换非 PNG 格式图片为 PNG
4. 统一命名和组织下载的图片

使用方法：
python fetch_cpu_assets.py

依赖库：
pip install --trusted-host pypi.tuna.tsinghua.edu.cn --trusted-host files.pythonhosted.org icrawler Pillow
"""

import os
import sys
import time
from typing import Dict, List
from PIL import Image
from icrawler.builtin import GoogleImageCrawler, BingImageCrawler


# 目标清单：映射我们的代码到搜索关键词
TARGETS = {
    # Intel 系列
    "intel_i9": "Intel Core i9 badge logo png transparent",
    "intel_i7": "Intel Core i7 badge logo png transparent",
    "intel_i5": "Intel Core i5 badge logo png transparent",
    "intel_i3": "Intel Core i3 badge logo png transparent",
    "intel_u9": "Intel Core Ultra 9 badge logo png transparent",
    "intel_u7": "Intel Core Ultra 7 badge logo png transparent",
    "intel_u5": "Intel Core Ultra 5 badge logo png transparent",
    "intel_u3": "Intel Core Ultra 3 badge logo png transparent",
    
    # AMD 系列
    "amd_r9": "AMD Ryzen 9 logo badge sticker png",
    "amd_r7": "AMD Ryzen 7 logo badge sticker png",
    "amd_r5": "AMD Ryzen 5 logo badge sticker png",
    "amd_r3": "AMD Ryzen 3 logo badge sticker png",
    "amd_tr": "AMD Threadripper logo badge png",
    "amd_athlon": "AMD Athlon logo badge png",
    
    # Apple 系列
    "apple_m1": "Apple M1 chip icon png",
    "apple_m1_pro": "Apple M1 Pro chip icon png",
    "apple_m1_max": "Apple M1 Max chip icon png",
    "apple_m1_ultra": "Apple M1 Ultra chip icon png",
    "apple_m2": "Apple M2 chip icon png",
    "apple_m2_pro": "Apple M2 Pro chip icon png",
    "apple_m2_max": "Apple M2 Max chip icon png",
    "apple_m2_ultra": "Apple M2 Ultra chip icon png",
    "apple_m3": "Apple M3 chip icon png",
    "apple_m3_pro": "Apple M3 Pro chip icon png",
    "apple_m3_max": "Apple M3 Max chip icon png",
    "apple_m3_ultra": "Apple M3 Ultra chip icon png",
    "apple_m4": "Apple M4 chip icon png",
    "apple_m4_pro": "Apple M4 Pro chip icon png",
    "apple_m4_max": "Apple M4 Max chip icon png",
    
    # Qualcomm 系列
    "qualcomm_8cx_gen4": "Qualcomm Snapdragon 8cx Gen 4 logo png",
    "qualcomm_8cx_gen3": "Qualcomm Snapdragon 8cx Gen 3 logo png",
    "qualcomm_7c_gen3": "Qualcomm Snapdragon 7c Gen 3 logo png",
    "qualcomm_7c_plus_gen3": "Qualcomm Snapdragon 7c+ Gen 3 logo png",
    "qualcomm_x_elite": "Qualcomm Snapdragon X Elite logo png",
    "qualcomm_x_plus": "Qualcomm Snapdragon X Plus logo png"
}


# 下载配置
DOWNLOAD_COUNT = 5  # 每个型号下载前 5 张图片（增加可选数量）
OUTPUT_DIR = "temp_assets"  # 输出目录
SEARCH_ENGINE = "google"  # 默认搜索引擎：google 或 bing


def ensure_directory(path: str) -> None:
    """
    确保目录存在
    
    Args:
        path: 目录路径
    """
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"✅ 创建目录: {path}")


def clean_directory(path: str) -> None:
    """
    清空目录中的所有文件
    
    Args:
        path: 目录路径
    """
    if os.path.exists(path):
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)


def convert_to_png(input_path: str, output_path: str) -> bool:
    """
    将图片转换为 PNG 格式
    
    Args:
        input_path: 输入图片路径
        output_path: 输出 PNG 路径
    
    Returns:
        bool: 转换是否成功
    """
    try:
        with Image.open(input_path) as img:
            # 确保是 RGBA 模式（支持透明）
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            img.save(output_path, 'PNG', quality=95, optimize=True)
        return True
    except Exception as e:
        print(f"⚠️  转换失败 {input_path}: {e}")
        return False


def download_images_with_crawler(keyword: str, output_dir: str, max_num: int = 5, 
                                 engine: str = "google") -> int:
    """
    使用 icrawler 下载图片
    
    Args:
        keyword: 搜索关键词
        output_dir: 输出目录
        max_num: 最大下载数量
        engine: 搜索引擎 (google 或 bing)
    
    Returns:
        int: 成功下载的图片数量
    """
    try:
        print(f"🔍 使用 {engine.upper()} 搜索: {keyword}")
        
        # 清空目标目录
        clean_directory(output_dir)
        ensure_directory(output_dir)
        
        # 选择搜索引擎
        if engine.lower() == "bing":
            crawler = BingImageCrawler(
                storage={'root_dir': output_dir},
                log_level=30  # WARNING 级别，减少日志输出
            )
        else:
            crawler = GoogleImageCrawler(
                storage={'root_dir': output_dir},
                log_level=30  # WARNING 级别，减少日志输出
            )
        
        # 执行搜索和下载
        crawler.crawl(
            keyword=keyword,
            max_num=max_num,
            min_size=(200, 200),  # 最小尺寸 200x200
            file_idx_offset=0
        )
        
        # 统计下载的文件数
        downloaded_files = [f for f in os.listdir(output_dir) 
                          if os.path.isfile(os.path.join(output_dir, f))]
        
        print(f"✅ 下载完成: {len(downloaded_files)} 张图片")
        return len(downloaded_files)
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return 0


def get_brand_color(series_code: str) -> str:
    """
    根据系列代码获取品牌色
    
    Args:
        series_code: 系列代码，如 'intel_i9'
    
    Returns:
        str: 品牌色的十六进制值
    """
    brand_colors = {
        'intel': '#0071c5',  # Intel 蓝色
        'amd': '#ed1c24',    # AMD 红色
        'apple': '#86868b',  # Apple 灰色
        'qualcomm': '#4caf50'  # Qualcomm 绿色
    }
    
    for brand, color in brand_colors.items():
        if brand in series_code.lower():
            return color
    
    return '#808080'  # 默认灰色


def fetch_cpu_assets() -> None:
    """
    主函数：下载并处理 CPU 徽标图片
    """
    print("开始下载 CPU 徽标图片...")
    print(f"目标型号数量: {len(TARGETS)}")
    print(f"每个型号下载: {DOWNLOAD_COUNT} 张图片")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 60)
    
    # 确保输出目录存在
    ensure_directory(OUTPUT_DIR)
    
    # 遍历目标清单
    for code, keyword in TARGETS.items():
        print(f"\n处理: {code}")
        print(f"搜索关键词: {keyword}")
        
        # 创建型号专属目录
        model_dir = os.path.join(OUTPUT_DIR, code)
        ensure_directory(model_dir)
        
        # 清空目录（避免之前的文件影响）
        for file in os.listdir(model_dir):
            file_path = os.path.join(model_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        # 尝试多个搜索引擎
        image_urls = []
        
        # 1. 尝试 Google
        print("尝试使用 Google 搜索...")
        google_urls = search_google_images(keyword, max_results=DOWNLOAD_COUNT * 2)
        if google_urls:
            image_urls.extend(google_urls)
            print(f"Google 找到 {len(google_urls)} 张图片")
        
        # 2. 如果 Google 失败，尝试 Bing
        if len(image_urls) < DOWNLOAD_COUNT:
            print("尝试使用 Bing 搜索...")
            bing_urls = search_bing_images(keyword, max_results=DOWNLOAD_COUNT * 2)
            if bing_urls:
                image_urls.extend(bing_urls)
                print(f"Bing 找到 {len(bing_urls)} 张图片")
        
        # 3. 如果 Bing 也失败，尝试 DuckDuckGo
        if len(image_urls) < DOWNLOAD_COUNT:
            print("尝试使用 DuckDuckGo 搜索...")
            duckduckgo_urls = search_duckduckgo_images(keyword, max_results=DOWNLOAD_COUNT * 2)
            if duckduckgo_urls:
                image_urls.extend(duckduckgo_urls)
                print(f"DuckDuckGo 找到 {len(duckduckgo_urls)} 张图片")
        
        # 去重
        image_urls = list(set(image_urls))
        print(f"去重后找到 {len(image_urls)} 张图片")
        
        if not image_urls:
            print(f"未找到图片: {code}")
            print(f"完成: {code}")
            continue
        
        # 下载图片
        downloaded_count = 0
        for i, img_url in enumerate(image_urls, 1):
            if downloaded_count >= DOWNLOAD_COUNT:
                break
            
            # 生成保存路径
            ext = os.path.splitext(img_url)[1].lower()
            if not ext or ext not in ['.png', '.jpg', '.jpeg', '.webp', '.gif']:
                ext = '.png'
            
            temp_save_path = os.path.join(model_dir, f"temp_{i}{ext}")
            
            # 下载图片
            if download_image(img_url, temp_save_path):
                downloaded_count += 1
        
        if downloaded_count == 0:
            print(f"所有图片下载失败: {code}")
            print(f"完成: {code}")
            continue
        
        # 处理下载的文件
        # 获取目录中的所有文件
        files = [f for f in os.listdir(model_dir) if os.path.isfile(os.path.join(model_dir, f))]
        
        # 过滤出图片文件
        image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}
        image_files = []
        
        for file_name in files:
            ext = os.path.splitext(file_name)[1].lower()
            if ext in image_extensions:
                image_files.append(file_name)
        
        # 按文件名排序
        image_files.sort()
        
        # 处理前 DOWNLOAD_COUNT 个文件
        for i, file_name in enumerate(image_files[:DOWNLOAD_COUNT], 1):
            input_path = os.path.join(model_dir, file_name)
            output_name = f"{code}_candidate_{i}.png"
            output_path = os.path.join(model_dir, output_name)
            
            # 检查是否已经是 PNG
            ext = os.path.splitext(file_name)[1].lower()
            if ext == '.png':
                # 直接重命名
                if input_path != output_path:
                    os.rename(input_path, output_path)
                    print(f"重命名: {file_name} -> {output_name}")
            else:
                # 转换为 PNG
                convert_to_png(input_path, output_path)
                # 删除原文件
                os.remove(input_path)
                print(f"删除原文件: {file_name}")
        
        print(f"完成: {code}")
    
    print("=" * 60)
    print("所有型号处理完成！")
    print(f"\n后续操作建议：")
    print(f"1. 打开目录 {OUTPUT_DIR}")
    print(f"2. 检查每个型号文件夹中的候选图片")
    print(f"3. 删除不合适的图片")
    print(f"4. 将最好的一张图片重命名为 intel_i9.png 格式（例如 intel_i9.png）")
    print(f"5. 使用 manage_cpu_icons.py 脚本上传处理后的图片")


def main() -> None:
    """
    主入口
    """
    try:
        fetch_cpu_assets()
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
