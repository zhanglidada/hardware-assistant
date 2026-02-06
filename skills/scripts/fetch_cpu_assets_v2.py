#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CPU 徽标资源下载脚本 (使用 icrawler)

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
from typing import Dict
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
    
    # AMD 系列
    "amd_r9": "AMD Ryzen 9 logo badge sticker png",
    "amd_r7": "AMD Ryzen 7 logo badge sticker png",
    "amd_r5": "AMD Ryzen 5 logo badge sticker png",
    "amd_r3": "AMD Ryzen 3 logo badge sticker png",
    
    # Apple 系列（仅主要型号）
    "apple_m1": "Apple M1 chip icon png",
    "apple_m2": "Apple M2 chip icon png",
    "apple_m3": "Apple M3 chip icon png",
    "apple_m4": "Apple M4 chip icon png",
}


# 下载配置
DOWNLOAD_COUNT = 5  # 每个型号下载前 5 张图片
OUTPUT_DIR = "temp_assets"  # 输出目录
SEARCH_ENGINE = "google"  # 默认搜索引擎：google 或 bing


def ensure_directory(path: str) -> None:
    """确保目录存在"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"✅ 创建目录: {path}")


def clean_directory(path: str) -> None:
    """清空目录中的所有文件"""
    if os.path.exists(path):
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass


def convert_to_png(input_path: str, output_path: str) -> bool:
    """将图片转换为 PNG 格式"""
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
    """使用 icrawler 下载图片"""
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


def process_downloaded_images(model_dir: str, code: str) -> None:
    """处理下载的图片（重命名和转换格式）"""
    try:
        # 获取所有下载的图片
        files = sorted([f for f in os.listdir(model_dir) 
                       if os.path.isfile(os.path.join(model_dir, f))])
        
        # 过滤出图片文件
        image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp'}
        image_files = [f for f in files 
                      if os.path.splitext(f)[1].lower() in image_extensions]
        
        if not image_files:
            return
        
        print(f"📝 处理 {len(image_files)} 张图片...")
        
        # 处理每张图片
        for i, filename in enumerate(image_files[:DOWNLOAD_COUNT], 1):
            input_path = os.path.join(model_dir, filename)
            output_name = f"{code}_candidate_{i}.png"
            output_path = os.path.join(model_dir, output_name)
            
            # 检查文件扩展名
            ext = os.path.splitext(filename)[1].lower()
            
            if ext == '.png':
                # PNG 文件直接重命名
                if input_path != output_path:
                    try:
                        os.rename(input_path, output_path)
                        print(f"  ✅ {i}. 重命名: {filename} → {output_name}")
                    except:
                        pass
            else:
                # 其他格式转换为 PNG
                if convert_to_png(input_path, output_path):
                    print(f"  ✅ {i}. 转换: {filename} → {output_name}")
                    try:
                        os.remove(input_path)
                    except:
                        pass
        
        # 删除多余的原始文件
        remaining_files = [f for f in os.listdir(model_dir) 
                          if f not in [f"{code}_candidate_{i}.png" 
                                      for i in range(1, DOWNLOAD_COUNT + 1)]]
        for f in remaining_files:
            try:
                os.remove(os.path.join(model_dir, f))
            except:
                pass
                
    except Exception as e:
        print(f"⚠️  处理图片时出错: {e}")


def fetch_cpu_assets() -> None:
    """主函数：下载并处理 CPU 徽标图片"""
    print("🚀 开始下载 CPU 徽标图片...")
    print(f"📊 目标型号数量: {len(TARGETS)}")
    print(f"📥 每个型号下载: {DOWNLOAD_COUNT} 张图片")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print(f"🔍 搜索引擎: {SEARCH_ENGINE.upper()}")
    print("=" * 80)
    
    # 确保输出目录存在
    ensure_directory(OUTPUT_DIR)
    
    # 统计信息
    total_success = 0
    total_failed = 0
    
    # 遍历目标清单
    for idx, (code, keyword) in enumerate(TARGETS.items(), 1):
        print(f"\n[{idx}/{len(TARGETS)}] 处理: {code}")
        print(f"🔍 搜索关键词: {keyword}")
        
        # 创建型号专属目录
        model_dir = os.path.join(OUTPUT_DIR, code)
        ensure_directory(model_dir)
        
        # 下载图片
        downloaded_count = download_images_with_crawler(
            keyword=keyword,
            output_dir=model_dir,
            max_num=DOWNLOAD_COUNT * 2,  # 多下载一些以备选择
            engine=SEARCH_ENGINE
        )
        
        if downloaded_count == 0:
            print(f"❌ 未下载到任何图片: {code}")
            total_failed += 1
            
            # 如果 Google 失败，尝试 Bing
            if SEARCH_ENGINE.lower() == "google":
                print(f"🔄 尝试使用 Bing 搜索...")
                downloaded_count = download_images_with_crawler(
                    keyword=keyword,
                    output_dir=model_dir,
                    max_num=DOWNLOAD_COUNT * 2,
                    engine="bing"
                )
                
                if downloaded_count > 0:
                    total_failed -= 1
                    total_success += 1
        else:
            total_success += 1
        
        # 处理下载的文件
        if downloaded_count > 0:
            process_downloaded_images(model_dir, code)
        
        # 添加延迟，避免请求过快
        if idx < len(TARGETS):
            time.sleep(2)
    
    # 打印汇总信息
    print("\n" + "=" * 80)
    print(f"✅ 处理完成!")
    print(f"📊 成功: {total_success} 个型号")
    print(f"❌ 失败: {total_failed} 个型号")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print("\n📋 后续操作建议：")
    print(f"1. 打开目录: {os.path.abspath(OUTPUT_DIR)}")
    print(f"2. 检查每个型号文件夹中的候选图片")
    print(f"3. 选择最合适的图片重命名为标准格式 (如 intel_i9.png)")
    print(f"4. 删除不需要的候选图片")


def main() -> None:
    """主入口"""
    try:
        fetch_cpu_assets()
    except KeyboardInterrupt:
        print("\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
