<template>
  <view class="page-container">
    <!-- 搜索框 -->
    <view class="search-container">
      <wd-search
        v-model="searchKeyword"
        placeholder="搜索CPU、显卡或手机型号"
        shape="round"
        @search="handleSearch"
        @clear="handleClear"
      />
    </view>

    <!-- Tab 分类 -->
    <wd-tabs v-model="activeTab" class="category-tabs">
      <wd-tab title="CPU" name="cpu"></wd-tab>
      <wd-tab title="显卡" name="gpu"></wd-tab>
      <wd-tab title="手机" name="phone"></wd-tab>
    </wd-tabs>

    <!-- 硬件列表 -->
    <view class="hardware-list">
      <wd-cell-group v-if="filteredHardware.length > 0">
        <wd-cell
          v-for="item in filteredHardware"
          :key="item.id"
          class="hardware-card"
          @click="handleCardClick(item)"
        >
          <template #title>
            <view class="card-content">
              <!-- 左侧品牌标识 -->
              <view class="brand-logo" :class="getBrandClass(item.brand)">
                {{ getBrandShortName(item.brand) }}
              </view>
              
              <!-- 右侧信息 -->
              <view class="hardware-info">
                <view class="model">{{ item.model }}</view>
                <view class="specs">
                  <text v-if="activeTab === 'cpu'">
                    {{ (item as CpuSpecs).cores }} 核心 · 
                    {{ (item as CpuSpecs).baseClock }}-{{ (item as CpuSpecs).boostClock }}GHz · 
                    {{ (item as CpuSpecs).tdp }}W
                  </text>
                  <text v-else-if="activeTab === 'gpu'">
                    {{ (item as GpuSpecs).vram }}GB · 
                    {{ (item as GpuSpecs).busWidth }}bit · 
                    {{ (item as GpuSpecs).cudaCores }}核心
                  </text>
                  <text v-else>
                    {{ (item as PhoneSpecs).ram }}GB RAM · 
                    {{ (item as PhoneSpecs).storage }}GB 存储 · 
                    {{ (item as PhoneSpecs).screenSize }}英寸
                  </text>
                </view>
                <view class="price">¥{{ item.price.toLocaleString() }}</view>
                
                <!-- 对比按钮 -->
                <view class="compare-action">
                  <wd-button 
                    type="primary" 
                    size="mini" 
                    @click.stop="handleAddCompare(item)"
                    :disabled="isItemInCompare(item)"
                    plain
                  >
                    {{ isItemInCompare(item) ? '已添加' : '对比' }}
                  </wd-button>
                </view>
              </view>
            </view>
          </template>
        </wd-cell>
      </wd-cell-group>

      <!-- 空状态 -->
      <view v-else class="empty-state">
        <text class="empty-text">暂无相关硬件</text>
        <text class="empty-hint">尝试调整搜索关键词或切换分类</text>
      </view>
    </view>

    <!-- 底部提示 -->
    <view class="footer-tip">
      <text>共 {{ filteredHardware.length }} 个硬件</text>
    </view>

    <!-- 对比悬浮窗 -->
    <view v-if="compareStore.totalCount > 0" class="compare-float">
      <view class="float-content">
        <view class="selected-items">
          <view 
            v-for="item in allCompareItems" 
            :key="`${item.type}-${item.id}`"
            class="item-tag"
            :class="getBrandClass(item.brand)"
            @click="handleRemoveCompare(item)"
          >
            <text class="item-model">{{ getShortModel(item.model) }}</text>
            <text class="item-remove">×</text>
          </view>
        </view>
        
        <view class="float-actions">
          <wd-button 
            type="default" 
            size="small" 
            @click="handleClearCompare"
            plain
          >
            清空
          </wd-button>
          <wd-button 
            type="primary" 
            size="small" 
            @click="handleStartPK"
            :disabled="!compareStore.canStartPK"
          >
            开始PK ({{ compareStore.totalCount }})
          </wd-button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useCompareStore } from '../../stores/compare'
import type { CpuSpecs, GpuSpecs, PhoneSpecs } from '../../types/hardware'
import type { CompareItem } from '../../stores/compare'

// Pinia store
const compareStore = useCompareStore()

