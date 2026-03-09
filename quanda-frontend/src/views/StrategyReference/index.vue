<template>
  <div class="strategy-reference-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建参考
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-select v-model="filter.trend" placeholder="趋势" style="width: 120px;" clearable>
          <el-option label="上涨" value="up" />
          <el-option label="下跌" value="down" />
          <el-option label="震荡" value="sideways" />
        </el-select>
        <el-select v-model="filter.frequence" placeholder="周期" style="width: 120px;" clearable>
          <el-option label="日线" value="day" />
          <el-option label="60分" value="60min" />
          <el-option label="30分" value="30min" />
          <el-option label="15分" value="15min" />
          <el-option label="5分" value="5min" />
        </el-select>
        <el-button @click="fetchList">查询</el-button>
      </div>
    </div>

    <div class="reference-grid">
      <div 
        v-for="item in referenceList" 
        :key="item.id" 
        class="reference-card"
        @click="viewDetail(item)"
      >
        <div class="card-image">
          <img :src="item.image || '/placeholder.png'" :alt="item.name" />
        </div>
        <div class="card-content">
          <h4>{{ item.name }}</h4>
          <p class="description">{{ item.description }}</p>
          <div class="meta">
            <el-tag size="small" :type="getTrendType(item.pattern.trend)">
              {{ getTrendLabel(item.pattern.trend) }}
            </el-tag>
            <el-tag size="small">{{ item.frequence }}</el-tag>
            <span class="time">{{ formatTime(item.createTime) }}</span>
          </div>
          <div class="tags">
            <el-tag 
              v-for="tag in item.tags" 
              :key="tag" 
              size="small" 
              type="info"
            >
              {{ tag }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建对话框 -->
    <el-dialog 
      v-model="showCreateDialog" 
      title="新建策略参考" 
      width="900px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input 
            v-model="form.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入描述"
          />
        </el-form-item>
        <el-form-item label="上传截图">
          <el-upload
            class="upload-demo"
            :action="uploadUrl"
            :on-success="handleUploadSuccess"
            :before-upload="beforeUpload"
            :show-file-list="false"
          >
            <el-button type="primary">选择图片</el-button>
          </el-upload>
          <div v-if="form.image" class="preview-image">
            <img :src="form.image" alt="预览" />
          </div>
        </el-form-item>
        <el-form-item label="合约代码">
          <el-input v-model="form.code" placeholder="如: IF2512" />
        </el-form-item>
        <el-form-item label="K线周期">
          <el-select v-model="form.frequence" style="width: 100%;">
            <el-option label="日线" value="day" />
            <el-option label="60分钟" value="60min" />
            <el-option label="30分钟" value="30min" />
            <el-option label="15分钟" value="15min" />
            <el-option label="5分钟" value="5min" />
            <el-option label="1分钟" value="1min" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间区间">
          <el-date-picker
            v-model="form.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="标签">
          <el-select 
            v-model="form.tags" 
            multiple 
            filterable 
            allow-create
            placeholder="请选择或输入标签"
            style="width: 100%;"
          >
            <el-option label="突破" value="突破" />
            <el-option label="回调" value="回调" />
            <el-option label="震荡" value="震荡" />
            <el-option label="趋势" value="趋势" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="analyzeSegment" :loading="analyzing">
            分析区间数据
          </el-button>
        </el-form-item>
        <el-form-item v-if="analyzedData" label="分析结果">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="趋势">
              {{ getTrendLabel(analyzedData.pattern.trend) }}
            </el-descriptions-item>
            <el-descriptions-item label="BOLL位置">
              {{ getBollPositionLabel(analyzedData.pattern.bollPosition) }}
            </el-descriptions-item>
            <el-descriptions-item label="涨跌幅">
              {{ analyzedData.indicators.priceChange.toFixed(2) }}%
            </el-descriptions-item>
            <el-descriptions-item label="波动率">
              {{ analyzedData.indicators.volatility.toFixed(2) }}%
            </el-descriptions-item>
          </el-descriptions>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createReference" :loading="creating">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog 
      v-model="showDetailDialog" 
      title="策略参考详情" 
      width="1200px"
    >
      <div v-if="currentDetail" class="detail-content">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="detail-image">
              <img :src="currentDetail.image" :alt="currentDetail.name" />
            </div>
          </el-col>
          <el-col :span="12">
            <h3>{{ currentDetail.name }}</h3>
            <p>{{ currentDetail.description }}</p>
            <el-descriptions :column="1" border style="margin-top: 20px;">
              <el-descriptions-item label="合约代码">
                {{ currentDetail.code }}
              </el-descriptions-item>
              <el-descriptions-item label="K线周期">
                {{ currentDetail.frequence }}
              </el-descriptions-item>
              <el-descriptions-item label="时间区间">
                {{ currentDetail.startTime }} ~ {{ currentDetail.endTime }}
              </el-descriptions-item>
              <el-descriptions-item label="趋势">
                <el-tag :type="getTrendType(currentDetail.pattern.trend)">
                  {{ getTrendLabel(currentDetail.pattern.trend) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="BOLL位置">
                {{ getBollPositionLabel(currentDetail.pattern.bollPosition) }}
              </el-descriptions-item>
              <el-descriptions-item label="涨跌幅">
                {{ currentDetail.indicators.priceChange.toFixed(2) }}%
              </el-descriptions-item>
              <el-descriptions-item label="波动率">
                {{ currentDetail.indicators.volatility.toFixed(2) }}%
              </el-descriptions-item>
            </el-descriptions>
          </el-col>
        </el-row>
        <div class="kline-section" style="margin-top: 20px;">
          <h4>K线数据</h4>
          <KLineChart 
            :data="detailKlineData" 
            :showBoll="true" 
            height="400px" 
          />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { strategyReferenceApi } from '@/api/strategy-reference'
import KLineChart from '@/components/Charts/KLineChart.vue'
import type { StrategyReference } from '@/types/strategy-reference'

const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const creating = ref(false)
const analyzing = ref(false)
const referenceList = ref<StrategyReference[]>([])
const currentDetail = ref<StrategyReference | null>(null)
const analyzedData = ref<any>(null)
const uploadUrl = ref('/api/strategy-reference/upload')

const filter = ref({
  trend: '',
  frequence: ''
})

const form = ref({
  name: '',
  description: '',
  image: '',
  code: '',
  frequence: 'day',
  dateRange: [],
  tags: []
})

const detailKlineData = ref([])

const fetchList = async () => {
  try {
    referenceList.value = await strategyReferenceApi.getList(filter.value)
  } catch (error) {
    ElMessage.error('获取列表失败')
  }
}

const handleUploadSuccess = (response: any) => {
  // el-upload 组件的 on-success 接收原始响应（不经过拦截器）
  // 响应格式: { status: 200, res: { url: '...' } }
  if (response && response.res && response.res.url) {
    form.value.image = response.res.url
    ElMessage.success('上传成功')
  } else if (response && response.url) {
    // 如果拦截器已经处理过，直接取 url
    form.value.image = response.url
    ElMessage.success('上传成功')
  } else {
    ElMessage.error('上传失败')
  }
}

const beforeUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

const analyzeSegment = async () => {
  if (!form.value.code || !form.value.dateRange || form.value.dateRange.length !== 2) {
    ElMessage.warning('请填写合约代码和时间区间')
    return
  }

  analyzing.value = true
  try {
    analyzedData.value = await strategyReferenceApi.analyzeSegment(
      form.value.code,
      form.value.dateRange[0],
      form.value.dateRange[1],
      form.value.frequence
    )
    ElMessage.success('分析完成')
  } catch (error) {
    ElMessage.error('分析失败')
  } finally {
    analyzing.value = false
  }
}

const createReference = async () => {
  if (!form.value.name || !analyzedData.value) {
    ElMessage.warning('请填写完整信息并分析区间数据')
    return
  }

  creating.value = true
  try {
    const data = {
      ...form.value,
      startTime: form.value.dateRange[0],
      endTime: form.value.dateRange[1],
      pattern: analyzedData.value.pattern,
      indicators: analyzedData.value.indicators,
      klineData: analyzedData.value.klineData
    }
    
    await strategyReferenceApi.create(data)
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    fetchList()
  } catch (error) {
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}

const viewDetail = async (item: StrategyReference) => {
  try {
    currentDetail.value = await strategyReferenceApi.getDetail(item.id)

    // 转换K线数据格式
    if (currentDetail.value?.klineData) {
      detailKlineData.value = currentDetail.value.klineData.map((k: any) => ({
        time: k.date || k.datetime || '',
        open: k.open ?? 0,
        close: k.close ?? 0,
        high: k.high ?? 0,
        low: k.low ?? 0,
        volume: k.volume ?? 0
      }))
    }

    showDetailDialog.value = true
  } catch (error) {
    ElMessage.error('获取详情失败')
  }
}

const getTrendType = (trend: string) => {
  const map: Record<string, any> = {
    up: 'danger',
    down: 'success',
    sideways: 'warning'
  }
  return map[trend] || 'info'
}

const getTrendLabel = (trend: string) => {
  const map: Record<string, string> = {
    up: '上涨',
    down: '下跌',
    sideways: '震荡'
  }
  return map[trend] || trend
}

const getBollPositionLabel = (position: string) => {
  const map: Record<string, string> = {
    upper: '上轨附近',
    middle: '中轨附近',
    lower: '下轨附近',
    between: '轨道之间'
  }
  return map[position] || position
}

const formatTime = (time: string) => {
  return new Date(time).toLocaleDateString()
}

onMounted(() => {
  fetchList()
})
</script>

<style lang="scss" scoped>
.strategy-reference-page {
  .reference-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
  }

  .reference-card {
    background: #fff;
    border-radius: 8px;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.3s;
    border: 1px solid #e8e8e8;

    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      transform: translateY(-2px);
    }

    .card-image {
      width: 100%;
      height: 200px;
      overflow: hidden;
      background: #f5f5f5;

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }

    .card-content {
      padding: 16px;

      h4 {
        margin: 0 0 8px 0;
        font-size: 16px;
        font-weight: 600;
      }

      .description {
        color: #666;
        font-size: 14px;
        margin: 0 0 12px 0;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
      }

      .meta {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;

        .time {
          color: #999;
          font-size: 12px;
          margin-left: auto;
        }
      }

      .tags {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
      }
    }
  }

  .preview-image {
    margin-top: 10px;
    
    img {
      max-width: 300px;
      max-height: 200px;
      border-radius: 4px;
    }
  }

  .detail-content {
    .detail-image {
      width: 100%;
      
      img {
        width: 100%;
        border-radius: 8px;
      }
    }

    h3 {
      margin: 0 0 12px 0;
      font-size: 20px;
      font-weight: 600;
    }

    h4 {
      margin: 0 0 12px 0;
      font-size: 16px;
      font-weight: 600;
    }
  }
}
</style>
