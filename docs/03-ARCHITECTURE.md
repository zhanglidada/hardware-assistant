# 硬件助手 - 系统架构设计文档

> Architecture Design Document for Hardware Assistant

**文档版本**：v1.0.0  
**创建日期**：2026-02-06  
**最后更新**：2026-02-06  
**架构负责人**：硬件助手开发团队

---

## 1. 架构概述

### 1.1 架构目标
- **高可用性**：99.9% 服务可用性，支持降级策略
- **高性能**：首屏加载 < 2s，查询响应 < 100ms
- **可扩展性**：支持新硬件类型快速接入
- **可维护性**：清晰的模块划分，易于维护和迭代

### 1.2 架构原则
1. **分层架构**：表示层、业务层、数据层清晰分离
2. **模块化设计**：高内聚低耦合，便于复用和测试
3. **类型安全**：TypeScript 严格模式，零 `any` 类型
4. **契约优先**：接口定义先于实现
5. **错误优雅**：多层错误处理，友好降级

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户界面层                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  首页    │  │  详情页  │  │  对比页  │  │  排行页  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                     业务逻辑层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Composables  │  │ Pinia Store  │  │ 业务工具函数  │     │
│  │ (useCloudData)│  │ (compare.ts) │  │ (计算、验证)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                      数据访问层                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ 云数据库访问  │  │ 本地数据访问  │  │ 数据转换层    │     │
│  │ (wx.cloud)   │  │ (Mock Data)  │  │ (格式化)     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                       数据源层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ 微信云数据库  │  │ 本地 Mock     │  │ Python 爬虫   │     │
│  │ (主数据源)   │  │ (降级方案)    │  │ (数据采集)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 技术架构图

```
┌─────────────────────────────────────────────────────────────┐
│                       前端技术栈                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Uni-app    │  │    Vue 3     │  │  TypeScript  │     │
│  │   (框架)     │  │ (Composition)│  │  (类型系统)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │    Pinia     │  │ wot-design   │  │     SCSS     │     │
│  │  (状态管理)  │  │   (组件库)    │  │   (样式)     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                       后端技术栈                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │    Python    │  │  微信云开发   │  │   Pandas     │     │
│  │   (数据处理)  │  │  (云数据库)   │  │  (数据清洗)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 模块设计

### 3.1 前端模块划分

#### 3.1.1 页面模块（Pages）

| 模块 | 路径 | 职责 | 依赖 |
|------|------|------|------|
| 首页 | /pages/index | 硬件列表、搜索、分类 | useCloudData |
| 详情页 | /pages/detail | 硬件详细参数展示 | useCloudData, compare Store |
| 对比页 | /pages/compare | 硬件参数对比 | compare Store |
| 排行页 | /pages/ranking | 性能排行榜 | useCloudData |
| 收藏页 | /pages/favorites | 收藏管理 | favorites Store |

#### 3.1.2 Composables 模块

**useCloudData.ts**
```typescript
/**
 * 云数据访问 Composable
 * 功能：统一数据访问接口，支持分页、搜索、排序
 */
export interface CloudDataOptions {
  pageSize?: number;
  searchFields?: string[];
  orderBy?: { field: string; order: 'asc' | 'desc' };
  withCount?: boolean;
}

export function useCloudData<T>(
  collectionName: string,
  options?: CloudDataOptions
) {
  const list = ref<T[]>([]);
  const loading = ref(false);
  const finished = ref(false);
  const error = ref<string | null>(null);
  const total = ref(0);
  
  const refresh = async () => { /* 刷新数据 */ };
  const loadMore = async () => { /* 加载更多 */ };
  const search = async (keyword: string) => { /* 搜索 */ };
  
  return {
    list,
    loading,
    finished,
    error,
    total,
    refresh,
    loadMore,
    search
  };
}
```

#### 3.1.3 Stores 模块

**compare.ts**
```typescript
/**
 * 硬件对比状态管理
 * 功能：管理对比列表，限制对比数量
 */
export const useCompareStore = defineStore('compare', {
  state: () => ({
    cpuList: [] as CompareItem[],
    gpuList: [] as CompareItem[],
    phoneList: [] as CompareItem[]
  }),
  
  getters: {
    totalCount: (state) => {
      return state.cpuList.length + 
             state.gpuList.length + 
             state.phoneList.length;
    },
    canStartPK: (state) => {
      return state.cpuList.length >= 2 || 
             state.gpuList.length >= 2 || 
             state.phoneList.length >= 2;
    }
  },
  
  actions: {
    toggleCompare(item: BaseHardware & { type: string }) {
      // 添加或移除对比项
    },
    removeCompareItem(id: string, type: string) {
      // 移除单个对比项
    },
    clearCompare() {
      // 清空对比列表
    }
  }
});
```

**favorites.ts**
```typescript
/**
 * 收藏状态管理
 * 功能：管理用户收藏列表
 */
