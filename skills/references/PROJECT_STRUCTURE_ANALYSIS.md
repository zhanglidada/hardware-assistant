# 硬件助手 - 项目结构详解

> 深度分析项目的目录结构、核心文件和代码组织

## 项目概述

**硬件助手 (Hardware Assistant)** 是一个专业的硬件参数查询与对比微信小程序，采用现代化的前端架构和严格的类型系统。

## 目录结构概览

```
hardware-assistant/
├── 📁 src/                        # 源代码目录
│   ├── 📁 types/                  # TypeScript 类型定义
│   ├── 📁 composables/            # 组合式函数（业务逻辑）
│   ├── 📁 stores/                 # Pinia 状态管理
│   ├── 📁 pages/                  # 页面组件
│   ├── 📁 mock/                   # 本地模拟数据
│   ├── 📁 styles/                 # 样式文件
│   ├── 📁 utils/                  # 工具函数
│   ├── 📁 static/                 # 静态资源
│   ├── 📄 App.vue                 # 应用根组件
│   ├── 📄 main.ts                 # 应用入口
│   ├── 📄 pages.json              # 页面路由配置
│   └── 📄 manifest.json           # 应用配置
├── 📁 skills/                     # 项目文档
│   ├── 📄 SKILLS.md              # 技术能力清单
│   ├── 📄 ARCHITECTURE.md        # 系统架构文档
│   ├── 📁 references/            # 参考文档
│   └── 📁 scripts/               # 数据管道脚本
├── 📄 package.json               # 依赖管理
├── 📄 vite.config.ts             # Vite 构建配置
├── 📄 tsconfig.json              # TypeScript 配置
└── 📄 README.md                  # 项目说明
```

## 核心文件详解

### 1. 类型定义层 (`src/types/`)

#### `src/types/hardware.ts` ⭐⭐⭐⭐⭐

**职责**: 定义全局数据契约

**核心接口**:
```typescript
BaseHardware        // 硬件基础接口
├─ CpuSpecs        // CPU 规格
├─ GpuSpecs        // GPU 规格
└─ PhoneSpecs      // 手机规格
```

**特性**:
- 使用继承复用基础字段
- 品牌联合类型定义
- 完整的 JSDoc 注释
- TypeScript 严格模式

**为什么重要**: 
- 作为前后端通信契约
- 确保数据结构一致性
- 提供 IDE 智能提示
- 编译时类型检查

### 2. 数据访问层 (`src/composables/`)

#### `src/composables/useCloudData.ts` ⭐⭐⭐⭐⭐

**职责**: 统一数据访问接口

**核心功能**:
- 分页加载（每页20条）
- 搜索与筛选
- 排序支持
- 错误处理
- 智能降级

**架构模式**: Read-Through 缓存

```
用户请求 → 云数据库 → 成功返回
          ↓ 失败
     本地数据 → 返回数据 + 提示
```

**核心算法**:
1. 检查云开发环境
2. 尝试云数据库查询
3. 失败时降级到本地数据
4. 应用相同的查询逻辑
5. 返回统一格式数据

**为什么重要**:
- 抽象数据访问复杂性
- 保证应用始终可用
- 统一错误处理逻辑
- 支持多种数据源

### 3. 状态管理层 (`src/stores/`)

#### `src/stores/compare.ts` ⭐⭐⭐⭐

**职责**: 管理硬件对比状态

**核心状态**:
```typescript
{
  cpuList: CompareItem[]      // CPU 对比列表
  gpuList: CompareItem[]      // GPU 对比列表
  phoneList: CompareItem[]    // 手机对比列表
}
```

**核心操作**:
- `toggleCompare()` - 切换对比状态
- `removeCompareItem()` - 移除对比项
- `clearCompare()` - 清空对比列表
- `canStartPK` - 检查是否可对比

**业务规则**:
- 同类硬件最多对比 2 个
- 不同类硬件不能对比
- 自动去重处理

