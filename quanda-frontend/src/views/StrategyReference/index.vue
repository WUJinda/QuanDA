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
      >
        <div class="card-image" @click="viewDetail(item)">
          <img :src="item.image || '/placeholder.png'" :alt="item.name" />
        </div>
        <div class="card-content" @click="viewDetail(item)">
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
        <div class="card-actions">
          <button class="action-btn detail-btn" @click.stop="viewDetail(item)">
            <el-icon><View /></el-icon>
            详情
          </button>
          <button class="action-btn edit-btn" @click.stop="editReference(item)">
            <el-icon><Edit /></el-icon>
            编辑
          </button>
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
            :default-time="defaultTimeRange"
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

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑策略参考"
      width="900px"
      :close-on-click-modal="false"
    >
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="名称">
          <el-input v-model="editForm.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述"
          />
        </el-form-item>
        <el-form-item label="上传截图">
          <el-upload
            class="upload-demo"
            :action="uploadUrl"
            :on-success="handleEditUploadSuccess"
            :before-upload="beforeUpload"
            :show-file-list="false"
          >
            <el-button type="primary">更换图片</el-button>
          </el-upload>
          <div v-if="editForm.image" class="preview-image">
            <img :src="editForm.image" alt="预览" />
          </div>
        </el-form-item>
        <el-form-item label="合约代码">
          <el-input v-model="editForm.code" placeholder="如: IF2512" />
        </el-form-item>
        <el-form-item label="K线周期">
          <el-select v-model="editForm.frequence" style="width: 100%;">
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
            v-model="editForm.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            :default-time="defaultTimeRange"
          />
        </el-form-item>
        <el-form-item label="标签">
          <el-select
            v-model="editForm.tags"
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
          <el-button type="primary" @click="reanalyzeSegment" :loading="analyzing">
            重新分析区间数据
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
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="danger" @click="deleteReference" :loading="deleting">
          删除
        </el-button>
        <el-button type="primary" @click="updateReference" :loading="updating">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      width="95%"
      top="5vh"
    >
      <template #header>
        <div class="detail-header">
          <span class="detail-title">策略参考详情</span>
          <el-button
            :type="isBrushMode ? 'primary' : 'default'"
            :icon="Scissor"
            @click="toggleBrushMode"
          >
            {{ isBrushMode ? '取消截取' : '截取区域' }}
          </el-button>
        </div>
      </template>
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
          <div class="kline-header">
            <h4>K线数据</h4>
            <el-tag v-if="isBrushMode" type="primary" size="small">
              请在K线图上拖拽选择区域
            </el-tag>
          </div>
          <KLineChart
            v-if="detailKlineData.length > 0"
            ref="klineChartRef"
            :data="detailKlineData"
            :enable-brush="isBrushMode"
            height="400px"
            @brush-selected="handleBrushSelected"
          />
        </div>
      </div>
    </el-dialog>

    <!-- 截取区域确认对话框 -->
    <el-dialog
      v-model="showConfirmDialog"
      title="确认截取区域"
      width="600px"
      :close-on-click-modal="false"
    >
      <div v-if="selectedBrushData" class="brush-confirm-content">
        <div v-if="selectedBrushData.imageData" class="preview-section">
          <h4>预览图</h4>
          <img :src="selectedBrushData.imageData" alt="截取预览" class="preview-image" />
        </div>
        <el-descriptions :column="1" border class="info-section">
          <el-descriptions-item label="合约代码">
            {{ selectedBrushData.code }}
          </el-descriptions-item>
          <el-descriptions-item label="K线周期">
            {{ selectedBrushData.frequence }}
          </el-descriptions-item>
          <el-descriptions-item label="时间区间">
            {{ selectedBrushData.startTime }} ~ {{ selectedBrushData.endTime }}
          </el-descriptions-item>
          <el-descriptions-item label="K线数量">
            {{ selectedBrushData.klineData.length }} 根
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="showConfirmDialog = false">取消</el-button>
        <el-button @click="toggleBrushMode(true)">重新选择</el-button>
        <el-button type="primary" @click="confirmCapture" :loading="creatingFromBrush">
          确认截取
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, View, Edit, Scissor } from '@element-plus/icons-vue'
import { strategyReferenceApi } from '@/api/strategy-reference'
import KLineChart from '@/components/Charts/KLineChart.vue'
import type { StrategyReference, BrushSelectedData } from '@/types/strategy-reference'
import type { KLineData } from '@/types/market'

