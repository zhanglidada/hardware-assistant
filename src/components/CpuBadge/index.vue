<template>
  <view class="cpu-badge" :class="[`cpu-badge--${size}`, { 'cpu-badge--loading': isLoading }]" :style="badgeStyle">
    <!-- 图片显示 -->
    <image
      v-if="icon_cloud_id"
      :src="icon_cloud_id"
      :class="'cpu-badge__image'"
      mode="aspectFill"
      lazy-load
      @load="onImageLoad"
      @error="onImageError"
    />
    
    <!-- 兜底显示 -->
    <view v-else class="cpu-badge__fallback">
      <text class="cpu-badge__text">{{ seriesText }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

// Props
interface Props {
  series_code: string;
  display_name: string;
  icon_cloud_id: string;
  bg_color: string;
  size?: 'sm' | 'md' | 'lg';
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md'
});

// 状态
const isLoading = ref(true);
const imageError = ref(false);

// 计算属性
const badgeStyle = computed(() => {
  if (imageError.value || !props.icon_cloud_id) {
    return {
      backgroundColor: props.bg_color
    };
  }
  return {};
});

const seriesText = computed(() => {
  // 从 series_code 提取系列文本，如 'intel_i9' -> 'i9'
  const parts = props.series_code.split('_');
  return parts.length > 1 ? parts[1].toUpperCase() : props.series_code;
});

// 事件处理
const onImageLoad = () => {
  isLoading.value = false;
  imageError.value = false;
};

const onImageError = () => {
  isLoading.value = false;
  imageError.value = true;
};
</script>

<style lang="scss" scoped>
// iOS 18 风格 CPU 徽章组件
.cpu-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  
  // 尺寸变体
  &--sm {
    width: 32rpx;
    height: 32rpx;
  }
  
  &--md {
    width: 48rpx;
    height: 48rpx;
  }
  
  &--lg {
    width: 64rpx;
    height: 64rpx;
  }
  
  // 平滑圆角（Continuous Corners）
  border-radius: 12rpx;
  
  // 加载状态
  &--loading {
    opacity: 0.8;
  }
}

// 图片样式
.cpu-badge__image {
  width: 100%;
  height: 100%;
  // 图片本身不需要圆角，由容器控制
}

// 兜底显示样式
.cpu-badge__fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

// 兜底文本样式
.cpu-badge__text {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-weight: 600;
  color: white;
  text-shadow: 0 1rpx 2rpx rgba(0, 0, 0, 0.2);
  
  // 文本尺寸适应组件大小
  .cpu-badge--sm & {
    font-size: 16rpx;
  }
  
  .cpu-badge--md & {
    font-size: 20rpx;
  }
  
  .cpu-badge--lg & {
    font-size: 24rpx;
  }
}
</style>
