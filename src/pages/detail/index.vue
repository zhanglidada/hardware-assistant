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
      <view class="action-buttons">
        <wd-button
          type="default"
          size="large"
          @click="handleToggleFavorite"
          :custom-class="isFavorited ? 'favorited' : ''"
        >
          <text class="favorite-icon">{{ isFavorited ? '★' : '☆' }}</text>
          {{ isFavorited ? '已收藏' : '收藏' }}
        </wd-button>
        <wd-button
          type="primary"
          size="large"
          @click="handleAddToCompare"
        >
          加入对比
        </wd-button>
      </view>
    </view>

    <!-- 加载状态 -->
    <view v-if="loading" class="loading-state">
      <wd-loading text="加载中..." vertical />
    </view>
    
    <!-- 错误状态 -->
    <view v-else-if="error" class="error-state">
      <text class="error-text">{{ error }}</text>
      <view class="error-actions">
        <wd-button type="default" @click="handleBack" plain>返回列表</wd-button>
        <wd-button type="primary" @click="handleRetry">重试</wd-button>
      </view>
    </view>
    
    <!-- 数据为空状态 -->
    <view v-else-if="!hardwareData && !loading" class="empty-state">
      <text class="empty-text">未找到硬件信息</text>
      <wd-button type="default" @click="handleBack">返回列表</wd-button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useCompareStore } from '../../stores/compare'
import { useFavoritesStore } from '../../stores/favorites'
import type { CpuSpecs, GpuSpecs, PhoneSpecs } from '../../types/hardware'

// 路由参数
const queryParams = ref<{ id?: string; type?: 'cpu' | 'gpu' | 'phone' }>({})

// Pinia store
const compareStore = useCompareStore()
const favoritesStore = useFavoritesStore()

// 响应式数据
const loading = ref(true)
const error = ref<string | null>(null)
const hardwareData = ref<CpuSpecs | GpuSpecs | PhoneSpecs | null>(null)

// 页面加载
onLoad((options) => {
  queryParams.value = options || {}
  loadHardwareData()
})

// 检查是否支持微信云开发
const isCloudSupported = computed(() => {
  return typeof wx !== 'undefined' && wx.cloud
})

// 获取集合名称
const getCollectionName = () => {
  const type = queryParams.value.type
  switch (type) {
    case 'cpu':
      return 'cpu_collection'
    case 'gpu':
      return 'gpu_collection'
    case 'phone':
      return 'phone_collection'
    default:
      return ''
  }
}

// 从本地 Mock 数据加载
const loadLocalHardwareData = async (id: string, type: 'cpu' | 'gpu' | 'phone') => {
  try {
    let module: any
    if (type === 'cpu') {
      module = await import('../../mock/cpu_data.json')
    } else if (type === 'gpu') {
      module = await import('../../mock/gpu_data.json')
    } else {
      module = await import('../../mock/phone_data.json')
    }

    const data = (module.default || module) as (CpuSpecs | GpuSpecs | PhoneSpecs)[]
    return data.find(item => item.id === id) || null
  } catch (localError) {
    console.error('本地数据加载失败:', localError)
    return null
  }
}

// 加载硬件数据
const loadHardwareData = async () => {
  const { id, type } = queryParams.value
  
  // 验证参数
  if (!id || !type) {
    error.value = '缺少必要参数'
    loading.value = false
    return
  }
  
  // 检查云开发支持，失败则降级本地数据
  if (!isCloudSupported.value) {
    const localData = await loadLocalHardwareData(id, type)
    if (localData) {
      hardwareData.value = localData
      loading.value = false
      return
    }
    error.value = '当前环境不支持微信云开发'
    loading.value = false
    return
  }
  
  const collectionName = getCollectionName()
  if (!collectionName) {
    error.value = '无效的硬件类型'
    loading.value = false
    return
  }
  
  loading.value = true
  error.value = null
  
  try {
    // 使用查询条件而不是文档ID，因为云数据库中的_id可能不是我们的id字段
    const result = await wx.cloud!.database()
      .collection(collectionName)
      .where({ id: id })  // 使用id字段查询，而不是文档_id
      .limit(1)
      .get()
    
    if (result.data && result.data.length > 0) {
      hardwareData.value = result.data[0] as CpuSpecs | GpuSpecs | PhoneSpecs
    } else {
      // 云数据为空时尝试本地降级
      const localData = await loadLocalHardwareData(id, type)
      if (localData) {
        hardwareData.value = localData
      } else {
        error.value = '未找到硬件信息'
        hardwareData.value = null
        
        // 显示错误提示
        uni.showToast({
          title: '未找到硬件信息',
          icon: 'error',
          duration: 2000
        })
      }
    }
  } catch (err: any) {
    console.error('加载硬件数据失败:', err)
    const localData = await loadLocalHardwareData(id, type)
    if (localData) {
      hardwareData.value = localData
      error.value = null
    } else {
      error.value = err.message || '数据加载失败'
      hardwareData.value = null
      
      // 显示错误提示
      uni.showToast({
        title: '数据加载失败',
        icon: 'error',
        duration: 2000
      })
    }
  } finally {
    loading.value = false
  }
}

// 重试加载
const handleRetry = () => {
  loadHardwareData()
}

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
  if (!hardwareData.value) {
    uni.showToast({
      title: '暂无可加入的数据',
      icon: 'none'
    })
    return
  }
  const result = compareStore.toggleCompare(hardwareData.value)
  uni.showToast({
    title: result.message,
    icon: result.added ? 'success' : 'none'
  })
}

// 收藏状态
const isFavorited = computed(() => {
  if (!hardwareData.value) return false
  return favoritesStore.isFavorite(hardwareData.value.id)
})

// 切换收藏状态
const handleToggleFavorite = () => {
  if (!hardwareData.value || !queryParams.value.type) {
    uni.showToast({
      title: '暂无可收藏的数据',
      icon: 'none'
    })
    return
  }
  
  const result = favoritesStore.toggleFavorite(hardwareData.value, queryParams.value.type)
  uni.showToast({
    title: result ? '已收藏' : '已取消收藏',
    icon: result ? 'success' : 'none'
  })
}

// 返回列表
const handleBack = () => {
  // 获取页面栈信息
  const pages = getCurrentPages()
  
  // 如果页面栈长度大于1，说明有上一页，可以返回
  if (pages.length > 1) {
    uni.navigateBack()
  } else {
    // 如果页面栈长度等于1，说明是第一个页面（可能是通过特殊方式进入）
    // 跳转到首页
    uni.navigateTo({
      url: '/pages/index/index',
      fail: (err) => {
        console.error('跳转失败:', err)
        // 如果跳转失败，尝试切换到首页tab
        uni.switchTab({
          url: '/pages/index/index'
        })
      }
    })
  }
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

.params-section {
  margin: 30rpx;
  border-radius: 16rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 0;
  text-align: center;
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 30rpx;
  text-align: center;
  gap: 30rpx;
}

.error-text {
  font-size: 28rpx;
  color: #ff4444;
  text-align: center;
}

.error-actions {
  display: flex;
  gap: 20rpx;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 30rpx;
  text-align: center;
}

.empty-text {
  font-size: 32rpx;
  color: #999999;
  margin-bottom: 40rpx;
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

.action-buttons {
  display: flex;
  gap: 20rpx;
}

.action-buttons .wd-button {
  flex: 1;
}

.favorite-icon {
  font-size: 32rpx;
  margin-right: 8rpx;
}

.favorited {
  background-color: #ff6700 !important;
  border-color: #ff6700 !important;
  color: #ffffff !important;
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