const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showDetailDialog = ref(false)
const creating = ref(false)
const updating = ref(false)
const deleting = ref(false)
const analyzing = ref(false)
const referenceList = ref<StrategyReference[]>([])
const currentDetail = ref<StrategyReference | null>(null)
const editingId = ref<string | null>(null)
const analyzedData = ref<any>(null)
const uploadUrl = ref('/api/strategy-reference/upload')

const filter = ref({
  trend: '',
  frequence: ''
})

const form = ref<{
  name: string
  description: string
  image: string
  code: string
  frequence: string
  dateRange: string[]
  tags: string[]
}>({
  name: '',
  description: '',
  image: '',
  code: '',
  frequence: 'day',
  dateRange: [],
  tags: []
})

const editForm = ref<{
  name: string
  description: string
  image: string
  code: string
  frequence: string
  dateRange: string[]
  tags: string[]
}>({
  name: '',
  description: '',
  image: '',
  code: '',
  frequence: 'day',
  dateRange: [],
  tags: []
})

const detailKlineData = ref<KLineData[]>([])

// 区域截取相关状态
const isBrushMode = ref(false)  // 是否在截取模式
const selectedBrushData = ref<BrushSelectedData | null>(null)  // 选中的数据
const showConfirmDialog = ref(false)  // 确认对话框显示
const creatingFromBrush = ref(false)  // 从截取创建中

// 默认时间范围：最近两年
const defaultTimeRange = [
  new Date(2023, 0, 1, 9, 0, 0),  // 开始时间: 2023-01-01 09:00:00
  new Date(2025, 11, 31, 15, 0, 0)  // 结束时间: 2025-12-31 15:00:00
]

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

const handleEditUploadSuccess = (response: any) => {
  if (response && response.res && response.res.url) {
    editForm.value.image = response.res.url
    ElMessage.success('上传成功')
  } else if (response && response.url) {
    editForm.value.image = response.url
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

const editReference = (item: StrategyReference) => {
  editingId.value = item.id
  editForm.value = {
    name: item.name,
    description: item.description,
    image: item.image,
    code: item.code,
    frequence: item.frequence,
    dateRange: [item.startTime, item.endTime],
    tags: item.tags || []
  }
  analyzedData.value = {
    pattern: item.pattern,
    indicators: item.indicators
  }
  showEditDialog.value = true
}

const reanalyzeSegment = async () => {
  if (!editForm.value.code || !editForm.value.dateRange || editForm.value.dateRange.length !== 2) {
    ElMessage.warning('请填写合约代码和时间区间')
    return
  }

  analyzing.value = true
  try {
    analyzedData.value = await strategyReferenceApi.analyzeSegment(
      editForm.value.code,
      editForm.value.dateRange[0],
      editForm.value.dateRange[1],
      editForm.value.frequence
    )
    ElMessage.success('分析完成')
  } catch (error) {
    ElMessage.error('分析失败')
  } finally {
    analyzing.value = false
  }
}

const updateReference = async () => {
  if (!editForm.value.name || !analyzedData.value) {
    ElMessage.warning('请填写完整信息并分析区间数据')
    return
  }

  updating.value = true
  try {
    const data = {
      ...editForm.value,
      startTime: editForm.value.dateRange[0],
      endTime: editForm.value.dateRange[1],
      pattern: analyzedData.value.pattern,
      indicators: analyzedData.value.indicators
    }

    await strategyReferenceApi.update(editingId.value!, data)
    ElMessage.success('更新成功')
    showEditDialog.value = false
    fetchList()
  } catch (error) {
    ElMessage.error('更新失败')
  } finally {
    updating.value = false
  }
}

const deleteReference = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个策略参考吗？删除后无法恢复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    deleting.value = true
    await strategyReferenceApi.delete(editingId.value!)
    ElMessage.success('删除成功')
    showEditDialog.value = false
    fetchList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  } finally {
    deleting.value = false
  }
}

