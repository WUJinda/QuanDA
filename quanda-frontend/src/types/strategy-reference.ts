// 策略参考库类型定义
export interface StrategyReference {
  id: string
  name: string
  description: string
  image: string  // 截图URL
  code: string  // 合约代码
  frequence: string  // K线周期
  startTime: string  // 区间开始时间
  endTime: string  // 区间结束时间
  pattern: PatternInfo  // 形态信息
  indicators: IndicatorData  // 指标数据
  klineData: KLineSegment[]  // K线数据片段
  tags: string[]  // 标签
  createTime: string
  updateTime: string
}

export interface PatternInfo {
  type: string  // 形态类型：突破、回调、震荡等
  bollPosition: 'upper' | 'middle' | 'lower' | 'between'  // BOLL位置
  trend: 'up' | 'down' | 'sideways'  // 趋势方向
  description: string  // 形态描述
}

export interface IndicatorData {
  boll: {
    upper: number[]
    middle: number[]
    lower: number[]
  }
  ma: {
    ma5?: number[]
    ma10?: number[]
    ma20?: number[]
  }
  volume: number[]
  priceChange: number  // 区间涨跌幅
  volatility: number  // 波动率
}

export interface KLineSegment {
  time: string
  open: number
  close: number
  high: number
  low: number
  volume: number
}

export interface StrategyReferenceFilter {
  pattern?: string
  trend?: string
  frequence?: string
  tags?: string[]
  dateRange?: [string, string]
}

// K线区域选择数据
export interface BrushSelectedData {
  startTime: string
  endTime: string
  startIndex: number
  endIndex: number
  klineData: KLineSegment[]
  imageData?: string  // base64 截图
  code: string  // 合约代码
  frequence: string  // K线周期
}