**为什么重要**:
- 跨页面状态同步
- 业务规则封装
- 类型安全操作

### 4. 页面组件层 (`src/pages/`)

#### `src/pages/index/index.vue` - 首页 ⭐⭐⭐⭐⭐

**功能**: 硬件列表展示和搜索

**UI 特性**:
- 硬件分类标签页（CPU/GPU/手机）
- 搜索框（型号、品牌筛选）
- 硬件卡片展示
- 骨架屏加载
- 上拉加载更多
- 下拉刷新
- 对比浮动栏

**数据流**:
```
用户操作 → useCloudData → 云数据库/本地数据 → 响应式列表 → UI 更新
```

**代码组织**:
- `<script setup>` - 逻辑代码
- `<template>` - 模板结构
- `<style scoped>` - 样式定义

#### `src/pages/detail/index.vue` - 详情页 ⭐⭐⭐⭐

**功能**: 硬件详细规格展示

**UI 特性**:
- 品牌主题色
- 规格参数列表
- 价格与发布日期
- 添加到对比按钮

**数据来源**:
- URL 参数传递 ID
- onLoad 生命周期获取数据
- 类型守卫判断硬件类型

#### `src/pages/compare/index.vue` - 对比页 ⭐⭐⭐⭐

**功能**: 硬件横向对比

**UI 特性**:
- 左右分栏对比
- 参数差异展示
- 清空对比按钮
- 空状态引导

**数据来源**:
- Pinia Store（compare.ts）
- 响应式状态更新

#### `src/pages/debug/index.vue` - 调试页 ⭐⭐⭐

**功能**: 云数据库诊断工具

**检查项**:
- 云环境状态
- 集合存在性
- 数据加载测试
- 错误信息展示

**为什么重要**:
- 快速定位问题
- 降低调试难度
- 提升开发效率

### 5. Mock 数据层 (`src/mock/`)

**文件**:
- `cpu_data.json` - CPU 模拟数据
- `gpu_data.json` - GPU 模拟数据
- `phone_data.json` - 手机模拟数据
- `json.d.ts` - JSON 类型声明

**为什么重要**:
- 本地开发不依赖云数据库
- 降级方案的数据来源
- 测试数据标准化

### 6. 样式层 (`src/styles/`)

**文件**:
- `wot-design-uni.scss` - UI 组件库样式
- `fix-font-loading.scss` - 字体加载修复
- `uni.scss` - 全局样式变量

**样式组织**:
- 使用 SCSS 预处理器
- 支持 `rpx` 响应式单位
- 全局样式变量统一管理

### 7. 配置文件

#### `vite.config.ts` ⭐⭐⭐⭐

**核心配置**:
```typescript
{
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@wot-design/uni': '...'  // UI 库路径别名
    }
  }
}
```

**为什么重要**:
- 解决 UI 库样式导入问题
- 简化模块导入路径
- 优化构建性能

#### `tsconfig.json` ⭐⭐⭐⭐

**核心配置**:
```json
{
  "compilerOptions": {
    "strict": true,           // 严格模式
    "types": ["@dcloudio/types"],
    "resolveJsonModule": true // 支持 JSON 导入
  }
}
```

**为什么重要**:
- 启用 TypeScript 严格检查
- 配置类型声明
- 优化编译选项

#### `pages.json` ⭐⭐⭐⭐

**核心配置**:
```json
{
  "pages": [
    {"path": "pages/index/index"},
    {"path": "pages/detail/index"},
    {"path": "pages/compare/index"},
    {"path": "pages/debug/index"}
  ],
  "tabBar": {
    "list": [...]
  }
}
```

**为什么重要**:
- 定义页面路由
- 配置底部导航
- 设置页面样式

## 数据管道 (`skills/scripts/`)

### 采集器 (`scrapers/`)

**模块**:
- `cpu.py` - CPU 数据采集
- `gpu.py` - GPU 数据采集
- `phone.py` - 手机数据采集

