/**
 * useCloudData Hook 使用示例
 * 演示如何使用微信云数据库数据访问 Hook
 */

import { useHardwareList, useCloudData } from './useCloudData'
import type { CpuSpecs, GpuSpecs, PhoneSpecs } from '../types/hardware'

/**
 * 示例1: 使用硬件专用 Hook
 */
export function useCpuListExample() {
  // 使用硬件专用 Hook，自动推断类型
  const cpuList = useHardwareList<CpuSpecs>('cpu_collection', {
    // 查询条件：只获取 Intel 品牌的 CPU
    where: {
      brand: 'Intel'
    },
    // 按价格降序排序
    orderBy: {
      field: 'price',
      order: 'desc'
    },
    // 获取总数
    withCount: true
  })

  // 在组件中使用的示例
  const exampleUsage = () => {
    // 初始加载数据
    cpuList.refresh()

    // 加载更多数据
    cpuList.loadMore()

    // 搜索特定型号
    cpuList.search('Core i7')

    // 重置所有状态
    cpuList.reset()
  }

  return {
    cpuList,
    exampleUsage
  }
}

/**
 * 示例2: 使用通用 Hook
 */
export function useGpuListExample() {
  // 使用通用 Hook，需要显式指定类型
  const gpuList = useCloudData<GpuSpecs>('gpu_collection', {
    // 查询条件：显存大于等于 8GB
    where: {
      vram: {
        $gte: 8
      }
    },
    // 按核心频率降序排序
    orderBy: {
      field: 'coreClock',
      order: 'desc'
    }
  })

  return gpuList
}

/**
 * 示例3: 手机数据查询
 */
export function usePhoneListExample() {
  const phoneList = useHardwareList<PhoneSpecs>('phone_collection', {
    // 查询条件：支持5G的手机
    where: {
      support5G: true
    },
    // 按发布时间降序排序
    orderBy: {
      field: 'releaseDate',
      order: 'desc'
    },
    withCount: true
  })

  return phoneList
}

/**
 * 示例4: 复杂查询条件
 */
export function useComplexQueryExample() {
  // 复杂查询：价格在3000-8000之间，且支持光线追踪的显卡
  const complexQuery = useCloudData<GpuSpecs>('gpu_collection', {
    where: {
      price: {
        $gte: 3000,
        $lte: 8000
      },
      rayTracing: true
    },
    orderBy: {
      field: 'price',
      order: 'asc'
    }
  })

  return complexQuery
}

/**
 * 示例5: 在 Vue 组件中使用
 * 这是一个虚拟的 Vue 组件示例
 */
/*
<script setup lang="ts">
import { useHardwareList } from '@/composables/useCloudData'
import type { CpuSpecs } from '@/types/hardware'

// 初始化 CPU 列表
const { 
  list: cpuList, 
  loading, 
  finished, 
  refresh, 
  loadMore 
} = useHardwareList<CpuSpecs>('cpu_collection')

// 页面加载时刷新数据
onMounted(() => {
  refresh()
})

// 下拉刷新
const onRefresh = () => {
  refresh()
}

// 上拉加载更多
const onLoadMore = () => {
  loadMore()
}
</script>

<template>
  <wd-pull-refresh 
    v-model="loading" 
    :finished="finished" 
    @refresh="onRefresh" 
    @load="onLoadMore"
  >
    <wd-list>
      <wd-cell 
        v-for="cpu in cpuList" 
        :key="cpu.id"
        :title="cpu.model"
        :label="`品牌: ${cpu.brand} | 价格: ¥${cpu.price}`"
      >
        <template #value>
          <wd-tag type="primary">{{ cpu.cores }} 核心</wd-tag>
        </template>
      </wd-cell>
    </wd-list>
  </wd-pull-refresh>
</template>
*/

/**
 * 使用说明总结:
 * 
 * 1. 基本使用:
 *    const { list, loading, finished, refresh, loadMore } = useHardwareList<T>('collection_name')
 * 
 * 2. 带查询条件:
 *    const hardwareList = useHardwareList<T>('collection_name', {
 *      where: { brand: 'Intel' },
 *      orderBy: { field: 'price', order: 'desc' },
 *      withCount: true
 *    })
 * 
 * 3. 方法调用:
 *    - refresh(): 刷新数据（重置到第一页）
 *    - loadMore(): 加载更多数据（分页）
 *    - search(options): 搜索数据（带新查询条件）
 *    - reset(): 重置所有状态
 * 
 * 4. 状态监控:
 *    - list: 数据列表（响应式）
 *    - loading: 是否正在加载
 *    - finished: 是否已加载完成
 *    - refreshing: 是否正在刷新
 *    - error: 错误信息
 *    - page: 当前页码
 *    - total: 总数据量
 *    - isCloudSupported: 是否支持微信云开发
 * 
 * 5. 错误处理:
 *    - 自动显示错误提示
 *    - 支持优雅降级（云开发不可用时）
 *    - 详细的错误日志
 */