export const useFavoritesStore = defineStore('favorites', {
  state: () => ({
    items: [] as FavoriteItem[]
  }),
  
  actions: {
    toggleFavorite(item: BaseHardware) {
      // 添加或移除收藏
    },
    isFavorited(id: string): boolean {
      // 检查是否已收藏
    }
  },
  
  persist: true // 持久化存储
});
```

---

## 4. 数据模型设计

### 4.1 核心数据模型

#### 4.1.1 基础硬件接口

```typescript
/**
 * 硬件基础接口
 * 所有硬件类型的基础属性
 */
export interface BaseHardware {
  id: string;                    // 唯一标识
  brand: string;                 // 品牌
  model: string;                 // 型号
  price: number;                 // 价格（人民币）
  releaseDate: string;           // 发布日期 (YYYY-MM-DD)
  description?: string;          // 描述
}
```

#### 4.1.2 CPU 数据模型

```typescript
/**
 * CPU 规格接口
 * 继承自 BaseHardware
 */
export interface CpuSpecs extends BaseHardware {
  cores: string;                 // 核心配置 (如 "8P+16E")
  baseClock: number;             // 基础频率 (GHz)
  boostClock: number;            // 加速频率 (GHz)
  socket: string;                // 接口类型 (如 LGA1700)
  tdp: number;                   // 热设计功耗 (W)
  integratedGraphics: boolean;   // 是否集成显卡
  cache: number;                 // 缓存大小 (MB)
}
```

#### 4.1.3 GPU 数据模型

```typescript
/**
 * GPU 规格接口
 */
export interface GpuSpecs extends BaseHardware {
  vram: number;                  // 显存 (GB)
  busWidth: number;              // 位宽 (bit)
  cudaCores: number;             // CUDA 核心数
  coreClock: number;             // 核心频率 (MHz)
  boostClock: number;            // 加速频率 (MHz)
  rayTracing: boolean;           // 是否支持光追
}
```

#### 4.1.4 手机数据模型

```typescript
/**
 * 手机规格接口
 */
export interface PhoneSpecs extends BaseHardware {
  ram: number;                   // 内存 (GB)
  storage: number;               // 存储 (GB)
  screenSize: number;            // 屏幕尺寸 (英寸)
  screenResolution: string;      // 屏幕分辨率
  processor: string;             // 处理器型号
  batteryCapacity: number;       // 电池容量 (mAh)
  camera: string;                // 摄像头规格
  os: string;                    // 操作系统
  support5G: boolean;            // 是否支持 5G
}
```

### 4.2 数据库 Schema 设计

#### 4.2.1 集合设计

| 集合名称 | 说明 | 索引 |
|---------|------|------|
| cpu_collection | CPU 数据 | id, brand, model, releaseDate |
| gpu_collection | GPU 数据 | id, brand, model, releaseDate |
| phone_collection | 手机数据 | id, brand, model, releaseDate |
| cpu_series_collection | CPU 系列信息 | series_code |

#### 4.2.2 索引策略

```javascript
// CPU 集合索引
db.cpu_collection.createIndex({
  id: 1,           // 唯一索引
  brand: 1,        // 品牌索引（用于筛选）
  releaseDate: -1  // 发布日期索引（用于排序）
});

// 搜索索引
db.cpu_collection.createIndex({
  model: "text",   // 全文搜索索引
  brand: "text"
});
```

---

## 5. 接口设计

### 5.1 数据访问接口

#### 5.1.1 查询接口

```typescript
/**
 * 查询硬件列表
 * @param collection - 集合名称
 * @param options - 查询选项
 */
async function queryHardwareList<T>(
  collection: string,
  options: {
    skip?: number;
    limit?: number;
    orderBy?: { field: string; order: 'asc' | 'desc' };
    where?: Record<string, any>;
  }
): Promise<{ data: T[]; total: number }> {
  // 实现查询逻辑
}
```

#### 5.1.2 搜索接口

```typescript
/**
 * 搜索硬件
 * @param collection - 集合名称
 * @param keyword - 搜索关键词
 */
async function searchHardware<T>(
  collection: string,
  keyword: string
): Promise<T[]> {
  // 实现搜索逻辑
}
```

### 5.2 状态管理接口

#### 5.2.1 对比操作接口

```typescript
interface CompareStoreActions {
  /**
   * 切换对比状态
   * @returns 操作结果
   */
  toggleCompare(item: BaseHardware & { type: string }): {
    added: boolean;
    message: string;
  };
  
  /**
   * 移除对比项
   */
  removeCompareItem(id: string, type: string): void;
  
  /**
   * 清空对比列表
   */
  clearCompare(): void;
}
```

---

## 6. 数据流设计

### 6.1 查询数据流

```
用户操作（点击、搜索）
    ↓
页面组件触发查询
    ↓
useCloudData Composable
    ↓
检查缓存（可选）
    ↓
云数据库查询
    ↓
数据格式化/转换
    ↓
更新响应式状态
    ↓
界面重新渲染
```

### 6.2 对比数据流

```
用户点击"添加对比"
    ↓
调用 compare Store 的 toggleCompare
    ↓
验证对比数量（最多 2 个）
    ↓
更新 Store 状态
    ↓
Toast 提示操作结果
    ↓
对比页面响应式更新
```

### 6.3 数据更新流程

```
Python 爬虫采集数据
    ↓
数据清洗和验证
    ↓
