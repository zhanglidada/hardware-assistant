import { defineStore } from 'pinia'
import type { CpuSpecs, GpuSpecs } from '../types/hardware'

export interface CompareItem {
  id: string
  type: 'cpu' | 'gpu'
  model: string
  brand: string
  price: number
}

export const useCompareStore = defineStore('compare', {
  state: () => ({
    cpuList: [] as CompareItem[],
    gpuList: [] as CompareItem[],
  }),

  getters: {
    // 获取所有对比项总数
    totalCount: (state) => state.cpuList.length + state.gpuList.length,
    
    // 检查某个硬件是否已在对比列表中
    isInCompare: (state) => {
      return (id: string, type: 'cpu' | 'gpu') => {
        const list = type === 'cpu' ? state.cpuList : state.gpuList
        return list.some(item => item.id === id)
      }
    },
    
    // 获取对比项详情（用于PK页面）
    compareItems: (state) => {
      return {
        cpu: state.cpuList,
        gpu: state.gpuList,
      }
    },
    
    // 检查是否可以开始PK（至少有两个同类型硬件）
    canStartPK: (state) => {
      return state.cpuList.length >= 2 || state.gpuList.length >= 2
    },
  },

  actions: {
    // 切换硬件对比状态
    toggleCompare(item: CpuSpecs | GpuSpecs) {
      const type = 'cores' in item ? 'cpu' : 'gpu'
      const list = type === 'cpu' ? this.cpuList : this.gpuList
      const index = list.findIndex(i => i.id === item.id)
      
      if (index > -1) {
        // 如果已存在，则移除
        list.splice(index, 1)
        return { added: false, message: '已从对比列表中移除' }
      } else {
        // 检查是否已达到上限（最多2个）
        if (list.length >= 2) {
          return { added: false, message: `最多只能对比2个${type === 'cpu' ? 'CPU' : '显卡'}` }
        }
        
        // 添加到对比列表
        const compareItem: CompareItem = {
          id: item.id,
          type,
          model: item.model,
          brand: item.brand,
          price: item.price,
        }
        
        list.push(compareItem)
        return { added: true, message: '已加入对比列表' }
      }
    },
    
    // 清空对比列表
    clearCompare(type?: 'cpu' | 'gpu') {
      if (type) {
        if (type === 'cpu') {
          this.cpuList = []
        } else {
          this.gpuList = []
        }
      } else {
        this.cpuList = []
        this.gpuList = []
      }
    },
    
    // 移除单个对比项
    removeCompareItem(id: string, type: 'cpu' | 'gpu') {
      const list = type === 'cpu' ? this.cpuList : this.gpuList
      const index = list.findIndex(item => item.id === id)
      if (index > -1) {
        list.splice(index, 1)
        return true
      }
      return false
    },
  },
})
