<template>
  <view class="page-container">
    <view class="ranking-page">
      <!-- 头部 -->
      <view class="ranking-header">
        <view class="header-title">
          <text class="title-text">硬件性能排行</text>
          <text class="title-sub">权威榜单，一目了然</text>
        </view>
      </view>

      <!-- 排行榜类型标签 -->
      <view class="ranking-type">
        <view class="tabs-container">
          <view 
            v-for="tab in tabs" 
            :key="tab.name"
            class="tab-item"
            :class="{ active: activeTab === tab.name }"
            @click="handleTabClick(tab.name)"
          >
            <text class="tab-title">{{ tab.title }}</text>
            <text v-if="tab.name === 'cpu'" class="tab-arrow" :class="{ active: showCpuSubTabs }">▼</text>
            <text v-else-if="tab.name === 'gpu'" class="tab-arrow" :class="{ active: showGpuSubTabs }">▼</text>
          </view>
        </view>

        <!-- CPU 子选项 (展开式) -->
        <view v-if="showCpuSubTabs" class="cpu-sub-tabs">
          <view 
            class="sub-tab-item" 
            :class="{ active: activeCpuSubTab === 'all' }"
            @click="selectCpuSubTab('all')"
          >
            全部
          </view>
          <view 
            class="sub-tab-item" 
            :class="{ active: activeCpuSubTab === 'desktop' }"
            @click="selectCpuSubTab('desktop')"
          >
            桌面CPU
          </view>
          <view 
            class="sub-tab-item" 
            :class="{ active: activeCpuSubTab === 'mobile' }"
            @click="selectCpuSubTab('mobile')"
          >
            移动CPU
          </view>
        </view>

        <!-- GPU 子选项 (展开式) -->
        <view v-if="showGpuSubTabs" class="cpu-sub-tabs">
          <view 
            class="sub-tab-item" 
            :class="{ active: activeGpuSubTab === 'all' }"
            @click="selectGpuSubTab('all')"
          >
            全部
          </view>
          <view 
            class="sub-tab-item" 
            :class="{ active: activeGpuSubTab === 'desktop' }"
            @click="selectGpuSubTab('desktop')"
          >
            桌面显卡
          </view>
          <view 
            class="sub-tab-item" 
            :class="{ active: activeGpuSubTab === 'mobile' }"
            @click="selectGpuSubTab('mobile')"
          >
            移动端显卡
          </view>
          <view 
            class="sub-tab-item" 
            :class="{ active: activeGpuSubTab === 'integrated' }"
            @click="selectGpuSubTab('integrated')"
          >
            核显
          </view>
        </view>
      </view>

      <!-- 排行榜列表 -->
      <view class="ranking-list">
        <!-- 骨架屏加载状态 -->
        <view v-if="currentLoading && rankingList.length === 0" class="skeleton-container">
          <wd-skeleton
            v-for="i in 5"
            :key="i"
            class="skeleton-item"
            :row="2"
            :row-width="['70%', '50%']"
            :title="true"
            title-width="40%"
          />
        </view>
        
        <!-- 错误状态 -->
        <view v-else-if="currentError" class="error-state">
          <text class="error-text">{{ currentError }}</text>
          <wd-button type="primary" size="small" @click="loadRankingData">重试</wd-button>
        </view>
        
        <!-- 排行榜数据 -->
        <view v-else-if="rankingList.length > 0" class="ranking-items">
          <view
            v-for="(item, index) in rankingList"
            :key="item.id"
            class="ranking-item"
            @click="handleItemClick(item)"
          >
            <!-- 排名序号 -->
            <view class="rank-number" :class="getRankClass(index)">
              {{ index + 1 }}
            </view>
            
            <!-- 硬件信息 -->
            <view class="hardware-info">
              <view class="info-top">
                <view class="brand-model">
                  <view class="brand-tag" :class="getBrandClass(item.brand)">
                    {{ item.brand }}
                  </view>
                  <text class="model-text">{{ item.model }}</text>
                </view>
                <view class="score-favorite-row">
                  <view class="score-badge">
                    <text class="score-text">{{ getHardwareScore(item) }}</text>
                    <text class="score-label">分</text>
                  </view>
                  <view class="favorite-action" @click.stop="handleToggleFavorite(item)">
                    <image 
                      :src="isItemFavorited(item) ? '/static/tabbar/collect-active.png' : '/static/tabbar/collect.png'" 
                      class="favorite-icon"
                      mode="aspectFit"
                    />
                  </view>
                </view>
              </view>
              
              <view class="info-bottom">
                <!-- 规格标签 -->
                <view class="spec-tags">
                  <template v-if="activeTab === 'cpu'">
                    <view class="spec-tag">
                      <text class="spec-label">核心</text>
                      <text class="spec-value">{{ (item as CpuSpecs).cores }}</text>
                    </view>
                    <view class="spec-tag">
                      <text class="spec-label">频率</text>
                      <text class="spec-value">{{ (item as CpuSpecs).boostClock }}GHz</text>
                    </view>
                    <view class="spec-tag">
                      <text class="spec-label">缓存</text>
                      <text class="spec-value">{{ (item as CpuSpecs).cache }}MB</text>
                    </view>
                  </template>
                  <template v-else-if="activeTab === 'gpu'">
                    <view class="spec-tag">
                      <text class="spec-label">显存</text>
                      <text class="spec-value">{{ (item as GpuSpecs).vram }}GB</text>
                    </view>
                    <view class="spec-tag">
                      <text class="spec-label">核心</text>
                      <text class="spec-value">{{ (item as GpuSpecs).cudaCores.toLocaleString() }}</text>
                    </view>
                    <view class="spec-tag">
                      <text class="spec-label">频率</text>
                      <text class="spec-value">{{ (item as GpuSpecs).coreClock }}MHz</text>
                    </view>
                  </template>
                  <template v-else>
                    <view class="spec-tag">
                      <text class="spec-label">内存</text>
                      <text class="spec-value">{{ (item as PhoneSpecs).ram }}GB</text>
                    </view>
                    <view class="spec-tag">
                      <text class="spec-label">存储</text>
                      <text class="spec-value">{{ (item as PhoneSpecs).storage }}GB</text>
                    </view>
                    <view class="spec-tag">
                      <text class="spec-label">处理器</text>
                      <text class="spec-value">{{ (item as PhoneSpecs).processor }}</text>
                    </view>
                  </template>
                </view>
                

              </view>
            </view>
          </view>
        </view>

        <!-- 空状态 -->
        <view v-else class="empty-state">
          <view class="empty-icon">🏆</view>
          <text class="empty-text">暂无排行数据</text>
          <text class="empty-hint">请稍后再试</text>
        </view>
      </view>

      <!-- 底部说明 -->
      <view class="ranking-footer">
        <text class="footer-text">* 排行榜基于硬件参数综合计算得出，仅供参考</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useCompareStore } from '../../stores/compare'
