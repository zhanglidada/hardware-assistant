# 硬件助手 - 规范驱动开发文档体系

> 本目录包含硬件助手项目的完整开发规范文档，采用规范驱动开发（Specification-Driven Development, SDD）方法论

## 📚 文档导航

### 核心文档
| 文档 | 说明 | 状态 |
|------|------|------|
| [01-PRD.md](./01-PRD.md) | 产品需求文档 | ✅ |
| [02-DESIGN-SYSTEM.md](./02-DESIGN-SYSTEM.md) | UI/UX 设计系统 | ✅ |
| [03-ARCHITECTURE.md](./03-ARCHITECTURE.md) | 系统架构设计 | ✅ |
| [04-DEVELOPMENT-STANDARDS.md](./04-DEVELOPMENT-STANDARDS.md) | 开发规范 | ✅ |
| [05-TASKS.md](./05-TASKS.md) | 任务分解与里程碑 | ✅ |

### 参考文档
- [../SDD.md](../SDD.md) - 综合规范驱动开发文档（原版）
- [../skills/SKILLS.md](../skills/SKILLS.md) - 技术能力清单
- [../PROJECT_ARCHITECTURE_ANALYSIS.md](../PROJECT_ARCHITECTURE_ANALYSIS.md) - 项目架构分析

## 🎯 规范驱动开发（SDD）方法论

### 什么是 SDD？
规范驱动开发是一种**先定义规范、后编写代码**的开发方法论，强调：
1. **需求先行**：在编码前明确产品需求和用户故事
2. **设计优先**：先设计系统架构和接口规范
3. **标准约束**：用开发规范约束代码实现
4. **质量保证**：通过测试和审查确保符合规范

### SDD 的优势
- ✅ **减少返工**：避免因需求不明确导致的重复开发
- ✅ **提高质量**：规范约束确保代码质量
- ✅ **团队协作**：文档化的规范降低沟通成本
- ✅ **可维护性**：清晰的架构和规范便于后期维护

## 📖 文档使用指南

### 开发前
1. 阅读 [01-PRD.md](./01-PRD.md) 了解产品需求和用户故事
2. 阅读 [02-DESIGN-SYSTEM.md](./02-DESIGN-SYSTEM.md) 了解 UI/UX 设计规范
3. 阅读 [03-ARCHITECTURE.md](./03-ARCHITECTURE.md) 了解系统架构

### 开发中
1. 遵循 [04-DEVELOPMENT-STANDARDS.md](./04-DEVELOPMENT-STANDARDS.md) 的编码规范
2. 参考 [05-TASKS.md](./05-TASKS.md) 跟踪开发进度
3. 定期 Code Review 确保符合规范

### 开发后
1. 编写测试用例验证功能
2. 更新文档记录变更
3. 进行代码审查

## 🔄 文档更新流程

### 何时更新文档？
- 新增功能或修改需求时 → 更新 PRD
- UI/UX 设计变更时 → 更新 DESIGN-SYSTEM
- 架构调整时 → 更新 ARCHITECTURE
- 编码规范变更时 → 更新 DEVELOPMENT-STANDARDS
- 任务计划调整时 → 更新 TASKS

### 如何更新文档？
1. 在对应文档中添加变更内容
2. 在文档末尾的**变更日志**中记录变更
3. 更新文档版本号
4. 提交 Git Commit 并注明文档变更

## 🏗️ 文档结构说明

### 01-PRD.md（产品需求文档）
定义产品的功能需求、用户画像、用户故事和验收标准
- 用户画像和使用场景
- 功能需求列表（带优先级）
- 用户故事和验收标准
- 非功能需求（性能、安全等）

### 02-DESIGN-SYSTEM.md（设计系统）
定义 UI/UX 设计规范，确保界面一致性
- 色彩系统
- 字体系统
- 间距系统
- 组件设计规范
- 交互设计规范

### 03-ARCHITECTURE.md（架构设计）
定义系统的技术架构和模块设计
- 系统架构图
- 模块划分
- 数据模型设计
- 接口设计
- 技术选型

### 04-DEVELOPMENT-STANDARDS.md（开发规范）
定义代码编写、测试、部署的规范
- 编码规范
- Git 工作流规范
- 测试规范
- 部署规范
- 文档规范

### 05-TASKS.md（任务分解）
将需求分解为可执行的任务和里程碑
- 功能模块任务清单
- 开发里程碑
- 任务优先级
- 任务依赖关系

## 📝 文档撰写原则

### SMART 原则
- **Specific**（具体的）：文档内容具体明确
- **Measurable**（可衡量的）：需求和目标可量化
- **Achievable**（可实现的）：技术方案切实可行
- **Relevant**（相关的）：文档内容与项目相关
- **Time-bound**（有时限的）：任务有明确的时间节点

### 文档质量标准
1. **完整性**：覆盖所有关键领域
2. **准确性**：内容准确无误
3. **可读性**：结构清晰、易于理解
4. **可维护性**：便于更新和修改
5. **一致性**：术语和格式统一

## 🔗 相关资源

- [Uni-app 官方文档](https://uniapp.dcloud.net.cn/)
- [Vue 3 官方文档](https://cn.vuejs.org/)
- [TypeScript 官方文档](https://www.typescriptlang.org/)
- [微信小程序开发文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)
- [wot-design-uni 组件库](https://wot-design-uni.netlify.app/)

## 📧 联系方式

如有文档相关问题，请联系项目负责人或在项目 Issue 中提出。

---

**最后更新时间**：2026-02-06  
**文档版本**：v1.0.0  
**维护者**：硬件助手开发团队
