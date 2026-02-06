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

    <!-- 数据更新通知标签栏 -->
    <view v-if="showNotification" class="notification-bar" :class="{ 'show': showNotification, 'hide': !showNotification }">
      <view class="notification-content" @click="handleNotificationClick">
        <view class="notification-icon">
          <wd-icon name="bell" size="32rpx" color="#007AFF"></wd-icon>
        </view>
        <view class="notification-text">
          <text class="notification-title">{{ notification.title }}</text>
          <text class="notification-desc">{{ notification.description }}</text>
        </view>
        <view class="notification-arrow">
          <wd-icon name="chevron-right" size="28rpx" color="#8E8E93"></wd-icon>
        </view>
      </view>
    </view>

    <!-- Tab 分类 -->
    <wd-tabs v-model="activeTab" class="category-tabs" @change="handleTabChange">
      <wd-tab title="CPU" name="cpu"></wd-tab>
      <wd-tab title="显卡" name="gpu"></wd-tab>
      <wd-tab title="手机" name="phone"></wd-tab>
    </wd-tabs>

    <!-- 硬件列表 -->
    <view class="hardware-list">
      <!-- 骨架屏加载状态 -->
      <view v-if="currentLoading && filteredHardware.length === 0" class="skeleton-container">
        <wd-skeleton
          v-for="i in 3"
          :key="i"
          class="skeleton-card"
          :row="3"
          :row-width="['60%', '80%', '40%']"
          :title="true"
          title-width="70%"
        />
      </view>
      
      <!-- 错误状态 -->
      <view v-else-if="currentError" class="error-state">
        <text class="error-text">{{ currentError }}</text>
        <wd-button type="primary" size="small" @click="loadInitialData">重试</wd-button>
      </view>
      
      <!-- 数据列表 -->
      <view v-else-if="filteredHardware.length > 0" class="hardware-grid">
        <view
          v-for="item in filteredHardware"
          :key="item.id"
          class="hardware-card"
          @click="handleCardClick(item)"
        >
          <!-- 品牌背景装饰 -->
          <view class="brand-bg" :class="getBrandClass(item.brand)"></view>
          
          <!-- 卡片内容 -->
          <view class="card-content">
            <!-- 左侧品牌标识 -->
            <view class="brand-logo-container">
              <view class="brand-logo" :class="getBrandClass(item.brand)">
                {{ getBrandShortName(item.brand) }}
              </view>
              <!-- 新品标签 -->
              <view v-if="isNewRelease(item)" class="new-badge">
                <wd-icon name="fire" size="14" color="#ff6b00"></wd-icon>
                <text class="new-text">新品</text>
              </view>
            </view>
            
            <!-- 右侧信息 -->
            <view class="hardware-info">
              <view class="model-favorite-row">
                <text class="model">{{ item.model }}</text>
                <view class="favorite-action" @click.stop="handleToggleFavorite(item)">
                  <image 
                    :src="isItemFavorited(item) ? '/static/tabbar/collect-active.png' : '/static/tabbar/collect.png'" 
                    class="favorite-icon"
                    mode="aspectFit"
                  />
                </view>
              </view>
              
              <!-- 规格标签 -->
              <view class="specs-tags">
                <template v-if="activeTab === 'cpu'">
                  <view class="spec-tag" :class="getBrandClass(item.brand)">
                    <text class="spec-value">{{ (item as CpuSpecs).cores }} 核心</text>
                  </view>
                  <view class="spec-tag" :class="getBrandClass(item.brand)">
                    <text class="spec-value">{{ (item as CpuSpecs).baseClock }}-{{ (item as CpuSpecs).boostClock }}GHz</text>
                  </view>
                  <view class="spec-tag" :class="getBrandClass(item.brand)">
                    <text class="spec-value">{{ (item as CpuSpecs).tdp }}W</text>
                  </view>
                </template>
                <template v-else-if="activeTab === 'gpu'">
                  <view class="spec-tag" :class="getBrandClass(item.brand)">
                    <text class="spec-value">{{ (item as GpuSpecs).vram }}GB</text>
                  </view>
                  <view class="spec-tag" :class="getBrandClass(item.brand)">
                    <text class="spec-value">{{ (item as GpuSpecs).busWidth }}bit</text>
                  </view>
                  <view class="spec-tag" :class="getBrandClass(item.brand)">
                    <text class="spec-value">{{ (item as GpuSpecs).cudaCores }}核心</text>
                  </view>
                </template>
                <template v-else>
                  <view class="spec-tag" :class="getBrandClass(item.brand)">
                    <text class="spec-value">{{ (item as PhoneSpecs).ram }}GB RAM</text>
                  </view>
                  <view class="spec-tag" :class="getBrandClass(item.brand)">
                    <text class="spec-value">{{ (item as PhoneSpecs).storage }}GB</text>
                  </view>
                  <view class="spec-tag" :class="getBrandClass(item.brand)">
                    <text class="spec-value">{{ (item as PhoneSpecs).screenSize }}英寸</text>
                  </view>
                </template>
              </view>
            </view>
          </view>
        </view>
        
        <!-- 加载更多提示 -->
        <view v-if="currentLoading && filteredHardware.length > 0" class="load-more-tip">
          <wd-loading text="加载更多..." />
        </view>
        
        <!-- 没有更多数据提示 -->
        <view v-else-if="currentFinished && filteredHardware.length > 0" class="no-more-tip">
          <text class="no-more-text">没有更多数据了</text>
        </view>
      </view>

      <!-- 空状态 -->
      <view v-else class="empty-state">
        <view class="empty-illustration">
          <wd-icon name="search" size="80" color="#cccccc"></wd-icon>
        </view>
        <text class="empty-text">暂无相关硬件</text>
        <text class="empty-hint">尝试调整搜索关键词或切换分类</text>
        <wd-button 
          type="default" 
          size="small" 
          @click="handleClear"
          class="clear-filter-btn"
        >
          清除筛选条件
        </wd-button>
      </view>
    </view>

    <!-- 底部提示 -->
    <view class="footer-tip">
      <text>共 {{ filteredHardware.length }} 个硬件</text>
    </view>


    <!-- 对比悬浮窗 -->
    <view v-if="compareStore.totalCount > 0" class="compare-float" :class="{ 'bounce-animation': showBounce }">
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
            round
          >
            清空
          </wd-button>
          <wd-button 
            type="primary" 
            size="small" 
            @click="handleStartPK"
            :disabled="!compareStore.canStartPK"
            round
          >
            开始PK ({{ compareStore.totalCount }})
          </wd-button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { onReachBottom } from '@dcloudio/uni-app'