import { useHardwareList } from '../../composables/useCloudData'
import type { CpuSpecs, GpuSpecs, PhoneSpecs } from '../../types/hardware'

// Pinia store
const compareStore = useCompareStore()

// 响应式数据
const activeTab = ref<'cpu' | 'gpu' | 'phone'>('cpu')
const activeCpuSubTab = ref<'all' | 'desktop' | 'mobile'>('all')
const activeGpuSubTab = ref<'all' | 'desktop' | 'mobile' | 'integrated'>('all')
const showCpuSubTabs = ref(false)
const showGpuSubTabs = ref(false)

// 标签定义
const tabs = [
  { name: 'cpu', title: 'CPU性能榜' },
  { name: 'gpu', title: '显卡性能榜' },
  { name: 'phone', title: '手机性能榜' }
]

// 收藏状态管理
const favoriteItems = ref<Set<string>>(new Set())

// 使用云数据库 Hook 加载数据
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
  loadRankingData()
})

// 加载排行榜数据
const loadRankingData = () => {
  if (activeTab.value === 'cpu') {
    cpuListHook.refresh()
  } else if (activeTab.value === 'gpu') {
    gpuListHook.refresh()
  } else {
    phoneListHook.refresh()
  }
}

// Tab切换处理
const handleTabChange = (name: string) => {
  activeTab.value = name as 'cpu' | 'gpu' | 'phone'
  loadRankingData()
}

// Tab点击处理（支持展开/收起子选项）
const handleTabClick = (name: string) => {
  const tabName = name as 'cpu' | 'gpu' | 'phone'
  if (tabName === 'cpu' && activeTab.value === 'cpu') {
    // 如果当前已经选中CPU，再次点击则切换展开/收起状态
    showCpuSubTabs.value = !showCpuSubTabs.value
    showGpuSubTabs.value = false
  } else if (tabName === 'gpu' && activeTab.value === 'gpu') {
    // 如果当前已经选中GPU，再次点击则切换展开/收起状态
    showGpuSubTabs.value = !showGpuSubTabs.value
    showCpuSubTabs.value = false
  } else {
    // 切换到其他标签
    activeTab.value = tabName
    showCpuSubTabs.value = false
    showGpuSubTabs.value = false
    loadRankingData()
  }
}

