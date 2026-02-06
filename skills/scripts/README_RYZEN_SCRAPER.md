# AMD Ryzen 处理器数据抓取工具

## 功能说明

从维基百科 [List of AMD Ryzen processors](https://en.wikipedia.org/wiki/List_of_AMD_Ryzen_processors) 页面抓取所有 AMD Ryzen 处理器的详细参数数据。

## 使用方法

### 1. 安装依赖

```bash
cd /Users/zhangli/hardware-assistant/skills/scripts
# 如果遇到 SSL 证书错误，请使用 --trusted-host 参数
pip install --trusted-host pypi.tuna.tsinghua.edu.cn --trusted-host files.pythonhosted.org pandas lxml html5lib
```

### 2. 运行脚本

```bash
python fetch_amd_ryzen_wiki.py
```

### 3. 查看输出

脚本会自动创建 `output` 目录并生成以下文件：

- **ryzen_raw_{timestamp}.json** - 原始数据（包含表格索引）
- **ryzen_simplified_{timestamp}.json** - 简化数据（仅包含处理器参数）
- **ryzen_summary_{timestamp}.json** - 汇总信息

## 输出数据示例

### 汇总信息 (ryzen_summary_*.json)

```json
{
  "total_records": 365,
  "tables_count": 46,
  "timestamp": "20260205_073403",
  "source_url": "https://en.wikipedia.org/wiki/List_of_AMD_Ryzen_processors"
}
```

### 处理器数据 (ryzen_simplified_*.json)

```json
[
  {
    "Branding and Model - Branding and Model": "Ryzen 7",
    "Branding and Model - Branding and Model.1": "1800X[2]",
    "Cores (threads) - Cores (threads)": "8 (16)",
    "Clock rate (GHz) - Base": 3.6,
    "Clock rate (GHz) - PBO 1–2 (≥3)": "4.0 (3.7)",
    "L3 cache (total) - L3 cache (total)": "16 MB",
    "TDP - TDP": "95 W",
    "Release date - Release date": "March 2, 2017",
    "Launch price[a] - Launch price[a]": "US $499"
  }
]
```

## 数据统计

- **总记录数**: 365 条
- **表格数量**: 46 个
- **数据覆盖**: 
  - Ryzen 1000 系列（Zen）
  - Ryzen 2000 系列（Zen+）
  - Ryzen 3000 系列（Zen 2）
  - Ryzen 4000 系列（Zen 2 APU）
  - Ryzen 5000 系列（Zen 3/Zen 3+）
  - Ryzen 7000 系列（Zen 4）
  - Ryzen 9000 系列（Zen 5）
  - Threadripper 系列
  - PRO 系列

## 数据字段说明

维基百科表格中的主要字段包括：

- **Branding and Model**: 品牌和型号
- **Cores (threads)**: 核心数（线程数）
- **Clock rate (GHz)**: 时钟频率（基础/加速）
- **L3 cache**: 三级缓存
- **TDP**: 热设计功耗
- **Release date**: 发布日期
- **Launch price**: 发布价格

## 技术实现

### 核心技术

1. **pandas.read_html()** - 自动解析 HTML 表格
2. **User-Agent 伪装** - 避免被维基百科拒绝访问
3. **SSL 证书绕过** - 处理本地证书验证问题
4. **数据清洗** - 自动处理 NaN 值和元组键名

### 关键代码

```python
# 设置 User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 ...'
}

# 获取 HTML 内容
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as response:
    html_content = response.read().decode('utf-8')

# 解析表格
tables = pd.read_html(StringIO(html_content))
```

## 后续处理建议

### 1. 数据清洗

- 移除引用标记（如 `[2]`、`[a]` 等）
- 统一单位格式（GHz、MB、W）
- 解析核心配置（如 `8 (16)` → cores: 8, threads: 16）
- 解析价格信息（如 `US $499` → currency: USD, price: 499）

### 2. 数据转换

```python
import json
import re

def clean_model_name(name):
    """移除引用标记"""
    return re.sub(r'\[.*?\]', '', name).strip()

def parse_cores_threads(value):
    """解析核心/线程数"""
    match = re.match(r'(\d+)\s*\((\d+)\)', value)
    if match:
        return {'cores': int(match.group(1)), 'threads': int(match.group(2))}
    return None

# 读取数据
with open('output/ryzen_simplified_*.json') as f:
    data = json.load(f)

# 清洗数据
for item in data:
    if 'Branding and Model - Branding and Model.1' in item:
        item['model'] = clean_model_name(item['Branding and Model - Branding and Model.1'])
    
    if 'Cores (threads) - Cores (threads)' in item:
        item.update(parse_cores_threads(item['Cores (threads) - Cores (threads)']))
```

### 3. 导入数据库

```python
# 转换为标准格式
processors = []
for item in data:
    processor = {
        'brand': 'AMD',
        'series': 'Ryzen',
        'model': clean_model_name(item.get('Branding and Model - Branding and Model.1', '')),
        'cores': parse_cores_threads(item.get('Cores (threads) - Cores (threads)', '')),
        'base_clock': item.get('Clock rate (GHz) - Base'),
        'cache_l3': item.get('L3 cache (total) - L3 cache (total)'),
        'tdp': item.get('TDP - TDP'),
        'release_date': item.get('Release date - Release date'),
        'launch_price': item.get('Launch price[a] - Launch price[a]')
    }
    processors.append(processor)
```

## 注意事项

1. **网络访问**: 需要能够访问维基百科
2. **证书问题**: macOS 可能需要安装 Python 证书
3. **数据更新**: 维基百科数据会不断更新，建议定期重新抓取
4. **字段变化**: 不同系列的表格字段可能略有差异

## 故障排查

### SSL 证书错误

```bash
# 安装 Python 证书（macOS）
/Applications/Python\ 3.*/Install\ Certificates.command
```

### 403 Forbidden 错误

脚本已内置 User-Agent 伪装，如仍遇到问题：
1. 检查网络连接
2. 尝试使用 VPN
3. 更新 User-Agent 字符串

### ImportError

```bash
pip install --trusted-host pypi.tuna.tsinghua.edu.cn pandas lxml html5lib
```

## 相关资源

- [维基百科 - AMD Ryzen 处理器列表](https://en.wikipedia.org/wiki/List_of_AMD_Ryzen_processors)
- [Pandas 文档 - read_html](https://pandas.pydata.org/docs/reference/api/pandas.read_html.html)
- [项目主文档](../../README.md)