**统一接口**:
```python
def run() -> List[Dict]:
    """返回标准化的硬件数据列表"""
    pass
```

### 数据处理脚本

**核心脚本**:
- `update_db.py` - 主控制器，协调更新
- `convert_to_jsonl.py` - 格式转换
- `fix_json_for_cloud.py` - 云数据库优化

**备份机制**:
- `backups/` - 按日期组织备份
- 每次更新前自动备份
- 支持历史版本恢复

## 代码组织原则

### 1. 分层架构
```
展示层 (Pages)
    ↓
业务逻辑层 (Composables)
    ↓
状态管理层 (Stores)
    ↓
类型定义层 (Types)
    ↓
数据层 (Cloud DB / Mock)
```

### 2. 单一职责
- 每个文件职责明确
- 函数功能单一
- 组件解耦

### 3. 命名规范
- 组件文件: PascalCase
- Composable: `useXxx` 前缀
- Store: `xxxStore` 后缀
- 类型: `XxxSpecs` / `XxxInterface`

### 4. 关注点分离
- 数据访问 → Composable
- 状态管理 → Store
- UI 渲染 → Page Component
- 类型定义 → Types

## 项目特点总结

### 1. 类型安全
- TypeScript 严格模式
- 零 `any` 类型
- 完整类型定义

### 2. 模块化设计
- 高内聚低耦合
- 可复用组件
- 清晰的依赖关系

### 3. 工程化标准
- 统一的代码规范
- 完善的文档注释
- 标准的项目结构

### 4. 可维护性
- 清晰的代码组织
- 完整的类型系统
- 详细的文档说明

---

**相关文档**:
- [系统架构](../ARCHITECTURE.md) - 架构设计详解
- [技术能力清单](../SKILLS.md) - 技术亮点总结
- [项目状态](./PROJECT_STATUS.md) - 功能完成情况

#### `src/pages/detail/index.vue` - 详情页
**功能**: 硬件详细参数展示
**UI特性**:
- 渐变头部设计
- 参数表格展示
- 性能雷达图可视化
- 加入对比功能

#### `src/pages/compare/index.vue` - 对比页
**功能**: 多硬件参数对比
**UI特性**:
- 表格化对比视图
- 参数差异高亮
- 可视化评分系统

#### `src/pages/debug/index.vue` - 调试页
**功能**: 系统诊断和测试
**UI特性**:
- 环境状态检查
- 云数据库测试工具
- 本地数据验证
- 问题诊断报告

### 5. 数据层 (`src/mock/`)

#### 本地数据文件
- `cpu_data.json`: 12条CPU数据，涵盖Intel和AMD历代产品
- `gpu_data.json`: 5条GPU数据，涵盖NVIDIA和AMD最新显卡
- `phone_data.json`: 5条手机数据，涵盖主流品牌旗舰机型

**数据特点**:
- 结构化JSON格式，符合`hardware.ts`类型定义
- 包含历史数据和最新产品
- 价格单位为人民币
- 发布日期为ISO格式

## 🛠️ 数据管道系统 (`scripts/`)

### 1. 数据采集层 (`scripts/scrapers/`)

#### `cpu.py`, `gpu.py`, `phone.py`
**功能**: 从数据源采集硬件信息
**技术栈**: Python + Requests/BeautifulSoup
**工作流程**:
1. 访问硬件评测网站或官方数据源
2. 解析HTML/JSON数据
3. 提取结构化信息
4. 保存为原始JSON文件

### 2. 数据清洗层

#### `scripts/fix_json_for_cloud.py`
**功能**: 修复JSON数据格式，适配云数据库
**关键处理**:
- 转换日期格式为MongoDB ISODate格式
- 添加唯一`_id`字段
- 确保字段类型一致性
- 处理特殊字符和编码