生成 JSONL 文件
    ↓
备份旧数据（按日期）
    ↓
导入云数据库
    ↓
验证导入结果
    ↓
记录更新日志
    ↓
前端数据刷新
```

---

## 7. 性能优化设计

### 7.1 前端性能优化

#### 7.1.1 分页加载
```typescript
// 每页 20 条数据，上拉加载更多
const PAGE_SIZE = 20;

const loadMore = async () => {
  if (loading.value || finished.value) return;
  
  loading.value = true;
  const result = await queryHardwareList({
    skip: list.value.length,
    limit: PAGE_SIZE
  });
  
  list.value.push(...result.data);
  finished.value = result.data.length < PAGE_SIZE;
  loading.value = false;
};
```

#### 7.1.2 骨架屏加载
```vue
<!-- 骨架屏组件 -->
<wd-skeleton
  v-if="loading && list.length === 0"
  :row="3"
  :row-width="['70%', '50%', '30%']"
/>
```

#### 7.1.3 计算属性缓存
```typescript
// 使用 computed 缓存计算结果
const rankingList = computed(() => {
  return [...list.value]
    .sort((a, b) => getScore(b) - getScore(a))
    .slice(0, 20);
});
```

### 7.2 数据库性能优化

#### 7.2.1 索引优化
```javascript
// 为常用查询字段创建索引
db.cpu_collection.createIndex({ brand: 1, releaseDate: -1 });
```

#### 7.2.2 查询优化
```typescript
// 只查询需要的字段
const result = await db.collection('cpu_collection')
  .field({
    id: true,
    brand: true,
    model: true,
    price: true
    // 不查询 description 等长字段
  })
  .get();
```

---

## 8. 错误处理设计

### 8.1 错误处理策略

#### 8.1.1 多层错误处理
```
页面层错误处理
    ↓
Composable 层错误处理
    ↓
数据访问层错误处理
    ↓
最终降级到本地数据
```

#### 8.1.2 错误恢复机制
```typescript
async function fetchWithFallback<T>(
  fetcher: () => Promise<T>,
  fallback: T
): Promise<T> {
  try {
    return await fetcher();
  } catch (error) {
    console.error('数据获取失败，使用降级数据', error);
    return fallback;
  }
}
```

### 8.2 降级策略

```typescript
// 云数据库不可用时，自动切换到本地数据
const loadData = async () => {
  try {
    // 尝试从云数据库加载
    const data = await loadFromCloud();
    return data;
  } catch (error) {
    // 降级到本地 Mock 数据
    console.warn('云数据库不可用，使用本地数据');
    return loadFromLocal();
  }
};
```

---

## 9. 安全设计

### 9.1 数据访问安全

#### 9.1.1 云数据库权限
```json
{
  "permissions": {
    "read": true,
    "write": false,
    "create": false,
    "delete": false
  }
}
```

#### 9.1.2 输入验证
```typescript
// 搜索关键词验证
function validateSearchKeyword(keyword: string): boolean {
  if (!keyword || keyword.length > 50) return false;
  // 防止 SQL 注入（虽然是 NoSQL，但仍需防范）
  const dangerousChars = /[<>'"&]/;
  return !dangerousChars.test(keyword);
}
```

---

## 10. 扩展性设计

### 10.1 新增硬件类型流程

1. **定义数据模型**：在 `types/hardware.ts` 中定义新接口
2. **创建数据采集脚本**：在 `scripts/scrapers/` 中创建新脚本
3. **配置数据库集合**：创建新的云数据库集合
4. **更新前端页面**：添加新的硬件类型选项
5. **添加测试用例**：确保新功能正常工作

### 10.2 插件化设计（未来）

```typescript
// 插件接口
interface HardwarePlugin {
  type: string;
  schema: Record<string, any>;
  renderCard: (item: BaseHardware) => JSX.Element;
  calculateScore: (item: BaseHardware) => number;
}

// 注册插件
registerHardwarePlugin(cpuPlugin);
registerHardwarePlugin(gpuPlugin);
```

---

## 11. 部署架构

### 11.1 部署环境

```
微信小程序平台
    ↓
├── 前端代码（Uni-app 编译产物）
├── 云函数（可选）
└── 云数据库（主数据源）

本地环境
    ↓
├── Python 数据处理脚本
├── 备份数据（JSON 文件）
└── Mock 数据（本地测试）
```

### 11.2 数据同步流程

```
本地数据处理
    ↓
生成 JSONL 文件
    ↓
备份到本地（按日期）
    ↓
上传到云数据库
    ↓
前端自动刷新
```

---

## 12. 变更日志

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-02-06 | 初始版本创建 | 开发团队 |

---

## 13. 参考资料

- [微信小程序云开发文档](https://developers.weixin.qq.com/miniprogram/dev/wxcloud/basis/getting-started.html)
- [Vue 3 Composition API](https://cn.vuejs.org/guide/extras/composition-api-faq.html)
- [Pinia 状态管理](https://pinia.vuejs.org/)
- [../PROJECT_ARCHITECTURE_ANALYSIS.md](../PROJECT_ARCHITECTURE_ANALYSIS.md)

---

**文档结束**