// 选择CPU子选项
const selectCpuSubTab = (subTab: 'all' | 'desktop' | 'mobile') => {
  activeCpuSubTab.value = subTab
  showCpuSubTabs.value = false
  // 不需要重新加载数据，因为rankingList计算属性会自动响应变化
}

// 选择GPU子选项
const selectGpuSubTab = (subTab: 'all' | 'desktop' | 'mobile' | 'integrated') => {
  activeGpuSubTab.value = subTab
  showGpuSubTabs.value = false
  // 不需要重新加载数据，因为rankingList计算属性会自动响应变化
}

// 获取当前数据源
const currentDataSource = computed(() => {
  if (activeTab.value === 'cpu') {
    return cpuListHook.list.value
  } else if (activeTab.value === 'gpu') {
    return gpuListHook.list.value
  } else {
    return phoneListHook.list.value
  }
})

// 获取当前加载状态
const currentLoading = computed(() => {
  if (activeTab.value === 'cpu') {
    return cpuListHook.loading.value
  } else if (activeTab.value === 'gpu') {
    return gpuListHook.loading.value
  } else {
    return phoneListHook.loading.value
  }
})

// 获取当前错误状态
const currentError = computed(() => {
  if (activeTab.value === 'cpu') {
    return cpuListHook.error.value
  } else if (activeTab.value === 'gpu') {
    return gpuListHook.error.value
  } else {
    return phoneListHook.error.value
  }
})

// 计算硬件综合得分
const getHardwareScore = (item: CpuSpecs | GpuSpecs | PhoneSpecs): number => {
  let score = 0
  
  // 基础分：价格越低得分越高（价格在1000-10000之间）
  const priceScore = Math.max(0, 100 - (item.price / 100))
  score += priceScore * 0.3
  
  if (activeTab.value === 'cpu') {
    const cpu = item as CpuSpecs
    // 核心数得分
    const cores = parseInt(cpu.cores.toString()) || 0
    score += Math.min(cores * 5, 50) * 0.3
    
    // 频率得分
    const freqScore = Math.min(cpu.boostClock * 10, 50)
    score += freqScore * 0.2
    
    // 缓存得分
    const cacheScore = Math.min(cpu.cache / 2, 20)
    score += cacheScore * 0.2
  } else if (activeTab.value === 'gpu') {
    const gpu = item as GpuSpecs
    // 显存得分
    score += Math.min(gpu.vram * 10, 40) * 0.3
    
    // CUDA核心得分
    const coresScore = Math.min(gpu.cudaCores / 100, 40)
    score += coresScore * 0.3
    
    // 频率得分
    const freqScore = Math.min(gpu.coreClock / 100, 20)
    score += freqScore * 0.2
    
    // 光线追踪加分
    if (gpu.rayTracing) {
      score += 10
    }
  } else {
    const phone = item as PhoneSpecs
    // 内存得分
    score += Math.min(phone.ram * 10, 30) * 0.3
    
    // 存储得分
    const storageScore = Math.min(phone.storage / 10, 30)
    score += storageScore * 0.3
    
    // 电池容量得分
    const batteryScore = Math.min(phone.batteryCapacity / 100, 20)
    score += batteryScore * 0.2
    
    // 5G支持加分
    if (phone.support5G) {
      score += 10
    }
  }
  
  return Math.round(score)
}

