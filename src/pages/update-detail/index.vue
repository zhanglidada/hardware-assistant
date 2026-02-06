<template>
  <view class="page-container">
    <!-- 更新详情头部 -->
    <view class="update-header" :class="{ 'animate-in': isAnimated }">
      <view class="update-icon">
        <wd-icon name="bell" size="56rpx" color="#007AFF"></wd-icon>
      </view>
      <view class="update-title-section">
        <text class="update-title">数据更新通知</text>
        <text class="update-time">{{ updateInfo.time }}</text>
      </view>
    </view>

    <!-- 更新内容卡片 -->
    <view class="update-card" :class="{ 'animate-in': isAnimated }" style="animation-delay: 0.1s;">
      <view class="update-card-header">
        <text class="update-card-title">更新内容</text>
      </view>
      <view class="update-content">
        <view v-for="(item, index) in updateInfo.content" :key="index" class="update-item" :class="{ 'animate-in': isAnimated }" :style="{ animationDelay: `${0.2 + index * 0.1}s` }">
          <view class="update-item-icon">
            <wd-icon name="check-circle" size="32rpx" color="#34C759"></wd-icon>
          </view>
          <view class="update-item-content">
            <text class="update-item-title">{{ item.title }}</text>
            <text class="update-item-desc">{{ item.description }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 更新详情卡片 -->
    <view class="update-card" :class="{ 'animate-in': isAnimated }" style="animation-delay: 0.3s;">
      <view class="update-card-header">
        <text class="update-card-title">更新详情</text>
      </view>
      <view class="update-detail-content">
        <text class="update-detail-text">{{ updateInfo.detail }}</text>
      </view>
    </view>

    <!-- 底部操作 -->
    <view class="bottom-actions" :class="{ 'animate-in': isAnimated }" style="animation-delay: 0.4s;">
      <wd-button 
        type="primary" 
        size="large" 
        @click="handleViewHardware"
        class="action-button"
      >
        查看最新硬件
      </wd-button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'

// 动画控制变量
const isAnimated = ref(false)

// 更新信息数据
const updateInfo = ref({
  time: '2026年2月6日',
  content: [
    {
      title: 'CPU数据更新',
      description: '添加了Intel和AMD的最新CPU型号，包括Intel Core Ultra系列和AMD Ryzen 9000系列'
    },
    {
      title: '显卡数据更新',
      description: '更新了NVIDIA和AMD的最新显卡数据，包括RTX 5000系列和RX 7000系列'
    },
    {
      title: '手机数据更新',
      description: '添加了最新的智能手机型号，包括iPhone 16系列和各品牌旗舰机型'
    }
  ],
  detail: '本次更新包含了2026年最新的硬件数据，所有数据均来自官方渠道和权威评测机构。更新内容涵盖了CPU、显卡和手机三大类硬件，确保您能够获取到最准确、最全面的硬件信息。'
})

// 页面加载时获取更新信息
onLoad((options: any) => {
  console.log('更新详情页面加载，参数:', options)
  // 这里可以根据传入的参数获取具体的更新信息
  // 例如：const updateId = options.id
  // 然后根据updateId从API或本地存储获取详细信息
})

// 页面挂载后触发动画
onMounted(() => {
  setTimeout(() => {
    isAnimated.value = true
  }, 100)
})

// 查看最新硬件
const handleViewHardware = () => {
  uni.switchTab({
    url: '/pages/index/index',
    success: () => {
      console.log('成功跳转到首页')
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
</script>

<style scoped lang="scss">
/* CSS 变量定义 */
:root {
  --primary-color: #007AFF;
  --success-color: #34C759;
  --background-color: #F2F2F7;
  --card-background: #FFFFFF;
  --text-primary: #000000;
  --text-secondary: #8E8E93;
  --text-tertiary: #C7C7CC;
  --border-color: #E5E5EA;
}

.page-container {
  min-height: 100vh;
  background-color: var(--background-color);
  padding: 32rpx;
}

/* 动画效果 */
.animate-in {
  animation: fadeInUp 0.6s cubic-bezier(0.25, 1, 0.5, 1) forwards;
  opacity: 0;
  transform: translateY(20rpx);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 更新头部样式 */
.update-header {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
  padding: 18rpx 40rpx;
  background-color: var(--card-background);
  border-radius: 32rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
  transition: all 0.4s cubic-bezier(0.25, 1, 0.5, 1);
}

.update-icon {
  margin-right: 24rpx;
  flex-shrink: 0;
  width: 72rpx;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 122, 255, 0.1);
  border-radius: 20rpx;
  transition: all 0.3s ease;
}

.update-title-section {
  flex: 1;
}

.update-title {
  display: block;
  font-size: 36rpx;
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 8rpx;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.2;
}

.update-time {
  display: block;
  font-size: 26rpx;
  color: var(--text-secondary);
  font-weight: 500;
}

/* 更新卡片样式 */
.update-card {
  background-color: var(--card-background);
  border-radius: 32rpx;
  box-shadow: 0 6rpx 20rpx rgba(0, 0, 0, 0.08);
  margin-bottom: 28rpx;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.25, 1, 0.5, 1);
}

.update-card-header {
  padding: 28rpx 36rpx;
  border-bottom: 1rpx solid var(--border-color);
  background-color: rgba(0, 122, 255, 0.01);
}

.update-card-title {
  font-size: 30rpx;
  font-weight: 700;
  color: var(--text-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* 更新内容样式 */
.update-content {
  padding: 36rpx;
}

.update-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 32rpx;
  padding: 24rpx;
  background-color: rgba(0, 122, 255, 0.02);
  border-radius: 24rpx;
  transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1);
  
  &:last-child {
    margin-bottom: 0;
  }
  
  &:hover {
    background-color: rgba(0, 122, 255, 0.04);
    transform: translateY(-2rpx);
  }
}

.update-item-icon {
  margin-right: 20rpx;
  flex-shrink: 0;
  margin-top: 4rpx;
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(52, 199, 89, 0.1);
  border-radius: 16rpx;
}

.update-item-content {
  flex: 1;
}

.update-item-title {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12rpx;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.3;
}

.update-item-desc {
  display: block;
  font-size: 24rpx;
  color: var(--text-secondary);
  line-height: 1.6;
  font-weight: 500;
}

/* 更新详情内容样式 */
.update-detail-content {
  padding: 36rpx;
}

.update-detail-text {
  font-size: 26rpx;
  color: var(--text-secondary);
  line-height: 1.7;
  text-align: justify;
  font-weight: 500;
}

/* 底部操作样式 */
.bottom-actions {
  margin-top: 56rpx;
  padding: 0 32rpx;
  margin-bottom: 40rpx;
}

.action-button {
  width: 100%;
  height: 104rpx;
  font-size: 30rpx;
  font-weight: 700;
  border-radius: 52rpx;
  transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1);
  box-shadow: 0 8rpx 24rpx rgba(0, 122, 255, 0.3);
  
  &:active {
    transform: scale(0.98);
    box-shadow: 0 4rpx 12rpx rgba(0, 122, 255, 0.2);
  }
}

/* 响应式适配 */
@media (max-width: 375px) {
  .page-container {
    padding: 24rpx;
  }
  
  .update-header {
    padding: 28rpx 32rpx;
  }
  
  .update-title {
    font-size: 32rpx;
  }
  
  .update-time {
    font-size: 24rpx;
  }
  
  .update-card {
    margin-bottom: 24rpx;
  }
  
  .update-content {
    padding: 28rpx;
  }
  
  .update-item {
    padding: 20rpx;
    margin-bottom: 24rpx;
  }
  
  .update-item-title {
    font-size: 26rpx;
  }
  
  .update-item-desc {
    font-size: 22rpx;
  }
  
  .bottom-actions {
    margin-top: 48rpx;
  }
  
  .action-button {
    height: 96rpx;
    font-size: 28rpx;
  }
}
</style>