# 硬件助手 - 开发规范文档

> Development Standards for Hardware Assistant

**文档版本**：v1.0.0  
**创建日期**：2026-02-06  
**最后更新**：2026-02-06  
**规范负责人**：硬件助手开发团队

---

## 1. 编码规范

### 1.1 TypeScript 规范

#### 1.1.1 严格模式
```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictPropertyInitialization": true
  }
}
```

**强制要求**：
- ✅ 禁止使用 `any` 类型
- ✅ 所有函数参数必须明确类型
- ✅ 所有返回值必须明确类型
- ✅ 使用 `unknown` 替代 `any`

#### 1.1.2 类型定义

**✅ 推荐**：
```typescript
// 使用接口定义对象类型
interface CpuSpecs {
  cores: string;
  baseClock: number;
  boostClock: number;
}

// 使用类型别名定义联合类型
type HardwareType = 'cpu' | 'gpu' | 'phone';

// 使用泛型提高复用性
function useCloudData<T>(collectionName: string): {
  list: Ref<T[]>;
  loading: Ref<boolean>;
}
```

**❌ 禁止**：
```typescript
// 禁止使用 any
function processData(data: any) { }

// 禁止隐式 any
function getItem(id) { }

// 禁止使用 Object 类型
function updateObject(obj: Object) { }
```

### 1.2 Vue 3 组件规范

#### 1.2.1 Composition API

**✅ 推荐写法**：
```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import type { CpuSpecs } from '@/types/hardware';

// Props 定义
interface Props {
  id: string;
  type: 'cpu' | 'gpu' | 'phone';
}
const props = defineProps<Props>();

// Emits 定义
const emit = defineEmits<{
  (e: 'update', value: string): void;
  (e: 'delete', id: string): void;
}>();

// 响应式数据
const hardware = ref<CpuSpecs | null>(null);
const loading = ref(false);

// 计算属性
const displayName = computed(() => {
  return hardware.value ? `${hardware.value.brand} ${hardware.value.model}` : '';
});

// 生命周期
onMounted(() => {
  loadData();
});

// 方法
const loadData = async () => {
  loading.value = true;
  try {
    // 加载数据逻辑
  } finally {
    loading.value = false;
  }
};
</script>
```

#### 1.2.2 组件命名规范

| 类型 | 命名规则 | 示例 |
|------|---------|------|
| 组件名称 | PascalCase | `HardwareCard.vue` |
| 组件文件夹 | kebab-case | `hardware-card/` |
| Composable | use 前缀 + camelCase | `useCloudData.ts` |
| Store | camelCase | `compare.ts` |

### 1.3 命名规范

#### 1.3.1 变量命名

```typescript
// 变量：camelCase
const hardwareList = [];
const isLoading = false;

// 常量：UPPER_SNAKE_CASE
const MAX_COMPARE_COUNT = 2;
const API_BASE_URL = 'https://api.example.com';

// 私有变量：下划线前缀（可选）
const _internalCache = new Map();

// 布尔值：is/has/can 前缀
const isActive = true;
const hasError = false;
const canEdit = true;
```

#### 1.3.2 函数命名

```typescript
// 普通函数：camelCase，动词开头
function loadData() { }
function calculateScore() { }
function validateInput() { }

// 事件处理函数：handle 前缀
function handleClick() { }
function handleInputChange() { }

// 工具函数：动词 + 名词
function formatDate() { }
function parseJSON() { }
```

### 1.4 注释规范

#### 1.4.1 JSDoc 注释

```typescript
/**
 * 查询硬件列表
 * @param collection - 集合名称
 * @param options - 查询选项
 * @param options.skip - 跳过的记录数
 * @param options.limit - 限制返回数量
 * @returns 硬件列表和总数
 * @throws {Error} 当集合名称无效时抛出错误
 */
async function queryHardwareList<T>(
  collection: string,
  options: {
    skip?: number;
    limit?: number;
  }
): Promise<{ data: T[]; total: number }> {
  // 实现代码
}
```

#### 1.4.2 代码注释

```typescript
// ✅ 推荐：解释"为什么"
// 使用 Set 存储收藏 ID，提高查找性能
const favoriteIds = new Set<string>();

// ✅ 推荐：复杂逻辑的说明
// 移动端 CPU 判断逻辑：
// 1. Socket 包含 BGA（焊接式接口）
// 2. 型号包含 Mobile/Laptop 关键词
// 3. 型号以 H/U/Y 等移动端后缀结尾
const isMobile = socket.includes('BGA') || 
                 model.includes('MOBILE') ||
                 /[0-9]\s*(H|U|Y)(\s|$)/.test(model);

// ❌ 禁止：显而易见的注释
// 设置 loading 为 true
loading.value = true;
```

