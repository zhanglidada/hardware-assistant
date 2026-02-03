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
  where?: Record<string, any>
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
   * 本地Mock数据降级
   */
  const loadLocalMockData = async (reason: string): Promise<LoadResult<T>> => {
    console.warn(`⚠️ 云数据不可用，已切换到本地数据: ${reason}`)
    try {
      let data: T[] = []
      
      // 动态导入本地Mock数据
      switch (collectionName) {
        case 'cpu_collection':
          const cpuModule = await import('../mock/cpu_data.json')
          data = (cpuModule.default || cpuModule) as T[]
          break
        case 'gpu_collection':
          const gpuModule = await import('../mock/gpu_data.json')
          data = (gpuModule.default || gpuModule) as T[]
          break
        case 'phone_collection':
          const phoneModule = await import('../mock/phone_data.json')
          data = (phoneModule.default || phoneModule) as T[]
          break
        default:
          console.warn(`⚠️ 未找到对应集合的Mock数据: ${collectionName}`)
          data = []
      }

      return {
        list: data,
        hasMore: false,
        total: data.length
      }
    } catch (localError: any) {
      console.error('❌ 本地数据加载失败:', localError)
      return {
        list: [],
        hasMore: false
      }
    }
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
        console.warn('❌ 当前环境不支持微信云开发')
        return await loadLocalMockData('当前环境不支持微信云开发')
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
      } else {
        console.log(`⚠️ 集合 ${collectionName} 查询成功但返回空数据`)
        console.log('可能的原因:')
        console.log('1. 集合中没有数据')
        console.log('2. orderBy字段不存在导致查询失败')
        console.log('3. 查询条件过滤了所有数据')
        
        // 尝试不使用orderBy查询
        if (options.orderBy) {
          console.log(`🔄 尝试不使用orderBy查询集合 ${collectionName}`)
          try {
            const db = wx.cloud!.database()
            const simpleQuery = db.collection(collectionName)
              .skip(skip.value)
              .limit(pageSize.value)
            const simpleResult = await simpleQuery.get()
            console.log(`简单查询结果: ${simpleResult.data.length} 条数据`)
            if (simpleResult.data.length > 0) {
              console.log('第一条数据字段:', Object.keys(simpleResult.data[0]))
            }
          } catch (simpleError) {
            console.log('简单查询错误:', simpleError)
          }
        }
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
      const isOrderByError = errorLower.includes('orderby') || 
                            errorLower.includes('排序') ||
                            errorLower.includes('index')
      
      if (isCollectionError || isPermissionError || isEnvError) {
        console.warn(`⚠️ 云数据库访问失败 (${errorMessage})`)
        return await loadLocalMockData(errorMessage)
      } else if (isOrderByError) {
        console.warn(`⚠️ orderBy字段错误 (${errorMessage})，尝试不使用排序查询`)
        
        // 尝试不使用orderBy查询
        try {
          const db = wx.cloud!.database()
          const query = db.collection(collectionName)
            .skip(skip.value)
            .limit(pageSize.value)
          
          const result = await query.get()
          console.log(`✅ 无排序查询成功: 获取到 ${result.data.length} 条数据`)
          
          return {
            list: result.data as T[],
            hasMore: result.data.length === pageSize.value,
            total: result.data.length
          }
        } catch (noOrderError) {
          console.error('无排序查询也失败:', noOrderError)
          // 显示警告但不抛出错误，让用户至少能看到数据
          showError(`排序字段错误，已禁用排序功能`)
          // 返回空列表，让前端可以显示错误或空状态
          return {
            list: [],
            hasMore: false
          }
        }
      } else {
        // 显示错误提示
        showError(`数据加载失败: ${errorMessage}`)
        throw err
      }
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
    console.warn('❌ 当前环境不支持微信云开发，无法进行搜索')
    showError('当前环境不支持微信云开发，无法进行搜索')
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
