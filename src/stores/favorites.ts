import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { CpuSpecs, GpuSpecs, PhoneSpecs } from '@/types/hardware'

type HardwareItem = CpuSpecs | GpuSpecs | PhoneSpecs

export interface FavoriteItem {
  id: string
  model: string
  brand: string
  releaseDate: string
  price: number
  description?: string
  type: 'cpu' | 'gpu' | 'phone'
  addTime: number
  specs?: Record<string, any>
}

export const useFavoritesStore = defineStore('favorites', () => {
  const favorites = ref<FavoriteItem[]>([])
  const STORAGE_KEY = 'hardware_favorites'

  const loadFavorites = () => {
    try {
      const stored = uni.getStorageSync(STORAGE_KEY)
      if (stored) {
        favorites.value = JSON.parse(stored)
      }
    } catch (error) {
      console.error('加载收藏失败:', error)
      favorites.value = []
    }
  }

  const saveFavorites = () => {
    try {
      uni.setStorageSync(STORAGE_KEY, JSON.stringify(favorites.value))
    } catch (error) {
      console.error('保存收藏失败:', error)
    }
  }

  const addFavorite = (item: HardwareItem, type: 'cpu' | 'gpu' | 'phone') => {
    const exists = favorites.value.some(fav => fav.id === item.id)
    if (exists) {
      return false
    }

    favorites.value.unshift({
      id: item.id,
      model: item.model,
      brand: item.brand,
      releaseDate: item.releaseDate,
      price: item.price,
      description: item.description,
      type,
      addTime: Date.now(),
      specs: item as Record<string, any>
    })
    saveFavorites()
    return true
  }

  const removeFavorite = (id: string) => {
    const index = favorites.value.findIndex(fav => fav.id === id)
    if (index !== -1) {
      favorites.value.splice(index, 1)
      saveFavorites()
      return true
    }
    return false
  }

  const toggleFavorite = (item: HardwareItem, type: 'cpu' | 'gpu' | 'phone') => {
    const exists = favorites.value.some(fav => fav.id === item.id)
    if (exists) {
      removeFavorite(item.id)
      return false
    } else {
      addFavorite(item, type)
      return true
    }
  }

  const isFavorite = (id: string) => {
    return favorites.value.some(fav => fav.id === id)
  }

  const getFavoritesByType = (type: 'cpu' | 'gpu' | 'phone') => {
    return favorites.value.filter(fav => fav.type === type)
  }

  const clearAllFavorites = () => {
    favorites.value = []
    saveFavorites()
  }

  const favoritesCount = computed(() => favorites.value.length)

  const cpuFavorites = computed(() => getFavoritesByType('cpu'))
  const gpuFavorites = computed(() => getFavoritesByType('gpu'))
  const phoneFavorites = computed(() => getFavoritesByType('phone'))

  loadFavorites()

  return {
    favorites,
    favoritesCount,
    cpuFavorites,
    gpuFavorites,
    phoneFavorites,
    addFavorite,
    removeFavorite,
    toggleFavorite,
    isFavorite,
    getFavoritesByType,
    clearAllFavorites,
    loadFavorites
  }
})