#### `scripts/fix_original_json.py`
**功能**: 修复原始数据格式问题
**关键处理**:
- 标准化字段命名
- 统一单位系统
- 数据去重和验证
- 生成备份文件

### 3. 数据转换层

#### `scripts/convert_to_jsonl.py`
**功能**: JSON转JSONL格式
**目的**: 适配云数据库批量导入
**输出格式**: 每行一个完整的JSON对象

#### `scripts/convert_json.js`
**功能**: JSON格式转换工具
**特点**: Node.js实现，支持命令行操作

### 4. 数据库管理层

#### `scripts/update_db.py`
**功能**: 批量更新云数据库
**工作流程**:
1. 读取JSONL格式数据
2. 连接微信云数据库
3. 批量插入或更新数据
4. 生成导入报告

### 5. 调试工具层

#### `scripts/debug_cloud_db.js`
**功能**: 云数据库调试工具
**特性**:
- 环境状态检查
- 集合存在性验证
- 数据查询测试
- 错误诊断报告

#### `scripts/quick_diagnosis.js`
**功能**: 快速系统诊断
**特性**:
- 一键式诊断
- 问题分类和优先级
- 解决方案建议
- 控制台友好输出

## 🎨 样式系统 (`src/styles/`)

### 1. `src/styles/wot-design-uni.scss`
**功能**: UI组件库样式定制
**定制内容**:
- 品牌颜色主题
- 组件样式覆盖
- 响应式断点
- 动画效果

### 2. `src/styles/fix-font-loading.scss`
**功能**: 字体加载问题修复
**问题背景**: 微信小程序无法加载外部字体
**解决方案**:
- 使用系统字体回退
- 覆盖`@font-face`规则
- 确保文字可读性

### 3. `src/uni.scss`
**功能**: Uni-app框架样式变量
**定义内容**:
- 颜色系统
- 间距系统
- 字体系统
- 边框圆角

## ⚙️ 配置文件详解

### 1. `.clinerules` - 项目编码规范
**重要性**: ⭐⭐⭐⭐⭐
**内容分类**:
- **技术栈规范**: Uni-app + Vue 3 + TypeScript
- **编码标准**: 禁止使用`any`类型，必须定义接口
- **架构原则**: 逻辑分离，View层只负责UI
- **小程序约束**: 禁止DOM API，使用Uni-app API
- **工作流程**: Git提交规范，代码审查标准

### 2. `package.json` - 依赖管理
**关键依赖**:
- `@dcloudio/uni-app`: 跨端开发框架
- `vue`: 3.4.21版本，使用Composition API
- `typescript`: 4.9.5版本，严格模式
- `pinia`: 状态管理库
- `wot-design-uni`: UI组件库

**脚本命令**:
- `dev:mp-weixin`: 微信小程序开发模式
- `build:mp-weixin`: 生产构建
- `type-check`: TypeScript类型检查

### 3. `vite.config.ts` - 构建配置
**配置特性**:
- Uni-app插件集成
- 路径别名配置
- 开发服务器设置
- 构建优化选项

### 4. `tsconfig.json` - TypeScript配置
**严格模式设置**:
- `strict: true`
- `noImplicitAny: true`
- `strictNullChecks: true`
- 路径别名映射

### 5. `src/pages.json` - 页面路由
**配置内容**:
- 页面路径定义
- 导航栏样式
- 页面样式配置
- 组件自动导入规则

### 6. `src/manifest.json` - 应用配置
**配置内容**:
- 应用名称和描述
- 权限配置
- 平台特定设置
- 版本信息

## 🔄 数据流架构

### 1. 用户界面层
```
用户操作 → 页面组件 → 调用Composables → 更新Store状态 → 重新渲染UI
```

### 2. 数据获取层
```
页面加载 → useCloudData Hook → 检查云环境 → 云数据库查询 → 成功返回数据
                                      ↓
                               失败 → 错误处理 → 降级到本地数据 → 返回数据
```

