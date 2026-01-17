<template>
  <view class="compare-page">
    <!-- 头部 -->
    <view class="compare-header">
      <view class="header-title">
        <text class="title-text">硬件PK对比</text>
        <text class="title-sub">左右分栏，直观对比</text>
      </view>
      <view class="header-actions">
        <wd-button 
          type="default" 
          size="small" 
          @click="handleBack"
          plain
        >
          返回
        </wd-button>
        <wd-button 
          type="primary" 
          size="small" 
          @click="handleClearAll"
        >
          清空对比
        </wd-button>
      </view>
    </view>

    <!-- 对比类型标签 -->
    <view class="compare-type">
      <wd-tag 
        :type="compareType === 'cpu' ? 'primary' : compareType === 'gpu' ? 'success' : 'warning'"
        size="large"
        round
      >
        {{ compareType === 'cpu' ? 'CPU 对比' : compareType === 'gpu' ? '显卡 对比' : '手机 对比' }}
      </wd-tag>
      <text class="compare-count">共 {{ compareItems.length }} 个硬件</text>
    </view>

    <!-- 硬件选择器 -->
    <view class="hardware-selector" v-if="compareItems.length >= 2">
      <view class="selector-title">选择对比硬件</view>
      <view class="selector-items">
        <view 
          v-for="item in compareItems" 
          :key="item.id"
          class="selector-item"
          :class="{ 'selected': selectedLeftId === item.id || selectedRightId === item.id }"
          @click="toggleHardwareSelection(item.id)"
        >
          <view class="selector-brand" :class="getBrandClass(item.brand)">{{ item.brand }}</view>
          <view class="selector-model">{{ item.model }}</view>
          <view class="selector-price">¥{{ item.price.toLocaleString() }}</view>
          <view class="selector-position" v-if="selectedLeftId === item.id">左侧</view>
          <view class="selector-position" v-else-if="selectedRightId === item.id">右侧</view>
        </view>
      </view>
    </view>

    <!-- 对比内容 -->
    <view class="compare-content" v-if="compareItems.length >= 2 && leftItem && rightItem">
      <view class="compare-columns">
        <!-- 左侧硬件 -->
        <view class="compare-column left-column">
          <view class="hardware-card">
            <view class="card-header">
              <view class="card-header-top">
                <view class="brand-tag" :class="getBrandClass(leftItem.brand)">
                  {{ leftItem.brand }}
                </view>
                <wd-button 
                  type="default" 
                  size="mini" 
                  @click="swapHardware"
                  plain
                >
                  交换位置
                </wd-button>
              </view>
              <view class="model-name">{{ leftItem.model }}</view>
              <view class="price-tag">¥{{ leftItem.price.toLocaleString() }}</view>
            </view>
            
            <view class="card-body">
              <view class="param-list">
                <view 
                  v-for="param in leftParams" 
                  :key="param.label"
                  class="param-item"
                >
                  <view class="param-label">{{ param.label }}</view>
                  <view class="param-value">{{ param.value }}</view>
                  <view class="param-desc" v-if="param.desc">{{ param.desc }}</view>
                </view>
              </view>
            </view>
          </view>
        </view>

        <!-- 中间对比线 -->
        <view class="compare-divider">
          <view class="divider-line"></view>
          <view class="divider-text">VS</view>
          <view class="divider-line"></view>
        </view>

        <!-- 右侧硬件 -->
        <view class="compare-column right-column">
          <view class="hardware-card">
            <view class="card-header">
              <view class="card-header-top">
                <view class="brand-tag" :class="getBrandClass(rightItem.brand)">
                  {{ rightItem.brand }}
                </view>
                <wd-button 
                  type="default" 
                  size="mini" 
                  @click="removeHardware(rightItem.id)"
                  plain
                >
                  移除
                </wd-button>
              </view>
              <view class="model-name">{{ rightItem.model }}</view>
              <view class="price-tag">¥{{ rightItem.price.toLocaleString() }}</view>
            </view>
            
            <view class="card-body">
              <view class="param-list">
                <view 
                  v-for="param in rightParams" 
                  :key="param.label"
                  class="param-item"
                >
                  <view class="param-label">{{ param.label }}</view>
                  <view class="param-value">{{ param.value }}</view>
                  <view class="param-desc" v-if="param.desc">{{ param.desc }}</view>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 对比结果 -->
      <view class="compare-result">
        <view class="result-title">对比结果</view>
        <view class="result-items">
          <view 
            v-for="result in comparisonResults" 
            :key="result.label"
            class="result-item"
          >
            <view class="result-label">{{ result.label }}</view>
            <view class="result-bars">
              <view class="bar-container">
                <view 
                  class="bar left-bar" 
                  :style="{ width: `${result.leftPercent}%` }"
                  :class="getBarClass(result.winner, 'left')"
                >
                  <text class="bar-value">{{ result.leftValue }}</text>
                </view>
              </view>
              <view class="bar-container">
                <view 
                  class="bar right-bar" 
                  :style="{ width: `${result.rightPercent}%` }"
                  :class="getBarClass(result.winner, 'right')"
                >
                  <text class="bar-value">{{ result.rightValue }}</text>
                </view>
              </view>
            </view>
            <view class="result-winner" v-if="result.winner">
              {{ result.winner === 'left' ? '左侧胜出' : '右侧胜出' }}
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 不足2个硬件的提示 -->
    <view v-else class="empty-state">
      <view class="empty-icon">⚔️</view>
      <text class="empty-text">需要至少2个同类型硬件才能进行对比</text>
      <text class="empty-hint">请返回列表页面选择更多硬件</text>
      <wd-button 
        type="primary" 
        @click="handleBack"
        style="margin-top: 40rpx;"
      >
        返回列表
      </wd-button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useCompareStore } from '../../stores/compare'