const viewDetail = async (item: StrategyReference) => {
  try {
    // 先打开对话框
    showDetailDialog.value = true

    // 获取详情数据
    const detail = await strategyReferenceApi.getDetail(item.id)
    currentDetail.value = detail

    // 转换K线数据格式
    if (detail?.klineData) {
      const klineData = detail.klineData.map((k: any) => ({
        time: k.date || k.datetime || '',
        open: k.open ?? 0,
        close: k.close ?? 0,
        high: k.high ?? 0,
        low: k.low ?? 0,
        volume: k.volume ?? 0
      }))

      // 使用 nextTick 确保对话框渲染完成后再设置数据
      await nextTick()
      detailKlineData.value = klineData
    }
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

// 切换截取模式
const toggleBrushMode = (keepConfirm = false) => {
  isBrushMode.value = !isBrushMode.value
  if (!isBrushMode.value && !keepConfirm) {
    // 取消截取模式时，清除选择并关闭确认对话框
    showConfirmDialog.value = false
    selectedBrushData.value = null
  }
}

// 处理K线图区域选择
const handleBrushSelected = (data: {
  startTime: string
  endTime: string
  startIndex: number
  endIndex: number
  klineData: KLineData[]
  imageData?: string
}) => {
  if (data.klineData.length < 2) {
    ElMessage.warning('请选择至少包含2根K线的区域')
    return
  }

  // 使用当前详情的合约代码和周期
  selectedBrushData.value = {
    ...data,
    code: currentDetail.value?.code || '',
    frequence: currentDetail.value?.frequence || 'day',
    klineData: data.klineData.map(k => ({
      time: k.time,
      open: k.open,
      close: k.close,
      high: k.high,
      low: k.low,
      volume: k.volume
    }))
  }

  // 退出截取模式，显示确认对话框
  isBrushMode.value = false
  showConfirmDialog.value = true
}

// 确认截取并创建策略参考
const confirmCapture = async () => {
  if (!selectedBrushData.value) return

  creatingFromBrush.value = true
  try {
    let imageUrl = ''

    // 如果有截图，先上传
    if (selectedBrushData.value.imageData) {
      // 将 base64 转换为 Blob
      const response = await fetch(selectedBrushData.value.imageData)
      const blob = await response.blob()
      const file = new File([blob], 'brush-capture.png', { type: 'image/png' })

      // 上传图片
      const uploadResult = await strategyReferenceApi.uploadImage(file)
      imageUrl = uploadResult.url || ''
    }

    // 分析区间数据
    const analyzedResult = await strategyReferenceApi.analyzeSegment(
      selectedBrushData.value.code,
      selectedBrushData.value.startTime,
      selectedBrushData.value.endTime,
      selectedBrushData.value.frequence
    ) as any

    // 创建策略参考，自动添加"截取"标签
    const createData = {
      name: `${selectedBrushData.value.code} ${selectedBrushData.value.startTime} 截取`,
      description: `从K线图截取的区间：${selectedBrushData.value.startTime} 至 ${selectedBrushData.value.endTime}`,
      image: imageUrl,
      code: selectedBrushData.value.code,
      frequence: selectedBrushData.value.frequence,
      startTime: selectedBrushData.value.startTime,
      endTime: selectedBrushData.value.endTime,
      tags: ['截取', ...new Set((analyzedResult as any).pattern?.type ? [(analyzedResult as any).pattern.type] : [])],
      pattern: (analyzedResult as any).pattern,
      indicators: (analyzedResult as any).indicators,
      klineData: selectedBrushData.value.klineData
    }

    await strategyReferenceApi.create(createData)
    ElMessage.success('截取成功，已创建新的策略参考')
    showConfirmDialog.value = false
    showDetailDialog.value = false
    fetchList()
  } catch (error) {
    ElMessage.error('创建失败：' + (error as Error).message)
  } finally {
    creatingFromBrush.value = false
  }
}

onMounted(() => {
  fetchList()
})
</script>

<style lang="scss" scoped>
/* 现代科技感 + 活力橙双主色设计系统 */
.strategy-reference-page {
  /* 双主色设计系统 - 科技蓝 + 活力橙 */
  --color-tech-blue: #5B8FF9;
  --color-tech-blue-light: #7AA5FF;
  --color-tech-blue-lighter: #A3C0FF;
  --color-vibrant-orange: #FF8C42;
  --color-vibrant-orange-light: #FFA666;
  --color-vibrant-orange-lighter: #FFBF8A;
  
  --color-success: #52C41A;
  --color-danger: #FF4D4F;
  --color-warning: #FAAD14;
  --color-purple: #9254DE;
  
  --color-bg: #FFFFFF;
  --color-bg-light: #F7F9FC;
  --color-bg-lighter: #EFF3F8;
  --color-text: #1A1A1A;
  --color-text-secondary: #5A5A5A;
  --color-text-tertiary: #8C8C8C;
  --color-border: #E5E8EF;
  --color-border-light: #F0F2F7;
  
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --radius-xxl: 24px;
  
  --shadow-sm: 0 2px 8px rgba(91, 143, 249, 0.08);
  --shadow-md: 0 4px 16px rgba(91, 143, 249, 0.12);
  --shadow-lg: 0 8px 24px rgba(91, 143, 249, 0.16);
  --shadow-hover: 0 12px 32px rgba(91, 143, 249, 0.20);
  --shadow-orange: 0 6px 20px rgba(255, 140, 66, 0.25);
  
  --spacing-xs: 8px;
  --spacing-sm: 12px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;

  padding: var(--spacing-lg);
  background: linear-gradient(135deg, #F7F9FC 0%, #EFF3F8 100%);
  min-height: 100vh;

  /* 工具栏 - 毛玻璃效果 + 双色点缀 */
  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-md) var(--spacing-xl);
    margin-bottom: var(--spacing-xl);
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: var(--radius-xl);
    border: 2px solid rgba(91, 143, 249, 0.15);
    box-shadow: var(--shadow-md);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;

    /* 装饰性渐变背景 */
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, var(--color-tech-blue) 0%, var(--color-vibrant-orange) 100%);
    }

    &:hover {
      box-shadow: var(--shadow-lg);
      border-color: rgba(91, 143, 249, 0.3);
    }

    .toolbar-left,
    .toolbar-right {
      display: flex;
      align-items: center;
      gap: var(--spacing-sm);
    }

    /* 主按钮 - 科技蓝渐变 */
    :deep(.el-button--primary) {
      background: linear-gradient(135deg, var(--color-tech-blue) 0%, var(--color-tech-blue-light) 100%);
      border: none;
      border-radius: var(--radius-md);
      padding: 10px 20px;
      font-weight: 600;
      box-shadow: 0 4px 12px rgba(91, 143, 249, 0.3);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(91, 143, 249, 0.4);
      }

      &:active {
        transform: translateY(0);
      }
    }

    /* 次要按钮 */
    :deep(.el-button:not(.el-button--primary)) {
      background: white;
      border: 2px solid var(--color-border);
      color: var(--color-text-secondary);
      border-radius: var(--radius-md);
      padding: 8px 18px;
      font-weight: 600;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

      &:hover {
        border-color: var(--color-vibrant-orange);
        color: var(--color-vibrant-orange);
        background: linear-gradient(135deg, rgba(255, 140, 66, 0.08) 0%, rgba(255, 140, 66, 0.04) 100%);
        transform: translateY(-2px);
        box-shadow: var(--shadow-orange);
      }
    }

    /* 选择器样式 */
    :deep(.el-select) {
      .el-input__wrapper {
        border-radius: var(--radius-md);
        border: 2px solid var(--color-border);
        background: white;
        box-shadow: none;
        transition: all 0.3s ease;

        &:hover {
          border-color: var(--color-tech-blue-light);
        }

        &.is-focus {
          border-color: var(--color-tech-blue);
          box-shadow: 0 0 0 3px rgba(91, 143, 249, 0.1);
        }
      }
    }
  }

  /* 卡片网格布局 - 响应式 */
  .reference-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: var(--spacing-xl);
    animation: fadeIn 0.6s ease;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  /* 卡片样式 - 现代科技感设计 */
  .reference-card {
    background: white;
    border-radius: var(--radius-xl);
    overflow: hidden;
    cursor: pointer;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    border: 2px solid var(--color-border-light);
    box-shadow: var(--shadow-sm);
    position: relative;
    animation: slideInUp 0.5s cubic-bezier(0.4, 0, 0.2, 1) backwards;

    /* 顶部装饰条 - 双色渐变 */
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: linear-gradient(90deg, var(--color-tech-blue) 0%, var(--color-vibrant-orange) 100%);
      opacity: 0;
      transition: opacity 0.3s ease;
      z-index: 1;
    }

    /* 悬停效果 - 卡片上浮 + 阴影加深 + 边框高亮 */
    &:hover {
      transform: translateY(-8px) scale(1.02);
      box-shadow: var(--shadow-hover);
      border-color: var(--color-tech-blue-lighter);

      &::before {
        opacity: 1;
      }

      .card-image {
        &::after {
          opacity: 0.6;
        }

        img {
          transform: scale(1.08);
        }
      }

      .card-content h4 {
        background: linear-gradient(135deg, var(--color-tech-blue) 0%, var(--color-vibrant-orange) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
    }

    /* 延迟动画 */
    @for $i from 1 through 20 {
      &:nth-child(#{$i}) {
        animation-delay: #{$i * 0.05}s;
      }
    }

    /* 图片容器 - 渐变背景 + 遮罩效果 */
    .card-image {
      width: 100%;
      height: 220px;
      overflow: hidden;
      background: linear-gradient(135deg, rgba(91, 143, 249, 0.08) 0%, rgba(255, 140, 66, 0.05) 100%);
      position: relative;

      /* 渐变遮罩 */
      &::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(180deg, transparent 50%, rgba(0, 0, 0, 0.05) 100%);
        pointer-events: none;
        transition: opacity 0.3s ease;
      }

      /* 图标装饰 */
      &::before {
        content: '📊';
        position: absolute;
        top: var(--spacing-sm);
        right: var(--spacing-sm);
        font-size: 24px;
        z-index: 2;
        opacity: 0.7;
        transition: all 0.3s ease;
      }

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
      }
    }

    /* 卡片内容 - 层次分明 */
    .card-content {
      padding: var(--spacing-lg) var(--spacing-xl);

      h4 {
        margin: 0 0 var(--spacing-sm) 0;
        font-size: 19px;
        font-weight: 700;
        color: var(--color-text);
        line-height: 1.4;
        letter-spacing: -0.3px;
        transition: all 0.3s ease;
      }

      .description {
      .description {
        color: var(--color-text-secondary);
        font-size: 14px;
        line-height: 1.7;
        margin: 0 0 var(--spacing-md) 0;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        line-clamp: 2;
        -webkit-box-orient: vertical;
        min-height: 48px;
        padding: var(--spacing-sm);
        background: var(--color-bg-light);
        border-radius: var(--radius-sm);
        border-left: 3px solid var(--color-tech-blue);
      }
      /* 元数据区域 - 图标化设计 */
      .meta {
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
        margin-bottom: var(--spacing-md);
        flex-wrap: wrap;

        /* 趋势标签样式 - 渐变背景 */
        :deep(.el-tag) {
          border-radius: var(--radius-sm);
          font-weight: 600;
          padding: 4px 12px;
          height: 26px;
          line-height: 18px;
          font-size: 12px;
          border: none;
          box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
          transition: all 0.3s ease;

          &:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
          }

          &.el-tag--danger {
            background: linear-gradient(135deg, #FF4D4F 0%, #FF7875 100%);
            color: white;
          }

          &.el-tag--success {
            background: linear-gradient(135deg, #52C41A 0%, #73D13D 100%);
            color: white;
          }

          &.el-tag--warning {
            background: linear-gradient(135deg, #FAAD14 0%, #FFC53D 100%);
            color: white;
          }
        }

        .time {
          color: var(--color-text-tertiary);
          font-size: 12px;
          margin-left: auto;
          display: flex;
          align-items: center;
          gap: 4px;

          &::before {
            content: '🕐';
            font-size: 14px;
          }
        }
      }

      /* 标签区域 - 圆角设计 */
      .tags {
        display: flex;
        flex-wrap: wrap;
        gap: var(--spacing-xs);

        :deep(.el-tag--small) {
          border-radius: var(--radius-md);
          font-size: 12px;
          padding: 3px 10px;
          background: linear-gradient(135deg, rgba(91, 143, 249, 0.08) 0%, rgba(255, 140, 66, 0.05) 100%);
          color: var(--color-text-secondary);
          border: 1px solid var(--color-border);
        }
      }
    }

    /* 卡片操作按钮区域 - 双色按钮 */
    .card-actions {
      display: flex;
      gap: var(--spacing-sm);
      padding: var(--spacing-md) var(--spacing-xl);
      border-top: 2px solid var(--color-border-light);
      background: linear-gradient(180deg, white 0%, var(--color-bg-light) 100%);

      .action-btn {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        padding: 10px 16px;
        border: none;
        border-radius: var(--radius-md);
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;

        .el-icon {
          font-size: 16px;
          transition: transform 0.3s ease;
        }

        /* 按钮光泽效果 */
        &::before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
          transition: left 0.5s ease;
        }

        &:hover::before {
          left: 100%;
        }

        &.detail-btn {
          background: linear-gradient(135deg, rgba(91, 143, 249, 0.12) 0%, rgba(91, 143, 249, 0.06) 100%);
          color: var(--color-tech-blue);
          border: 2px solid rgba(91, 143, 249, 0.2);

          &:hover {
            background: linear-gradient(135deg, var(--color-tech-blue) 0%, var(--color-tech-blue-light) 100%);
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(91, 143, 249, 0.35);

            .el-icon {
              transform: scale(1.1);
            }
          }

          &:active {
            transform: translateY(0);
          }
        }

        &.edit-btn {
          background: linear-gradient(135deg, rgba(255, 140, 66, 0.12) 0%, rgba(255, 140, 66, 0.06) 100%);
          color: var(--color-vibrant-orange);
          border: 2px solid rgba(255, 140, 66, 0.2);

          &:hover {
            background: linear-gradient(135deg, var(--color-vibrant-orange) 0%, var(--color-vibrant-orange-light) 100%);
            color: white;
            transform: translateY(-2px);
            box-shadow: var(--shadow-orange);

            .el-icon {
              transform: scale(1.1);
            }
          }

          &:active {
            transform: translateY(0);
          }
        }
      }
    }
  }

  @keyframes slideInUp {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  /* 预览图片 - 精致边框 */
  .preview-image {
    margin-top: var(--spacing-md);
    padding: var(--spacing-lg);
    background: linear-gradient(135deg, rgba(91, 143, 249, 0.05) 0%, rgba(255, 140, 66, 0.03) 100%);
    border-radius: var(--radius-lg);
    display: inline-block;
    border: 2px solid var(--color-border-light);

    img {
      max-width: 400px;
      max-height: 250px;
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-md);
      border: 2px solid white;
    }
  }

  /* 详情内容 - 精致布局 */
  .detail-content {
    .detail-image {
      width: 100%;
      background: linear-gradient(135deg, rgba(91, 143, 249, 0.05) 0%, rgba(255, 140, 66, 0.03) 100%);
      border-radius: var(--radius-xl);
      overflow: hidden;
      box-shadow: var(--shadow-md);
      border: 2px solid var(--color-border-light);

      img {
        width: 100%;
        display: block;
        transition: transform 0.3s ease;

        &:hover {
          transform: scale(1.02);
        }
      }
    }

    h3 {
      margin: 0 0 var(--spacing-md) 0;
      font-size: 32px;
      font-weight: 800;
      color: var(--color-text);
      line-height: 1.2;
      letter-spacing: -0.5px;
      background: linear-gradient(135deg, var(--color-tech-blue) 0%, var(--color-vibrant-orange) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    h3 + p {
      color: var(--color-text-secondary);
      font-size: 16px;
      line-height: 1.7;
      margin-bottom: var(--spacing-xl);
      padding: var(--spacing-md);
      background: var(--color-bg-light);
      border-radius: var(--radius-md);
      border-left: 4px solid var(--color-tech-blue);
    }

    h4 {
      margin: 0 0 var(--spacing-md) 0;
      font-size: 20px;
      font-weight: 700;
      color: var(--color-text);
      display: flex;
      align-items: center;
      gap: var(--spacing-sm);

      &::before {
        content: '📈';
        font-size: 24px;
      }
    }

    .kline-section {
      background: white;
      border-radius: var(--radius-xl);
      padding: var(--spacing-xl);
      margin-top: var(--spacing-xl);
      border: 2px solid var(--color-border-light);
      box-shadow: var(--shadow-sm);

      .kline-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--spacing-lg);
        padding-bottom: var(--spacing-md);
        border-bottom: 2px solid var(--color-border-light);
      }
    }

    :deep(.el-descriptions) {
      .el-descriptions__label {
        font-weight: 600;
        color: var(--color-text);
        background: linear-gradient(135deg, rgba(91, 143, 249, 0.08) 0%, rgba(255, 140, 66, 0.05) 100%);
      }

      .el-descriptions__content {
        color: var(--color-text-secondary);
        font-weight: 500;
      }
    }
  }

  /* 详情对话框头部 - 双色设计 */
  .detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;

    .detail-title {
      font-size: 20px;
      font-weight: 700;
      background: linear-gradient(135deg, var(--color-tech-blue) 0%, var(--color-vibrant-orange) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .el-button {
      border-radius: var(--radius-md);
      font-weight: 600;
      transition: all 0.3s ease;

      &.el-button--primary {
        background: linear-gradient(135deg, var(--color-vibrant-orange) 0%, var(--color-vibrant-orange-light) 100%);
        border: none;
        box-shadow: var(--shadow-orange);

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(255, 140, 66, 0.35);
        }
      }
    }
  }

  /* 截取确认对话框 - 精致设计 */
  .brush-confirm-content {
    .preview-section {
      margin-bottom: var(--spacing-xl);
      padding: var(--spacing-lg);
      background: linear-gradient(135deg, rgba(91, 143, 249, 0.03) 0%, rgba(255, 140, 66, 0.02) 100%);
      border-radius: var(--radius-lg);
      border: 2px solid var(--color-border-light);

      h4 {
        margin-bottom: var(--spacing-md);
        font-size: 18px;
        font-weight: 700;
        color: var(--color-text);
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);

        &::before {
          content: '✂️';
          font-size: 20px;
        }
      }

      .preview-image {
        width: 100%;
        max-height: 350px;
        object-fit: contain;
        border-radius: var(--radius-md);
        border: 2px solid var(--color-border);
        background: white;
        box-shadow: var(--shadow-md);
      }
    }

    .info-section {
      margin-top: var(--spacing-lg);
      border-radius: var(--radius-md);
      overflow: hidden;
      border: 2px solid var(--color-border-light);
    }
  }
}