---

## 2. Git 工作流规范

### 2.1 分支管理

```
main                    # 主分支，保持稳定
  ├── develop           # 开发分支
  │   ├── feature/xxx   # 功能分支
  │   ├── bugfix/xxx    # Bug修复分支
  │   └── refactor/xxx  # 重构分支
  └── hotfix/xxx        # 紧急修复分支
```

### 2.2 提交信息规范

#### 2.2.1 提交格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### 2.2.2 Type 类型

| Type | 说明 | 示例 |
|------|------|------|
| feat | 新功能 | `feat(ranking): 添加CPU子选项过滤功能` |
| fix | Bug修复 | `fix(detail): 修复性能评分计算错误` |
| docs | 文档更新 | `docs: 更新API文档` |
| style | 代码格式调整 | `style: 格式化代码` |
| refactor | 重构 | `refactor(compare): 重构对比逻辑` |
| perf | 性能优化 | `perf(list): 优化列表渲染性能` |
| test | 测试 | `test(utils): 添加工具函数单元测试` |
| chore | 构建/工具变动 | `chore: 更新依赖包` |

#### 2.2.3 提交示例

```bash
# 新功能
git commit -m "feat(ranking): 添加CPU桌面/移动筛选功能

- 添加activeCpuSubTab响应式变量
- 实现基于Socket和型号的移动端判断逻辑
- 添加子选项过滤UI组件
- 更新rankingList计算属性

Closes #123"

# Bug修复
git commit -m "fix(detail): 修复详情页加载失败问题

当硬件ID不存在时，详情页会白屏。
现在改为显示友好的错误提示。

Fixes #456"
```

### 2.3 代码审查规范

#### 2.3.1 审查清单

**代码质量**：
- [ ] 代码符合 TypeScript 严格模式
- [ ] 没有使用 `any` 类型
- [ ] 函数复杂度合理（单个函数 < 50 行）
- [ ] 没有重复代码（DRY 原则）

**功能完整性**：
- [ ] 功能符合需求文档
- [ ] 边界情况已处理
- [ ] 错误处理完善
- [ ] 用户提示友好

**性能**：
- [ ] 没有性能瓶颈
- [ ] 列表使用分页或虚拟滚动
- [ ] 使用 computed 缓存计算结果

**测试**：
- [ ] 核心功能有单元测试
- [ ] 测试覆盖率 ≥ 80%
- [ ] 所有测试通过

---

## 3. 测试规范

### 3.1 单元测试

#### 3.1.1 测试框架
```json
{
  "devDependencies": {
    "vitest": "^0.34.0",
    "@vue/test-utils": "^2.4.0"
  }
}
```

#### 3.1.2 测试示例

```typescript
// useCloudData.test.ts
import { describe, it, expect, vi } from 'vitest';
import { useCloudData } from '@/composables/useCloudData';

describe('useCloudData', () => {
  it('应该正确初始化状态', () => {
    const { list, loading, finished } = useCloudData('cpu_collection');
    
    expect(list.value).toEqual([]);
    expect(loading.value).toBe(false);
    expect(finished.value).toBe(false);
  });
  
  it('应该正确加载数据', async () => {
    const { list, loading, refresh } = useCloudData('cpu_collection');
    
    await refresh();
    
    expect(loading.value).toBe(false);
    expect(list.value.length).toBeGreaterThan(0);
  });
  
  it('应该处理错误情况', async () => {
    const { error, refresh } = useCloudData('invalid_collection');
    
    await refresh();
    
    expect(error.value).toBeTruthy();
  });
});
```

### 3.2 测试覆盖率要求

| 模块 | 覆盖率要求 |
|------|-----------|
| Composables | ≥ 80% |
| Stores | ≥ 80% |
| Utils | ≥ 90% |
| Components | ≥ 70% |

---

## 4. 文档规范

### 4.1 代码文档

#### 4.1.1 文件头部注释

```typescript
/**
 * @file useCloudData.ts
 * @description 云数据访问 Composable，提供统一的数据访问接口
 * @author 硬件助手开发团队
 * @date 2026-02-06
 */
```

#### 4.1.2 模块导出注释