// 响应式数据
const searchKeyword = ref('')
const activeTab = ref<'cpu' | 'gpu' | 'phone'>('cpu')

// 加载数据
const cpuList = ref<CpuSpecs[]>([])
const gpuList = ref<GpuSpecs[]>([])
const phoneList = ref<PhoneSpecs[]>([])

onMounted(() => {
  // 直接使用模拟数据，避免JSON导入问题
  cpuList.value = [
    {
      id: 'cpu-001',
      model: 'Intel Core i9-14900K',
      brand: 'Intel',
      releaseDate: '2024-01-01',
      price: 4999,
      description: 'Intel第14代酷睿旗舰处理器，性能核+能效核混合架构',
      cores: '8P+16E',
      baseClock: 3.2,
      boostClock: 6.0,
      socket: 'LGA1700',
      tdp: 125,
      integratedGraphics: true,
      cache: 36
    },
    {
      id: 'cpu-002',
      model: 'AMD Ryzen 9 7950X3D',
      brand: 'AMD',
      releaseDate: '2024-02-15',
      price: 5299,
      description: 'AMD Zen4架构，3D V-Cache技术，游戏性能卓越',
      cores: '16',
      baseClock: 4.2,
      boostClock: 5.7,
      socket: 'AM5',
      tdp: 120,
      integratedGraphics: true,
      cache: 144
    },
    {
      id: 'cpu-003',
      model: 'Intel Core i7-14700K',
      brand: 'Intel',
      releaseDate: '2024-01-01',
      price: 3299,
      description: '第14代酷睿i7，核心数量大幅增加，性价比高',
      cores: '8P+12E',
      baseClock: 3.4,
      boostClock: 5.6,
      socket: 'LGA1700',
      tdp: 125,
      integratedGraphics: true,
      cache: 33
    },
    {
      id: 'cpu-004',
      model: 'AMD Ryzen 7 7800X3D',
      brand: 'AMD',
      releaseDate: '2024-03-10',
      price: 2999,
      description: '游戏神U，3D V-Cache技术带来超低延迟',
      cores: '8',
      baseClock: 4.2,
      boostClock: 5.0,
      socket: 'AM5',
      tdp: 120,
      integratedGraphics: true,
      cache: 104
    },
    {
      id: 'cpu-005',
      model: 'Intel Core i5-14600K',
      brand: 'Intel',
      releaseDate: '2024-01-01',
      price: 2299,
      description: '主流级高性能处理器，适合游戏和创作',
      cores: '6P+8E',
      baseClock: 3.5,
      boostClock: 5.3,
      socket: 'LGA1700',
      tdp: 125,
      integratedGraphics: true,
      cache: 24
    }
  ] as CpuSpecs[]
  
  gpuList.value = [
    {
      id: 'gpu-001',
      model: 'NVIDIA GeForce RTX 4090',
      brand: 'NVIDIA',
      releaseDate: '2024-01-10',
      price: 12999,
      description: 'NVIDIA Ada Lovelace架构旗舰显卡，性能怪兽',
      vram: 24,
      busWidth: 384,
      cudaCores: 16384,
      coreClock: 2235,
      memoryClock: 21000,
      powerConsumption: 450,
      rayTracing: true,
      upscalingTech: 'DLSS'
    },
    {
      id: 'gpu-002',
      model: 'AMD Radeon RX 7900 XTX',
      brand: 'AMD',
      releaseDate: '2024-02-20',
      price: 7999,
      description: 'AMD RDNA3架构旗舰显卡，高性价比选择',
      vram: 24,
      busWidth: 384,
      cudaCores: 6144,
      coreClock: 2300,
      memoryClock: 20000,
      powerConsumption: 355,
      rayTracing: true,
      upscalingTech: 'FSR'
    },
    {
      id: 'gpu-003',
      model: 'NVIDIA GeForce RTX 4080 SUPER',
      brand: 'NVIDIA',
      releaseDate: '2024-03-15',
      price: 8999,
      description: 'RTX 4080升级版，性能接近RTX 4090',
      vram: 16,
      busWidth: 256,
      cudaCores: 10240,
      coreClock: 2295,
      memoryClock: 23000,
      powerConsumption: 320,
      rayTracing: true,
      upscalingTech: 'DLSS'
    },
    {
      id: 'gpu-004',
      model: 'AMD Radeon RX 7800 XT',
      brand: 'AMD',
      releaseDate: '2024-04-05',
      price: 4599,
      description: '中高端显卡，2K游戏利器',
      vram: 16,
      busWidth: 256,
      cudaCores: 3840,
      coreClock: 2124,
      memoryClock: 19500,
      powerConsumption: 263,
      rayTracing: true,
      upscalingTech: 'FSR'
    },
    {
      id: 'gpu-005',
      model: 'NVIDIA GeForce RTX 4070 Ti SUPER',
      brand: 'NVIDIA',
      releaseDate: '2024-05-12',
      price: 6499,
      description: '2K游戏甜点卡，DLSS3加持',
      vram: 16,
      busWidth: 256,
      cudaCores: 8448,
      coreClock: 2310,
      memoryClock: 21000,
      powerConsumption: 285,
      rayTracing: true,
      upscalingTech: 'DLSS'
    }
  ] as GpuSpecs[]
  
  phoneList.value = [
    {
      id: 'phone-001',
      model: 'iPhone 15 Pro Max',
      brand: 'Apple',
      releaseDate: '2024-09-22',
      price: 9999,
      description: '苹果旗舰手机，A17 Pro芯片，钛金属边框',
      processor: 'A17 Pro',
      ram: 8,
      storage: 256,
      screenSize: 6.7,
      resolution: '2796x1290',
      refreshRate: 120,
      batteryCapacity: 4422,
      camera: '48MP+12MP+12MP',
      os: 'iOS',
      support5G: true
    },
    {
      id: 'phone-002',
      model: 'Xiaomi 14 Ultra',
      brand: 'Xiaomi',
      releaseDate: '2024-02-25',
      price: 6499,
      description: '小米影像旗舰，徕卡四摄，骁龙8 Gen 3',
      processor: '骁龙8 Gen 3',
      ram: 16,
      storage: 512,
      screenSize: 6.73,
      resolution: '3200x1440',
      refreshRate: 120,
      batteryCapacity: 5300,
      camera: '50MP+50MP+50MP+50MP',
      os: 'Android',
      support5G: true
    },
    {
      id: 'phone-003',
      model: 'Huawei Mate 60 Pro+',
      brand: 'Huawei',
      releaseDate: '2024-08-29',
      price: 8999,
      description: '华为旗舰，麒麟9000S芯片，卫星通话',
      processor: '麒麟9000S',
      ram: 12,
      storage: 512,
      screenSize: 6.82,
      resolution: '2720x1260',
      refreshRate: 120,
      batteryCapacity: 5000,
      camera: '50MP+48MP+40MP',
      os: 'Android',
      support5G: true
    },
    {
      id: 'phone-004',
      model: 'Samsung Galaxy S24 Ultra',
      brand: 'Samsung',
      releaseDate: '2024-01-31',
      price: 9699,
      description: '三星旗舰，骁龙8 Gen 3，S Pen手写笔',
      processor: '骁龙8 Gen 3',
      ram: 12,
      storage: 512,
      screenSize: 6.8,
      resolution: '3120x1440',
      refreshRate: 120,
      batteryCapacity: 5000,
      camera: '200MP+12MP+10MP+10MP',
      os: 'Android',
      support5G: true
    },
    {
      id: 'phone-005',
      model: 'OnePlus 12',
      brand: '其他',
      releaseDate: '2024-01-23',
      price: 4299,
      description: '一加旗舰，骁龙8 Gen 3，哈苏影像',
      processor: '骁龙8 Gen 3',
      ram: 16,
      storage: 512,
      screenSize: 6.82,
      resolution: '3168x1440',
      refreshRate: 120,
      batteryCapacity: 5400,
      camera: '50MP+48MP+64MP',
      os: 'Android',
      support5G: true
    }
  ] as PhoneSpecs[]
})

