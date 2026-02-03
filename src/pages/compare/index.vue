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
import { ref, computed, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useCompareStore } from '../../stores/compare'
import { useHardwareList } from '../../composables/useCloudData'
import type { CpuSpecs, GpuSpecs, PhoneSpecs } from '../../types/hardware'

// Pinia store
const compareStore = useCompareStore()

// 路由参数
const queryParams = ref<{ type?: 'cpu' | 'gpu' | 'phone' }>({})

// 使用云数据库 Hook 加载完整数据
const cpuListHook = useHardwareList<CpuSpecs>('cpu_collection', {
  orderBy: {
    field: 'releaseDate',
    order: 'desc'
  },
  withCount: true
})

const gpuListHook = useHardwareList<GpuSpecs>('gpu_collection', {
  orderBy: {
    field: 'releaseDate',
    order: 'desc'
  },
  withCount: true
})

const phoneListHook = useHardwareList<PhoneSpecs>('phone_collection', {
  orderBy: {
    field: 'releaseDate',
    order: 'desc'
  },
  withCount: true
})

// 页面加载时初始化数据
onMounted(() => {
  // 初始加载数据
  if (compareType.value === 'cpu') {
    cpuListHook.refresh()
  } else if (compareType.value === 'gpu') {
    gpuListHook.refresh()
  } else {
    phoneListHook.refresh()
  }
})

// 安全解析工具函数
const safeParse = {
  // 解析CPU核心数，如 "8P+16E" -> 24
  parseCores: (cores: string): number => {
    if (!cores) return 0
    try {
      // 处理 "8P+16E" 格式
      const parts = cores.split('+')
      let total = 0
      for (const part of parts) {
        // 提取数字部分
        const match = part.match(/\d+/)
        if (match) {
          total += parseInt(match[0], 10)
        }
      }
      return total || 0
    } catch {
      return 0
    }
  },

  // 解析频率，如 "5.2 GHz" -> 5.2
  parseFrequency: (freq: string | number): number => {
    if (typeof freq === 'number') return freq
    if (!freq) return 0
    try {
      // 提取数字部分
      const match = freq.toString().match(/(\d+(\.\d+)?)/)
      return match ? parseFloat(match[1]) : 0
    } catch {
      return 0
    }
  },

  // 解析存储，如 "256 GB" -> 256
  parseStorage: (storage: string | number): number => {
    if (typeof storage === 'number') return storage
    if (!storage) return 0
    try {
      // 提取数字部分
      const match = storage.toString().match(/(\d+(\.\d+)?)/)
      return match ? parseFloat(match[1]) : 0
    } catch {
      return 0
    }
  },

  // 安全数值比较，避免NaN
  safeCompare: (a: any, b: any, isLowerBetter = false): { left: number; right: number; winner: 'left' | 'right' | null } => {
    const leftNum = typeof a === 'number' ? a : parseFloat(a)
    const rightNum = typeof b === 'number' ? b : parseFloat(b)
    
    // 处理NaN
    const leftValid = !isNaN(leftNum) && isFinite(leftNum)
    const rightValid = !isNaN(rightNum) && isFinite(rightNum)
    
    if (!leftValid && !rightValid) {
      return { left: 50, right: 50, winner: null }
    }
    if (!leftValid) {
      return { left: 0, right: 100, winner: 'right' }
    }
    if (!rightValid) {
      return { left: 100, right: 0, winner: 'left' }
    }
    
    const max = Math.max(leftNum, rightNum)
    const min = Math.min(leftNum, rightNum)
    
    // 避免除以零
    const leftPercent = max > 0 ? (leftNum / max) * 100 : 50
    const rightPercent = max > 0 ? (rightNum / max) * 100 : 50
    
    let winner: 'left' | 'right' | null = null
    if (isLowerBetter) {
      winner = leftNum < rightNum ? 'left' : rightNum < leftNum ? 'right' : null
    } else {
      winner = leftNum > rightNum ? 'left' : rightNum > leftNum ? 'right' : null
    }
    
    return { left: leftPercent, right: rightPercent, winner }
  }
}

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

