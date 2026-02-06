# CPU 图标获取指南

## 问题说明

自动从搜索引擎爬取图标面临以下困难：
1. **反爬虫机制**：Google/Bing 等搜索引擎有严格的反爬虫策略
2. **动态加载**：现代网站多使用 JavaScript 动态加载图片
3. **URL 失效**：直接图片链接经常变更或失效
4. **版权问题**：自动下载可能涉及版权风险

## 推荐方案：手动获取 + 脚本整理

### 方案 A：从官方网站获取（推荐）

#### Intel 图标
1. 访问 [Intel 品牌资源中心](https://www.intel.com/content/www/us/en/brand-experience/brand-center.html)
2. 或访问 [Intel 新闻稿资源](https://www.intel.com/content/www/us/en/newsroom.html)
3. 下载对应系列的徽标（i9, i7, i5, i3）

#### AMD 图标
1. 访问 [AMD 品牌资源](https://www.amd.com/en/partner/resources/brand-guidelines.html)
2. 或从产品页面获取：https://www.amd.com/en/products/processors/desktops/ryzen.html
3. 下载 Ryzen 9/7/5/3 系列徽标

#### Apple 图标
1. 访问 [Apple 新闻稿](https://www.apple.com/newsroom/)
2. 搜索 M1/M2/M3/M4 相关新闻
3. 从新闻图片中提取芯片图标

### 方案 B：使用浏览器扩展（最简单）

1. **安装浏览器扩展**
   - Chrome/Edge: [Image Downloader](https://chrome.google.com/webstore/detail/image-downloader/cnpniohnfphhjihaiiggeabnkjhpaldj)
   - Firefox: [Download All Images](https://addons.mozilla.org/en-US/firefox/addon/download-all-images/)

2. **搜索并下载**
   ```
   # 在 Google 图片搜索以下关键词：
   - "Intel Core i9 logo png transparent"
   - "AMD Ryzen 9 badge png"
   - "Apple M1 chip icon png"
   ```

3. **使用扩展批量下载**
   - 点击扩展图标
   - 筛选最小尺寸（如 200x200）
   - 批量下载到本地

### 方案 C：使用专业图标网站

1. **Brands of the World** - https://www.brandsoftheworld.com/
   - 搜索 "Intel Core" 或 "AMD Ryzen"
   - 下载矢量格式（SVG/EPS）
   - 使用 Illustrator 或在线工具转换为 PNG

2. **Wikimedia Commons** - https://commons.wikimedia.org/
   ```
   搜索关键词：
   - "Intel Core logo"
   - "AMD Ryzen logo"
   ```

3. **Seek Logo** - https://seeklogo.com/
   - 提供各种品牌的高质量 logo
   - 支持 SVG/PNG 下载

## 自动化脚本使用（需手动收集 URL）

### 步骤 1：准备图片 URL 列表

创建文件 `cpu_icon_urls.txt`：
```
# Intel i9
https://example.com/intel-i9-badge.png

# AMD Ryzen 9
https://example.com/amd-ryzen-9-logo.png

... 更多 URL
```

### 步骤 2：使用下载脚本

```python
#!/usr/bin/env python3
import requests
import os

def download_from_url_list(url_file, output_dir="cpu_icons"):
    os.makedirs(output_dir, exist_ok=True)
    
    with open(url_file) as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    for i, url in enumerate(urls, 1):
        filename = f"icon_{i:02d}.png"
        filepath = os.path.join(output_dir, filename)
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ 下载成功: {filename}")
        except Exception as e:
            print(f"❌ 下载失败 {url}: {e}")

# 使用示例
download_from_url_list('cpu_icon_urls.txt')
```

## 图标整理脚本

一旦手动下载了图标，使用以下脚本整理：

```bash
cd /Users/zhangli/hardware-assistant/skills/scripts
python organize_cpu_icons.py
```

该脚本会：
1. 扫描下载目录中的所有图片
2. 转换为 PNG 格式
3. 统一尺寸（可选）
4. 按命名规范重命名

## 命名规范

```
intel_i9.png       # Intel Core i9
intel_i7.png       # Intel Core i7
intel_i5.png       # Intel Core i5
intel_i3.png       # Intel Core i3
amd_r9.png         # AMD Ryzen 9
amd_r7.png         # AMD Ryzen 7
amd_r5.png         # AMD Ryzen 5
amd_r3.png         # AMD Ryzen 3
apple_m1.png       # Apple M1
apple_m2.png       # Apple M2
apple_m3.png       # Apple M3
apple_m4.png       # Apple M4
```

## 图标要求

- **格式**: PNG（透明背景优先）
- **尺寸**: 至少 200x200 像素（推荐 512x512）
- **分辨率**: 72 DPI 或更高
- **背景**: 透明或纯白色
- **质量**: 清晰、无失真

## 版权注意事项

- ✅ **官方资源**：优先使用品牌方提供的官方素材
- ✅ **编辑用途**：确保在许可范围内使用
- ❌ **商业用途**：避免未授权的商业使用
- ✅ **归属标注**：适当标注来源（Intel®, AMD®, Apple®）

## 常见问题

### Q: 为什么不能自动爬取？
A: 搜索引擎的反爬虫机制、版权限制、动态加载等技术障碍使自动化不可靠。

### Q: 有没有合法的 API？
A: Intel/AMD/Apple 不提供公开的徽标 API。建议从官方素材库手动下载。

### Q: 可以使用 Selenium 吗？
A: 可以，但会显著增加复杂度和运行时间，且仍可能被检测。

### Q: 推荐的在线工具？
A: 
- **格式转换**: https://cloudconvert.com/
- **背景移除**: https://www.remove.bg/
- **尺寸调整**: https://www.iloveimg.com/resize-image

## 替代方案：生成简化图标

如果无法获取官方图标，可以生成简化版：

```python
from PIL import Image, ImageDraw, ImageFont

def create_text_badge(text, filename, size=512):
    """创建文字徽章作为临时图标"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制背景圆形
    draw.ellipse([10, 10, size-10, size-10], fill='#0071c5', outline='white', width=5)
    
    # 添加文字
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size//4)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size - text_width) // 2, (size - text_height) // 2)
    draw.text(position, text, fill='white', font=font)
    
    img.save(filename)
    print(f"✅ 生成: {filename}")

# 使用示例
create_text_badge("i9", "intel_i9.png")
create_text_badge("R9", "amd_r9.png")
```

## 总结

**最佳实践**：
1. 从官方网站手动下载高质量图标
2. 使用浏览器扩展辅助批量下载
3. 用脚本统一格式和命名
4. 如无法获取，生成简化版临时使用

**时间估算**：
- 手动搜索下载：30-60 分钟
- 整理和重命名：10 分钟
- 总计：约 1 小时

这比调试复杂的爬虫系统更高效、更可靠。