### 3. 状态管理流
```
用户添加对比 → compareStore.toggleCompare() → 更新Pinia状态 → 持久化到本地存储
                                      ↓
                               页面监听状态变化 → 更新UI显示
```

## 🛡️ 错误处理机制

### 多层错误处理策略

#### 第一层：云数据库错误分类
```typescript
const errorLower = errorMessage.toLowerCase()
const isCollectionError = errorLower.includes('collection') || 
                         errorLower.includes('不存在') ||
                         errorLower.includes('not exist')
const isPermissionError = errorLower.includes('permission') || 
                         errorLower.includes('权限')
const isEnvError = errorLower.includes('环境') || 
                  errorLower.includes('env')
const isOrderByError = errorLower.includes('orderby') || 
                      errorLower.includes('排序') ||
                      errorLower.includes('index')
```

#### 第二层：优雅降级
1. **集合不存在**: 显示错误，使用本地数据
2. **权限问题**: 显示错误，使用本地数据
3. **排序字段错误**: 尝试无排序查询
4. **其他错误**: 显示通用错误提示

#### 第三层：用户反馈
- Toast提示错误信息
- 空状态页面展示
- 重试按钮提供
- 调试页面链接

## 📱 微信小程序适配

### 1. API适配
- 使用`uni.`前缀的跨端API
- 避免使用`window`, `document`等浏览器API
- 使用`wx.cloud`进行云开发

### 2. 样式适配
- 使用`rpx`单位进行响应式设计
- 考虑安全区域（iPhone刘海屏）
- 适配小程序组件样式

### 3. 性能优化
- 图片懒加载
- 数据分页加载
- 组件按需引入
- 避免过大的初始包体积

## 🧪 测试策略

### 1. 类型测试
- TypeScript严格模式
- 接口定义完整性检查
- 类型兼容性验证

### 2. 数据测试
- JSON Schema验证
- 数据格式一致性检查
- 边界条件测试

### 3. 集成测试
- 云数据库连接测试
- 页面跳转测试
- 状态管理测试

### 4. 用户体验测试
- 加载状态测试
- 错误处理测试
- 响应式设计测试

## 🚀 部署流程

### 1. 开发环境
```bash
pnpm install
pnpm dev:mp-weixin
# 在微信开发者工具中打开dist/dev/mp-weixin
```

### 2. 生产构建
```bash
pnpm build:mp-weixin
# 上传dist/build/mp-weixin到微信公众平台
```

### 3. 数据更新
```bash
# 运行数据管道
python scripts/scrapers/cpu.py
python scripts/convert_to_jsonl.py
python scripts/fix_json_for_cloud.py
python scripts/update_db.py
```

## 📈 项目演进路线

### 已完成
- ✅ 基础架构搭建
- ✅ 类型系统定义
- ✅ 数据访问层实现
- ✅ 核心页面开发
- ✅ 数据管道系统
- ✅ 错误处理机制
- ✅ 现代化UI设计

### 进行中
- 🔄 性能优化
- 🔄 测试覆盖
- 🔄 文档完善

### 规划中
- 📋 更多硬件品类
- 📋 用户系统
- 📋 社区功能
- 📋 AI推荐

## 🎯 架构设计原则

### 1. 类型安全优先
- 所有数据都有明确的类型定义
## 项目特点总结

### 1. 类型安全
- TypeScript 严格模式
- 零 `any` 类型
- 完整类型定义

### 2. 模块化设计
- 高内聚低耦合
- 可复用组件
- 清晰的依赖关系

### 3. 工程化标准
- 统一的代码规范
- 完善的文档注释
- 标准的项目结构

### 4. 可维护性
- 清晰的代码组织
- 完整的类型系统
- 详细的文档说明

---

**相关文档**:
- [系统架构](../ARCHITECTURE.md) - 架构设计详解
- [技术能力清单](../SKILLS.md) - 技术亮点总结
- [项目状态](./PROJECT_STATUS.md) - 功能完成情况
