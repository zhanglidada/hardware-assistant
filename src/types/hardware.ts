/**
 * 硬件基础接口
 */
export interface BaseHardware {
  /** 唯一标识符 */
  id: string;
  /** 型号名称 */
  model: string;
  /** 品牌：Intel, AMD, NVIDIA 等 */
  brand: 'Intel' | 'AMD' | 'NVIDIA' | '其他';
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
