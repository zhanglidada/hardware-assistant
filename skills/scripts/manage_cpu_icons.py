#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CPU 图标管理脚本

功能：
1. 读取本地文件夹中的 CPU 系列图标图片
2. 模拟调用微信云开发 API 上传图片
3. 生成包含上传后 Cloud ID 的 JSON 数据文件

使用方法：
python manage_cpu_icons.py --input ./cpu_icons --output ./output/cpu_series_data.json
"""

import os
import json
import argparse
from typing import Dict, List, Optional


def upload_file(local_file_path: str, cloud_path: str) -> str:
    """
    模拟上传文件到微信云开发存储
    
    Args:
        local_file_path: 本地文件路径
        cloud_path: 云存储路径
    
    Returns:
        str: 云存储文件 ID，格式为 'cloud://...'
    """
    # 模拟逻辑，实际项目中需要调用微信云开发 SDK
    # 这里根据文件名生成模拟的 Cloud ID
    file_name = os.path.basename(local_file_path)
    cloud_file_id = f"cloud://hardware-assistant.6861-hardware-assistant-1302257382/icons/cpu/{file_name}"
    print(f"模拟上传: {local_file_path} -> {cloud_file_id}")
    return cloud_file_id


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


def get_display_name(series_code: str) -> str:
    """
    根据系列代码生成显示名称
    
    Args:
        series_code: 系列代码，如 'intel_i9'
    
    Returns:
        str: 显示名称，如 'Intel® Core™ i9'
    """
    display_names = {
        'intel_i9': 'Intel® Core™ i9',
        'intel_i7': 'Intel® Core™ i7',
        'intel_i5': 'Intel® Core™ i5',
        'intel_i3': 'Intel® Core™ i3',
        'intel_u9': 'Intel® Core™ Ultra 9',
        'intel_u7': 'Intel® Core™ Ultra 7',
        'intel_u5': 'Intel® Core™ Ultra 5',
        'intel_u3': 'Intel® Core™ Ultra 3',
        'amd_r9': 'AMD Ryzen™ 9',
        'amd_r7': 'AMD Ryzen™ 7',
        'amd_r5': 'AMD Ryzen™ 5',
        'amd_r3': 'AMD Ryzen™ 3',
        'amd_tr': 'AMD Ryzen™ Threadripper',
        'amd_athlon': 'AMD Athlon™',
        'apple_m1': 'Apple M1',
        'apple_m1_pro': 'Apple M1 Pro',
        'apple_m1_max': 'Apple M1 Max',
        'apple_m1_ultra': 'Apple M1 Ultra',
        'apple_m2': 'Apple M2',
        'apple_m2_pro': 'Apple M2 Pro',
        'apple_m2_max': 'Apple M2 Max',
        'apple_m2_ultra': 'Apple M2 Ultra',
        'apple_m3': 'Apple M3',
        'apple_m3_pro': 'Apple M3 Pro',
        'apple_m3_max': 'Apple M3 Max',
        'apple_m3_ultra': 'Apple M3 Ultra',
        'apple_m4': 'Apple M4',
        'apple_m4_pro': 'Apple M4 Pro',
        'apple_m4_max': 'Apple M4 Max',
        'qualcomm_8cx_gen4': 'Qualcomm Snapdragon 8cx Gen 4',
        'qualcomm_8cx_gen3': 'Qualcomm Snapdragon 8cx Gen 3',
        'qualcomm_7c_gen3': 'Qualcomm Snapdragon 7c Gen 3',
        'qualcomm_7c_plus_gen3': 'Qualcomm Snapdragon 7c+ Gen 3',
        'qualcomm_x_elite': 'Qualcomm Snapdragon X Elite',
        'qualcomm_x_plus': 'Qualcomm Snapdragon X Plus'
    }
    
    return display_names.get(series_code, series_code.replace('_', ' ').title())


def process_cpu_icons(input_dir: str, output_file: str) -> List[Dict]:
    """
    处理 CPU 图标并生成数据
    
    Args:
        input_dir: 输入图片文件夹路径
        output_file: 输出 JSON 文件路径
    
    Returns:
        List[Dict]: 处理后的 CPU 系列数据
    """
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"输入文件夹不存在: {input_dir}")
    
    cpu_series_data = []
    
    # 支持的图片格式
    supported_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
    
    # 遍历文件夹中的图片文件
    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)
        
        # 跳过非文件和非图片文件
        if not os.path.isfile(file_path):
            continue
        
        ext = os.path.splitext(file_name)[1].lower()
        if ext not in supported_extensions:
            continue
        
        # 从文件名生成系列代码（去掉扩展名）
        series_code = os.path.splitext(file_name)[0]
        
        # 生成云存储路径
        cloud_path = f"icons/cpu/{file_name}"
        
        # 模拟上传文件
        icon_cloud_id = upload_file(file_path, cloud_path)
        
        # 获取品牌色和显示名称
        bg_color = get_brand_color(series_code)
        display_name = get_display_name(series_code)
        
        # 构建数据结构
        series_data = {
            'series_code': series_code,
            'display_name': display_name,
            'icon_cloud_id': icon_cloud_id,
            'bg_color': bg_color
        }
        
        cpu_series_data.append(series_data)
        print(f"处理完成: {series_code} -> {display_name}")
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 生成 JSON 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cpu_series_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n处理完成！")
    print(f"共处理 {len(cpu_series_data)} 个 CPU 系列图标")
    print(f"数据已保存到: {output_file}")
    
    return cpu_series_data


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='CPU 图标管理脚本')
    parser.add_argument('--input', type=str, default='./cpu_icons', 
                        help='输入图片文件夹路径')
    parser.add_argument('--output', type=str, default='./output/cpu_series_data.json', 
                        help='输出 JSON 文件路径')
    
    args = parser.parse_args()
    
    try:
        process_cpu_icons(args.input, args.output)
    except Exception as e:
        print(f"错误: {e}")
        exit(1)


if __name__ == '__main__':
    main()
