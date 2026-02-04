<template>
  <view class="profile-container">
    <!-- 用户信息头部 -->
    <view class="user-header">
      <view class="avatar-container">
        <image class="avatar" src="/static/logo.png" mode="aspectFit" />
      </view>
      <view class="user-info">
        <text class="username">硬件爱好者</text>
        <text class="user-desc">探索硬件性能，发现最佳选择</text>
      </view>
    </view>

    <!-- 功能菜单 -->
    <view class="menu-section">
      <view class="menu-title">我的功能</view>
      
      <view class="menu-list">
        <!-- 我的收藏 -->
        <view class="menu-item" @click="navigateToFavorites">
          <view class="menu-item-left">
            <image class="menu-icon" src="/static/tabbar/collect.png" mode="aspectFit" />
            <text class="menu-text">我的收藏</text>
          </view>
          <view class="menu-item-right">
            <text class="menu-count">{{ favoriteCount }}</text>
            <text class="arrow">›</text>
          </view>
        </view>

        <!-- 性能对比 -->
        <view class="menu-item" @click="navigateToCompare">
          <view class="menu-item-left">
            <image class="menu-icon" src="/static/tabbar/compare.png" mode="aspectFit" />
            <text class="menu-text">性能对比</text>
          </view>
          <view class="menu-item-right">
            <text class="arrow">›</text>
          </view>
        </view>

        <!-- 性能排行 -->
        <view class="menu-item" @click="navigateToRanking">
          <view class="menu-item-left">
            <image class="menu-icon" src="/static/tabbar/ranking.png" mode="aspectFit" />
            <text class="menu-text">性能排行</text>
          </view>
          <view class="menu-item-right">
            <text class="arrow">›</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 统计信息 -->
    <view class="stats-section">
      <view class="stats-title">使用统计</view>
      <view class="stats-grid">
        <view class="stat-item">
          <text class="stat-value">{{ favoriteCount }}</text>
          <text class="stat-label">收藏数量</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ compareCount }}</text>
          <text class="stat-label">对比次数</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ viewCount }}</text>
          <text class="stat-label">浏览次数</text>
        </view>
      </view>
    </view>

    <!-- 关于应用 -->
    <view class="about-section">
      <view class="about-item">
        <text class="about-label">版本</text>
        <text class="about-value">1.0.0</text>
      </view>
      <view class="about-item">
        <text class="about-label">更新时间</text>
        <text class="about-value">2026-02-04</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useFavoritesStore } from '@/stores/favorites'

const favoritesStore = useFavoritesStore()

const favoriteCount = ref(0)
const compareCount = ref(0)
const viewCount = ref(0)

onMounted(() => {
  loadStats()
})

const loadStats = () => {
  favoriteCount.value = favoritesStore.favorites.length
  compareCount.value = uni.getStorageSync('compareCount') || 0
  viewCount.value = uni.getStorageSync('viewCount') || 0
}

const navigateToFavorites = () => {
  uni.navigateTo({
    url: '/pages/favorites/index'
  })
}

const navigateToCompare = () => {
  uni.switchTab({
    url: '/pages/compare/index'
  })
}

const navigateToRanking = () => {
  uni.switchTab({
    url: '/pages/ranking/index'
  })
}
</script>

<style lang="scss" scoped>
.profile-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 40rpx;
}

.user-header {
  background: linear-gradient(135deg, #0071c5 0%, #00a0e9 100%);
  padding: 60rpx 40rpx 80rpx;
  display: flex;
  align-items: center;
  color: white;
}

.avatar-container {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 30rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.15);
}

.avatar {
  width: 80rpx;
  height: 80rpx;
}

.user-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.username {
  font-size: 36rpx;
  font-weight: bold;
  margin-bottom: 10rpx;
}

.user-desc {
  font-size: 24rpx;
  opacity: 0.9;
}

.menu-section {
  margin: -40rpx 30rpx 30rpx;
  background-color: white;
  border-radius: 20rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.menu-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
}

.menu-list {
  display: flex;
  flex-direction: column;
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 30rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item-left {
  display: flex;
  align-items: center;
}

.menu-icon {
  width: 48rpx;
  height: 48rpx;
  margin-right: 20rpx;
}

.menu-text {
  font-size: 30rpx;
  color: #333;
}

.menu-item-right {
  display: flex;
  align-items: center;
}

.menu-count {
  font-size: 26rpx;
  color: #999;
  margin-right: 10rpx;
}

.arrow {
  font-size: 48rpx;
  color: #ccc;
  line-height: 1;
}

.stats-section {
  margin: 0 30rpx 30rpx;
  background-color: white;
  border-radius: 20rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.stats-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 30rpx;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20rpx;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20rpx 0;
}

.stat-value {
  font-size: 48rpx;
  font-weight: bold;
  color: #0071c5;
  margin-bottom: 10rpx;
}

.stat-label {
  font-size: 24rpx;
  color: #999;
}

.about-section {
  margin: 0 30rpx;
  background-color: white;
  border-radius: 20rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.about-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.about-item:last-child {
  border-bottom: none;
}

.about-label {
  font-size: 28rpx;
  color: #666;
}

.about-value {
  font-size: 28rpx;
  color: #333;
}
</style>