// 根据当前Tab获取数据源
const currentDataSource = computed(() => {
  if (activeTab.value === 'cpu') {
    return cpuList.value
  } else if (activeTab.value === 'gpu') {
    return gpuList.value
  } else {
    return phoneList.value
  }
})

// 过滤硬件数据
const filteredHardware = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()
  const data = currentDataSource.value
  
  if (!keyword) {
    return data
  }
  
  // 使用类型断言解决联合类型调用问题，使用 indexOf 替代 includes 避免 ES2015+ 方法兼容性问题
  return (data as (CpuSpecs | GpuSpecs | PhoneSpecs)[]).filter((item: CpuSpecs | GpuSpecs | PhoneSpecs) => 
    item.model.toLowerCase().indexOf(keyword) !== -1 ||
    item.brand.toLowerCase().indexOf(keyword) !== -1 ||
    (item.description && item.description.toLowerCase().indexOf(keyword) !== -1)
  )
})

// 获取品牌样式类
const getBrandClass = (brand: string) => {
  switch (brand) {
    case 'Intel': return 'brand-intel'
    case 'AMD': return 'brand-amd'
    case 'NVIDIA': return 'brand-nvidia'
    case 'Apple': return 'brand-apple'
    case 'Xiaomi': return 'brand-xiaomi'
    case 'Huawei': return 'brand-huawei'
    case 'Samsung': return 'brand-samsung'
    default: return 'brand-other'
  }
}

