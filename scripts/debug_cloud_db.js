/**
 * 调试微信云数据库连接
 * 在微信开发者工具控制台中运行此脚本
 */

// 检查云环境初始化
function checkCloudInit() {
  console.log('=== 检查微信云开发环境 ===');
  
  if (typeof wx === 'undefined') {
    console.error('❌ wx 对象未定义');
    return false;
  }
  
  if (!wx.cloud) {
    console.error('❌ wx.cloud 未定义');
    return false;
  }
  
  console.log('✅ wx.cloud 存在');
  
  // 检查当前云环境
  const cloudEnv = wx.cloud.CloudID;
  console.log('云环境ID:', cloudEnv || '未设置');
  
  return true;
}

// 测试数据库连接
async function testDatabaseConnection() {
  console.log('\n=== 测试数据库连接 ===');
  
  try {
    // 测试获取数据库实例
    const db = wx.cloud.database();
    console.log('✅ 数据库实例获取成功');
    
    // 测试集合列表（需要云函数支持，这里只测试基础连接）
    console.log('数据库名称:', db.config?.env || '默认环境');
    
    return true;
  } catch (error) {
    console.error('❌ 数据库连接失败:', error);
    return false;
  }
}

// 测试集合查询
async function testCollectionQuery(collectionName) {
  console.log(`\n=== 测试集合查询: ${collectionName} ===`);
  
  try {
    const db = wx.cloud.database();
    const collection = db.collection(collectionName);
    
    // 尝试获取记录数量
    const countResult = await collection.count();
    console.log(`✅ 集合 ${collectionName} 存在`);
    console.log(`📊 记录总数: ${countResult.total}`);
    
    // 尝试获取前几条记录
    const queryResult = await collection.limit(3).get();
    console.log(`📋 前3条记录:`, queryResult.data);
    
    return {
      exists: true,
      total: countResult.total,
      sample: queryResult.data
    };
  } catch (error) {
    console.error(`❌ 集合 ${collectionName} 查询失败:`, error.message);
    
    // 检查错误类型
    if (error.message.includes('collection not exists') || 
        error.message.includes('DATABASE_COLLECTION_NOT_EXIST')) {
      console.log(`⚠️ 集合 ${collectionName} 不存在`);
      return { exists: false, error: '集合不存在' };
    } else if (error.message.includes('permission denied')) {
      console.log(`⚠️ 权限不足，无法访问集合 ${collectionName}`);
      return { exists: true, error: '权限不足' };
    }
    
    return { exists: false, error: error.message };
  }
}

// 检查所有硬件集合
async function checkAllHardwareCollections() {
  console.log('\n=== 检查所有硬件集合 ===');
  
  const collections = [
    'cpu_collection',
    'gpu_collection', 
    'phone_collection'
  ];
  
  const results = {};
  
  for (const collection of collections) {
    results[collection] = await testCollectionQuery(collection);
  }
  
  return results;
}

// 检查云函数调用（可选）
async function testCloudFunction() {
  console.log('\n=== 测试云函数调用 ===');
  
  try {
    // 尝试调用一个简单的云函数
    const result = await wx.cloud.callFunction({
      name: 'test',
      data: {}
    }).catch(() => ({ result: { message: '云函数test不存在' } }));
    
    console.log('云函数测试结果:', result);
    return true;
  } catch (error) {
    console.log('云函数测试失败（可能未部署）:', error.message);
    return false;
  }
}

// 检查本地存储的数据
function checkLocalMockData() {
  console.log('\n=== 检查本地模拟数据 ===');
  
  try {
    // 尝试导入本地数据
    const mockData = {
      cpu: require('../src/mock/cpu_data.json'),
      gpu: require('../src/mock/gpu_data.json'),
      phone: require('../src/mock/phone_data.json')
    };
    
    console.log('✅ 本地数据加载成功');
    console.log(`📊 CPU数据: ${mockData.cpu.length} 条记录`);
    console.log(`📊 GPU数据: ${mockData.gpu.length} 条记录`);
    console.log(`📊 手机数据: ${mockData.phone.length} 条记录`);
    
    // 检查第一条记录的结构
    if (mockData.cpu.length > 0) {
      console.log('📋 CPU第一条记录结构:', Object.keys(mockData.cpu[0]));
      console.log('📋 是否有_id字段:', '_id' in mockData.cpu[0]);
      console.log('📋 releaseDate格式:', mockData.cpu[0].releaseDate);
    }
    
    return mockData;
  } catch (error) {
    console.error('❌ 本地数据加载失败:', error);
    return null;
  }
}

// 主调试函数
async function mainDebug() {
  console.log('🚀 开始微信云数据库调试');
  console.log('='.repeat(50));
  
  // 1. 检查云环境
  const cloudOk = checkCloudInit();
  if (!cloudOk) {
    console.log('\n⚠️ 云环境检查失败，应用将使用本地数据');
    return;
  }
  
  // 2. 测试数据库连接
  const dbOk = await testDatabaseConnection();
  if (!dbOk) {
    console.log('\n⚠️ 数据库连接失败，应用将使用本地数据');
    return;
  }
  
  // 3. 检查所有集合
  const collectionResults = await checkAllHardwareCollections();
  
  // 4. 检查本地数据
  const localData = checkLocalMockData();
  
  // 5. 汇总结果
  console.log('\n' + '='.repeat(50));
  console.log('📊 调试结果汇总');
  console.log('='.repeat(50));
  
  let hasCloudData = false;
  for (const [collection, result] of Object.entries(collectionResults)) {
    if (result.exists && result.total > 0) {
      console.log(`✅ ${collection}: 有云数据 (${result.total} 条)`);
      hasCloudData = true;
    } else if (result.exists && result.total === 0) {
      console.log(`⚠️ ${collection}: 集合存在但为空`);
    } else {
      console.log(`❌ ${collection}: 集合不存在或无权限`);
    }
  }
  
  if (!hasCloudData) {
    console.log('\n💡 建议:');
    console.log('1. 检查云环境ID是否正确');
    console.log('2. 确认数据已正确导入到云数据库');
    console.log('3. 检查集合名称是否匹配');
    console.log('4. 检查数据库权限设置');
  }
  
  // 6. 提供修复建议
  console.log('\n🔧 可能的解决方案:');
  console.log('1. 确认云环境ID: 在微信云控制台查看环境ID');
  console.log('2. 重新导入数据: 确保使用正确的集合名称');
  console.log('3. 修改代码中的集合名称: 检查是否与云数据库中的名称一致');
  console.log('4. 检查数据库权限: 在云控制台设置集合权限为"所有用户可读"');
}

// 导出函数供控制台使用
if (typeof wx !== 'undefined') {
  wx.debugCloudDB = {
    checkCloudInit,
    testDatabaseConnection,
    testCollectionQuery,
    checkAllHardwareCollections,
    checkLocalMockData,
    mainDebug
  };
  
  console.log('🔧 调试工具已加载，使用 wx.debugCloudDB.mainDebug() 开始调试');
}

// 如果直接运行，则执行主调试
if (typeof wx !== 'undefined' && wx.cloud) {
  setTimeout(() => {
    console.log('⏰ 3秒后自动开始调试...');
    setTimeout(mainDebug, 3000);
  }, 1000);
}
