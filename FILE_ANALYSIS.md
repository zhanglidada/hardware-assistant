# 📁 项目文件功能说明

## 概述

本项目采用分层架构设计，每个文件都有明确的职责和功能。以下是项目中所有关键文件的详细说明。

## Data Schema

### `src/types/hardware.ts`
**类型**: TypeScript Type Definitions
**描述**: 硬件数据类型定义
**主要职责**:
- 定义CPU/GPU/手机数据结构
- 类型安全保证
- 接口契约定义
- 数据验证基础
**定义接口**:
- `BaseHardware`
- `CpuSpecs`
- `GpuSpecs`
- `PhoneSpecs`

## Data Access Layer

### `src/composables/useCloudData.ts`
**类型**: TypeScript Composable
**描述**: 云数据库数据访问Hook
**主要职责**:
- 统一数据获取接口
- 分页加载实现
- 错误处理和降级
- 搜索功能支持
- 本地缓存策略

## State Management

### `src/stores/compare.ts`
**类型**: TypeScript Store
**描述**: 硬件对比状态管理
**主要职责**:
- 对比项状态管理
- 对比逻辑实现
- 状态持久化
- 对比规则验证

## Page Component

### `src/pages/index/index.vue`
**类型**: Vue Component
**描述**: 页面主组件 - index页面
**主要职责**:
- 页面UI渲染
- 用户交互处理
- 数据绑定和展示
- 组件生命周期管理

### `src/pages/detail/index.vue`
**类型**: Vue Component
**描述**: 页面主组件 - detail页面
**主要职责**:
- 页面UI渲染
- 用户交互处理
- 数据绑定和展示
- 组件生命周期管理

### `src/pages/compare/index.vue`
**类型**: Vue Component
**描述**: 页面主组件 - compare页面
**主要职责**:
- 页面UI渲染
- 用户交互处理
- 数据绑定和展示
- 组件生命周期管理

## Application Component

### `src/App.vue`
**类型**: Vue Component
**描述**: 应用组件
**主要职责**:
- 应用初始化和配置
- 全局状态管理
- 云环境初始化

## Debug Component

### `src/pages/debug/index.vue`
**类型**: Vue Component
**描述**: 调试页面组件
**主要职责**:
- 云数据库状态检查
- 数据加载测试
- 环境诊断
- 问题排查工具

## Mock Data

### `src/mock/cpu_data.json`
**类型**: JSON Data
**描述**: CPU硬件模拟数据
**主要职责**:
- 本地开发数据支持
- 云数据库降级数据
- 数据类型验证参考
- 测试数据源

### `src/mock/gpu_data.json`
**类型**: JSON Data
**描述**: GPU硬件模拟数据
**主要职责**:
- 本地开发数据支持
- 云数据库降级数据
- 数据类型验证参考
- 测试数据源

### `src/mock/phone_data.json`
**类型**: JSON Data
**描述**: 手机硬件模拟数据
**主要职责**:
- 本地开发数据支持
- 云数据库降级数据
- 数据类型验证参考
- 测试数据源

## Data Scraper

### `scripts/scrapers/cpu.py`
**类型**: Python Script
**描述**: CPU数据采集脚本
**主要职责**:
- 从数据源采集硬件信息
- 数据清洗和格式化
- 生成结构化JSON数据
- 数据质量验证

### `scripts/scrapers/gpu.py`
**类型**: Python Script
**描述**: GPU数据采集脚本
**主要职责**:
- 从数据源采集硬件信息
- 数据清洗和格式化
- 生成结构化JSON数据
- 数据质量验证

### `scripts/scrapers/phone.py`
**类型**: Python Script
**描述**: 手机数据采集脚本
**主要职责**:
- 从数据源采集硬件信息
- 数据清洗和格式化
- 生成结构化JSON数据
- 数据质量验证

## Data Transformer

### `scripts/convert_to_jsonl.py`
**类型**: Python Script
**描述**: 数据格式转换脚本
**主要职责**:
- JSON到JSONL格式转换
- 数据批量处理
- 格式标准化
- 导入准备

### `scripts/convert_json.js`
**类型**: JavaScript Utility
**描述**: JSON转换工具
**主要职责**:
- JSON格式转换
- 数据批量处理
- 命令行工具
- 格式验证

## Data Cleaner

### `scripts/fix_json_for_cloud.py`
**类型**: Python Script
**描述**: JSON数据修复脚本
**主要职责**:
- 修复JSON格式问题
- 转换日期格式为ISODate
- 添加唯一_id字段
- 确保云数据库兼容性