// 获取排序后的排行榜列表
const rankingList = computed(() => {
  let data = [...currentDataSource.value]

  // CPU 子榜单过滤
  if (activeTab.value === 'cpu' && activeCpuSubTab.value !== 'all') {
    data = data.filter(item => {
      const cpu = item as CpuSpecs
      const model = (cpu.model || '').toUpperCase()
      const socket = (cpu.socket || '').toUpperCase()
      
      // 移动端判断逻辑:
      // 1. 接口包含 BGA (通常是焊接在主板上的移动端CPU)
      // 2. 型号包含 Mobile/Laptop 等关键词
      // 3. 型号以移动端常见后缀结尾 (H, U, Y, M, HX等)
      const isMobile = socket.includes('BGA') || 
                       model.includes('MOBILE') ||
                       model.includes('LAPTOP') ||
                       /[0-9]\s*(H|HQ|HK|U|Y|M|HS|HX|G[1-7])(\s|$)/.test(model)
      
      return activeCpuSubTab.value === 'mobile' ? isMobile : !isMobile
    })
  }
  
  // GPU 子榜单过滤
  if (activeTab.value === 'gpu' && activeGpuSubTab.value !== 'all') {
    data = data.filter(item => {
      const gpu = item as GpuSpecs
      const model = (gpu.model || '').toUpperCase()
      
      // 移动端判断逻辑:
      // 1. 型号包含 Mobile/Laptop 等关键词
      // 2. 型号以移动端常见后缀结尾 (M, Max-Q, Super 等)
      const isMobile = model.includes('MOBILE') ||
                       model.includes('LAPTOP') ||
                       model.includes('MAX-Q') ||
                       model.includes('MAXQ') ||
                       model.includes('M ')
      
      // 核显判断逻辑:
      const isIntegrated = model.includes('INTEGRATED') ||
                          model.includes('IGPU') ||
                          model.includes('UHD') ||
                          model.includes('Iris') ||
                          model.includes('Vega') ||
                          model.includes('Radeon') && model.includes('Integrated')
      
      if (activeGpuSubTab.value === 'desktop') {
        return !isMobile && !isIntegrated
      } else if (activeGpuSubTab.value === 'mobile') {
        return isMobile && !isIntegrated
      } else if (activeGpuSubTab.value === 'integrated') {
        return isIntegrated
      }
      
      return true
    })
  }
  
  // 按综合得分排序（从高到低）
  return data.sort((a, b) => {
    const scoreA = getHardwareScore(a)
    const scoreB = getHardwareScore(b)
    return scoreB - scoreA
  }).slice(0, 20) // 只显示前20名
})