import type { CpuSpecs, GpuSpecs, PhoneSpecs } from '../../types/hardware'

// Pinia store
const compareStore = useCompareStore()

// 路由参数
const queryParams = ref<{ type?: 'cpu' | 'gpu' | 'phone' }>({})

// 模拟数据
const cpuMockData: CpuSpecs[] = [
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
]

const gpuMockData: GpuSpecs[] = [
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
]

const phoneMockData: PhoneSpecs[] = [
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
]

// 页面加载
onLoad((options) => {
  queryParams.value = options || {}
})

// 选择的硬件ID
const selectedLeftId = ref<string>('')
const selectedRightId = ref<string>('')

// 对比类型
const compareType = computed(() => {
  return queryParams.value.type || 'cpu'
})

// 对比项列表
const compareItems = computed(() => {
  const items = compareType.value === 'cpu' 
    ? compareStore.cpuList 
    : compareType.value === 'gpu'
    ? compareStore.gpuList
    : compareStore.phoneList
  
  // 如果没有选择左侧硬件，默认选择第一个
  if (items.length >= 1 && !selectedLeftId.value) {
    selectedLeftId.value = items[0].id
  }
  
  // 如果没有选择右侧硬件，默认选择第二个（如果有）
  if (items.length >= 2 && !selectedRightId.value) {
    selectedRightId.value = items[1].id
  }
  
  return items
})

// 根据ID从模拟数据中查找完整硬件信息
const findHardwareById = (id: string, type: 'cpu' | 'gpu' | 'phone') => {
  const dataSource = type === 'cpu' ? cpuMockData : type === 'gpu' ? gpuMockData : phoneMockData
  // 使用 for 循环替代 find 方法
  for (let i = 0; i < dataSource.length; i++) {
    if (dataSource[i].id === id) {
      return dataSource[i]
    }
  }
  return null
}

// 左侧硬件（根据选择）
const leftItem = computed(() => {
  if (!selectedLeftId.value) return null
  return findHardwareById(selectedLeftId.value, compareType.value)
})

