<template>
  <view class="favorites-container">
    <!-- Tab 分类 -->
    <wd-tabs v-model="activeTab" class="category-tabs" @change="handleTabChange">
      <wd-tab title="CPU" name="cpu"></wd-tab>
      <wd-tab title="显卡" name="gpu"></wd-tab>
      <wd-tab title="手机" name="phone"></wd-tab>
    </wd-tabs>

    <!-- 空状态 -->
    <view v-if="currentFavorites.length === 0" class="empty-state">
      <image class="empty-icon" src="/static/tabbar/collect.png" mode="aspectFit" />
      <text class="empty-text">暂无收藏</text>
      <text class="empty-desc">点击硬件详情页的收藏按钮即可添加</text>
      <wd-button type="primary" size="small" @click="goToHome">去逛逛</wd-button>
    </view>

    <!-- 收藏列表 -->
    <view v-else class="favorites-list">
      <view
        v-for="item in currentFavorites"
        :key="item.id"
        class="favorite-card"
        @click="handleCardClick(item)"
      >
        <!-- 卡片头部 -->
        <view class="card-header">
          <view class="brand-badge" :class="item.brand.toLowerCase()">
            {{ item.brand }}
          </view>
          <view class="remove-btn" @click.stop="handleRemove(item.id)">
            <text class="remove-icon">×</text>
          </view>
        </view>

        <!-- 卡片内容 -->
        <view class="card-content">
          <text class="model-name">{{ item.model }}</text>
          <text class="price">¥{{ item.price }}</text>
        </view>

        <!-- 卡片底部 -->
        <view class="card-footer">
          <text class="release-date">发布日期: {{ item.releaseDate }}</text>
          <text class="add-time">{{ formatAddTime(item.addTime) }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useFavoritesStore } from '@/stores/favorites'
import type { FavoriteItem } from '@/stores/favorites'

const favoritesStore = useFavoritesStore()

const activeTab = ref<'cpu' | 'gpu' | 'phone'>('cpu')

const currentFavorites = computed(() => {
  switch (activeTab.value) {
    case 'cpu':
      return favoritesStore.cpuFavorites
    case 'gpu':
      return favoritesStore.gpuFavorites
    case 'phone':
      return favoritesStore.phoneFavorites
    default:
      return []
  }
})

onMounted(() => {
  favoritesStore.loadFavorites()
})

const handleTabChange = (name: string) => {
  activeTab.value = name as 'cpu' | 'gpu' | 'phone'
}

const handleCardClick = (item: FavoriteItem) => {
  uni.navigateTo({
    url: `/pages/detail/index?id=${item.id}&type=${item.type}`
  })
}

const handleRemove = (id: string) => {
  uni.showModal({
    title: '确认删除',
    content: '确定要取消收藏这个硬件吗？',
    success: (res) => {
      if (res.confirm) {
        favoritesStore.removeFavorite(id)
        uni.showToast({
          title: '已取消收藏',
          icon: 'success'
        })
      }
    }
  })
}

const formatAddTime = (timestamp: number) => {
  const now = Date.now()
  const diff = now - timestamp
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    return '今天收藏'
  } else if (days === 1) {
    return '昨天收藏'
  } else if (days < 7) {
    return `${days}天前收藏`
  } else {
    const date = new Date(timestamp)
    return `${date.getMonth() + 1}月${date.getDate()}日收藏`
  }
}

const goToHome = () => {
  uni.switchTab({
    url: '/pages/index/index'
  })
}
</script>

<style lang="scss" scoped>
.favorites-container {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.category-tabs {
  background-color: white;
  position: sticky;
  top: 0;
  z-index: 10;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 200rpx 40rpx;
}

.empty-icon {
  width: 200rpx;
  height: 200rpx;
  opacity: 0.3;
  margin-bottom: 40rpx;
}

.empty-text {
  font-size: 32rpx;
  color: #333;
  font-weight: bold;
  margin-bottom: 20rpx;
}

.empty-desc {
  font-size: 26rpx;
  color: #999;
  margin-bottom: 40rpx;
  text-align: center;
}

.favorites-list {
  padding: 20rpx;
}

.favorite-card {
  background-color: white;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.favorite-card:active {
  transform: scale(0.98);
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.brand-badge {
  padding: 8rpx 20rpx;
  border-radius: 8rpx;
  font-size: 22rpx;
  font-weight: bold;
  color: white;
}

.brand-badge.intel {
  background: linear-gradient(135deg, #0071c5 0%, #00a0e9 100%);
}

.brand-badge.amd {
  background: linear-gradient(135deg, #ed1c24 0%, #ff6b6b 100%);
}

.brand-badge.nvidia {
  background: linear-gradient(135deg, #76b900 0%, #9ae000 100%);
}

.brand-badge.apple {
  background: linear-gradient(135deg, #555555 0%, #888888 100%);
}

.brand-badge.xiaomi {
  background: linear-gradient(135deg, #ff6700 0%, #ff8f33 100%);
}

.brand-badge.huawei {
  background: linear-gradient(135deg, #cf0a2c 0%, #ff3366 100%);
}

.brand-badge.samsung {
  background: linear-gradient(135deg, #1428a0 0%, #3d5afe 100%);
}

.brand-badge.其他 {
  background: linear-gradient(135deg, #999999 0%, #cccccc 100%);
}

.remove-btn {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border-radius: 50%;
}

.remove-icon {
  font-size: 48rpx;
  color: #999;
  line-height: 1;
}

.card-content {
  margin-bottom: 20rpx;
}

.model-name {
  display: block;
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 10rpx;
}

.price {
  display: block;
  font-size: 36rpx;
  font-weight: bold;
  color: #ff6700;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 20rpx;
  border-top: 1rpx solid #f0f0f0;
}

.release-date {
  font-size: 24rpx;
  color: #999;
}

.add-time {
  font-size: 24rpx;
  color: #0071c5;
}
</style>