import { useCompareStore } from '../../stores/compare'
import { useHardwareList } from '../../composables/useCloudData'
import type { CpuSpecs, GpuSpecs, PhoneSpecs } from '../../types/hardware'
import type { CompareItem } from '../../stores/compare'

// Pinia store
const compareStore = useCompareStore()

// 响应式数据
const searchKeyword = ref('')
const activeTab = ref<'cpu' | 'gpu' | 'phone'>('cpu')
const showBounce = ref(false)
const activeNav = ref<'home' | 'ranking' | 'compare' | 'mine'>('home')

// 数据更新通知相关数据
const showNotification = ref(true)
const notification = ref({
  title: '数据更新通知',
  description: '最新硬件数据已更新，包括Intel和AMD的最新CPU型号',
  time: '刚刚',
  id: '1',
  type: 'data_update'
})

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

const handleTabChange = ({ name }: { name: string }) => {
  // 切换 Tab 时，如果该列表还没有数据，则执行刷新加载
  if (name === 'cpu' && cpuListHook.list.value.length === 0) {
    cpuListHook.refresh()
  } else if (name === 'gpu' && gpuListHook.list.value.length === 0) {
    gpuListHook.refresh()
  } else if (name === 'phone' && phoneListHook.list.value.length === 0) {
    phoneListHook.refresh()
  }
}

