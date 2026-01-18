/**
 * 微信云数据库数据访问 Hook
 * 提供统一的数据获取、分页加载、错误处理等功能
 */

import { ref, computed, type Ref } from 'vue'

/**
 * 分页查询参数
 */
export interface PaginationParams {
  /** 当前页码，从0开始 */
  page: number
  /** 每页数据量 */
  pageSize: number
  /** 跳过的数据量 */
  skip: number
}

/**
 * 数据加载状态
 */
export interface LoadState {
  /** 是否正在加载 */
  loading: boolean
  /** 是否已加载完成（没有更多数据） */
  finished: boolean
  /** 是否正在刷新 */
  refreshing: boolean
  /** 错误信息 */
  error: string | null
}

/**
 * 数据加载结果
 */
export interface LoadResult<T> {
  /** 数据列表 */
  list: T[]
  /** 是否有更多数据 */
  hasMore: boolean
  /** 总数据量 */
  total?: number
}

/**
 * 云数据库查询选项
 */
export interface CloudQueryOptions {
  /** 查询条件 */
  where?: any
  /** 排序字段 */
  orderBy?: {
    field: string
    order: 'asc' | 'desc'
  }
  /** 是否获取总数 */
  withCount?: boolean
}

/**
 * 微信云数据库数据访问 Hook
 * @param collectionName 集合名称
 * @param options 查询选项
 * @returns 数据访问方法和状态
 */
