#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CPU 徽标资源下载脚本 (直接下载版)

功能：
1. 从预定义的 URL 列表直接下载 CPU 徽标图片
2. 自动转换非 PNG 格式图片为 PNG
3. 统一命名和组织下载的图片

使用方法：
python fetch_cpu_assets_direct.py

依赖库：
pip install --trusted-host pypi.tuna.tsinghua.edu.cn --trusted-host files.pythonhosted.org requests Pillow
"""

import os
import sys
import requests
from typing import Dict, List
from PIL import Image
from io import BytesIO


# 直接图片 URL 列表 (从可靠来源)
CPU_ICON_URLS = {
    # Intel 系列 - 来自 Intel 官方资源
    "intel_i9": [
        "https://www.intel.com/content/dam/www/central-libraries/us/en/images/2022-11/core-i9-gen13-badge-rwd.png",
        "https://cdn.mos.cms.futurecdn.net/2g4P4yuKzRs5f7xXWLmQ7Y.png",
    ],
    "intel_i7": [
        "https://www.intel.com/content/dam/www/central-libraries/us/en/images/2022-11/core-i7-gen13-badge-rwd.png",
        "https://cdn.mos.cms.futurecdn.net/WbfpKoVSHTuiP7xN7ZQwf5.png",
    ],
    "intel_i5": [
        "https://www.intel.com/content/dam/www/central-libraries/us/en/images/2022-11/core-i5-gen13-badge-rwd.png",
    ],
    "intel_i3": [
        "https://www.intel.com/content/dam/www/central-libraries/us/en/images/2022-11/core-i3-gen13-badge-rwd.png",
    ],
    
    # AMD 系列  
    "amd_r9": [
        "https://www.amd.com/content/dam/amd/en/images/badges/1486537-amd-ryzen-9-badge.png",
        "https://assets.hardwarezone.com/img/2024/07/amd-ryzen-9-9950x-16-cores-badge.png",
    ],
    "amd_r7": [
        "https://www.amd.com/content/dam/amd/en/images/badges/1486534-amd-ryzen-7-badge.png",
        "https://assets.hardwarezone.com/img/2024/07/amd-ryzen-7-9700x-8-cores-badge.png",
    ],
    "amd_r5": [
        "https://www.amd.com/content/dam/amd/en/images/badges/1486531-amd-ryzen-5-badge.png",
    ],
    "amd_r3": [
        "https://www.amd.com/content/dam/amd/en/images/badges/1486528-amd-ryzen-3-badge.png",
    ],
}


# 下载配置
OUTPUT_DIR = "temp_assets"  # 输出目录


def ensure_directory(path: str) -> None:
    """确保目录存在"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"✅ 创建目录: {path}")


def download_image(url: str, save_path: str, timeout: int = 30) -> bool:
    """
    下载图片到指定路径
    
    Args:
        url: 图片 URL
        save_path: 保存路径
        timeout: 超时时间
    
    Returns:
        bool: 下载是否成功
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        return True
    except Exception as e:
        print(f"  ⚠️  下载失败: {e}")
        return False


def convert_to_png(input_path: str, output_path: str) -> bool:
    """将图片转换为 PNG 格式"""
    try:
        with Image.open(input_path) as img:
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            img.save(output_path, 'PNG', quality=95, optimize=True)
        return True
    except Exception as e:
        print(f"  ⚠️  转换失败: {e}")
        return False


def fetch_cpu_assets_direct() -> None:
    """主函数：直接下载 CPU 徽标图片"""
    print("🚀 开始下载 CPU 徽标图片 (直接下载模式)...")
    print(f"📊 目标型号数量: {len(CPU_ICON_URLS)}")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print("=" * 80)
    
    # 确保输出目录存在
    ensure_directory(OUTPUT_DIR)
    
    # 统计信息
    total_success = 0
    total_failed = 0
    
    # 遍历目标清单
    for idx, (code, urls) in enumerate(CPU_ICON_URLS.items(), 1):
        print(f"\n[{idx}/{len(CPU_ICON_URLS)}] 处理: {code}")
        print(f"📥 可用 URL 数量: {len(urls)}")
        
        # 创建型号专属目录
        model_dir = os.path.join(OUTPUT_DIR, code)
        ensure_directory(model_dir)
        
        # 尝试下载每个 URL
        downloaded_count = 0
        for url_idx, url in enumerate(urls, 1):
            print(f"  🔗 尝试 URL {url_idx}: {url[:60]}...")
            
            # 生成临时文件名
            ext = os.path.splitext(url)[1].split('?')[0]  # 移除查询参数
            if not ext or ext.lower() not in ['.png', '.jpg', '.jpeg', '.webp']:
                ext = '.png'
            
            temp_path = os.path.join(model_dir, f"temp_{url_idx}{ext}")
            
            # 下载图片
            if download_image(url, temp_path):
                downloaded_count += 1
                print(f"  ✅ 下载成功")
                
                # 转换为 PNG（如果需要）
                final_name = f"{code}_candidate_{url_idx}.png"
                final_path = os.path.join(model_dir, final_name)
                
                if ext.lower() == '.png':
                    try:
                        os.rename(temp_path, final_path)
                        print(f"  ✅ 保存为: {final_name}")
                    except:
                        pass
                else:
                    if convert_to_png(temp_path, final_path):
                        print(f"  ✅ 转换并保存为: {final_name}")
                        try:
                            os.remove(temp_path)
                        except:
                            pass
        
        if downloaded_count > 0:
            print(f"✅ {code}: 成功下载 {downloaded_count} 张图片")
            total_success += 1
        else:
            print(f"❌ {code}: 所有 URL 都失败")
            total_failed += 1
    
    # 打印汇总信息
    print("\n" + "=" * 80)
    print(f"✅ 处理完成!")
    print(f"📊 成功: {total_success} 个型号")
    print(f"❌ 失败: {total_failed} 个型号")
    print(f"📁 输出目录: {os.path.abspath(OUTPUT_DIR)}")
    print("\n📋 后续操作建议：")
    print(f"1. 打开目录: {os.path.abspath(OUTPUT_DIR)}")
    print(f"2. 检查每个型号文件夹中的图片")
    print(f"3. 选择最合适的图片重命名为 {code}.png")
    print(f"4. 删除候选文件，保留最终版本")


def main() -> None:
    """主入口"""
    try:
        fetch_cpu_assets_direct()
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
