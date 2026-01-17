import { defineStore } from 'pinia'
import type { CpuSpecs, GpuSpecs, PhoneSpecs } from '../types/hardware'

export interface CompareItem {
  id: string
  type: 'cpu' | 'gpu' | 'phone'
  model: string
  brand: string
  price: number
}

// 最大对比数量常量
const MAX_COMPARE_ITEMS = 2

export const useCompareStore = defineStore('compare', {
  state: () => ({
    cpuList: [] as CompareItem[],
    gpuList: [] as CompareItem[],
    phoneList: [] as CompareItem[],
  }),

  getters: {
    // 获取所有对比项总数
    totalCount: (state) => state.cpuList.length + state.gpuList.length + state.phoneList.length,
    
    // 检查某个硬件是否已在对比列表中
    isInCompare: (state) => {
      return (id: string, type: 'cpu' | 'gpu' | 'phone') => {
        const list = type === 'cpu' ? state.cpuList : type === 'gpu' ? state.gpuList : state.phoneList
        return list.some(item => item.id === id)
      }
    },
    
    // 获取对比项详情（用于PK页面）
    compareItems: (state) => {
      return {
        cpu: state.cpuList,
        gpu: state.gpuList,
        phone: state.phoneList,
      }
    },
    
    // 检查是否可以开始PK（至少有两个同类型硬件）
    canStartPK: (state) => {
      return state.cpuList.length >= 2 || state.gpuList.length >= 2 || state.phoneList.length >= 2
    },
    
    // 获取指定类型的对比列表是否已满
    isListFull: (state) => {
      return (type: 'cpu' | 'gpu' | 'phone') => {
        const list = type === 'cpu' ? state.cpuList : type === 'gpu' ? state.gpuList : state.phoneList
        return list.length >= MAX_COMPARE_ITEMS
      }
    },
  },

  actions: {
    // 类型守卫：判断是否为CPU
    isCpuSpecs(item: CpuSpecs | GpuSpecs | PhoneSpecs): item is CpuSpecs {
      return 'cores' in item
    },
    
    // 类型守卫：判断是否为GPU
    isGpuSpecs(item: CpuSpecs | GpuSpecs | PhoneSpecs): item is GpuSpecs {
      return 'vram' in item
    },
    
    // 类型守卫：判断是否为手机
    isPhoneSpecs(item: CpuSpecs | GpuSpecs | PhoneSpecs): item is PhoneSpecs {
      return 'ram' in item
    },
    
    // 获取对应类型的列表
    getListByType(type: 'cpu' | 'gpu' | 'phone'): CompareItem[] {
      return type === 'cpu' ? this.cpuList : type === 'gpu' ? this.gpuList : this.phoneList
    },
    
    // 切换硬件对比状态
    toggleCompare(item: CpuSpecs | GpuSpecs | PhoneSpecs) {
      let type: 'cpu' | 'gpu' | 'phone'
      if (this.isCpuSpecs(item)) {
        type = 'cpu'
      } else if (this.isGpuSpecs(item)) {
        type = 'gpu'
      } else {
        type = 'phone'
      }
      
      const list = this.getListByType(type)
      const index = list.findIndex(i => i.id === item.id)
      
      if (index > -1) {
        // 如果已存在，则移除
        list.splice(index, 1)
        return { added: false, message: '已从对比列表中移除' }
      } else {
        // 检查是否已达到上限（最多2个）
        if (list.length >= MAX_COMPARE_ITEMS) {
          const typeName = type === 'cpu' ? 'CPU' : type === 'gpu' ? '显卡' : '手机'
          return { added: false, message: `最多只能对比${MAX_COMPARE_ITEMS}个${typeName}` }
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
    clearCompare(type?: 'cpu' | 'gpu' | 'phone') {
      if (type) {
        const list = this.getListByType(type)
        list.length = 0 // 更高效的方式清空数组
      } else {
        this.cpuList.length = 0
        this.gpuList.length = 0
        this.phoneList.length = 0
      }
    },
    
    // 移除单个对比项
    removeCompareItem(id: string, type: 'cpu' | 'gpu' | 'phone') {
      const list = this.getListByType(type)
      const index = list.findIndex(item => item.id === id)
      
      // 边界检查
      if (index < 0 || index >= list.length) {
        return false
      }
      
      list.splice(index, 1)
      return true
    },
    
    // 添加对比项（直接添加，不检查重复）
    addCompareItem(item: CpuSpecs | GpuSpecs | PhoneSpecs): { success: boolean; message: string } {
      let type: 'cpu' | 'gpu' | 'phone'
      if (this.isCpuSpecs(item)) {
        type = 'cpu'
      } else if (this.isGpuSpecs(item)) {
        type = 'gpu'
      } else {
        type = 'phone'
      }
      
      const list = this.getListByType(type)
      
      // 检查是否已存在
      if (list.some(existing => existing.id === item.id)) {
        return { success: false, message: '该硬件已在对比列表中' }
      }
      
        // 检查是否已达到上限
        if (list.length >= MAX_COMPARE_ITEMS) {
          const typeName = type === 'cpu' ? 'CPU' : type === 'gpu' ? '显卡' : '手机'
          return { success: false, message: `最多只能对比${MAX_COMPARE_ITEMS}个${typeName}` }
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
      return { success: true, message: '已加入对比列表' }
    },
    
    // 批量设置对比项（用于初始化或恢复状态）
    setCompareItems(items: CompareItem[]) {
      // 按类型分组
      const cpuItems: CompareItem[] = []
      const gpuItems: CompareItem[] = []
      const phoneItems: CompareItem[] = []
      
      // 去重处理（使用数组替代 Set 以确保 ES5 兼容性）
      const seenIds: string[] = []
      
      for (const item of items) {
        // 跳过重复项（使用 indexOf 替代 includes 确保 ES5 兼容性）
        if (seenIds.indexOf(item.id) !== -1) {
          continue
        }
        
        // 根据类型分组，并确保不超过最大数量
        if (item.type === 'cpu' && cpuItems.length < MAX_COMPARE_ITEMS) {
          cpuItems.push(item)
          seenIds.push(item.id)
        } else if (item.type === 'gpu' && gpuItems.length < MAX_COMPARE_ITEMS) {
          gpuItems.push(item)
          seenIds.push(item.id)
        } else if (item.type === 'phone' && phoneItems.length < MAX_COMPARE_ITEMS) {
          phoneItems.push(item)
          seenIds.push(item.id)
        }
      }
      
      this.cpuList = cpuItems
      this.gpuList = gpuItems
      this.phoneList = phoneItems
    },
  },
})