// 获取排名样式类
const getRankClass = (index: number) => {
  if (index === 0) return 'rank-gold'
  if (index === 1) return 'rank-silver'
  if (index === 2) return 'rank-bronze'
  return 'rank-normal'
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

// 项目点击处理
const handleItemClick = (item: CpuSpecs | GpuSpecs | PhoneSpecs) => {
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

// 添加对比项
const handleAddCompare = (item: CpuSpecs | GpuSpecs | PhoneSpecs) => {
  const result = compareStore.toggleCompare(item)
  if (result.added) {
    uni.showToast({
      title: result.message,
      icon: 'success'
    })
  } else {
    uni.showToast({
      title: result.message,
      icon: 'none'
    })
  }
}

// 收藏功能方法
// 检查项目是否已收藏
const isItemFavorited = (item: CpuSpecs | GpuSpecs | PhoneSpecs) => {
  return favoriteItems.value.has(item.id)
}

// 切换收藏状态
const handleToggleFavorite = (item: CpuSpecs | GpuSpecs | PhoneSpecs) => {
  const itemId = item.id
  const isFavorited = favoriteItems.value.has(itemId)
  
  if (isFavorited) {
    // 取消收藏
    favoriteItems.value.delete(itemId)
    uni.showToast({
      title: '已取消收藏',
      icon: 'success'
    })
  } else {
    // 添加收藏
    favoriteItems.value.add(itemId)
    uni.showToast({
      title: '已收藏',
      icon: 'success'
    })
  }
  
  // 更新收藏状态
  favoriteItems.value = new Set(favoriteItems.value)
}
</script>

<style scoped lang="scss">
.ranking-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.ranking-header {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  padding: 40rpx 30rpx 30rpx;
  color: #ffffff;
}

.header-title {
  text-align: center;
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

.ranking-type {
  background-color: #ffffff;
  padding: 0;
  margin-bottom: 20rpx;
  border-radius: 12rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.tabs-container {
  display: flex;
  border-bottom: 1rpx solid #f0f0f0;
}

.tab-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24rpx 0;
  position: relative;
  cursor: pointer;
  transition: all 0.3s;
  gap: 8rpx;
  
  &.active {
    color: #007aff;
    font-weight: 500;
    
    &::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 20%;
      width: 60%;
      height: 3rpx;
      background-color: #007aff;
      border-radius: 3rpx 3rpx 0 0;
    }
  }
  
  &:active {
    background-color: rgba(0, 122, 255, 0.05);
  }
}

.tab-title {
  font-size: 28rpx;
  color: #666;
  transition: all 0.3s;
}

.tab-item.active .tab-title {
  color: #007aff;
}

.tab-arrow {
  font-size: 20rpx;
  color: #999;
  transition: all 0.3s;
  transform: rotate(0deg);
  
  &.active {
    transform: rotate(180deg);
    color: #007aff;
  }
}

.cpu-sub-tabs {
  display: flex;
  flex-direction: column;
  padding: 16rpx 24rpx;
  border-top: 1rpx solid #f0f0f0;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.sub-tab-item {
  font-size: 26rpx;
  color: #666;
  padding: 16rpx 32rpx;
  border-radius: 8rpx;
  background-color: #ffffff;
  transition: all 0.3s;
  border: 1rpx solid #e0e0e0;
  box-shadow: 0 2rpx 4rpx rgba(0, 0, 0, 0.05);
  margin-bottom: 12rpx;
  
  &:last-child {
    margin-bottom: 0;
  }
  
  &.active {
    background-color: #007aff;
    color: #ffffff;
    border-color: #007aff;
    box-shadow: 0 4rpx 12rpx rgba(0, 122, 255, 0.2);
    font-weight: 500;
  }
  
  &:active {
    transform: scale(0.98);
    opacity: 0.9;
  }
}

.ranking-list {
  padding: 0 30rpx;
}

/* 骨架屏样式 */
.skeleton-container {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  padding: 20rpx 0;
}

.skeleton-item {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

/* 排行榜项目样式 */
.ranking-items {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  padding: 20rpx 0;
}

.ranking-item {
  background-color: #ffffff;
  border-radius: 20rpx;
  padding: 30rpx;
  display: flex;
  align-items: flex-start;
  gap: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  
  &:active {
    transform: translateY(-2rpx);
    box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
  }
}

.rank-number {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  font-weight: bold;
  color: #ffffff;
  flex-shrink: 0;
  font-family: 'DIN Alternate', 'Helvetica Neue', Arial, sans-serif;
}

.rank-gold {
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  color: #8b6914;
}

.rank-silver {
  background: linear-gradient(135deg, #c0c0c0, #e0e0e0);
  color: #666666;
}

.rank-bronze {
  background: linear-gradient(135deg, #cd7f32, #e6a15c);
  color: #8b4513;
}

.rank-normal {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #ffffff;
}

.hardware-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.info-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.brand-model {
  display: flex;
  align-items: center;
  gap: 12rpx;
  flex: 1;
}

.brand-tag {
  padding: 6rpx 16rpx;
  border-radius: 30rpx;
  font-size: 22rpx;
  font-weight: bold;
  color: #ffffff;
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

.model-text {
  font-size: 28rpx;
  font-weight: bold;
  color: #333333;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 300rpx;
}

.score-favorite-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.score-badge {
  background: linear-gradient(135deg, #667eea, #764ba2);
  padding: 8rpx 16rpx;
  border-radius: 30rpx;
  display: flex;
  align-items: center;
  gap: 4rpx;
}

.score-text {
  font-size: 32rpx;
  font-weight: bold;
  color: #ffffff;
  font-family: 'DIN Alternate', 'Helvetica Neue', Arial, sans-serif;
}

.score-label {
  font-size: 22rpx;
  color: #ffffff;
  opacity: 0.9;
}

.favorite-action {
  flex-shrink: 0;
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
  
  &:active {
    background-color: rgba(0, 0, 0, 0.05);
  }
}

.favorite-icon {
  width: 64rpx;
  height: 64rpx;
}

.info-bottom {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.spec-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.spec-tag {
  display: flex;
  align-items: center;
  gap: 6rpx;
  padding: 6rpx 12rpx;
  background-color: #f5f5f5;
  border-radius: 16rpx;
  font-size: 22rpx;
}

.spec-label {
  color: #666666;
}

.spec-value {
  color: #333333;
  font-weight: bold;
  font-family: 'DIN Alternate', 'Helvetica Neue', Arial, sans-serif;
}



/* 错误状态 */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 32rpx;
  text-align: center;
  gap: 32rpx;
}

.error-text {
  font-size: 28rpx;
  color: #ff4444;
  text-align: center;
  font-weight: 500;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 32rpx;
  text-align: center;
  gap: 24rpx;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: 16rpx;
}

.empty-text {
  font-size: 32rpx;
  color: #666666;
  font-weight: 600;
}

.empty-hint {
  font-size: 26rpx;
  color: #999999;
}

/* 底部说明 */
.ranking-footer {
  padding: 40rpx 30rpx;
  text-align: center;
}

.footer-text {
  font-size: 24rpx;
  color: #999999;
  font-style: italic;
}
</style>