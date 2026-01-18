<script setup lang="ts">
import { onLaunch, onShow, onHide } from "@dcloudio/uni-app";

onLaunch(() => {
  console.log("App Launch");
  
  // 初始化微信云开发
  if (typeof wx !== 'undefined' && wx.cloud) {
    try {
      wx.cloud.init({
        traceUser: true,
        env: 'cloud1-1gqg24ni14cea8dd' // 云环境ID: cloud1-1gqg24ni14cea8dd
      });
      console.log("✅ 微信云开发初始化成功");
    } catch (error) {
      console.error("❌ 微信云开发初始化失败:", error);
      uni.showToast({
        title: '云服务初始化失败',
        icon: 'error',
        duration: 2000
      });
    }
  } else {
    console.warn("⚠️ 当前环境不支持微信云开发");
  }
});

onShow(() => {
  console.log("App Show");
});

onHide(() => {
  console.log("App Hide");
});
</script>
<style>
/* 导入字体修复样式 */
@import './styles/fix-font-loading.scss';
</style>
