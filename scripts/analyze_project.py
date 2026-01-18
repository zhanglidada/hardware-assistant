#!/usr/bin/env python3
"""
项目文件功能分析脚本
分析每个文件的功能和作用，生成文档
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any

def analyze_file(file_path: Path) -> Dict[str, Any]:
    """分析单个文件的功能"""
    rel_path = file_path.relative_to(Path.cwd())
    
    # 根据文件扩展名和路径判断功能
    if file_path.suffix == '.vue':
        return analyze_vue_file(file_path, rel_path)
    elif file_path.suffix == '.ts':
        return analyze_typescript_file(file_path, rel_path)
    elif file_path.suffix == '.json':
        return analyze_json_file(file_path, rel_path)
    elif file_path.suffix == '.py':
        return analyze_python_file(file_path, rel_path)
    elif file_path.suffix == '.js':
        return analyze_javascript_file(file_path, rel_path)
    elif file_path.suffix == '.scss':
        return analyze_scss_file(file_path, rel_path)
    else:
        return analyze_other_file(file_path, rel_path)

def analyze_vue_file(file_path: Path, rel_path: Path) -> Dict[str, Any]:
    """分析Vue文件"""
    name = rel_path.stem
    parent = rel_path.parent.name
    
    if parent == 'index':
        return {
            "path": str(rel_path),
            "type": "Vue Component",
            "category": "Page Component",
            "description": f"页面主组件 - {name}页面",
            "responsibilities": [
                "页面UI渲染",
                "用户交互处理",
                "数据绑定和展示",
                "组件生命周期管理"
            ]
        }
    elif 'debug' in str(rel_path):
        return {
            "path": str(rel_path),
            "type": "Vue Component",
            "category": "Debug Component",
            "description": "调试页面组件",
            "responsibilities": [
                "云数据库状态检查",
                "数据加载测试",
                "环境诊断",
                "问题排查工具"
            ]
        }
    else:
        return {
            "path": str(rel_path),
            "type": "Vue Component",
            "category": "Application Component",
            "description": "应用组件",
            "responsibilities": [
                "应用初始化和配置",
                "全局状态管理",
                "云环境初始化"
            ]
        }

def analyze_typescript_file(file_path: Path, rel_path: Path) -> Dict[str, Any]:
    """分析TypeScript文件"""
    name = rel_path.stem
    
    if 'hardware' in str(rel_path):
        return {
            "path": str(rel_path),
            "type": "TypeScript Type Definitions",
            "category": "Data Schema",
            "description": "硬件数据类型定义",
            "responsibilities": [
                "定义CPU/GPU/手机数据结构",
                "类型安全保证",
                "接口契约定义",
                "数据验证基础"
            ],
            "interfaces": ["BaseHardware", "CpuSpecs", "GpuSpecs", "PhoneSpecs"]
        }
    elif 'useCloudData' in str(rel_path):
        return {
            "path": str(rel_path),
            "type": "TypeScript Composable",
            "category": "Data Access Layer",
            "description": "云数据库数据访问Hook",
            "responsibilities": [
                "统一数据获取接口",
                "分页加载实现",
                "错误处理和降级",
                "搜索功能支持",
                "本地缓存策略"
            ]
        }
    elif 'compare' in str(rel_path):
        return {
            "path": str(rel_path),
            "type": "TypeScript Store",
            "category": "State Management",
            "description": "硬件对比状态管理",
            "responsibilities": [
                "对比项状态管理",
                "对比逻辑实现",
                "状态持久化",
                "对比规则验证"
            ]
        }
    elif 'env.d' in str(rel_path):
        return {
            "path": str(rel_path),
            "type": "TypeScript Declaration",
            "category": "Type Declarations",
            "description": "环境类型声明",
            "responsibilities": [
                "模块类型扩展",
                "环境变量类型定义",
                "第三方库类型补充"
            ]
        }
    else:
        return {
            "path": str(rel_path),
            "type": "TypeScript Configuration",
            "category": "Build Configuration",
            "description": "TypeScript配置",
            "responsibilities": [
                "编译选项配置",
                "类型检查规则",
                "模块解析设置"
            ]
        }

def analyze_json_file(file_path: Path, rel_path: Path) -> Dict[str, Any]:
    """分析JSON文件"""
    name = rel_path.stem
    
    if 'cpu_data' in name or 'gpu_data' in name or 'phone_data' in name:
        return {
            "path": str(rel_path),
            "type": "JSON Data",
            "category": "Mock Data",
            "description": f"{name.split('_')[0].upper()}硬件模拟数据",
            "responsibilities": [
                "本地开发数据支持",
                "云数据库降级数据",
                "数据类型验证参考",
                "测试数据源"
            ]
        }
    elif 'package' in name:
        return {
            "path": str(rel_path),
            "type": "JSON Configuration",
            "category": "Project Configuration",
            "description": "项目依赖和脚本配置",
            "responsibilities": [
                "依赖包管理",
                "脚本命令定义",
                "项目元数据",
                "构建配置"
            ]
        }
    elif 'pages' in name:
        return {
            "path": str(rel_path),
            "type": "JSON Configuration",
            "category": "Routing Configuration",
            "description": "页面路由配置",
            "responsibilities": [
                "页面路径定义",
                "导航栏配置",
                "页面样式设置",
                "组件自动导入规则"
            ]
        }
    elif 'manifest' in name:
        return {
            "path": str(rel_path),
            "type": "JSON Configuration",
            "category": "App Configuration",
            "description": "应用清单配置",
            "responsibilities": [
                "应用基本信息",
                "权限配置",
                "平台特定设置",
                "版本信息"
            ]
        }
    elif 'tsconfig' in name:
        return {
            "path": str(rel_path),
            "type": "JSON Configuration",
            "category": "Build Configuration",
            "description": "TypeScript编译配置",
            "responsibilities": [
                "编译目标设置",
                "模块解析配置",
                "类型检查规则",
                "路径别名定义"
            ]
        }
    else:
        return {
            "path": str(rel_path),
            "type": "JSON Data",
            "category": "Configuration",
            "description": "配置文件",
            "responsibilities": ["配置数据存储"]
        }

def analyze_python_file(file_path: Path, rel_path: Path) -> Dict[str, Any]:
    """分析Python文件"""
    name = rel_path.stem
    
    if 'cpu' in name or 'gpu' in name or 'phone' in name:
        return {
            "path": str(rel_path),
            "type": "Python Script",
            "category": "Data Scraper",
            "description": f"{name.split('_')[0].upper()}数据采集脚本",
            "responsibilities": [
                "从数据源采集硬件信息",
                "数据清洗和格式化",
                "生成结构化JSON数据",
                "数据质量验证"
            ]
        }
    elif 'convert' in name:
        return {
            "path": str(rel_path),
            "type": "Python Script",
            "category": "Data Transformer",
            "description": "数据格式转换脚本",
            "responsibilities": [
                "JSON到JSONL格式转换",
                "数据批量处理",
                "格式标准化",
                "导入准备"
            ]
        }
    elif 'fix_json' in name:
        return {
            "path": str(rel_path),
            "type": "Python Script",
            "category": "Data Cleaner",
            "description": "JSON数据修复脚本",
            "responsibilities": [
                "修复JSON格式问题",
                "转换日期格式为ISODate",
                "添加唯一_id字段",
                "确保云数据库兼容性"
            ]
        }
    elif 'update_db' in name:
        return {
            "path": str(rel_path),
            "type": "Python Script",
            "category": "Database Manager",
            "description": "数据库更新脚本",
            "responsibilities": [
                "批量数据导入",
                "数据库集合管理",
                "数据版本控制",
                "备份和恢复"
            ]
        }
    elif 'test_scraper' in name:
        return {
            "path": str(rel_path),
            "type": "Python Script",
            "category": "Test Script",
            "description": "数据采集测试脚本",
            "responsibilities": [
                "采集功能测试",
                "数据质量验证",
                "性能测试",
                "错误处理测试"
            ]
        }
    else:
        return {
            "path": str(rel_path),
            "type": "Python Script",
            "category": "Utility Script",
            "description": "工具脚本",
            "responsibilities": ["辅助功能实现"]
        }

def analyze_javascript_file(file_path: Path, rel_path: Path) -> Dict[str, Any]:
    """分析JavaScript文件"""
    name = rel_path.stem
    
    if 'debug' in name:
        return {
            "path": str(rel_path),
            "type": "JavaScript Utility",
            "category": "Debug Tool",
            "description": "云数据库调试工具",
            "responsibilities": [
                "环境状态检查",
                "数据库连接测试",
                "集合状态验证",
                "问题诊断和报告"
            ]
        }
    elif 'quick_diagnosis' in name:
        return {
            "path": str(rel_path),
            "type": "JavaScript Utility",
            "category": "Diagnostic Tool",
            "description": "快速诊断工具",
            "responsibilities": [
                "一键系统诊断",
                "错误检测和报告",
                "解决方案建议",
                "控制台友好输出"
            ]
        }
    elif 'convert_json' in name:
        return {
            "path": str(rel_path),
            "type": "JavaScript Utility",
            "category": "Data Transformer",
            "description": "JSON转换工具",
            "responsibilities": [
                "JSON格式转换",
                "数据批量处理",
                "命令行工具",
                "格式验证"
            ]
        }
    else:
        return {
            "path": str(rel_path),
            "type": "JavaScript File",
            "category": "Utility",
            "description": "工具文件",
            "responsibilities": ["功能实现"]
        }

def analyze_scss_file(file_path: Path, rel_path: Path) -> Dict[str, Any]:
    """分析SCSS文件"""
    name = rel_path.stem
    
    if 'fix-font' in name:
        return {
            "path": str(rel_path),
            "type": "SCSS Stylesheet",
            "category": "CSS Fix",
            "description": "字体加载修复样式",
            "responsibilities": [
                "解决外部字体加载问题",
                "系统字体回退",
                "@font-face规则覆盖",
                "微信小程序兼容性"
            ]
        }
    elif 'wot-design' in name:
        return {
            "path": str(rel_path),
            "type": "SCSS Stylesheet",
            "category": "UI Framework",
            "description": "UI组件库样式配置",
            "responsibilities": [
                "组件库样式定制",
                "主题变量配置",
                "样式覆盖和扩展",
                "设计系统集成"
            ]
        }
    elif 'uni' in name:
        return {
            "path": str(rel_path),
            "type": "SCSS Stylesheet",
            "category": "Framework Styles",
            "description": "Uni-app框架样式变量",
            "responsibilities": [
                "全局样式变量定义",
                "主题颜色系统",
                "尺寸和间距规范",
                "响应式设计基础"
            ]
        }
    else:
        return {
            "path": str(rel_path),
            "type": "SCSS Stylesheet",
            "category": "Styles",
            "description": "样式文件",
            "responsibilities": ["样式定义"]
        }

def analyze_other_file(file_path: Path, rel_path: Path) -> Dict[str, Any]:
    """分析其他类型文件"""
    name = rel_path.name
    
    if name == '.clinerules':
        return {
            "path": str(rel_path),
            "type": "Configuration File",
            "category": "Coding Standards",
            "description": "项目编码规范和架构标准",
            "responsibilities": [
                "技术栈规范定义",
                "编码标准强制执行",
                "架构设计原则",
                "开发工作流规范"
            ]
        }
    elif name == 'vite.config.ts':
        return {
            "path": str(rel_path),
            "type": "TypeScript Configuration",
            "category": "Build Configuration",
            "description": "Vite构建工具配置",
            "responsibilities": [
                "构建流程配置",
                "插件系统集成",
                "开发服务器设置",
                "路径别名配置"
            ]
        }
    elif name == '.gitignore':
        return {
            "path": str(rel_path),
            "type": "Configuration File",
            "category": "Version Control",
            "description": "Git忽略规则配置",
            "responsibilities": [
                "忽略不需要版本控制的文件",
                "保护敏感信息",
                "优化仓库大小",
                "避免冲突文件"
            ]
        }
    elif name == 'index.html':
        return {
            "path": str(rel_path),
            "type": "HTML File",
            "category": "Entry Point",
            "description": "应用HTML入口文件",
            "responsibilities": [
                "应用根HTML结构",
                "元数据定义",
                "资源引入",
                "PWA支持基础"
            ]
        }
    elif 'shims' in name:
        return {
            "path": str(rel_path),
            "type": "TypeScript Declaration",
            "category": "Type Declarations",
            "description": "类型声明补充文件",
            "responsibilities": [
                "模块类型扩展",
                "全局类型定义",
                "第三方库类型补充",
                "环境兼容性"
            ]
        }
    else:
        return {
            "path": str(rel_path),
            "type": "Other File",
            "category": "Miscellaneous",
            "description": "其他文件",
            "responsibilities": ["特定功能实现"]
        }

def analyze_directory(root_dir: Path) -> List[Dict[str, Any]]:
    """分析目录结构"""
    analysis = []
    
    for file_path in root_dir.rglob('*'):
        if file_path.is_file():
            # 跳过一些不需要分析的文件
            if any(skip in str(file_path) for skip in [
                'node_modules', '.git', 'dist', 
                'pnpm-lock.yaml', 'PROJECT_STATUS.md'
            ]):
                continue
                
            try:
                file_analysis = analyze_file(file_path)
                analysis.append(file_analysis)
            except Exception as e:
                print(f"分析文件失败 {file_path}: {e}")
    
    return analysis

def categorize_analysis(analysis: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """按类别分类分析结果"""
    categories = {}
    
    for item in analysis:
        category = item.get('category', 'Uncategorized')
        if category not in categories:
            categories[category] = []
        categories[category].append(item)
    
    return categories

def generate_markdown(categories: Dict[str, List[Dict[str, Any]]]) -> str:
    """生成Markdown文档"""
    md_lines = []
    
    md_lines.append("# 📁 项目文件功能说明")
    md_lines.append("")
    md_lines.append("## 概述")
    md_lines.append("")
    md_lines.append("本项目采用分层架构设计，每个文件都有明确的职责和功能。以下是项目中所有关键文件的详细说明。")
    md_lines.append("")
    
    # 按类别组织
    category_order = [
        "Data Schema",
        "Data Access Layer", 
        "State Management",
        "Page Component",
        "Application Component",
        "Debug Component",
        "Mock Data",
        "Data Scraper",
        "Data Transformer",
        "Data Cleaner",
        "Database Manager",
        "Debug Tool",
        "Diagnostic Tool",
        "CSS Fix",
        "UI Framework",
        "Framework Styles",
        "Project Configuration",
        "Routing Configuration",
        "App Configuration",
        "Build Configuration",
        "Coding Standards",
        "Version Control",
        "Entry Point",
        "Type Declarations",
        "Test Script",
        "Utility Script",
        "Utility",
        "Miscellaneous"
    ]
    
    for category in category_order:
        if category in categories:
            md_lines.append(f"## {category}")
            md_lines.append("")
            
            for item in categories[category]:
                md_lines.append(f"### `{item['path']}`")
                md_lines.append("")
                md_lines.append(f"**类型**: {item['type']}")
                md_lines.append("")
                md_lines.append(f"**描述**: {item['description']}")
                md_lines.append("")
                md_lines.append("**主要职责**:")
                for resp in item.get('responsibilities', []):
                    md_lines.append(f"- {resp}")
                
                if 'interfaces' in item:
                    md_lines.append("")
                    md_lines.append("**定义接口**:")
                    for interface in item['interfaces']:
                        md_lines.append(f"- `{interface}`")
                
                md_lines.append("")
    
    return "\n".join(md_lines)

def generate_readme_supplement(categories: Dict[str, List[Dict[str, Any]]], project_root: Path) -> str:
    """生成README补充内容"""
    md_lines = []
    
    md_lines.append("## 📋 文件功能详细说明")
    md_lines.append("")
    md_lines.append("### 核心架构文件")
    md_lines.append("")
    
    # 核心文件分类
    core_categories = [
        "Data Schema",
        "Data Access Layer", 
        "State Management",
        "Project Configuration",
        "Coding Standards"
    ]
    
    for category in core_categories:
        if category in categories:
            md_lines.append(f"#### {category}")
            md_lines.append("")
            for item in categories[category]:
                md_lines.append(f"- **`{item['path']}`**: {item['description']}")
                for resp in item.get('responsibilities', [])[:3]:  # 只显示前3个职责
                    md_lines.append(f"  - {resp}")
            md_lines.append("")
    
    md_lines.append("### 数据管道文件")
    md_lines.append("")
    
    data_categories = [
        "Data Scraper",
        "Data Transformer",
        "Data Cleaner",
        "Database Manager",
        "Mock Data"
    ]
    
    for category in data_categories:
        if category in categories:
            md_lines.append(f"#### {category}")
            md_lines.append("")
            for item in categories[category]:
                md_lines.append(f"- **`{item['path']}`**: {item['description']}")
            md_lines.append("")
    
    md_lines.append("### 页面组件文件")
    md_lines.append("")
    
    page_categories = [
        "Page Component",
        "Application Component",
        "Debug Component"
    ]
    
    for category in page_categories:
        if category in categories:
            md_lines.append(f"#### {category}")
            md_lines.append("")
            for item in categories[category]:
                md_lines.append(f"- **`{item['path']}`**: {item['description']}")
            md_lines.append("")
    
    md_lines.append("### 工具和配置文件")
    md_lines.append("")
    
    tool_categories = [
        "Debug Tool",
        "Diagnostic Tool",
        "CSS Fix",
        "UI Framework",
        "Framework Styles",
        "Routing Configuration",
        "App Configuration",
        "Build Configuration",
        "Version Control",
        "Entry Point",
        "Type Declarations"
    ]
    
    for category in tool_categories:
        if category in categories:
            md_lines.append(f"#### {category}")
            md_lines.append("")
            for item in categories[category]:
                md_lines.append(f"- **`{item['path']}`**: {item['description']}")
            md_lines.append("")
    
    # 保存补充内容
    supplement_file = project_root / "README_SUPPLEMENT.md"
    with open(supplement_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_lines))
    
    print(f"README补充内容已保存到: {supplement_file}")
    
    return "\n".join(md_lines)

def main():
    """主函数"""
    project_root = Path.cwd()
    print(f"分析项目目录: {project_root}")
    
    # 分析项目文件
    analysis = analyze_directory(project_root)
    print(f"分析了 {len(analysis)} 个文件")
    
    # 分类分析结果
    categories = categorize_analysis(analysis)
    print(f"文件分类: {len(categories)} 个类别")
    
    # 生成Markdown
    markdown = generate_markdown(categories)
    
    # 保存到文件
    output_file = project_root / "FILE_ANALYSIS.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"分析结果已保存到: {output_file}")
    
    # 同时生成简化的README补充内容
    generate_readme_supplement(categories, project_root)
    
    return analysis
