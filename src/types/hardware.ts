/**
 * 硬件基础接口
 */
export interface BaseHardware {
  /** 唯一标识符 */
  id: string;
  /** 型号名称 */
  model: string;
  /** 品牌：Intel, AMD, NVIDIA, Apple, Xiaomi, Huawei, Samsung 等 */
  brand: 'Intel' | 'AMD' | 'NVIDIA' | 'Apple' | 'Xiaomi' | 'Huawei' | 'Samsung' | '其他';
  /** 发布日期，格式：YYYY-MM-DD */
  releaseDate: string;
  /** 参考价格（人民币） */
  price: number;
  /** 描述信息 */
  description?: string;
}

/**
 * CPU 规格接口，继承自 BaseHardware
 */
export interface CpuSpecs extends BaseHardware {
  /** 核心配置，例如：'8P+16E' 表示 8个性能核 + 16个能效核 */
  cores: string;
  /** 基础频率，单位：GHz */
  baseClock: number;
  /** 最大加速频率，单位：GHz */
  boostClock: number;
  /** 接口类型，例如：LGA1700, AM5 */
  socket: string;
  /** 热设计功耗，单位：W */
  tdp: number;
  /** 是否集成显卡 */
  integratedGraphics: boolean;
  /** 缓存大小，单位：MB */
  cache: number;
}

/**
 * GPU 规格接口，继承自 BaseHardware
 */
export interface GpuSpecs extends BaseHardware {
  /** 显存大小，单位：GB */
  vram: number;
  /** 显存位宽，单位：bit */
  busWidth: number;
  /** CUDA核心数（NVIDIA）或流处理器数（AMD） */
  cudaCores: number;
  /** 核心频率，单位：MHz */
  coreClock: number;
  /** 显存频率，单位：MHz */
  memoryClock: number;
  /** 功耗，单位：W */
  powerConsumption: number;
  /** 是否支持光线追踪 */
  rayTracing: boolean;
  /** 是否支持DLSS/FSR */
  upscalingTech: 'DLSS' | 'FSR' | 'XeSS' | '无';
}

/**
 * 手机规格接口，继承自 BaseHardware
 */
export interface PhoneSpecs extends BaseHardware {
  /** 处理器型号 */
  processor: string;
  /** 内存大小，单位：GB */
  ram: number;
  /** 存储容量，单位：GB */
  storage: number;
  /** 屏幕尺寸，单位：英寸 */
  screenSize: number;
  /** 屏幕分辨率，格式：宽度x高度 */
  resolution: string;
  /** 刷新率，单位：Hz */
  refreshRate: number;
  /** 电池容量，单位：mAh */
  batteryCapacity: number;
  /** 摄像头配置，例如：'50MP+12MP+12MP' */
  camera: string;
  /** 操作系统 */
  os: 'iOS' | 'Android';
  /** 是否支持5G */
  support5G: boolean;
}

/**
 * CPU 系列信息接口
 */
export interface CpuSeriesInfo {
  /** 系列代码，主键，如 'intel_i9', 'amd_r7' */
  series_code: string;
  /** 显示名称，如 'Intel® Core™ i9' */
  display_name: string;
  /** 图标云存储ID，'cloud://...' 格式 */
  icon_cloud_id: string;
  /** 品牌色，用于做图片背景兜底 */
  bg_color: string;
}