// 根据ID从云数据库或本地数据中查找完整硬件信息
const findHardwareById = (id: string, type: 'cpu' | 'gpu' | 'phone') => {
  // 获取对应的数据源
  const dataSource = type === 'cpu' 
    ? cpuListHook.list.value 
    : type === 'gpu'
    ? gpuListHook.list.value
    : phoneListHook.list.value
  
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

// 获取硬件参数（与详情页面保持一致的逻辑）
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
  if (type === 'cpu' && 'cores' in item) {
    const cpuData = item as CpuSpecs
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
  if (type === 'gpu' && 'vram' in item) {
    const gpuData = item as GpuSpecs
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
  
  // 手机 特有参数（详情页面没有手机参数，但对比页面需要）
  if (type === 'phone' && 'ram' in item) {
    const phoneData = item as PhoneSpecs
    params.push(
      { label: '处理器', value: phoneData.processor, desc: '' },
      { label: '内存', value: `${phoneData.ram} GB`, desc: '' },
      { label: '存储', value: `${phoneData.storage} GB`, desc: '' },
      { label: '屏幕尺寸', value: `${phoneData.screenSize} 英寸`, desc: '' },
      { label: '分辨率', value: phoneData.resolution, desc: '' },
      { label: '刷新率', value: `${phoneData.refreshRate} Hz`, desc: '' },
      { label: '电池容量', value: `${phoneData.batteryCapacity} mAh`, desc: '' },
      { label: '摄像头', value: phoneData.camera, desc: '' },
      { label: '操作系统', value: phoneData.os, desc: '' },
      { label: '5G支持', value: phoneData.support5G ? '支持' : '不支持', desc: '' }
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
  
  // 价格对比（越低越好）- 使用安全比较避免NaN
  const priceComparison = safeParse.safeCompare(left.price, right.price, true)
  results.push({
    label: '价格',
    leftValue: `¥${left.price.toLocaleString()}`,
    rightValue: `¥${right.price.toLocaleString()}`,
    leftPercent: priceComparison.left,
    rightPercent: priceComparison.right,
    winner: priceComparison.winner
  })
  
  // CPU 对比项
  if (compareType.value === 'cpu') {
    const leftCpu = left as CpuSpecs
    const rightCpu = right as CpuSpecs
    
    // 核心数量 - 使用安全解析
    const leftCores = safeParse.parseCores(leftCpu.cores)
    const rightCores = safeParse.parseCores(rightCpu.cores)
    const coresComparison = safeParse.safeCompare(leftCores, rightCores)
    results.push({
      label: '核心总数',
      leftValue: `${leftCores}核`,
      rightValue: `${rightCores}核`,
      leftPercent: coresComparison.left,
      rightPercent: coresComparison.right,
      winner: coresComparison.winner
    })
    
    // 最高频率 - 使用安全解析
    const leftBoost = safeParse.parseFrequency(leftCpu.boostClock)
    const rightBoost = safeParse.parseFrequency(rightCpu.boostClock)
    const freqComparison = safeParse.safeCompare(leftBoost, rightBoost)
    results.push({
      label: '最高频率',
      leftValue: `${leftCpu.boostClock} GHz`,
      rightValue: `${rightCpu.boostClock} GHz`,
      leftPercent: freqComparison.left,
      rightPercent: freqComparison.right,
      winner: freqComparison.winner
    })
    
    // 缓存大小
    const cacheComparison = safeParse.safeCompare(leftCpu.cache, rightCpu.cache)
    results.push({
      label: '缓存',
      leftValue: `${leftCpu.cache} MB`,
      rightValue: `${rightCpu.cache} MB`,
      leftPercent: cacheComparison.left,
      rightPercent: cacheComparison.right,
      winner: cacheComparison.winner
    })
    
    // 功耗（越低越好）
    const tdpComparison = safeParse.safeCompare(leftCpu.tdp, rightCpu.tdp, true)
    results.push({
      label: '功耗',
      leftValue: `${leftCpu.tdp} W`,
      rightValue: `${rightCpu.tdp} W`,
      leftPercent: tdpComparison.left,
      rightPercent: tdpComparison.right,
      winner: tdpComparison.winner
    })
  }
  
  // GPU 对比项
  if (compareType.value === 'gpu') {
    const leftGpu = left as GpuSpecs
    const rightGpu = right as GpuSpecs
    
    // 显存
    const vramComparison = safeParse.safeCompare(leftGpu.vram, rightGpu.vram)
    results.push({
      label: '显存',
      leftValue: `${leftGpu.vram} GB`,
      rightValue: `${rightGpu.vram} GB`,
      leftPercent: vramComparison.left,
      rightPercent: vramComparison.right,
      winner: vramComparison.winner
    })
    
    // CUDA核心
    const coresComparison = safeParse.safeCompare(leftGpu.cudaCores, rightGpu.cudaCores)
    results.push({
      label: 'CUDA核心',
      leftValue: leftGpu.cudaCores.toLocaleString(),
      rightValue: rightGpu.cudaCores.toLocaleString(),
      leftPercent: coresComparison.left,
      rightPercent: coresComparison.right,
      winner: coresComparison.winner
    })
    
    // 核心频率
    const clockComparison = safeParse.safeCompare(leftGpu.coreClock, rightGpu.coreClock)
    results.push({
      label: '核心频率',
      leftValue: `${leftGpu.coreClock} MHz`,
      rightValue: `${rightGpu.coreClock} MHz`,
      leftPercent: clockComparison.left,
      rightPercent: clockComparison.right,
      winner: clockComparison.winner
    })
    
    // 功耗（越低越好）
    const powerComparison = safeParse.safeCompare(leftGpu.powerConsumption, rightGpu.powerConsumption, true)
    results.push({
      label: '功耗',
      leftValue: `${leftGpu.powerConsumption} W`,
      rightValue: `${rightGpu.powerConsumption} W`,
      leftPercent: powerComparison.left,
      rightPercent: powerComparison.right,
      winner: powerComparison.winner
    })
    
    // 光线追踪 - 处理可能缺失的技术
    if (leftGpu.rayTracing !== undefined && rightGpu.rayTracing !== undefined) {
      const rtLeft = leftGpu.rayTracing ? 100 : 0
      const rtRight = rightGpu.rayTracing ? 100 : 0
      const rtComparison = safeParse.safeCompare(rtLeft, rtRight)
      results.push({
        label: '光线追踪',
        leftValue: leftGpu.rayTracing ? '支持' : '不支持',
        rightValue: rightGpu.rayTracing ? '支持' : '不支持',
        leftPercent: rtComparison.left,
        rightPercent: rtComparison.right,
        winner: rtComparison.winner
      })
    }
  }
  
  // 手机 对比项
  if (compareType.value === 'phone') {
    const leftPhone = left as PhoneSpecs
    const rightPhone = right as PhoneSpecs
    
    // 内存
    const ramComparison = safeParse.safeCompare(leftPhone.ram, rightPhone.ram)
    results.push({
      label: '内存',
      leftValue: `${leftPhone.ram} GB`,
      rightValue: `${rightPhone.ram} GB`,
      leftPercent: ramComparison.left,
      rightPercent: ramComparison.right,
      winner: ramComparison.winner
    })
    
    // 存储
    const storageComparison = safeParse.safeCompare(leftPhone.storage, rightPhone.storage)
    results.push({
      label: '存储',
      leftValue: `${leftPhone.storage} GB`,
      rightValue: `${rightPhone.storage} GB`,
      leftPercent: storageComparison.left,
      rightPercent: storageComparison.right,
      winner: storageComparison.winner
    })
    
    // 屏幕尺寸
    const screenComparison = safeParse.safeCompare(leftPhone.screenSize, rightPhone.screenSize)
    results.push({
      label: '屏幕尺寸',
      leftValue: `${leftPhone.screenSize} 英寸`,
      rightValue: `${rightPhone.screenSize} 英寸`,
      leftPercent: screenComparison.left,
      rightPercent: screenComparison.right,
      winner: screenComparison.winner
    })
    
    // 电池容量
    const batteryComparison = safeParse.safeCompare(leftPhone.batteryCapacity, rightPhone.batteryCapacity)
    results.push({
      label: '电池容量',
      leftValue: `${leftPhone.batteryCapacity} mAh`,
      rightValue: `${rightPhone.batteryCapacity} mAh`,
      leftPercent: batteryComparison.left,
      rightPercent: batteryComparison.right,
      winner: batteryComparison.winner
    })
    
    // 刷新率
    const refreshComparison = safeParse.safeCompare(leftPhone.refreshRate, rightPhone.refreshRate)
    results.push({
      label: '刷新率',
      leftValue: `${leftPhone.refreshRate} Hz`,
      rightValue: `${rightPhone.refreshRate} Hz`,
      leftPercent: refreshComparison.left,
      rightPercent: refreshComparison.right,
      winner: refreshComparison.winner
    })
    
    // 5G支持 - 处理可能缺失的技术
    if (leftPhone.support5G !== undefined && rightPhone.support5G !== undefined) {
      const g5Left = leftPhone.support5G ? 100 : 0
      const g5Right = rightPhone.support5G ? 100 : 0
      const g5Comparison = safeParse.safeCompare(g5Left, g5Right)
      results.push({
        label: '5G支持',
        leftValue: leftPhone.support5G ? '支持' : '不支持',
        rightValue: rightPhone.support5G ? '支持' : '不支持',
        leftPercent: g5Comparison.left,
        rightPercent: g5Comparison.right,
        winner: g5Comparison.winner
      })
    }
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
  // 获取页面栈信息
  const pages = getCurrentPages()
  
  // 如果页面栈长度大于1，说明有上一页，可以返回
  if (pages.length > 1) {
    uni.navigateBack()
  } else {
    // 如果页面栈长度等于1，说明是第一个页面（可能是通过tabbar直接进入）
    // 切换到首页tab
    uni.switchTab({
      url: '/pages/index/index',
      fail: (err) => {
        console.error('切换tab失败:', err)
        // 如果切换tab失败，尝试跳转到首页
        uni.navigateTo({
          url: '/pages/index/index'
        })
      }
    })
  }
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
          // 获取页面栈信息
          const pages = getCurrentPages()
          
          // 如果页面栈长度大于1，说明有上一页，可以返回
          if (pages.length > 1) {
            uni.navigateBack()
          } else {
            // 如果页面栈长度等于1，说明是第一个页面（可能是通过tabbar直接进入）
            // 切换到首页tab
            uni.switchTab({
              url: '/pages/index/index',
              fail: (err) => {
                console.error('切换tab失败:', err)
                // 如果切换tab失败，尝试跳转到首页
                uni.navigateTo({
                  url: '/pages/index/index'
                })
              }
            })
          }
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
  align-items: stretch; /* 确保列高度一致 */
}

.compare-column {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.hardware-card {
  flex: 1; /* 确保卡片填充整个列高度 */
  display: flex;
  flex-direction: column;
}

.card-body {
  flex: 1; /* 确保内容区域填充剩余空间 */
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
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
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
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
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