/* Element Plus 组件全局样式优化 - 双色主题 */
:deep(.el-dialog) {
  border-radius: var(--radius-xxl);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  border: 2px solid rgba(91, 143, 249, 0.15);
  overflow: hidden;

  .el-dialog__header {
    padding: var(--spacing-xl);
    background: linear-gradient(135deg, rgba(91, 143, 249, 0.05) 0%, rgba(255, 140, 66, 0.03) 100%);
    border-bottom: 2px solid var(--color-border-light);

    .el-dialog__title {
      font-size: 22px;
      font-weight: 700;
      background: linear-gradient(135deg, var(--color-tech-blue) 0%, var(--color-vibrant-orange) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .el-dialog__headerbtn {
      top: var(--spacing-lg);
      right: var(--spacing-lg);
      width: 40px;
      height: 40px;
      border-radius: var(--radius-md);
      transition: all 0.3s ease;

      &:hover {
        background: rgba(255, 77, 79, 0.1);

        .el-dialog__close {
          color: var(--color-danger);
          transform: rotate(90deg);
        }
      }

      .el-dialog__close {
        transition: transform 0.3s ease;
      }
    }
  }

  .el-dialog__body {
    padding: var(--spacing-xl);
    max-height: 70vh;
    overflow-y: auto;

    /* 自定义滚动条 */
    &::-webkit-scrollbar {
      width: 8px;
    }

    &::-webkit-scrollbar-track {
      background: var(--color-bg-light);
      border-radius: var(--radius-sm);
    }

    &::-webkit-scrollbar-thumb {
      background: linear-gradient(135deg, var(--color-tech-blue) 0%, var(--color-vibrant-orange) 100%);
      border-radius: var(--radius-sm);

      &:hover {
        background: linear-gradient(135deg, var(--color-tech-blue-light) 0%, var(--color-vibrant-orange-light) 100%);
      }
    }
  }

  .el-dialog__footer {
    padding: var(--spacing-lg) var(--spacing-xl);
    background: var(--color-bg-light);
    border-top: 2px solid var(--color-border-light);

    .el-button {
      border-radius: var(--radius-md);
      padding: 10px 24px;
      font-weight: 600;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

      &:hover {
        transform: translateY(-2px);
      }

      &:active {
        transform: translateY(0);
      }
    }

    .el-button--primary {
      background: linear-gradient(135deg, var(--color-tech-blue) 0%, var(--color-tech-blue-light) 100%);
      border: none;
      box-shadow: 0 4px 12px rgba(91, 143, 249, 0.3);

      &:hover {
        box-shadow: 0 6px 20px rgba(91, 143, 249, 0.4);
      }
    }

    .el-button--danger {
      background: linear-gradient(135deg, var(--color-danger) 0%, #FF7875 100%);
      border: none;
      box-shadow: 0 4px 12px rgba(255, 77, 79, 0.3);

      &:hover {
        box-shadow: 0 6px 20px rgba(255, 77, 79, 0.4);
      }
    }
  }

  /* 表单样式 */
  .el-form {
    .el-form-item__label {
      font-weight: 600;
      color: var(--color-text);
      font-size: 14px;
    }

    .el-input__wrapper {
      border-radius: var(--radius-md);
      border: 2px solid var(--color-border);
      box-shadow: none;
      transition: all 0.3s ease;

      &:hover {
        border-color: var(--color-tech-blue-light);
      }

      &.is-focus {
        border-color: var(--color-tech-blue);
        box-shadow: 0 0 0 3px rgba(91, 143, 249, 0.1);
      }
    }

    .el-select .el-input__wrapper {
      &.is-focus {
        border-color: var(--color-tech-blue);
      }
    }

    .el-textarea__inner {
      border-radius: var(--radius-md);
      border: 2px solid var(--color-border);
      transition: all 0.3s ease;

      &:hover {
        border-color: var(--color-tech-blue-light);
      }

      &:focus {
        border-color: var(--color-tech-blue);
        box-shadow: 0 0 0 3px rgba(91, 143, 249, 0.1);
      }
    }

    .el-date-editor {
      .el-input__wrapper {
        border-radius: var(--radius-md);
      }
    }

    .el-upload {
      .el-button {
        background: linear-gradient(135deg, rgba(255, 140, 66, 0.1) 0%, rgba(255, 140, 66, 0.05) 100%);
        border: 2px solid var(--color-vibrant-orange);
        color: var(--color-vibrant-orange);
        border-radius: var(--radius-md);

        &:hover {
          background: linear-gradient(135deg, var(--color-vibrant-orange) 0%, var(--color-vibrant-orange-light) 100%);
          color: white;
          box-shadow: var(--shadow-orange);
        }
      }
    }
  }

  /* 描述列表样式 */
  .el-descriptions {
    border-radius: var(--radius-md);
    overflow: hidden;
    border: 2px solid var(--color-border-light);

    .el-descriptions__label {
      background: linear-gradient(135deg, rgba(91, 143, 249, 0.08) 0%, rgba(255, 140, 66, 0.05) 100%);
      font-weight: 600;
      color: var(--color-text);
    }

    .el-descriptions__content {
      background: white;
      color: var(--color-text-secondary);
      font-weight: 500;
    }
  }

  /* 标签样式 */
  .el-tag {
    border-radius: var(--radius-sm);
    font-weight: 600;
    border: none;
    padding: 4px 12px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);

    &.el-tag--primary {
      background: linear-gradient(135deg, var(--color-tech-blue) 0%, var(--color-tech-blue-light) 100%);
      color: white;
    }

    &.el-tag--success {
      background: linear-gradient(135deg, var(--color-success) 0%, #73D13D 100%);
      color: white;
    }

    &.el-tag--danger {
      background: linear-gradient(135deg, var(--color-danger) 0%, #FF7875 100%);
      color: white;
    }

    &.el-tag--warning {
      background: linear-gradient(135deg, var(--color-warning) 0%, #FFC53D 100%);
      color: white;
    }
  }
}
}
</style>
