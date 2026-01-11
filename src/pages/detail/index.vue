<template>
  <view class="detail-page">
    <!-- 头部信息 -->
    <view class="header-section">
      <view class="model-name">{{ hardwareData?.model || '加载中...' }}</view>
      <view class="release-date">发布日期：{{ hardwareData?.releaseDate || '-' }}</view>
      <view class="brand-tag" :class="getBrandClass(hardwareData?.brand || '')">
        {{ hardwareData?.brand || '' }}
      </view>
    </view>

    <!-- 参数表格 -->
    <view class="params-section">
      <wd-cell-group title="详细参数" border>
        <wd-cell
          v-for="param in hardwareParams"
          :key="param.label"
          :title="param.label"
          :value="param.value"
          :label="param.desc"
        />
      </wd-cell-group>
    </view>

    <!-- 性能雷达图 -->
    <view class="chart-section" v-if="radarData.categories.length > 0">
      <view class="section-title">性能雷达图</view>
      <view class="chart-container">
        <qiun-data-charts
          type="radar"
          :chartData="radarData"
          :opts="chartOptions"
          canvasId="hardware-radar"
          canvas2d
        />
      </view>
      <view class="chart-legend">
        <view class="legend-item" v-for="item in radarLegend" :key="item.name">
          <view class="legend-color" :style="{ backgroundColor: item.color }"></view>
          <text class="legend-text">{{ item.name }}: {{ item.value }}分</text>
        </view>
      </view>
    </view>

    <!-- 底部动作栏 -->
    <view class="action-bar">
      <wd-button
        type="primary"
        block
        size="large"
        @click="handleAddToCompare"
      >
        加入对比
      </wd-button>
    </view>

    <!-- 加载状态 -->
    <wd-loading v-if="loading" text="加载中..." vertical />
    
    <!-- 错误状态 -->
    <view v-else-if="!hardwareData && !loading" class="error-state">
      <text class="error-text">未找到硬件信息</text>
      <wd-button type="default" @click="handleBack">返回列表</wd-button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import type { CpuSpecs, GpuSpecs } from '../../types/hardware'

// 路由参数
const queryParams = ref<{ id?: string; type?: 'cpu' | 'gpu' }>({})

// 响应式数据
const loading = ref(true)
const hardwareData = ref<CpuSpecs | GpuSpecs | null>(null)

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

// 页面加载
onLoad((options) => {
  queryParams.value = options || {}
  loadHardwareData()
})

// 加载硬件数据
const loadHardwareData = () => {
  loading.value = true
  
  setTimeout(() => {
    const { id, type } = queryParams.value
    
    if (!id || !type) {
      hardwareData.value = null
      loading.value = false
      return
    }
    
    const dataSource = type === 'cpu' ? cpuMockData : gpuMockData
    const found = dataSource.find(item => item.id === id)
    
    hardwareData.value = found || null
    loading.value = false
  }, 300) // 模拟加载延迟
}

// 获取品牌样式类
const getBrandClass = (brand: string) => {
  switch (brand) {
    case 'Intel': return 'brand-intel'
    case 'AMD': return 'brand-amd'
    case 'NVIDIA': return 'brand-nvidia'
    default: return 'brand-other'
  }
}

// 硬件参数列表
const hardwareParams = computed(() => {
  if (!hardwareData.value) return []
  
  const data = hardwareData.value
  const params = []
  
  // 通用参数
  params.push(
    { label: '型号', value: data.model, desc: '' },
    { label: '品牌', value: data.brand, desc: '' },
    { label: '参考价格', value: `¥${data.price.toLocaleString()}`, desc: '' },
    { label: '发布日期', value: data.releaseDate, desc: '' }
  )
  
  // CPU 特有参数
  if (queryParams.value.type === 'cpu' && 'cores' in data) {
    const cpuData = data as CpuSpecs
    params.push(
      { label: '核心配置', value: cpuData.cores, desc: '性能核+能效核' },
      { label: '频率范围', value: `${cpuData.baseClock}-${cpuData.boostClock} GHz`, desc: '基础-最大加速频率' },
      { label: '接口', value: cpuData.socket, desc: '' },
      { label: '热设计功耗', value: `${cpuData.tdp} W`, desc: '' },
      { label: '缓存', value: `${cpuData.cache} MB`, desc: '' },
      { label: '集成显卡', value: cpuData.integratedGraphics ? '是' : '否', desc: '' }
    )
  }
  
  // GPU 特有参数
  if (queryParams.value.type === 'gpu' && 'vram' in data) {
    const gpuData = data as GpuSpecs
    params.push(
      { label: '显存', value: `${gpuData.vram} GB`, desc: '' },
      { label: '位宽', value: `${gpuData.busWidth} bit`, desc: '' },
      { label: 'CUDA核心', value: gpuData.cudaCores.toLocaleString(), desc: '流处理器数量' },
      { label: '核心频率', value: `${gpuData.coreClock} MHz`, desc: '' },
      { label: '显存频率', value: `${gpuData.memoryClock} MHz`, desc: '' },
      { label: '功耗', value: `${gpuData.powerConsumption} W`, desc: '' },
      { label: '光线追踪', value: gpuData.rayTracing ? '支持' : '不支持', desc: '' },
      { label: '超分辨率', value: gpuData.upscalingTech, desc: '' }
    )
  }
  
  return params
})