### `scripts/fix_original_json.py`
**类型**: Python Script
**描述**: 原始JSON修复脚本
**主要职责**:
- 修复原始数据格式问题
- 数据标准化处理
- 质量检查
- 备份管理

## Database Manager

### `scripts/update_db.py`
**类型**: Python Script
**描述**: 数据库更新脚本
**主要职责**:
- 批量数据导入
- 数据库集合管理
- 数据版本控制
- 备份和恢复

## Debug Tool

### `scripts/debug_cloud_db.js`
**类型**: JavaScript Utility
**描述**: 云数据库调试工具
**主要职责**:
- 环境状态检查
- 数据库连接测试
- 集合状态验证
- 问题诊断和报告

## Diagnostic Tool

### `scripts/quick_diagnosis.js`
**类型**: JavaScript Utility
**描述**: 快速诊断工具
**主要职责**:
- 一键系统诊断
- 错误检测和报告
- 解决方案建议
- 控制台友好输出

## CSS Fix

### `src/styles/fix-font-loading.scss`
**类型**: SCSS Stylesheet
**描述**: 字体加载修复样式
**主要职责**:
- 解决外部字体加载问题
- 系统字体回退
- @font-face规则覆盖
- 微信小程序兼容性

## UI Framework

### `src/styles/wot-design-uni.scss`
**类型**: SCSS Stylesheet
**描述**: UI组件库样式配置
**主要职责**:
- 组件库样式定制
- 主题变量配置
- 样式覆盖和扩展
- 设计系统集成

## Framework Styles

### `src/uni.scss`
**类型**: SCSS Stylesheet
**描述**: Uni-app框架样式变量
**主要职责**:
- 全局样式变量定义
- 主题颜色系统
- 尺寸和间距规范
- 响应式设计基础

## Project Configuration

### `package.json`
**类型**: JSON Configuration
**描述**: 项目依赖和脚本配置
**主要职责**:
- 依赖包管理
- 脚本命令定义
- 项目元数据
- 构建配置

## Routing Configuration

### `src/pages.json`
**类型**: JSON Configuration
**描述**: 页面路由配置
**主要职责**:
- 页面路径定义
- 导航栏配置
- 页面样式设置
- 组件自动导入规则

## App Configuration

### `src/manifest.json`
**类型**: JSON Configuration
**描述**: 应用清单配置
**主要职责**:
- 应用基本信息
- 权限配置
- 平台特定设置
- 版本信息

## Build Configuration

### `vite.config.ts`
**类型**: TypeScript Configuration
**描述**: Vite构建工具配置
**主要职责**:
- 构建流程配置
- 插件系统集成
- 开发服务器设置
- 路径别名配置

### `tsconfig.json`
**类型**: JSON Configuration
**描述**: TypeScript编译配置
**主要职责**:
- 编译目标设置
- 模块解析配置
- 类型检查规则
- 路径别名定义

## Coding Standards

### `.clinerules`
**类型**: Configuration File
**描述**: 项目编码规范和架构标准
**主要职责**:
- 技术栈规范定义
- 编码标准强制执行
- 架构设计原则
- 开发工作流规范

## Version Control

### `.gitignore`
**类型**: Configuration File
**描述**: Git忽略规则配置
**主要职责**:
- 忽略不需要版本控制的文件
- 保护敏感信息
- 优化仓库大小
- 避免冲突文件

## Entry Point

### `index.html`
**类型**: HTML File
**描述**: 应用HTML入口文件
**主要职责**:
- 应用根HTML结构
- 元数据定义
- 资源引入
- PWA支持基础

## Type Declarations

### `src/env.d.ts`
**类型**: TypeScript Declaration
**描述**: 环境类型声明
**主要职责**:
- 模块类型扩展
- 环境变量类型定义
- 第三方库类型补充

### `shims-uni.d.ts`
**类型**: TypeScript Declaration
**描述**: 类型声明补充文件
**主要职责**:
- 模块类型扩展
- 全局类型定义
- 第三方库类型补充
- 环境兼容性

## Test Script

### `scripts/test_scraper.py`
**类型**: Python Script
**描述**: 数据采集测试脚本
**主要职责**:
- 采集功能测试
- 数据质量验证
- 性能测试
- 错误处理测试

## Utility Script

### `scripts/convert_to_jsonl.py`
**类型**: Python Script
**描述**: 数据格式转换脚本
**主要职责**:
- JSON到JSONL格式转换
- 数据批量处理
- 格式标准化
- 导入准备

## Utility

### `scripts/analyze_project.py`
**类型**: Python Script
**描述**: 项目分析脚本
**主要职责**:
- 项目文件功能分析
- 文档自动生成
- 代码质量检查
- 架构验证