// 获取品牌简称
const getBrandShortName = (brand: string) => {
  switch (brand) {
    case 'Intel': return 'INT'
    case 'AMD': return 'AMD'
    case 'NVIDIA': return 'NVI'
    case 'Apple': return 'APP'
    case 'Xiaomi': return 'XIA'
    case 'Huawei': return 'HUA'
    case 'Samsung': return 'SAM'
    default: return 'OTH'
  }
}

// 搜索处理
const handleSearch = () => {
  console.log('搜索关键词:', searchKeyword.value)
}

// 清空搜索
const handleClear = () => {
  searchKeyword.value = ''
}

// 卡片点击跳转
const handleCardClick = (item: CpuSpecs | GpuSpecs | PhoneSpecs) => {
  const type = activeTab.value
  const id = item.id
  
  uni.navigateTo({
    url: `/pages/detail/index?id=${id}&type=${type}`,
    fail: (err) => {
      console.error('跳转失败:', err)
      uni.showToast({
        title: '详情页面未找到',
        icon: 'error'
      })
    }
  })
}

// 获取所有对比项（合并CPU、GPU和手机）
const allCompareItems = computed(() => {
  return [...compareStore.cpuList, ...compareStore.gpuList, ...compareStore.phoneList]
})

// 获取型号简称（用于标签显示）
const getShortModel = (model: string) => {
  // 提取主要部分，如 "Intel Core i9-14900K" -> "i9-14900K"
  const parts = model.split(' ')
  return parts.length > 2 ? parts.slice(-2).join(' ') : model
}

// 移除对比项
const handleRemoveCompare = (item: CompareItem) => {
  compareStore.removeCompareItem(item.id, item.type)
  uni.showToast({
    title: '已移除',
    icon: 'success'
  })
}

// 清空对比列表
const handleClearCompare = () => {
  uni.showModal({
    title: '提示',
    content: '确定要清空所有对比项吗？',
    success: (res) => {
      if (res.confirm) {
        compareStore.clearCompare()
        uni.showToast({
          title: '已清空',
          icon: 'success'
        })
      }
    }
  })
}

// 开始PK
const handleStartPK = () => {
  if (!compareStore.canStartPK) {
    uni.showToast({
      title: '请至少选择2个同类型硬件',
      icon: 'error'
    })
    return
  }
  
  // 检查是否有足够数量的同类型硬件
  const compareItems = compareStore.compareItems
  let compareType: 'cpu' | 'gpu' | 'phone' | null = null
  
  if (compareItems.cpu.length >= 2) {
    compareType = 'cpu'
  } else if (compareItems.gpu.length >= 2) {
    compareType = 'gpu'
  } else if (compareItems.phone.length >= 2) {
    compareType = 'phone'
  }
  
  if (!compareType) {
    uni.showToast({
      title: '请至少选择2个同类型硬件',
      icon: 'error'
    })
    return
  }
  
  // 跳转到PK页面
  uni.navigateTo({
    url: `/pages/compare/index?type=${compareType}`,
    fail: (err) => {
      console.error('跳转失败:', err)
      uni.showToast({
        title: 'PK页面未找到',
        icon: 'error'
      })
    }
  })
}