// 生成雷达图数据
const radarData = computed(() => {
  if (!hardwareData.value) {
    return {
      categories: [],
      series: []
    }
  }
  
  const data = hardwareData.value
  
  // 根据硬件参数生成雷达图数据
  let performance = 85
  let powerEfficiency = 70
  let costPerformance = 75
  let popularity = 80
  let novelty = 90
  
  // 根据价格调整性价比
  if (data.price > 10000) {
    costPerformance = 60
    popularity = 85
  } else if (data.price > 5000) {
    costPerformance = 70
    popularity = 80
  } else {
    costPerformance = 85
    popularity = 75
  }
  
  // 根据发布日期调整新旧程度
  const releaseDate = new Date(data.releaseDate)
  const now = new Date()
  const monthsDiff = (now.getFullYear() - releaseDate.getFullYear()) * 12 + 
                    (now.getMonth() - releaseDate.getMonth())
  
  if (monthsDiff <= 3) {
    novelty = 95
  } else if (monthsDiff <= 6) {
    novelty = 85
  } else if (monthsDiff <= 12) {
    novelty = 75
  } else {
    novelty = 60
  }
  
  // 品牌加成
  if (data.brand === 'NVIDIA') {
    performance += 5
    popularity += 10
  } else if (data.brand === 'Intel') {
    performance += 3
    powerEfficiency += 5
  } else if (data.brand === 'AMD') {
    costPerformance += 10
    powerEfficiency += 3
  }
  
  return {
    categories: ['性能', '功耗', '性价比', '热度', '新旧程度'],
    series: [
      {
        name: data.model,
        data: [performance, powerEfficiency, costPerformance, popularity, novelty],
        color: '#2979ff'
      }
    ]
  }
})

// 雷达图图例
const radarLegend = computed(() => {
  if (!radarData.value.series[0]) return []
  
  const series = radarData.value.series[0]
  return radarData.value.categories.map((category, index) => ({
    name: category,
    value: series.data[index],
    color: series.color
  }))
})

// 图表配置
const chartOptions = {
  padding: [20, 20, 20, 20],
  dataLabel: true,
  legend: {
    show: false
  },
  extra: {
    radar: {
      gridColor: '#e0e0e0',
      gridCount: 3,
      opacity: 0.3,
      labelColor: '#666666',
      max: 100
    }
  }
}

// 加入对比
const handleAddToCompare = () => {
  console.log('加入对比:', hardwareData.value)
  uni.showToast({
    title: '已加入对比',
    icon: 'success'
  })
}

// 返回列表
const handleBack = () => {
  uni.navigateBack()
}
</script>

<style scoped lang="scss">
.detail-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 120rpx;
}

.header-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 60rpx 40rpx 40rpx;
  color: #ffffff;
  position: relative;
}

.model-name {
  font-size: 48rpx;
  font-weight: bold;
  margin-bottom: 16rpx;
  line-height: 1.3;
}

.release-date {
  font-size: 28rpx;
  opacity: 0.9;
  margin-bottom: 24rpx;
}

.brand-tag {
  display: inline-block;
  padding: 8rpx 24rpx;
  border-radius: 40rpx;
  font-size: 24rpx;
  font-weight: bold;
  background-color: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10rpx);
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

.brand-other {
  background: linear-gradient(135deg, #666666, #999999);
}

.params-section {
  margin: 30rpx;
  border-radius: 16rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
}

.chart-section {
  margin: 30rpx;
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333333;
  margin-bottom: 30rpx;
}

.chart-container {
  height: 500rpx;
  width: 100%;
}

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
  margin-top: 30rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid #f0f0f0;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.legend-color {
  width: 24rpx;
  height: 24rpx;
  border-radius: 4rpx;
}

.legend-text {
  font-size: 26rpx;
  color: #666666;
}

.action-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20rpx 30rpx;
  background-color: #ffffff;
  box-shadow: 0 -4rpx 12rpx rgba(0, 0, 0, 0.08);
  z-index: 100;
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 30rpx;
  text-align: center;
}

.error-text {
  font-size: 32rpx;
  color: #999999;
  margin-bottom: 40rpx;
}
</style>
