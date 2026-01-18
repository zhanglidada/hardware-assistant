<template>
  <view class="debug-container">
    <view class="header">
      <text class="title">云数据库调试</text>
      <text class="subtitle">诊断数据加载问题</text>
    </view>

    <view class="section">
      <text class="section-title">环境状态</text>
      <view class="status-box">
        <text>wx对象: {{ wxExists ? '✅ 存在' : '❌ 不存在' }}</text>
        <text>wx.cloud: {{ wxCloudExists ? '✅ 存在' : '❌ 不存在' }}</text>
        <text>云环境: {{ cloudInitialized ? '✅ 已初始化' : '❌ 未初始化' }}</text>
      </view>
    </view>

    <view class="section">
      <text class="section-title">集合检查</text>
      <view class="collection-box">
        <view v-for="col in collections" :key="col.name" class="collection-item">
          <text>{{ col.name }}: </text>
          <text v-if="!col.checked" class="status-pending">待检查</text>
          <text v-else-if="col.error" class="status-error">{{ col.error }}</text>
          <text v-else class="status-success">{{ col.count }} 条记录</text>
          <wd-button v-if="!col.checked" size="mini" @click="checkCollection(col)">检查</wd-button>
        </view>
      </view>
      <wd-button @click="checkAllCollections" type="primary">检查所有集合</wd-button>
    </view>

    <view class="section">
      <text class="section-title">数据加载测试</text>
      <view class="test-buttons">
        <wd-button @click="testLoad('cpu')" size="small">测试CPU</wd-button>
        <wd-button @click="testLoad('gpu')" size="small">测试GPU</wd-button>
        <wd-button @click="testLoad('phone')" size="small">测试手机</wd-button>
      </view>
      <view v-if="testResult" class="result-box">
        <text>{{ testResult }}</text>
      </view>
    </view>

    <view class="section">
      <text class="section-title">本地数据</text>
      <view class="local-data">
        <text>CPU: {{ localData.cpu }} 条</text>
        <text>GPU: {{ localData.gpu }} 条</text>
        <text>手机: {{ localData.phone }} 条</text>
      </view>
    </view>

    <view class="section">
      <text class="section-title">问题诊断</text>
      <view class="diagnosis">
        <text v-if="diagnosis" class="diagnosis-text">{{ diagnosis }}</text>
        <text v-if="solution" class="solution-text">{{ solution }}</text>
      </view>
      <wd-button @click="runDiagnosis" type="primary" size="large">运行完整诊断</wd-button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// 状态
const wxExists = ref(false)
const wxCloudExists = ref(false)
const cloudInitialized = ref(false)

const collections = ref([
  { name: 'cpu_collection', checked: false, count: 0, error: '' },
  { name: 'gpu_collection', checked: false, count: 0, error: '' },
  { name: 'phone_collection', checked: false, count: 0, error: '' }
])

const testResult = ref('')
const localData = ref({ cpu: 0, gpu: 0, phone: 0 })
const diagnosis = ref('')
const solution = ref('')

onMounted(() => {
  checkEnv()
  loadLocal()
})

// 检查环境
const checkEnv = () => {
  wxExists.value = typeof wx !== 'undefined'
  if (wxExists.value) {
    wxCloudExists.value = !!wx.cloud
    if (wxCloudExists.value) {
      try {
        wx.cloud.database()
        cloudInitialized.value = true
      } catch {
        cloudInitialized.value = false
      }
    }
  }
}

// 检查集合
const checkCollection = async (col: any) => {
  if (!cloudInitialized.value) {
    col.error = '云环境未初始化'
    col.checked = true
    return
  }

  try {
    const db = (wx as any).cloud.database()
    const collection = db.collection(col.name)
    const result = await collection.count()
    col.count = result.total
    col.error = ''
    col.checked = true
  } catch (err: any) {
    col.count = 0
    col.error = err.message || '检查失败'
    col.checked = true
  }
}

// 检查所有集合
const checkAllCollections = async () => {
  for (const col of collections.value) {
    await checkCollection(col)
  }
}

