#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CPU 图标整理脚本

功能：
1. 扫描指定目录中的所有图片
2. 转换为 PNG 格式（透明背景）
3. 统一尺寸（可选）
4. 按命名规范重命名

使用方法：
python organize_cpu_icons.py [输入目录] [输出目录]

依赖库：
pip install Pillow
"""

import os
import sys
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image


# 目标尺寸
TARGET_SIZE = 512
# 支持的图片格式
SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.svg'}


def ensure_directory(path: str) -> None:
    """确保目录存在"""
    Path(path).mkdir(parents=True, exist_ok=True)


def resize_image(img: Image.Image, target_size: int) -> Image.Image:
    """
    等比例缩放图片
    
    Args:
        img: PIL Image 对象
        target_size: 目标尺寸（宽或高的最大值）
    
    Returns:
        Image: 缩放后的图片
    """
    # 计算缩放比例
    width, height = img.size
    if width == height == target_size:
        return img
    
    # 等比例缩放
    if width > height:
        new_width = target_size
        new_height = int(height * target_size / width)
    else:
        new_height = target_size
        new_width = int(width * target_size / height)
    
    return img.resize((new_width, new_height), Image.Resampling.LANCZOS)


def add_padding(img: Image.Image, target_size: int) -> Image.Image:
    """
    添加透明边距使图片成为正方形
    
    Args:
        img: PIL Image 对象
        target_size: 目标尺寸
    
    Returns:
        Image: 添加边距后的图片
    """
    width, height = img.size
    
    if width == height == target_size:
        return img
    
    # 创建透明背景
    result = Image.new('RGBA', (target_size, target_size), (0, 0, 0, 0))
    
    # 计算居中位置
    x = (target_size - width) // 2
    y = (target_size - height) // 2
    
    # 粘贴图片
    result.paste(img, (x, y), img if img.mode == 'RGBA' else None)
    
    return result


def process_image(input_path: str, output_path: str, target_size: int = TARGET_SIZE) -> bool:
    """
    处理单个图片
    
    Args:
        input_path: 输入图片路径
        output_path: 输出图片路径
        target_size: 目标尺寸
    
    Returns:
        bool: 处理是否成功
    """
    try:
        # 打开图片
        with Image.open(input_path) as img:
            # 转换为 RGBA 模式（支持透明）
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # 等比例缩放
            img = resize_image(img, target_size)
            
            # 添加边距使其成为正方形
            img = add_padding(img, target_size)
            
            # 保存为 PNG
            img.save(output_path, 'PNG', quality=95, optimize=True)
        
        return True
    except Exception as e:
        print(f"  ⚠️  处理失败: {e}")
        return False


def organize_icons(input_dir: str, output_dir: str) -> None:
    """
    整理图标文件
    
    Args:
        input_dir: 输入目录
        output_dir: 输出目录
    """
    print(f"🚀 开始整理 CPU 图标...")
    print(f"📁 输入目录: {input_dir}")
    print(f"📁 输出目录: {output_dir}")
    print(f"📐 目标尺寸: {TARGET_SIZE}x{TARGET_SIZE}")
    print("=" * 80)
    
    # 确保输出目录存在
    ensure_directory(output_dir)
    
    # 扫描输入目录
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ 输入目录不存在: {input_dir}")
        return
    
    # 获取所有图片文件
    image_files = []
    for ext in SUPPORTED_FORMATS:
        image_files.extend(input_path.glob(f"**/*{ext}"))
        image_files.extend(input_path.glob(f"**/*{ext.upper()}"))
    
    if not image_files:
        print(f"⚠️  未找到图片文件")
        return
    
    print(f"📊 找到 {len(image_files)} 个图片文件\n")
    
    # 统计信息
    success_count = 0
    failed_count = 0
    
    # 处理每个图片
    for idx, file_path in enumerate(sorted(image_files), 1):
        print(f"[{idx}/{len(image_files)}] 处理: {file_path.name}")
        
        # 生成输出文件名
        output_name = file_path.stem + ".png"
        output_path = Path(output_dir) / output_name
        
        # 处理图片
        if process_image(str(file_path), str(output_path), TARGET_SIZE):
            file_size = output_path.stat().st_size / 1024  # KB
            print(f"  ✅ 成功: {output_name} ({file_size:.1f} KB)")
            success_count += 1
        else:
            failed_count += 1
    
    # 打印汇总信息
    print("\n" + "=" * 80)
    print(f"✅ 整理完成!")
    print(f"📊 成功: {success_count} 个")
    print(f"❌ 失败: {failed_count} 个")
    print(f"📁 输出目录: {Path(output_dir).absolute()}")
    print("\n📋 后续步骤：")
    print(f"1. 检查输出目录中的图片")
    print(f"2. 按照命名规范重命名文件：")
    print(f"   - intel_i9.png, intel_i7.png, intel_i5.png, intel_i3.png")
    print(f"   - amd_r9.png, amd_r7.png, amd_r5.png, amd_r3.png")
    print(f"   - apple_m1.png, apple_m2.png, apple_m3.png, apple_m4.png")


def interactive_mode() -> None:
    """交互式模式：让用户选择输入和输出目录"""
    print("🎨 CPU 图标整理工具 - 交互模式")
    print("=" * 80)
    
    # 获取输入目录
    input_dir = input("📁 请输入图片所在目录路径（或按回车使用当前目录）: ").strip()
    if not input_dir:
        input_dir = "."
    
    # 获取输出目录
    output_dir = input("📁 请输入输出目录路径（或按回车使用 'organized_icons'）: ").strip()
    if not output_dir:
        output_dir = "organized_icons"
    
    # 执行整理
    organize_icons(input_dir, output_dir)


def main() -> None:
    """主入口"""
    try:
        if len(sys.argv) == 1:
            # 无参数：交互模式
            interactive_mode()
        elif len(sys.argv) == 2:
            # 一个参数：输入目录
            input_dir = sys.argv[1]
            output_dir = "organized_icons"
            organize_icons(input_dir, output_dir)
        elif len(sys.argv) == 3:
            # 两个参数：输入和输出目录
            input_dir = sys.argv[1]
            output_dir = sys.argv[2]
            organize_icons(input_dir, output_dir)
        else:
            print("使用方法:")
            print("  python organize_cpu_icons.py                    # 交互模式")
            print("  python organize_cpu_icons.py <输入目录>         # 使用默认输出目录")
            print("  python organize_cpu_icons.py <输入目录> <输出目录>")
            sys.exit(1)
    
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