// 右侧硬件（根据选择）
const rightItem = computed(() => {
  if (!selectedRightId.value) return null
  return findHardwareById(selectedRightId.value, compareType.value)
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

// 获取左侧硬件参数
const leftParams = computed(() => {
  if (!leftItem.value) return []
  return getHardwareParams(leftItem.value, compareType.value)
})

// 获取右侧硬件参数
const rightParams = computed(() => {
  if (!rightItem.value) return []
  return getHardwareParams(rightItem.value, compareType.value)
})

// 获取硬件参数
const getHardwareParams = (item: any, type: 'cpu' | 'gpu' | 'phone') => {
  const params = []
  
  // 通用参数
  params.push(
    { label: '型号', value: item.model, desc: '' },
    { label: '品牌', value: item.brand, desc: '' },
    { label: '参考价格', value: `¥${item.price.toLocaleString()}`, desc: '' },
    { label: '发布日期', value: item.releaseDate, desc: '' }
  )
  
  // CPU 特有参数
  if (type === 'cpu') {
    params.push(
      { label: '核心配置', value: item.cores, desc: '性能核+能效核' },
      { label: '频率范围', value: `${item.baseClock}-${item.boostClock} GHz`, desc: '基础-最大加速频率' },
      { label: '接口', value: item.socket, desc: '' },
      { label: '热设计功耗', value: `${item.tdp} W`, desc: '' },
      { label: '缓存', value: `${item.cache} MB`, desc: '' },
      { label: '集成显卡', value: item.integratedGraphics ? '是' : '否', desc: '' }
    )
  }
  
  // GPU 特有参数
  if (type === 'gpu') {
    params.push(
      { label: '显存', value: `${item.vram} GB`, desc: '' },
      { label: '位宽', value: `${item.busWidth} bit`, desc: '' },
      { label: 'CUDA核心', value: item.cudaCores.toLocaleString(), desc: '流处理器数量' },
      { label: '核心频率', value: `${item.coreClock} MHz`, desc: '' },
      { label: '显存频率', value: `${item.memoryClock} MHz`, desc: '' },
      { label: '功耗', value: `${item.powerConsumption} W`, desc: '' },
      { label: '光线追踪', value: item.rayTracing ? '支持' : '不支持', desc: '' },
      { label: '超分辨率', value: item.upscalingTech, desc: '' }
    )
  }
  
  // 手机 特有参数
  if (type === 'phone') {
    params.push(
      { label: '处理器', value: item.processor, desc: '' },
      { label: '内存', value: `${item.ram} GB`, desc: '' },
      { label: '存储', value: `${item.storage} GB`, desc: '' },
      { label: '屏幕尺寸', value: `${item.screenSize} 英寸`, desc: '' },
      { label: '分辨率', value: item.resolution, desc: '' },
      { label: '刷新率', value: `${item.refreshRate} Hz`, desc: '' },
      { label: '电池容量', value: `${item.batteryCapacity} mAh`, desc: '' },
      { label: '摄像头', value: item.camera, desc: '' },
      { label: '操作系统', value: item.os, desc: '' },
      { label: '5G支持', value: item.support5G ? '支持' : '不支持', desc: '' }
    )
  }
  
  return params
}

// 对比结果
const comparisonResults = computed(() => {
  if (!leftItem.value || !rightItem.value) return []
  
  const left = leftItem.value
  const right = rightItem.value
  const results = []
  
  // 价格对比（越低越好）
  const priceDiff = ((right.price - left.price) / left.price * 100).toFixed(1)
  const priceWinner = left.price < right.price ? 'left' : 'right'
  results.push({
    label: '价格',
    leftValue: `¥${left.price.toLocaleString()}`,
    rightValue: `¥${right.price.toLocaleString()}`,
    leftPercent: left.price < right.price ? 100 : (left.price / right.price * 100),
    rightPercent: right.price < left.price ? 100 : (right.price / left.price * 100),
    winner: priceWinner,
    diff: `${priceDiff}%`
  })
  
  // CPU 对比项
  if (compareType.value === 'cpu') {
    const leftCpu = left as CpuSpecs
    const rightCpu = right as CpuSpecs
    
    // 核心数量
    const leftCores = parseInt(leftCpu.cores.split('+')[0]) + (leftCpu.cores.indexOf('+') > -1 ? parseInt(leftCpu.cores.split('+')[1]) : 0)
    const rightCores = parseInt(rightCpu.cores.split('+')[0]) + (rightCpu.cores.indexOf('+') > -1 ? parseInt(rightCpu.cores.split('+')[1]) : 0)
    const coresWinner = leftCores > rightCores ? 'left' : 'right'
    results.push({
      label: '核心总数',
      leftValue: `${leftCores}核`,
      rightValue: `${rightCores}核`,
      leftPercent: (leftCores / Math.max(leftCores, rightCores)) * 100,
      rightPercent: (rightCores / Math.max(leftCores, rightCores)) * 100,
      winner: coresWinner
    })
    
    // 最高频率
    const freqWinner = leftCpu.boostClock > rightCpu.boostClock ? 'left' : 'right'
    results.push({
      label: '最高频率',
      leftValue: `${leftCpu.boostClock} GHz`,
      rightValue: `${rightCpu.boostClock} GHz`,
      leftPercent: (leftCpu.boostClock / Math.max(leftCpu.boostClock, rightCpu.boostClock)) * 100,
      rightPercent: (rightCpu.boostClock / Math.max(leftCpu.boostClock, rightCpu.boostClock)) * 100,
      winner: freqWinner
    })
    
    // 缓存大小
    const cacheWinner = leftCpu.cache > rightCpu.cache ? 'left' : 'right'
    results.push({
      label: '缓存',
      leftValue: `${leftCpu.cache} MB`,
      rightValue: `${rightCpu.cache} MB`,
      leftPercent: (leftCpu.cache / Math.max(leftCpu.cache, rightCpu.cache)) * 100,
      rightPercent: (rightCpu.cache / Math.max(leftCpu.cache, rightCpu.cache)) * 100,
      winner: cacheWinner
    })
    
    // 功耗（越低越好）
    const tdpWinner = leftCpu.tdp < rightCpu.tdp ? 'left' : 'right'
    results.push({
      label: '功耗',
      leftValue: `${leftCpu.tdp} W`,
      rightValue: `${rightCpu.tdp} W`,
      leftPercent: leftCpu.tdp < rightCpu.tdp ? 100 : (leftCpu.tdp / rightCpu.tdp * 100),
      rightPercent: rightCpu.tdp < leftCpu.tdp ? 100 : (rightCpu.tdp / leftCpu.tdp * 100),
      winner: tdpWinner
    })
  }
  
  // GPU 对比项
  if (compareType.value === 'gpu') {
    const leftGpu = left as GpuSpecs
    const rightGpu = right as GpuSpecs
    
    // 显存
    const vramWinner = leftGpu.vram > rightGpu.vram ? 'left' : 'right'
    results.push({
      label: '显存',
      leftValue: `${leftGpu.vram} GB`,
      rightValue: `${rightGpu.vram} GB`,
      leftPercent: (leftGpu.vram / Math.max(leftGpu.vram, rightGpu.vram)) * 100,
      rightPercent: (rightGpu.vram / Math.max(leftGpu.vram, rightGpu.vram)) * 100,
      winner: vramWinner
    })
    
    // CUDA核心
    const coresWinner = leftGpu.cudaCores > rightGpu.cudaCores ? 'left' : 'right'
    results.push({
      label: 'CUDA核心',
      leftValue: leftGpu.cudaCores.toLocaleString(),
      rightValue: rightGpu.cudaCores.toLocaleString(),
      leftPercent: (leftGpu.cudaCores / Math.max(leftGpu.cudaCores, rightGpu.cudaCores)) * 100,
      rightPercent: (rightGpu.cudaCores / Math.max(leftGpu.cudaCores, rightGpu.cudaCores)) * 100,
      winner: coresWinner
    })
    
    // 核心频率
    const clockWinner = leftGpu.coreClock > rightGpu.coreClock ? 'left' : 'right'
    results.push({
      label: '核心频率',
      leftValue: `${leftGpu.coreClock} MHz`,
      rightValue: `${rightGpu.coreClock} MHz`,
      leftPercent: (leftGpu.coreClock / Math.max(leftGpu.coreClock, rightGpu.coreClock)) * 100,
      rightPercent: (rightGpu.coreClock / Math.max(leftGpu.coreClock, rightGpu.coreClock)) * 100,
      winner: clockWinner
    })
    
    // 功耗（越低越好）
    const powerWinner = leftGpu.powerConsumption < rightGpu.powerConsumption ? 'left' : 'right'
    results.push({
      label: '功耗',
      leftValue: `${leftGpu.powerConsumption} W`,
      rightValue: `${rightGpu.powerConsumption} W`,
      leftPercent: leftGpu.powerConsumption < rightGpu.powerConsumption ? 100 : (leftGpu.powerConsumption / rightGpu.powerConsumption * 100),
      rightPercent: rightGpu.powerConsumption < leftGpu.powerConsumption ? 100 : (rightGpu.powerConsumption / leftGpu.powerConsumption * 100),
      winner: powerWinner
    })
  }
  
  // 手机 对比项
  if (compareType.value === 'phone') {
    const leftPhone = left as PhoneSpecs
    const rightPhone = right as PhoneSpecs
    
    // 内存
    const ramWinner = leftPhone.ram > rightPhone.ram ? 'left' : 'right'
    results.push({
      label: '内存',
      leftValue: `${leftPhone.ram} GB`,
      rightValue: `${rightPhone.ram} GB`,
      leftPercent: (leftPhone.ram / Math.max(leftPhone.ram, rightPhone.ram)) * 100,
      rightPercent: (rightPhone.ram / Math.max(leftPhone.ram, rightPhone.ram)) * 100,
      winner: ramWinner
    })
    
    // 存储
    const storageWinner = leftPhone.storage > rightPhone.storage ? 'left' : 'right'
    results.push({
      label: '存储',
      leftValue: `${leftPhone.storage} GB`,
      rightValue: `${rightPhone.storage} GB`,
      leftPercent: (leftPhone.storage / Math.max(leftPhone.storage, rightPhone.storage)) * 100,
      rightPercent: (rightPhone.storage / Math.max(leftPhone.storage, rightPhone.storage)) * 100,
      winner: storageWinner
    })
    
    // 屏幕尺寸
    const screenWinner = leftPhone.screenSize > rightPhone.screenSize ? 'left' : 'right'
    results.push({
      label: '屏幕尺寸',
      leftValue: `${leftPhone.screenSize} 英寸`,
      rightValue: `${rightPhone.screenSize} 英寸`,
      leftPercent: (leftPhone.screenSize / Math.max(leftPhone.screenSize, rightPhone.screenSize)) * 100,
      rightPercent: (rightPhone.screenSize / Math.max(leftPhone.screenSize, rightPhone.screenSize)) * 100,
      winner: screenWinner
    })
    
    // 电池容量
    const batteryWinner = leftPhone.batteryCapacity > rightPhone.batteryCapacity ? 'left' : 'right'
    results.push({
      label: '电池容量',
      leftValue: `${leftPhone.batteryCapacity} mAh`,
      rightValue: `${rightPhone.batteryCapacity} mAh`,
      leftPercent: (leftPhone.batteryCapacity / Math.max(leftPhone.batteryCapacity, rightPhone.batteryCapacity)) * 100,
      rightPercent: (rightPhone.batteryCapacity / Math.max(leftPhone.batteryCapacity, rightPhone.batteryCapacity)) * 100,
      winner: batteryWinner
    })
    
    // 刷新率
    const refreshWinner = leftPhone.refreshRate > rightPhone.refreshRate ? 'left' : 'right'
    results.push({
      label: '刷新率',
      leftValue: `${leftPhone.refreshRate} Hz`,
      rightValue: `${rightPhone.refreshRate} Hz`,
      leftPercent: (leftPhone.refreshRate / Math.max(leftPhone.refreshRate, rightPhone.refreshRate)) * 100,
      rightPercent: (rightPhone.refreshRate / Math.max(leftPhone.refreshRate, rightPhone.refreshRate)) * 100,
      winner: refreshWinner
    })
  }
  
  return results
})

// 获取进度条样式类
const getBarClass = (winner: string | null, side: 'left' | 'right') => {
  if (!winner) return ''
  return winner === side ? 'bar-winner' : 'bar-loser'
}

// 切换硬件选择
const toggleHardwareSelection = (id: string) => {
  if (selectedLeftId.value === id) {
    // 如果点击的是左侧硬件，取消选择
    selectedLeftId.value = ''
  } else if (selectedRightId.value === id) {
    // 如果点击的是右侧硬件，取消选择
    selectedRightId.value = ''
  } else {
    // 如果点击的是未选择的硬件
    if (!selectedLeftId.value) {
      selectedLeftId.value = id
    } else if (!selectedRightId.value) {
      selectedRightId.value = id
    } else {
      // 如果已经选择了两个，替换右侧硬件
      selectedRightId.value = id
    }
  }
}

// 交换左右硬件位置
const swapHardware = () => {
  if (selectedLeftId.value && selectedRightId.value) {
    const temp = selectedLeftId.value
    selectedLeftId.value = selectedRightId.value
    selectedRightId.value = temp
  }
}

// 移除硬件
const removeHardware = (id: string) => {
  compareStore.removeCompareItem(id, compareType.value)
  uni.showToast({
    title: '已移除',
    icon: 'success'
  })
  
  // 如果移除的是当前选择的硬件，清除选择
  if (selectedLeftId.value === id) {
    selectedLeftId.value = ''
  }
  if (selectedRightId.value === id) {
    selectedRightId.value = ''
  }
}

// 返回列表
const handleBack = () => {
  uni.navigateBack()
}

// 清空对比
const handleClearAll = () => {
  uni.showModal({
    title: '提示',
    content: '确定要清空所有对比项吗？',
    success: (res) => {
      if (res.confirm) {
        compareStore.clearCompare(compareType.value)
        uni.showToast({
          title: '已清空',
          icon: 'success'
        })
        setTimeout(() => {
          uni.navigateBack()
        }, 1500)
      }
    }
  })
}
</script>

<style scoped lang="scss">
.compare-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 40rpx;
}

.compare-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40rpx 30rpx 30rpx;
  color: #ffffff;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-title {
  flex: 1;
}