```typescript
/**
 * 云数据访问 Composable
 * 
 * 功能：
 * - 统一数据访问接口
 * - 支持分页加载
 * - 支持搜索功能
 * - 智能错误处理
 * - 自动降级到本地数据
 * 
 * @example
 * ```typescript
 * const { list, loading, refresh } = useCloudData<CpuSpecs>('cpu_collection');
 * await refresh();
 * ```
 * 
 * @param collectionName - 云数据库集合名称
 * @param options - 查询选项
 * @returns 响应式数据和方法
 */
export function useCloudData<T>(...) { }
```

### 4.2 README 文档

每个模块目录应包含 README.md 文件：

```markdown
# 模块名称

## 功能说明
简要描述模块的功能和用途。

## 使用方法
\`\`\`typescript
// 代码示例
\`\`\`

## API 文档
### 函数名称
- 参数说明
- 返回值说明
- 使用示例

## 注意事项
需要特别注意的地方。
```

---

## 5. 性能规范

### 5.1 性能指标

| 指标 | 目标 | 测试方法 |
|------|------|---------|
| 首屏加载时间 | < 2s | Lighthouse |
| 页面切换时间 | < 500ms | Performance API |
| 搜索响应时间 | < 300ms | Console.time |
| 列表滚动帧率 | ≥ 60fps | Chrome DevTools |

### 5.2 性能优化清单

**前端优化**：
- [ ] 使用分页加载（每页 20 条）
- [ ] 使用骨架屏优化加载体验
- [ ] 使用 computed 缓存计算结果
- [ ] 避免不必要的重新渲染
- [ ] 图片使用懒加载

**数据库优化**：
- [ ] 为常用字段创建索引
- [ ] 只查询需要的字段
- [ ] 使用聚合查询减少请求次数
- [ ] 实现数据缓存机制

---

## 6. 安全规范

### 6.1 输入验证

```typescript
// ✅ 推荐：验证所有用户输入
function validateSearchKeyword(keyword: string): boolean {
  // 长度验证
  if (!keyword || keyword.length > 50) return false;
  
  // 特殊字符过滤
  const dangerousChars = /[<>'"&]/;
  if (dangerousChars.test(keyword)) return false;
  
  return true;
}
```

### 6.2 数据访问权限

```json
// 云数据库权限配置
{
  "permissions": {
    "read": true,
    "write": false,
    "create": false,
    "delete": false
  }
}
```

---

## 7. 错误处理规范

### 7.1 错误处理层级

```typescript
// 第一层：页面层
try {
  await loadData();
} catch (error) {
  uni.showToast({
    title: '数据加载失败',
    icon: 'error'
  });
}

// 第二层：Composable 层
const loadData = async () => {
  try {
    return await fetchFromCloud();
  } catch (error) {
    console.error('云数据加载失败', error);
    return await fetchFromLocal();
  }
};

// 第三层：数据访问层
const fetchFromCloud = async () => {
  try {
    const result = await db.collection('cpu_collection').get();
    return result.data;
  } catch (error) {
    throw new Error('云数据库访问失败');
  }
};
```

### 7.2 错误信息规范

```typescript
// ✅ 推荐：友好的错误提示
uni.showToast({
  title: '网络连接失败，请检查网络设置',
  icon: 'error'
});

// ❌ 禁止：技术性错误提示
uni.showToast({
  title: 'Error: ECONNREFUSED at TCPConnectWrap',
  icon: 'error'
});
```

---

## 8. 代码审查清单

### 8.1 提交前自检

**代码质量**：
- [ ] 代码通过 TypeScript 类型检查
- [ ] 代码通过 ESLint 检查
- [ ] 没有 console.log 调试代码
- [ ] 没有未使用的导入和变量

**功能完整性**：
- [ ] 功能符合需求
- [ ] 边界情况已处理
- [ ] 错误提示友好
- [ ] 加载状态完善

**性能**：
- [ ] 没有明显的性能问题
- [ ] 列表使用分页或虚拟滚动
- [ ] 计算属性使用 computed

**测试**：
- [ ] 核心功能有单元测试
- [ ] 所有测试通过
- [ ] 测试覆盖率达标

---

## 9. 持续集成规范

### 9.1 CI/CD 流程

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: pnpm install
      - run: pnpm run type-check
      - run: pnpm run lint
      - run: pnpm run test
      - run: pnpm run build
```

---

## 10. 变更日志

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-02-06 | 初始版本创建 | 开发团队 |

---

## 11. 参考资料

- [TypeScript 官方文档](https://www.typescriptlang.org/)
- [Vue 3 风格指南](https://cn.vuejs.org/style-guide/)
- [ESLint 规则](https://eslint.org/docs/rules/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**文档结束**
