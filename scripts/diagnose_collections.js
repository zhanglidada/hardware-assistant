#!/usr/bin/env node

/**
 * 诊断云数据库集合问题
 * 用于检查为什么gpu_collection和phone_collection查询不到数据
 */

console.log('🔍 诊断云数据库集合问题');
console.log('='.repeat(60));

// 模拟微信环境
const mockWx = {
  cloud: {
    init: () => console.log('云环境初始化'),
    database: () => {
      console.log('获取数据库实例');
      return {
        config: { env: 'cloud1-1gqg24ni14cea8dd' },
        collection: (name) => {
          console.log(`访问集合: ${name}`);
          return {
            where: (condition) => {
              console.log(`查询条件: ${JSON.stringify(condition)}`);
              return {
                orderBy: (field, order) => {
                  console.log(`排序: ${field} ${order}`);
                  return {
                    skip: (skip) => {
                      console.log(`跳过: ${skip}`);
                      return {
                        limit: (limit) => {
                          console.log(`限制: ${limit}`);
                          return {
                            get: async () => {
                              console.log('执行查询...');
                              // 模拟不同集合的响应
                              if (name === 'cpu_collection') {
                                return {
                                  data: [
                                    { id: '1', model: 'Intel Core i9', brand: 'Intel', price: 3999 },
                                    { id: '2', model: 'AMD Ryzen 9', brand: 'AMD', price: 2999 }
                                  ]
                                };
                              } else if (name === 'gpu_collection') {
                                // 模拟gpu_collection返回空数据
                                return { data: [] };
                              } else if (name === 'phone_collection') {
                                // 模拟phone_collection返回空数据
                                return { data: [] };
                              }
                              return { data: [] };
                            },
                            count: async () => {
                              console.log('获取总数...');
                              if (name === 'cpu_collection') {
                                return { total: 2 };
                              } else {
                                return { total: 0 };
                              }
                            }
                          };
                        }
                      };
                    }
                  };
                }
              };
            }
          };
        }
      };
    }
  }
};

// 分析useCloudData.ts中的问题
console.log('\n📋 分析 useCloudData.ts 中的潜在问题:');
console.log('='.repeat(60));

const potentialIssues = [
  {
    issue: '1. 集合名称不匹配',
    description: '代码中使用的集合名称与云数据库中的实际名称不一致',
    check: () => {
      const codeCollections = ['cpu_collection', 'gpu_collection', 'phone_collection'];
      console.log('代码中使用的集合名称:', codeCollections);
      console.log('请确认云数据库中是否存在完全相同的集合名称');
    }
  },
  {
    issue: '2. 数据格式问题',
    description: '云数据库中的数据格式与代码期望的格式不匹配',
    check: () => {
      console.log('检查数据类型:');
      console.log('- 是否有 _id 字段？');
      console.log('- releaseDate 是否为字符串格式？');
      console.log('- 字段名称是否与 hardware.ts 中定义的一致？');
    }
  },
  {
    issue: '3. 查询条件问题',
    description: 'orderBy 字段在集合中不存在',
    check: () => {
      console.log('代码中的 orderBy 配置:');
      console.log('- CPU: { field: "releaseDate", order: "desc" }');
      console.log('- GPU: { field: "releaseDate", order: "desc" }');
      console.log('- Phone: { field: "releaseDate", order: "desc" }');
      console.log('请确认每个集合中都有 releaseDate 字段');
    }
  },
  {
    issue: '4. 权限问题',
    description: '集合权限设置不正确',
    check: () => {
      console.log('权限检查:');
      console.log('- 集合权限是否设置为"所有用户可读"？');
      console.log('- 是否开启了安全规则？');
    }
  },
  {
    issue: '5. 数据为空',
    description: '集合存在但没有数据',
    check: () => {
      console.log('数据检查:');
      console.log('- 使用微信开发者工具的云控制台查看集合数据');
      console.log('- 确认每个集合中都有数据记录');
    }
  },
  {
    issue: '6. 环境配置问题',
    description: '云环境ID配置错误',
    check: () => {
      console.log('环境配置检查:');
      console.log('- App.vue 中的 env: "cloud1-1gqg24ni14cea8dd"');
      console.log('- 请确认这是正确的云环境ID');
    }
  }
];

// 执行检查
potentialIssues.forEach((item, index) => {
  console.log(`\n${item.issue}: ${item.description}`);
  console.log('-'.repeat(40));
  item.check();
});

// 提供解决方案
console.log('\n🔧 解决方案:');
console.log('='.repeat(60));

const solutions = [
  {
    step: '1. 检查集合数据',
    action: '在微信开发者工具的云控制台中:',
    details: [
      '打开云开发控制台',
      '选择数据库标签',
      '检查 cpu_collection, gpu_collection, phone_collection',
      '确认每个集合都有数据'
    ]
  },
  {
    step: '2. 检查数据格式',
    action: '对比第一条记录的结构:',
    details: [
      '检查是否有 _id 字段（云数据库自动生成）',
      '检查 releaseDate 字段是否为字符串',
      '检查字段名称是否与代码中的接口定义匹配'
    ]
  },
  {
    step: '3. 测试直接查询',
    action: '在云控制台中执行查询:',
    details: [
      '对每个集合执行: db.collection("xxx").get()',
      '检查返回的数据',
      '确认 orderBy 字段存在'
    ]
  },
  {
    step: '4. 修改代码调试',
    action: '临时修改 useCloudData.ts:',
    details: [
      '移除 orderBy 条件测试',
      '增加更详细的日志输出',
      '检查错误信息'
    ]
  },
  {
    step: '5. 使用调试工具',
    action: '运行内置调试工具:',
    details: [
      '在微信开发者工具控制台中运行: wx.debugCloudDB.mainDebug()',
      '或访问调试页面: /pages/debug/index'
    ]
  }
];

solutions.forEach(solution => {
  console.log(`\n${solution.step}: ${solution.action}`);
  solution.details.forEach(detail => {
    console.log(`  • ${detail}`);
  });
});

// 创建测试用例
console.log('\n🧪 测试用例:');
console.log('='.repeat(60));

const testCases = `
// 测试用例 1: 基本查询（无排序）
const test1 = async () => {
  const db = wx.cloud.database();
  const result = await db.collection('gpu_collection').limit(5).get();
  console.log('GPU基础查询结果:', result.data);
};

// 测试用例 2: 检查字段
const test2 = async () => {
  const db = wx.cloud.database();
  const result = await db.collection('gpu_collection').limit(1).get();
  if (result.data.length > 0) {
    const item = result.data[0];
    console.log('GPU字段检查:', Object.keys(item));
    console.log('是否有releaseDate字段:', 'releaseDate' in item);
  }
};

// 测试用例 3: 计数查询
const test3 = async () => {
  const db = wx.cloud.database();
  const result = await db.collection('gpu_collection').count();
  console.log('GPU记录总数:', result.total);
};

console.log('在微信开发者工具控制台中运行这些测试用例');
`;

console.log(testCases);

console.log('\n📊 诊断完成');
console.log('='.repeat(60));
console.log('建议按以下步骤排查:');
console.log('1. 首先确认云数据库中集合和数据的存在');
console.log('2. 检查数据格式是否匹配代码期望');
console.log('3. 使用简单查询测试，逐步添加条件');
console.log('4. 查看控制台错误信息');
console.log('5. 使用调试工具获取详细信息');
