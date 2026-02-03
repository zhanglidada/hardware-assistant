# 微信云数据库集合创建指南

## 问题描述
应用报错：`database collection not exists`，表示云数据库集合不存在。

## 解决方案

### 方法1：在微信开发者工具中手动创建集合

1. **打开微信开发者工具**
   - 打开硬件参数小助手项目
   - 确保已开通云开发服务

2. **进入云开发控制台**
   - 点击开发者工具左侧的"云开发"按钮
   - 或访问：https://developers.weixin.qq.com/miniprogram/dev/wxcloud/basis/getting-started.html

3. **创建数据库集合**
   需要创建以下3个集合：
   - `cpu_collection` - CPU数据
   - `gpu_collection` - 显卡数据  
   - `phone_collection` - 手机数据

4. **操作步骤**
   ```
   云开发控制台 → 数据库 → 集合名称 → 新建集合
   ```

### 方法2：使用云函数自动创建集合

创建一个云函数来初始化数据库：

```javascript
// cloudfunctions/initDatabase/index.js
const cloud = require('wx-server-sdk')
cloud.init()

exports.main = async (event, context) => {
  const db = cloud.database()
  
  // 创建集合（如果不存在）
  const collections = ['cpu_collection', 'gpu_collection', 'phone_collection']
  
  for (const collectionName of collections) {
    try {
      // 尝试创建集合
      await db.createCollection(collectionName)
      console.log(`集合 ${collectionName} 创建成功`)
    } catch (err) {
      // 集合可能已存在
      console.log(`集合 ${collectionName} 可能已存在:`, err.message)
    }
  }
  
  return {
    success: true,
    message: '数据库初始化完成'
  }
}
```

### 方法3：修改代码使用已存在的集合

如果不想创建新集合，可以修改代码使用已存在的集合名称：

1. **修改 `src/pages/index/index.vue`**
   ```typescript
   // 将集合名称改为已存在的集合
   const cpuListHook = useHardwareList<CpuSpecs>('existing_cpu_collection', {
     // ... 其他配置
   })
   ```

2. **修改 `src/composables/useCloudData.ts`**
   ```typescript
   // 检查集合是否存在，不存在则使用备用数据
   ```

## 数据导入

创建集合后，需要导入数据：

### 1. 使用微信开发者工具导入
- 进入云开发控制台 → 数据库
- 选择对应集合 → 导入
- 选择对应的JSON文件：
  - `src/mock/cpu_data.json`
  - `src/mock/gpu_data.json` 
  - `src/mock/phone_data.json`

### 2. 使用云函数批量导入
```javascript
// cloudfunctions/importData/index.js
const cloud = require('wx-server-sdk')
cloud.init()

exports.main = async (event, context) => {
  const db = cloud.database()
  const { collectionName, data } = event
  
  try {
    // 批量插入数据
    const result = await db.collection(collectionName).add({
      data: data
    })
    
    return {
      success: true,
      inserted: result._id
    }
  } catch (err) {
    return {
      success: false,
      error: err.message
    }
  }
}
```

## 环境配置

### 1. 更新云环境ID
修改 `src/App.vue` 中的云环境ID：

```javascript
wx.cloud.init({
  traceUser: true,
  env: 'your-actual-env-id' // ← 替换为实际的云环境ID
})
```

### 2. 获取云环境ID
1. 打开微信开发者工具
2. 点击"云开发"按钮
3. 在控制台顶部查看环境ID

## 测试验证

### 1. 测试集合是否存在
```javascript
// 在微信开发者工具控制台测试
wx.cloud.database().collection('cpu_collection').count()
  .then(res => console.log('集合存在，数据量:', res.total))
  .catch(err => console.error('集合不存在或错误:', err))
```

### 2. 测试数据查询
```javascript
// 测试查询功能
wx.cloud.database().collection('cpu_collection').get()
  .then(res => console.log('数据:', res.data))
  .catch(err => console.error('查询失败:', err))
```

## 故障排除

### 常见问题1：权限不足
**错误**: `Permission denied`
**解决方案**: 
1. 进入云开发控制台 → 数据库 → 权限设置
2. 设置为"所有用户可读，仅创建者可读写"

### 常见问题2：环境ID错误
**错误**: `Environment not found`
**解决方案**:
1. 确认云环境ID是否正确
2. 检查是否已开通云开发服务
3. 确认小程序已关联云环境

### 常见问题3：集合名称错误
**错误**: `collection not exists`
**解决方案**:
1. 确认集合名称拼写正确
2. 检查集合是否已创建
3. 确认集合权限设置正确

## 备用方案

如果云数据库问题无法立即解决，可以暂时使用本地数据：

1. **修改 `useCloudData.ts`** 添加本地数据回退
2. **使用 `src/mock/` 文件夹中的JSON数据**
3. **显示友好提示**，告知用户数据服务暂不可用

## 联系支持

如果问题仍然存在：
1. 查看微信云开发文档：https://developers.weixin.qq.com/miniprogram/dev/wxcloud/basis/getting-started.html
2. 在微信开放社区提问
3. 联系微信云开发技术支持