export function useCloudData<T = any>(
  collectionName: string,
  options: CloudQueryOptions = {}
) {
  // 响应式状态
  const list: Ref<T[]> = ref([])
  const loading = ref(false)
  const finished = ref(false)
  const refreshing = ref(false)
  const error = ref<string | null>(null)
  const page = ref(0)
  const pageSize = ref(20)
  const total = ref(0)

  /**
   * 计算跳过的数据量
   */
  const skip = computed(() => page.value * pageSize.value)

/**
 * 检查是否支持微信云开发
 */
const isCloudSupported = computed(() => {
  if (typeof wx === 'undefined') {
    console.log('❌ wx对象不存在，不在微信环境')
    return false
  }
  
  // 检查 wx.cloud 是否存在
  if (!wx.cloud) {
    console.log('❌ wx.cloud不存在，未引入云开发SDK')
    return false
  }
  
  // 检查云环境是否已初始化
  try {
    const db = wx.cloud.database()
    if (!db) {
      console.log('❌ 无法获取数据库实例')
      return false
    }
    
    // 检查环境配置
    const config = (db as any).config
    if (!config || !config.env) {
      console.log('⚠️ 数据库配置不完整:', config)
    } else {
      console.log(`✅ 云环境可用，环境ID: ${config.env}`)
    }
    
    return true
  } catch (error: any) {
    console.log('❌ 微信云数据库初始化失败:', error.message)
    return false
  }
})

  /**
   * 显示错误提示
   */
  const showError = (message: string) => {
    error.value = message
    uni.showToast({
      title: message,
      icon: 'error',
      duration: 2000
    })
  }

  /**
   * 显示加载提示
   */
  const showLoading = (title = '加载中...') => {
    uni.showLoading({
      title,
      mask: true
    })
  }

  /**
   * 隐藏加载提示
   */
  const hideLoading = () => {
    uni.hideLoading()
  }

  /**
   * 构建查询条件
   */
  const buildQuery = () => {
    if (!isCloudSupported.value) {
      throw new Error('当前环境不支持微信云开发')
    }

    try {
      // 使用非空断言，因为isCloudSupported已经检查过了
      const db = wx.cloud!.database()
      console.log(`📊 构建查询: 集合=${collectionName}, skip=${skip.value}, limit=${pageSize.value}`)
      
      let query = db.collection(collectionName)

      // 添加查询条件
      if (options.where) {
        console.log('🔍 查询条件:', options.where)
        query = query.where(options.where)
      }

      // 添加排序
      if (options.orderBy) {
        console.log(`📈 排序: ${options.orderBy.field} ${options.orderBy.order}`)
        query = query.orderBy(options.orderBy.field, options.orderBy.order)
      }

      // 添加分页
      query = query.skip(skip.value).limit(pageSize.value)

      return query
    } catch (error: any) {
      console.error('❌ 构建查询失败:', error)
      throw new Error(`构建查询失败: ${error.message}`)
    }
  }

  /**
   * 获取数据总数
   */
  const fetchTotalCount = async (): Promise<number> => {
    if (!isCloudSupported.value) {
      return 0
    }

    try {
      // 使用非空断言，因为isCloudSupported已经检查过了
      const db = wx.cloud!.database()
      let query = db.collection(collectionName)
      
      if (options.where) {
        query = query.where(options.where)
      }

      const result = await query.count()
      return result.total
    } catch (err) {
      console.error('获取数据总数失败:', err)
      return 0
    }
  }

  /**
   * 加载本地模拟数据（备用方案）
   */
  const loadLocalMockData = async (): Promise<LoadResult<T>> => {
    console.log(`使用本地模拟数据: ${collectionName}`)
    
    try {
      // 根据集合名称加载对应的本地数据
      let mockData: any[] = []
      
      switch (collectionName) {
        case 'cpu_collection':
          const cpuModule = await import('../mock/cpu_data.json')
          mockData = cpuModule.default || []
          break
        case 'gpu_collection':
          const gpuModule = await import('../mock/gpu_data.json')
          mockData = gpuModule.default || []
          break
        case 'phone_collection':
          const phoneModule = await import('../mock/phone_data.json')
          mockData = phoneModule.default || []
          break
        default:
          console.warn(`未找到集合 ${collectionName} 的本地数据`)
          mockData = []
      }
      
      // 应用查询条件（简单过滤）
      let filteredData = mockData
      if (options.where && options.where.$or) {
        const keyword = options.where.$or[0]?.model || options.where.$or[0]?.brand || ''
        if (keyword) {
          filteredData = mockData.filter(item => 
            item.model?.includes(keyword) || 
            item.brand?.includes(keyword) ||
            item.description?.includes(keyword)
          )
        }
      }
      
      // 应用排序
      if (options.orderBy) {
        filteredData.sort((a, b) => {
          const aVal = a[options.orderBy!.field]
          const bVal = b[options.orderBy!.field]
          if (options.orderBy!.order === 'asc') {
            return aVal > bVal ? 1 : -1
          } else {
            return aVal < bVal ? 1 : -1
          }
        })
      }
      
      // 应用分页
      const startIndex = skip.value
      const endIndex = startIndex + pageSize.value
      const pagedData = filteredData.slice(startIndex, endIndex)
      
      // 判断是否有更多数据
      const hasMore = endIndex < filteredData.length
      
      return {
        list: pagedData as T[],
        hasMore,
        total: filteredData.length
      }
    } catch (err) {
      console.error('加载本地数据失败:', err)
      return {
        list: [],
        hasMore: false
      }
    }
  }

  /**
   * 加载数据
   * @param isRefresh 是否为刷新操作
   */
  const loadData = async (isRefresh = false): Promise<LoadResult<T>> => {
    // 重置错误状态
    error.value = null

    // 设置加载状态
    if (isRefresh) {
      refreshing.value = true
    } else {
      loading.value = true
    }

    console.log(`🚀 开始加载数据: 集合=${collectionName}, 刷新=${isRefresh}`)

    try {
      // 检查云开发支持
      if (!isCloudSupported.value) {
        console.warn('❌ 当前环境不支持微信云开发，使用本地数据')
        return await loadLocalMockData()
      }

      // 构建查询
      const query = buildQuery()

      // 执行查询
      console.log('📤 执行云数据库查询...')
      const result = await query.get()
      console.log(`✅ 查询成功: 获取到 ${result.data.length} 条数据`)

      // 获取数据
      const data = result.data as T[]
      
      if (data.length > 0) {
        console.log('📝 第一条数据:', JSON.stringify(data[0]).substring(0, 100) + '...')
      }

      // 更新总数（如果需要）
      if (options.withCount && isRefresh) {
        total.value = await fetchTotalCount()
      }

      // 判断是否有更多数据
      const hasMore = data.length === pageSize.value

      return {
        list: data,
        hasMore,
        total: total.value > 0 ? total.value : undefined
      }
    } catch (err: any) {
      const errorMessage = err.message || '数据加载失败'
      console.error('❌ 数据加载失败:', err)
      
      // 检查错误类型
      const errorLower = errorMessage.toLowerCase()
      const isCollectionError = errorLower.includes('collection') || 
                               errorLower.includes('不存在') ||
                               errorLower.includes('not exist')
      const isPermissionError = errorLower.includes('permission') || 
                               errorLower.includes('权限')
      const isEnvError = errorLower.includes('环境') || 
                        errorLower.includes('env')
      
      if (isCollectionError || isPermissionError || isEnvError) {
        console.warn(`⚠️ 云数据库访问失败 (${errorMessage})，使用本地数据作为备用`)
        
        // 使用本地数据
        const localResult = await loadLocalMockData()
        
        // 显示提示信息
        if (isRefresh) {
          uni.showToast({
            title: '使用本地演示数据',
            icon: 'none',
            duration: 2000
          })
        }
        
        return localResult
      } else {
        // 显示错误提示
        showError(`数据加载失败: ${errorMessage}`)
      }
      
      // 尝试使用本地数据作为最后的手段
      return await loadLocalMockData()
    } finally {
      // 重置加载状态
      if (isRefresh) {
        refreshing.value = false
      } else {
        loading.value = false
      }
      hideLoading()
    }
  }

  /**
   * 加载更多数据（分页）
   */
  const loadMore = async (): Promise<void> => {
    // 如果正在加载或已加载完成，则直接返回
    if (loading.value || finished.value) {
      return
    }

    // 显示加载提示
    showLoading('加载更多...')

    const result = await loadData(false)

    if (result.list.length > 0) {
      // 追加数据
      list.value = [...list.value, ...result.list]
      page.value += 1
    }

    // 更新完成状态
    finished.value = !result.hasMore

    // 如果没有数据且不是第一页，显示提示
    if (result.list.length === 0 && page.value > 0) {
      uni.showToast({
        title: '没有更多数据了',
        icon: 'none',
        duration: 1500
      })
    }
  }

  /**
   * 刷新数据（重置到第一页）
   */
  const refresh = async (): Promise<void> => {
    // 如果正在刷新，则直接返回
    if (refreshing.value) {
      return
    }

    // 显示加载提示
    showLoading('刷新中...')

    // 重置状态
    page.value = 0
    finished.value = false

    const result = await loadData(true)

    if (result.list.length > 0) {
      // 替换数据
      list.value = result.list
      page.value = 1
    } else {
      // 清空数据
      list.value = []
    }

    // 更新完成状态
    finished.value = !result.hasMore

    // 显示刷新完成提示
    uni.showToast({
      title: '刷新完成',
      icon: 'success',
      duration: 1500
    })
  }

/**
 * 搜索数据（带条件查询）
 * @param keyword 搜索关键词
 * @param searchFields 搜索字段，默认为 ['model', 'brand', 'description']
 */
const search = async (
  keyword: string,
  searchFields: string[] = ['model', 'brand', 'description']
): Promise<void> => {
  if (!keyword.trim()) {
    // 如果关键词为空，清除搜索条件
    options.where = undefined
    await refresh()
    return
  }

  // 检查是否支持云数据库
  if (!isCloudSupported.value) {
    // 使用本地搜索
    console.log('使用本地搜索:', keyword)
    options.where = {
      $or: searchFields.map(field => ({
        [field]: keyword
      }))
    }
    reset()
    await refresh()
    return
  }

  // 微信云数据库支持正则表达式模糊搜索
  // 使用 db.RegExp 进行模糊匹配
  // 使用非空断言，因为isCloudSupported已经检查过了
  const db = wx.cloud!.database()
  const whereCondition = {
    $or: searchFields.map(field => ({
      [field]: (db as any).RegExp({
        regexp: keyword,
        options: 'i' // 不区分大小写
      })
    }))
  }

  // 更新查询选项
  options.where = whereCondition
  
  // 重置状态并刷新数据
  reset()
  await refresh()
}

/**
 * 清除搜索条件
 */
const clearSearch = async (): Promise<void> => {
  options.where = undefined
  await refresh()
}

  /**
   * 重置所有状态
   */
  const reset = (): void => {
    list.value = []
    loading.value = false
    finished.value = false
    refreshing.value = false
    error.value = null
    page.value = 0
    total.value = 0
  }

  // 返回状态和方法
  return {
    // 状态
    list,
    loading: computed(() => loading.value),
    finished: computed(() => finished.value),
    refreshing: computed(() => refreshing.value),
    error: computed(() => error.value),
    page: computed(() => page.value),
    pageSize: computed(() => pageSize.value),
    total: computed(() => total.value),
    skip,
    isCloudSupported,

    // 方法
    loadMore,
    refresh,
    search,
    reset,
    loadData
  }
}

/**
 * 硬件数据专用 Hook
 * @param collectionName 集合名称
 * @param options 查询选项
 * @returns 数据访问方法和状态
 */
export function useHardwareList<T extends { id: string }>(
  collectionName: string,
  options: CloudQueryOptions = {}
) {
  return useCloudData<T>(collectionName, options)
}

export default useCloudData