.title-text {
  display: block;
  font-size: 40rpx;
  font-weight: bold;
  margin-bottom: 8rpx;
}

.title-sub {
  display: block;
  font-size: 26rpx;
  opacity: 0.9;
}

.header-actions {
  display: flex;
  gap: 20rpx;
}

.compare-type {
  padding: 30rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
  background-color: #ffffff;
  margin-bottom: 20rpx;
}

.compare-count {
  font-size: 28rpx;
  color: #666666;
}

.compare-content {
  padding: 0 30rpx;
}

.compare-columns {
  display: flex;
  gap: 30rpx;
  margin-bottom: 40rpx;
}

.compare-column {
  flex: 1;
}

.hardware-card {
  background-color: #ffffff;
  border-radius: 20rpx;
  overflow: hidden;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 30rpx;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-bottom: 1rpx solid #f0f0f0;
}

.brand-tag {
  display: inline-block;
  padding: 8rpx 20rpx;
  border-radius: 40rpx;
  font-size: 24rpx;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 16rpx;
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

.model-name {
  font-size: 36rpx;
  font-weight: bold;
  color: #333333;
  margin-bottom: 12rpx;
  line-height: 1.3;
}

.price-tag {
  font-size: 28rpx;
  font-weight: bold;
  color: #ff6b00;
  background-color: rgba(255, 107, 0, 0.1);
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  display: inline-block;
}

.card-body {
  padding: 30rpx;
}

.param-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.param-item {
  border-bottom: 1rpx solid #f0f0f0;
  padding-bottom: 20rpx;
}

.param-item:last-child {
  border-bottom: none;
}

.param-label {
  font-size: 26rpx;
  color: #666666;
  margin-bottom: 8rpx;
}

.param-value {
  font-size: 28rpx;
  font-weight: bold;
  color: #333333;
  margin-bottom: 4rpx;
}

.param-desc {
  font-size: 24rpx;
  color: #999999;
}

.compare-divider {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 60rpx;
}

.divider-line {
  flex: 1;
  width: 2rpx;
  background-color: #e0e0e0;
}

.divider-text {
  padding: 16rpx;
  font-size: 28rpx;
  font-weight: bold;
  color: #ff6b00;
  background-color: #ffffff;
  border-radius: 50%;
  border: 2rpx solid #ff6b00;
}

.compare-result {
  background-color: #ffffff;
  border-radius: 20rpx;
  padding: 30rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
  margin-top: 40rpx;
}

.result-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333333;
  margin-bottom: 30rpx;
  text-align: center;
}

