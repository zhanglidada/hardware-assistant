# CPU 图标获取工具集

## 📚 文件说明

### 1. CPU_ICON_GUIDE.md
完整的 CPU 图标获取指南，包括：
- 为什么自动爬取困难
- 推荐的手动获取方法
- 官方资源链接
- 版权注意事项

### 2. organize_cpu_icons.py
图标整理工具，功能包括：
- 批量转换为 PNG 格式
- 统一尺寸（512x512）
- 添加透明背景
- 自动居中

### 3. fetch_cpu_assets_direct.py
直接下载脚本（需要有效 URL）

### 4. fetch_cpu_assets_v2.py
使用 icrawler 的爬虫版本（受反爬虫限制）

## 🚀 快速开始

### 方案 A：推荐方式（手动 + 脚本）

1. **手动下载图标**
   ```bash
   # 从官方网站或图标库手动下载 CPU 徽标
   # 保存到任意目录，如 Downloads/cpu_icons/
   ```

2. **使用整理脚本**
   ```bash
   cd /Users/zhangli/hardware-assistant/skills/scripts
   python organize_cpu_icons.py ~/Downloads/cpu_icons/ organized_icons/
   ```

3. **重命名文件**
   ```bash
   # 在 organized_icons/ 目录中按规范重命名
   # intel_i9.png, amd_r9.png, apple_m1.png 等
   ```

### 方案 B：使用浏览器扩展

1. 安装 [Image Downloader](https://chrome.google.com/webstore/detail/image-downloader/cnpniohnfphhjihaiiggeabnkjhpaldj)
2. Google 图片搜索 "Intel Core i9 logo png"
3. 使用扩展批量下载
4. 运行 `organize_cpu_icons.py` 整理

## 📋 命名规范

```
Intel 系列：
  intel_i9.png
  intel_i7.png
  intel_i5.png
  intel_i3.png

AMD 系列：
  amd_r9.png
  amd_r7.png
  amd_r5.png
  amd_r3.png

Apple 系列：
  apple_m1.png
  apple_m2.png
  apple_m3.png
  apple_m4.png
```

## 🔧 工具使用

### organize_cpu_icons.py

**交互模式：**
```bash
python organize_cpu_icons.py
# 然后按提示输入目录路径
```

**命令行模式：**
```bash
# 使用默认输出目录
python organize_cpu_icons.py <输入目录>

# 指定输出目录
python organize_cpu_icons.py <输入目录> <输出目录>
```

**示例：**
```bash
# 整理 Downloads 中的图片到 organized_icons
python organize_cpu_icons.py ~/Downloads/cpu_icons organized_icons

# 查看结果
ls -lh organized_icons/
```

## 📐 图标要求

- **格式**：PNG（透明背景）
- **尺寸**：512x512 像素
- **分辨率**：72 DPI 或更高
- **背景**：透明（RGBA）
- **质量**：无压缩损失

## 🌐 推荐资源

### 官方网站
- Intel 品牌中心：https://www.intel.com/content/www/us/en/brand-experience/brand-center.html
- AMD 品牌资源：https://www.amd.com/en/partner/resources/brand-guidelines.html
- Apple 新闻稿：https://www.apple.com/newsroom/

### 图标库
- Brands of the World：https://www.brandsoftheworld.com/
- Wikimedia Commons：https://commons.wikimedia.org/
- Seek Logo：https://seeklogo.com/

### 在线工具
- 格式转换：https://cloudconvert.com/
- 背景移除：https://www.remove.bg/
- 尺寸调整：https://www.iloveimg.com/resize-image

## ⚠️ 常见问题

### Q: 为什么不能自动爬取？
A: 搜索引擎有反爬虫机制，且涉及版权问题。手动获取更可靠、合法。

### Q: icrawler 为什么会失败？
A: Google/Bing 会检测并阻止自动化访问。建议使用手动方式。

### Q: 可以用 AI 生成图标吗？
A: 可以作为临时方案，但最好使用官方素材以保证一致性和专业性。

### Q: 图标太小怎么办？
A: 优先寻找矢量格式（SVG/EPS），或使用 AI 工具放大（如 waifu2x）。

## 📝 版权声明

- Intel®, Core™ 是 Intel Corporation 的商标
- AMD®, Ryzen™ 是 Advanced Micro Devices, Inc. 的商标
- Apple®, M1/M2/M3/M4 是 Apple Inc. 的商标

使用这些图标时请遵守相应的品牌使用准则。

## 🔗 相关文档

- [详细获取指南](CPU_ICON_GUIDE.md)
- [项目主文档](../../README.md)
- [数据抓取指南](README_RYZEN_SCRAPER.md)

## 💡 最佳实践

1. ✅ **优先使用官方素材**
2. ✅ **保持高质量**（至少 512x512）
3. ✅ **使用透明背景**
4. ✅ **统一命名规范**
5. ❌ **避免低分辨率图片**
6. ❌ **避免带水印的图片**

---

**总结**：手动获取 + 脚本整理是最可靠的方案，预计耗时 1 小时。