// 检查项目是否已在对比列表中
const isItemInCompare = (item: CpuSpecs | GpuSpecs | PhoneSpecs) => {
  const type = activeTab.value
  const compareList = type === 'cpu' ? compareStore.cpuList : type === 'gpu' ? compareStore.gpuList : compareStore.phoneList
  return compareList.some(compareItem => compareItem.id === item.id)
}

// 添加对比项
const handleAddCompare = (item: CpuSpecs | GpuSpecs | PhoneSpecs) => {
  const result = compareStore.toggleCompare(item)
  if (result.added) {
    uni.showToast({
      title: result.message,
      icon: 'success'
    })
  } else {
    // 如果已经存在，则移除
    uni.showToast({
      title: result.message,
      icon: 'none'
    })
  }
}
</script>

<style scoped lang="scss">
.page-container {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.search-container {
  padding: 20rpx 30rpx;
  background-color: #ffffff;
}

.category-tabs {
  background-color: #ffffff;
  margin-bottom: 20rpx;
}

.hardware-list {
  padding: 0 30rpx;
}

.hardware-card {
  margin-bottom: 20rpx;
  border-radius: 16rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
  
  :deep(.wd-cell__title) {
    width: 100%;
  }
}

.card-content {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 20rpx 0;
}

.brand-logo {
  width: 80rpx;
  height: 80rpx;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  font-weight: bold;
  color: #ffffff;
  margin-right: 24rpx;
  flex-shrink: 0;
}

.brand-intel {
  background: linear-gradient(135deg, #0071c5, #00a9ff);
}

.brand-amd {
  background: linear-gradient(135deg, #ed1c24, #ff6b6b);
}

.brand-nvidia {
  background: linear-gradient(135deg, #76b900, #a8e063);
}

.brand-apple {
  background: linear-gradient(135deg, #000000, #333333);
}

.brand-xiaomi {
  background: linear-gradient(135deg, #ff6900, #ffa726);
}

.brand-huawei {
  background: linear-gradient(135deg, #ff0036, #ff6b9d);
}

.brand-samsung {
  background: linear-gradient(135deg, #1428a0, #1a73e8);
}

.brand-other {
  background: linear-gradient(135deg, #666666, #999999);
}

.hardware-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.model {
  font-size: 32rpx;
  font-weight: bold;
  color: #333333;
  margin-bottom: 8rpx;
  line-height: 1.4;
}

.specs {
  font-size: 26rpx;
  color: #666666;
  margin-bottom: 12rpx;
  line-height: 1.4;
}

.price {
  font-size: 28rpx;
  font-weight: bold;
  color: #ff6b00;
  margin-bottom: 12rpx;
}

.compare-action {
  align-self: flex-start;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 0;
  text-align: center;
}

.empty-text {
  font-size: 32rpx;
  color: #999999;
  margin-bottom: 20rpx;
}

.empty-hint {
  font-size: 28rpx;
  color: #cccccc;
}

.footer-tip {
  padding: 30rpx;
  text-align: center;
  font-size: 26rpx;
  color: #999999;
  background-color: #ffffff;
  margin-top: 20rpx;
}

/* 对比悬浮窗样式 */
.compare-float {
  position: fixed;
  bottom: 40rpx;
  left: 30rpx;
  right: 30rpx;
  z-index: 1000;
}

.float-content {
  background-color: #ffffff;
  border-radius: 20rpx;
  padding: 24rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.selected-items {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.item-tag {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx 20rpx;
  border-radius: 40rpx;
  font-size: 24rpx;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.2s;
}

.item-tag:hover {
  opacity: 0.9;
  transform: translateY(-2rpx);
}

.item-model {
  font-weight: bold;
  max-width: 120rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-remove {
  font-size: 28rpx;
  font-weight: bold;
  margin-left: 4rpx;
}

.float-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20rpx;
}

.float-actions .wd-button {
  flex: 1;
}
</style>