// 页面加载时初始化数据
onMounted(() => {
  // 初始加载数据
  loadInitialData()
})

// 页面卸载时清理
onUnmounted(() => {
  // 清理相关资源
})

// 上拉触底加载更多
onReachBottom(() => {
  handleLoadMore()
})

// 加载初始数据
const loadInitialData = () => {
  if (activeTab.value === 'cpu') {
    cpuListHook.refresh()
  } else if (activeTab.value === 'gpu') {
    gpuListHook.refresh()
  } else {
    phoneListHook.refresh()
  }
}

// 加载更多数据
const handleLoadMore = () => {
  if (activeTab.value === 'cpu') {
    cpuListHook.loadMore()
  } else if (activeTab.value === 'gpu') {
    gpuListHook.loadMore()
  } else {
    phoneListHook.loadMore()
  }
}

// 根据当前Tab获取数据源
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

// 获取当前完成状态
const currentFinished = computed(() => {
  if (activeTab.value === 'cpu') {
    return cpuListHook.finished.value
  } else if (activeTab.value === 'gpu') {
    return gpuListHook.finished.value
  } else {
    return phoneListHook.finished.value
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

// 获取当前总数
const currentTotal = computed(() => {
  if (activeTab.value === 'cpu') {
    return cpuListHook.total.value
  } else if (activeTab.value === 'gpu') {
    return gpuListHook.total.value
  } else {
    return phoneListHook.total.value
  }
})

// 过滤硬件数据
const filteredHardware = computed(() => {
  // const keyword = searchKeyword.value.trim().toLowerCase()
  // const data = currentDataSource.value
  
  // if (!keyword) {
  //   return data
  // }
  
  // // 使用类型断言解决联合类型调用问题，使用 indexOf 替代 includes 避免 ES2015+ 方法兼容性问题
  // return (data as (CpuSpecs | GpuSpecs | PhoneSpecs)[]).filter((item: CpuSpecs | GpuSpecs | PhoneSpecs) => 
  //   item.model.toLowerCase().indexOf(keyword) !== -1 ||
  //   item.brand.toLowerCase().indexOf(keyword) !== -1 ||
  //   (item.description && item.description.toLowerCase().indexOf(keyword) !== -1)
  // )
  return currentDataSource.value
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
  const keyword = searchKeyword.value.trim()
  console.log('搜索关键词:', keyword)
  
  if (activeTab.value === 'cpu') {
    cpuListHook.search(keyword)
  } else if (activeTab.value === 'gpu') {
    gpuListHook.search(keyword)
  } else {
    phoneListHook.search(keyword)
  }
}

// 清空搜索
const handleClear = () => {
  searchKeyword.value = ''
  
  // 清除搜索条件，重新加载数据
  if (activeTab.value === 'cpu') {
    cpuListHook.search('')
  } else if (activeTab.value === 'gpu') {
    gpuListHook.search('')
  } else {
    phoneListHook.search('')
  }
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
  
  // 跳转到PK页面 - 使用 switchTab 因为 compare 是 tabBar 页面
  uni.switchTab({
    url: '/pages/compare/index',
    success: () => {
      // 成功跳转后，可以在对比页面中通过 onShow 或 onLoad 获取对比类型
      console.log('成功跳转到对比页面，对比类型:', compareType)
    },
    fail: (err) => {
      console.error('跳转失败:', err)
      uni.showToast({
        title: '跳转失败，请重试',
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

// 检查是否为新品发布
const isNewRelease = (item: CpuSpecs | GpuSpecs | PhoneSpecs): boolean => {
  // 假设6个月内发布的为新品
  const sixMonthsAgo = new Date()
  sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6)
  
  try {
    const releaseDate = new Date(item.releaseDate)
    return releaseDate > sixMonthsAgo
  } catch {
    return false
  }
}

// 添加对比项
const handleAddCompare = (item: CpuSpecs | GpuSpecs | PhoneSpecs) => {
  const result = compareStore.toggleCompare(item)
  if (result.added) {
    // 触发弹跳动画
    showBounce.value = true
    setTimeout(() => {
      showBounce.value = false
    }, 500)
    
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

// 导航点击处理
const handleNavClick = (nav: 'home' | 'ranking' | 'compare' | 'mine') => {
  activeNav.value = nav
  
  switch (nav) {
    case 'home':
      // 已经在首页，不需要跳转
      uni.showToast({
        title: '当前页面',
        icon: 'none'
      })
      break
    case 'ranking':
      uni.showToast({
        title: '性能排行功能开发中',
        icon: 'none'
      })
      break
    case 'compare':
      // 跳转到对比页面
      uni.navigateTo({
        url: '/pages/compare/index',
        fail: (err) => {
          console.error('跳转失败:', err)
          uni.showToast({
            title: '对比页面未找到',
            icon: 'error'
          })
        }
      })
      break
    case 'mine':
      uni.showToast({
        title: '我的页面开发中',
        icon: 'none'
      })
      break
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

// 数据更新通知点击处理
const handleNotificationClick = () => {
  console.log('点击通知:', notification.value)
  // 根据通知类型跳转到相应页面
  if (notification.value.type === 'data_update') {
    // 跳转到更新详情页面
    uni.navigateTo({
      url: '/pages/update-detail/index',
      fail: (err) => {
        console.error('跳转失败:', err)
        uni.showToast({
          title: '跳转失败，请重试',
          icon: 'error'
        })
      }
    })
  }
}

const handleCloseNotification = () => {
  showNotification.value = false
}
</script>

<style scoped lang="scss">
/* CSS 变量定义 */
:root {
  --brand-intel: #0071c5;
  --brand-amd: #ed1c24;
  --brand-nvidia: #76b900;
  --brand-apple: #000000;
  --brand-xiaomi: #ff6900;
  --brand-huawei: #ff0036;
  --brand-samsung: #1428a0;
  --brand-other: #666666;
  
  --brand-intel-light: rgba(0, 113, 197, 0.1);
  --brand-amd-light: rgba(237, 28, 36, 0.1);
  --brand-nvidia-light: rgba(118, 185, 0, 0.1);
  --brand-apple-light: rgba(0, 0, 0, 0.1);
  --brand-xiaomi-light: rgba(255, 105, 0, 0.1);
  --brand-huawei-light: rgba(255, 0, 54, 0.1);
  --brand-samsung-light: rgba(20, 40, 160, 0.1);
  --brand-other-light: rgba(102, 102, 102, 0.1);
}

.page-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
}

.search-container {
  padding: 24rpx 32rpx;
  background-color: #ffffff;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}

/* 数据更新通知标签栏样式 */
.notification-bar {
  margin: 0 32rpx 24rpx;
  border-radius: 32rpx;
  overflow: hidden;
  background-color: #ffffff;
  box-shadow: 0 6rpx 20rpx rgba(0, 0, 0, 0.08);
  transition: all 0.4s cubic-bezier(0.25, 1, 0.5, 1);
  transform: translateY(0);
  opacity: 1;
  position: relative;
  z-index: 10;
  
  &.hide {
    transform: translateY(-20rpx);
    opacity: 0;
    height: 0;
    margin-bottom: 0;
    overflow: hidden;
  }
}

.notification-content {
  display: flex;
  align-items: center;
  padding: 28rpx 32rpx;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1);
  position: relative;
  
  &:active {
    background-color: rgba(0, 122, 255, 0.05);
    transform: scale(0.98);
  }
  
  &:hover {
    background-color: rgba(0, 122, 255, 0.02);
  }
}

.notification-icon {
  margin-right: 20rpx;
  flex-shrink: 0;
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 122, 255, 0.1);
  border-radius: 20rpx;
  transition: all 0.3s ease;
}

.notification-text {
  flex: 1;
  min-width: 0;
  margin-right: 20rpx;
}

.notification-title {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
  color: #000000;
  margin-bottom: 4rpx;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.2;
}

.notification-desc {
  display: block;
  font-size: 24rpx;
  color: #8E8E93;
  line-height: 1.5;
  font-weight: 500;
}

.notification-arrow {
  flex-shrink: 0;
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1);
  background-color: rgba(0, 0, 0, 0.02);
  
  &:active {
    background-color: rgba(0, 0, 0, 0.08);
    transform: scale(0.9);
  }
  
  .wd-icon {
    transition: all 0.3s ease;
  }
}

.notification-content:hover .notification-arrow .wd-icon {
  transform: translateX(4rpx);
}

.category-tabs {
  background-color: #ffffff;
  margin-bottom: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
  
  :deep(.wd-tabs__nav) {
    padding: 0 32rpx;
  }
}

.hardware-list {
  padding: 0 32rpx;
}

/* 骨架屏样式 */
.skeleton-container {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  padding: 24rpx 0;
}

.skeleton-card {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 32rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

/* 硬件卡片样式 */
.hardware-grid {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  padding: 24rpx 0;
}

.hardware-card {
  position: relative;
  background: #ffffff;
  border-radius: 20rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  
  &:active {
    transform: translateY(-2rpx);
    box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
  }
}

.brand-bg {
  position: absolute;
  top: 0;
  right: 0;
  width: 120rpx;
  height: 120rpx;
  opacity: 0.05;
  filter: blur(20rpx);
  border-radius: 0 0 0 100rpx;
  
  &.brand-intel {
    background: var(--brand-intel);
  }
  &.brand-amd {
    background: var(--brand-amd);
  }
  &.brand-nvidia {
    background: var(--brand-nvidia);
  }
  &.brand-apple {
    background: var(--brand-apple);
  }
  &.brand-xiaomi {
    background: var(--brand-xiaomi);
  }
  &.brand-huawei {
    background: var(--brand-huawei);
  }
  &.brand-samsung {
    background: var(--brand-samsung);
  }
  &.brand-other {
    background: var(--brand-other);
  }
}

.card-content {
  display: flex;
  align-items: flex-start;
  padding: 32rpx;
  position: relative;
  z-index: 1;
}

.brand-logo-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 24rpx;
  flex-shrink: 0;
}

.brand-logo {
  width: 64rpx;
  height: 64rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20rpx;
  font-weight: 900;
  color: #ffffff;
  font-family: 'DIN Alternate', 'Helvetica Neue', Arial, sans-serif;
  
  &.brand-intel {
    background: linear-gradient(135deg, var(--brand-intel), #00a9ff);
  }
  &.brand-amd {
    background: linear-gradient(135deg, var(--brand-amd), #ff6b6b);
  }
  &.brand-nvidia {
    background: linear-gradient(135deg, var(--brand-nvidia), #a8e063);
  }
  &.brand-apple {
    background: linear-gradient(135deg, var(--brand-apple), #333333);
  }
  &.brand-xiaomi {
    background: linear-gradient(135deg, var(--brand-xiaomi), #ffa726);
  }
  &.brand-huawei {
    background: linear-gradient(135deg, var(--brand-huawei), #ff6b9d);
  }
  &.brand-samsung {
    background: linear-gradient(135deg, var(--brand-samsung), #1a73e8);
  }
  &.brand-other {
    background: linear-gradient(135deg, var(--brand-other), #999999);
  }
}

.new-badge {
  display: flex;
  align-items: center;
  gap: 4rpx;
  margin-top: 8rpx;
  padding: 4rpx 8rpx;
  background: linear-gradient(135deg, #ff6b00, #ffa726);
  border-radius: 12rpx;
  font-size: 20rpx;
  color: #ffffff;
  font-weight: bold;
  
  .new-text {
    font-size: 20rpx;
    font-weight: bold;
  }
}

.hardware-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.model-favorite-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.model {
  font-size: 28rpx;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.4;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  flex: 1;
  margin-right: 16rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

.specs-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
  margin-bottom: 8rpx;
}

.spec-tag {
  padding: 4rpx 10rpx;
  border-radius: 12rpx;
  font-size: 20rpx;
  font-weight: 500;
  
  &.brand-intel {
    background: var(--brand-intel-light);
    color: var(--brand-intel);
  }
  &.brand-amd {
    background: var(--brand-amd-light);
    color: var(--brand-amd);
  }
  &.brand-nvidia {
    background: var(--brand-nvidia-light);
    color: var(--brand-nvidia);
  }
  &.brand-apple {
    background: var(--brand-apple-light);
    color: var(--brand-apple);
  }
  &.brand-xiaomi {
    background: var(--brand-xiaomi-light);
    color: var(--brand-xiaomi);
  }
  &.brand-huawei {
    background: var(--brand-huawei-light);
    color: var(--brand-huawei);
  }
  &.brand-samsung {
    background: var(--brand-samsung-light);
    color: var(--brand-samsung);
  }
  &.brand-other {
    background: var(--brand-other-light);
    color: var(--brand-other);
  }
}

.spec-value {
  font-family: 'DIN Alternate', 'Helvetica Neue', Arial, sans-serif;
  font-weight: 600;
  font-size: 20rpx;
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

.load-more-tip {
  padding: 40rpx 0;
  text-align: center;
}

.no-more-tip {
  padding: 40rpx 0;
  text-align: center;
}

.no-more-text {
  font-size: 26rpx;
  color: #999999;
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

.empty-illustration {
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
  margin-bottom: 8rpx;
}

.clear-filter-btn {
  margin-top: 16rpx;
}

/* 底部提示 */
.footer-tip {
  padding: 32rpx;
  text-align: center;
  font-size: 26rpx;
  color: #999999;
  background-color: #ffffff;
  margin-top: 24rpx;
  font-weight: 500;
}

/* 对比悬浮窗样式 */
.compare-float {
  position: fixed;
  bottom: 40rpx;
  left: 32rpx;
  right: 32rpx;
  z-index: 1000;
  
  &.bounce-animation {
    animation: bounce 0.5s ease;
  }
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10rpx);
  }
}

.float-content {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24rpx;
  padding: 24rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1rpx solid rgba(255, 255, 255, 0.2);
}

.selected-items {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.item-tag {
  display: flex;
  align-items: center;
  gap: 6rpx;
  padding: 10rpx 16rpx;
  border-radius: 40rpx;
  font-size: 22rpx;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.2s;
  
  &.brand-intel {
    background: linear-gradient(135deg, var(--brand-intel), #00a9ff);
  }
  &.brand-amd {
    background: linear-gradient(135deg, var(--brand-amd), #ff6b6b);
  }
  &.brand-nvidia {
    background: linear-gradient(135deg, var(--brand-nvidia), #a8e063);
  }
  &.brand-apple {
    background: linear-gradient(135deg, var(--brand-apple), #333333);
  }
  &.brand-xiaomi {
    background: linear-gradient(135deg, var(--brand-xiaomi), #ffa726);
  }
  &.brand-huawei {
    background: linear-gradient(135deg, var(--brand-huawei), #ff6b9d);
  }
  &.brand-samsung {
    background: linear-gradient(135deg, var(--brand-samsung), #1a73e8);
  }
  &.brand-other {
    background: linear-gradient(135deg, var(--brand-other), #999999);
  }
  
  &:active {
    opacity: 0.9;
    transform: translateY(-2rpx);
  }
}

.item-model {
  font-weight: bold;
  max-width: 120rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: 'DIN Alternate', 'Helvetica Neue', Arial, sans-serif;
}

.item-remove {
  font-size: 24rpx;
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