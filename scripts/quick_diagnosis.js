/**
 * 快速诊断脚本
 * 在微信开发者工具控制台中运行
 */

async function quickDiagnosis() {
  console.log('🔍 开始快速诊断...')
  console.log('='.repeat(50))
  
  // 1. 检查环境
  console.log('1. 环境检查:')
  if (typeof wx === 'undefined') {
    console.log('❌ wx 对象不存在 - 不在微信环境')
    return
  }
  console.log('✅ wx 对象存在')
  
  if (!wx.cloud) {
    console.log('❌ wx.cloud 不存在 - 未引入云开发SDK')
    return
  }
  console.log('✅ wx.cloud 存在')
  
  // 2. 检查云环境初始化
  console.log('\n2. 云环境检查:')
  try {
    const db = wx.cloud.database()
    console.log('✅ 数据库实例获取成功')
    console.log('环境ID:', db.config?.env || '默认环境')
  } catch (error) {
    console.log('❌ 数据库连接失败:', error.message)
    return
  }
  
  // 3. 检查集合
  console.log('\n3. 集合检查:')
  const collections = ['cpu_collection', 'gpu_collection', 'phone_collection']
  
  for (const collectionName of collections) {
    try {
      const db = wx.cloud.database()
      const collection = db.collection(collectionName)
      const countResult = await collection.count()
      console.log(`📊 ${collectionName}: ${countResult.total} 条记录`)
      
      if (countResult.total > 0) {
        // 获取一条样本数据
        const sample = await collection.limit(1).get()
        console.log(`  样本: ${JSON.stringify(sample.data[0]).substring(0, 100)}...`)
      }
    } catch (error) {
      console.log(`❌ ${collectionName}: ${error.message}`)
    }
  }
  
  // 4. 检查首页数据加载
  console.log('\n4. 首页数据加载测试:')
  try {
    // 模拟首页数据加载
    const db = wx.cloud.database()
    const collection = db.collection('cpu_collection')
    const result = await collection.orderBy('releaseDate', 'desc').limit(10).get()
    console.log(`✅ CPU数据加载成功: ${result.data.length} 条记录`)
    
    if (result.data.length > 0) {
      console.log('第一条记录:', {
        id: result.data[0].id,
        model: result.data[0].model,
        brand: result.data[0].brand
      })
    }
  } catch (error) {
    console.log(`❌ 数据加载失败: ${error.message}`)
  }
  
  // 5. 检查本地数据
  console.log('\n5. 本地数据检查:')
  try {
    // 尝试访问本地数据（通过uni-app的require）
    const localData = {
      cpu: require('../src/mock/cpu_data.json'),
      gpu: require('../src/mock/gpu_data.json'),
      phone: require('../src/mock/phone_data.json')
    }
    console.log(`✅ 本地数据加载成功`)
    console.log(`   CPU: ${localData.cpu.length} 条`)
    console.log(`   GPU: ${localData.gpu.length} 条`)
    console.log(`   手机: ${localData.phone.length} 条`)
  } catch (error) {
    console.log(`❌ 本地数据加载失败: ${error.message}`)
  }
  
  console.log('\n' + '='.repeat(50))
  console.log('🚀 诊断完成')
  
  // 提供建议
  console.log('\n💡 建议:')
  console.log('1. 如果云数据库有数据但页面不显示，检查页面组件逻辑')
  console.log('2. 如果云数据库无数据，确认数据已正确导入')
  console.log('3. 访问调试页面: /pages/debug/index')
  console.log('4. 检查控制台是否有其他错误')
}

// 自动运行诊断
if (typeof wx !== 'undefined') {
  console.log('🔧 快速诊断工具已加载')
  console.log('运行 quickDiagnosis() 开始诊断')
  
  // 3秒后自动运行
  setTimeout(() => {
    console.log('⏰ 3秒后自动运行诊断...')
    setTimeout(quickDiagnosis, 3000)
  }, 1000)
} else {
  console.log('⚠️ 不在微信环境，无法运行诊断')
}
