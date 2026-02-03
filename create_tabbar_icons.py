#!/usr/bin/env python3
"""
创建微信小程序tabBar占位图标
生成简单的PNG图标文件
"""

from PIL import Image, ImageDraw
import os

# 创建tabbar目录
tabbar_dir = "src/static/tabbar"
os.makedirs(tabbar_dir, exist_ok=True)

# 图标配置
icons = [
    {"name": "home", "text": "H", "color": (153, 153, 153), "active_color": (0, 113, 197)},
    {"name": "ranking", "text": "R", "color": (153, 153, 153), "active_color": (0, 113, 197)},
    {"name": "compare", "text": "C", "color": (153, 153, 153), "active_color": (0, 113, 197)},
    {"name": "mine", "text": "A", "color": (153, 153, 153), "active_color": (0, 113, 197)},
]

# 图标尺寸（微信小程序推荐尺寸）
size = (50, 50)

for icon in icons:
    # 创建普通状态图标
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制圆形背景
    draw.ellipse([5, 5, 45, 45], fill=icon["color"])
    
    # 绘制文字
    # 这里简单起见，我们只保存一个空白图标，实际使用时需要替换为真实图标
    img.save(f"{tabbar_dir}/{icon['name']}.png")
    
    # 创建激活状态图标
    img_active = Image.new('RGBA', size, (255, 255, 255, 0))
    draw_active = ImageDraw.Draw(img_active)
    
    # 绘制圆形背景（激活状态）
    draw_active.ellipse([5, 5, 45, 45], fill=icon["active_color"])
    
    # 绘制文字
    img_active.save(f"{tabbar_dir}/{icon['name']}-active.png")

print(f"已创建占位图标到 {tabbar_dir}/")
print("注意：这些是占位图标，实际使用时需要替换为真实图标文件")