.result-items {
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.result-item {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.result-label {
  font-size: 28rpx;
  font-weight: bold;
  color: #333333;
}

.result-bars {
  display: flex;
  gap: 20rpx;
  height: 60rpx;
}

.bar-container {
  flex: 1;
  background-color: #f0f0f0;
  border-radius: 30rpx;
  overflow: hidden;
  position: relative;
}

.bar {
  height: 100%;
  border-radius: 30rpx;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 20rpx;
  transition: width 0.5s ease;
}

.left-bar {
  background: linear-gradient(90deg, #667eea, #764ba2);
}

.right-bar {
  background: linear-gradient(90deg, #ff6b00, #ff9e00);
}

.bar-winner {
  opacity: 1;
}

.bar-loser {
  opacity: 0.6;
}

.bar-value {
  font-size: 24rpx;
  font-weight: bold;
  color: #ffffff;
  text-shadow: 0 1rpx 2rpx rgba(0, 0, 0, 0.2);
}

.result-winner {
  font-size: 26rpx;
  font-weight: bold;
  color: #ff6b00;
  text-align: center;
  padding: 8rpx;
  background-color: rgba(255, 107, 0, 0.1);
  border-radius: 20rpx;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 30rpx;
  text-align: center;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: 30rpx;
}

.empty-text {
  font-size: 32rpx;
  color: #333333;
  margin-bottom: 20rpx;
}

.empty-hint {
  font-size: 28rpx;
  color: #666666;
}

/* 硬件选择器样式 */
.hardware-selector {
  background-color: #ffffff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin: 0 30rpx 30rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
}

.selector-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333333;
  margin-bottom: 20rpx;
  text-align: center;
}

.selector-items {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.selector-item {
  padding: 20rpx;
  border: 2rpx solid #e0e0e0;
  border-radius: 16rpx;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  transition: all 0.3s ease;
  position: relative;
  cursor: pointer;
}

.selector-item.selected {
  border-color: #667eea;
  background-color: rgba(102, 126, 234, 0.05);
  transform: translateY(-2rpx);
  box-shadow: 0 4rpx 12rpx rgba(102, 126, 234, 0.2);
}

.selector-brand {
  display: inline-block;
  padding: 6rpx 16rpx;
  border-radius: 30rpx;
  font-size: 22rpx;
  font-weight: bold;
  color: #ffffff;
  align-self: flex-start;
}

.selector-model {
  font-size: 28rpx;
  font-weight: bold;
  color: #333333;
  line-height: 1.3;
}

.selector-price {
  font-size: 26rpx;
  font-weight: bold;
  color: #ff6b00;
  background-color: rgba(255, 107, 0, 0.1);
  padding: 6rpx 12rpx;
  border-radius: 16rpx;
  align-self: flex-start;
}

.selector-position {
  position: absolute;
  top: 20rpx;
  right: 20rpx;
  font-size: 22rpx;
  font-weight: bold;
  color: #667eea;
  background-color: rgba(102, 126, 234, 0.1);
  padding: 4rpx 12rpx;
  border-radius: 30rpx;
}

.card-header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16rpx;
}
</style>