// 测试加载
const testLoad = async (type: string) => {
  const collectionName = `${type}_collection`
  testResult.value = `正在加载${type.toUpperCase()}数据...`
  
  try {
    // 使用动态导入避免类型问题
    const { useHardwareList } = await import('../../composables/useCloudData')
    const { loadData } = useHardwareList(collectionName)
    
    const result = await loadData(true)
    testResult.value = `✅ ${type.toUpperCase()}数据加载成功\n加载了 ${result.list.length} 条记录`
  } catch (err: any) {
    testResult.value = `❌ ${type.toUpperCase()}数据加载失败: ${err.message}`
  }
}

// 加载本地数据
const loadLocal = async () => {
  try {
    const cpu = await import('../../mock/cpu_data.json')
    localData.value.cpu = cpu.default?.length || 0
  } catch {
    localData.value.cpu = 0
  }
  
  try {
    const gpu = await import('../../mock/gpu_data.json')
    localData.value.gpu = gpu.default?.length || 0
  } catch {
    localData.value.gpu = 0
  }
  
  try {
    const phone = await import('../../mock/phone_data.json')
    localData.value.phone = phone.default?.length || 0
  } catch {
    localData.value.phone = 0
  }
}

// 运行诊断
const runDiagnosis = async () => {
  diagnosis.value = ''
  solution.value = ''
  
  // 检查环境
  checkEnv()
  
  // 检查集合
  await checkAllCollections()
  
  // 加载本地数据
  await loadLocal()
  
  // 分析问题
  const issues = []
  
  if (!wxExists.value) {
    issues.push('不在微信环境')
    solution.value = '请在微信开发者工具中运行'
  } else if (!wxCloudExists.value) {
    issues.push('未引入云开发SDK')
    solution.value = '检查项目配置，确保引入了云开发SDK'
  } else if (!cloudInitialized.value) {
    issues.push('云环境未初始化')
    solution.value = '检查App.vue中的云环境ID配置'
  }
  
  const emptyCollections = collections.value.filter(c => c.count === 0)
  if (emptyCollections.length === 3) {
    issues.push('所有集合都为空')
    solution.value = '请确认数据已正确导入云数据库，或检查集合权限'
  }
  
  if (localData.value.cpu === 0) {
    issues.push('本地数据为空')
    solution.value += '\n本地数据文件可能损坏，请检查src/mock/目录'
  }
  
  if (issues.length === 0) {
    diagnosis.value = '✅ 所有检查通过，系统正常'
    solution.value = '数据应该正常显示，如果仍有问题请检查页面组件'
  } else {
    diagnosis.value = `发现 ${issues.length} 个问题: ${issues.join(', ')}`
  }
}
</script>

<style scoped>
.debug-container {
  padding: 30rpx;
  min-height: 100vh;
  background: #f5f5f5;
}

.header {
  text-align: center;
  margin-bottom: 40rpx;
}

.title {
  font-size: 36rpx;
  font-weight: bold;
  display: block;
  color: #333;
}

.subtitle {
  font-size: 28rpx;
  color: #666;
  display: block;
}

.section {
  background: white;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.08);
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
  display: block;
  color: #333;
  border-bottom: 2rpx solid #f0f0f0;
  padding-bottom: 10rpx;
}

.status-box, .collection-box, .local-data {
  display: flex;
  flex-direction: column;
  gap: 15rpx;
  margin-bottom: 20rpx;
}

.collection-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 15rpx;
  background: #f8f9fa;
  border-radius: 12rpx;
}

.status-pending {
  color: #999;
}

.status-success {
  color: #52c41a;
}

.status-error {
  color: #ff4d4f;
}

.test-buttons {
  display: flex;
  gap: 20rpx;
  margin-bottom: 20rpx;
}

.result-box {
  padding: 20rpx;
  background: #f8f9fa;
  border-radius: 12rpx;
  font-size: 26rpx;
  line-height: 1.6;
}

.diagnosis {
  margin-bottom: 20rpx;
}

.diagnosis-text {
  color: #ff4d4f;
  display: block;
  margin-bottom: 10rpx;
  font-size: 28rpx;
}

.solution-text {
  color: #1890ff;
  display: block;
  font-size: 26rpx;
  line-height: 1.6;
  white-space: pre-line;
}
</style>
