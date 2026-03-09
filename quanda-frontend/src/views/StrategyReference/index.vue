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

const form = ref({
  name: '',
  description: '',
  image: '',
  code: '',
  frequence: 'day',
  dateRange: [],
  tags: []
})

const editForm = ref({
  name: '',
  description: '',
  image: '',
  code: '',
  frequence: 'day',
  dateRange: [],
  tags: []
})

const detailKlineData = ref<KLineData[]>([])
const klineChartRef = ref<InstanceType<typeof KLineChart> | null>(null)

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
    )

    // 创建策略参考，自动添加"截取"标签
    const createData = {
      name: `${selectedBrushData.value.code} ${selectedBrushData.value.startTime} 截取`,
      description: `从K线图截取的区间：${selectedBrushData.value.startTime} 至 ${selectedBrushData.value.endTime}`,
      image: imageUrl,
      code: selectedBrushData.value.code,
      frequence: selectedBrushData.value.frequence,
      startTime: selectedBrushData.value.startTime,
      endTime: selectedBrushData.value.endTime,
      tags: ['截取', ...new Set(analyzedResult.pattern?.type ? [analyzedResult.pattern.type] : [])],
      pattern: analyzedResult.pattern,
      indicators: analyzedResult.indicators,
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
/* 低饱和度科技蓝设计系统 */
.strategy-reference-page {
  /* CSS 变量定义 - 使用新的低饱和度配色 */
  --color-primary: #5B8FF9;
  --color-primary-hover: #4A7AD8;
  --color-secondary: #9254DE;
  --color-secondary-light: rgba(146, 84, 222, 0.08);
  --color-bg: #FFFFFF;
  --color-bg-light: #F5F7FA;
  --color-text: #262626;
  --color-text-secondary: #595959;
  --color-text-tertiary: #8C8C8C;
  --color-border: #E8E8E8;
  --color-success: #73D13D;
  --color-danger: #FF7A7E;
  --color-warning: #FFA940;

  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;

  --shadow-card: 0 2px 8px rgba(0, 0, 0, 0.06);
  --shadow-card-hover: 0 8px 24px rgba(91, 143, 249, 0.15);
  --shadow-btn: 0 4px 12px rgba(91, 143, 249, 0.25);

  --spacing-xs: 8px;
  --spacing-sm: 12px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;

  /* 工具栏样式 */
  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-md) var(--spacing-lg);
    background: var(--color-bg);
    border-radius: var(--radius-lg);
    margin-bottom: var(--spacing-lg);
    box-shadow: var(--shadow-card);
    border: 1px solid var(--color-border);

    .toolbar-left,
    .toolbar-right {
      display: flex;
      align-items: center;
      gap: var(--spacing-sm);
    }
  }

  /* 卡片网格布局 */
  .reference-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: var(--spacing-lg);
  }

  /* 卡片样式 - 核心组件 */
  .reference-card {
    background: var(--color-bg);
    border-radius: var(--radius-lg);
    overflow: hidden;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-card);
    position: relative;

    /* 悬停效果 - 卡片上浮 + 阴影加深 + 边框高亮 */
    &:hover {
      transform: translateY(-4px);
      box-shadow: var(--shadow-card-hover);
      border-color: var(--color-primary);

      .card-image img {
        transform: scale(1.05);
      }

      .card-content h4 {
        background: linear-gradient(135deg, #5B8FF9 0%, #7AA5FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
    }

    /* 图片容器 */
    .card-image {
      width: 100%;
      height: 200px;
      overflow: hidden;
      background: linear-gradient(135deg, rgba(91, 143, 249, 0.05) 0%, rgba(122, 165, 255, 0.02) 100%);
      position: relative;

      &::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(180deg, transparent 60%, rgba(0, 0, 0, 0.03) 100%);
        pointer-events: none;
      }

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
      }
    }

    /* 卡片内容 */
    .card-content {
      padding: var(--spacing-lg);

      h4 {
        margin: 0 0 var(--spacing-sm) 0;
        font-size: 18px;
        font-weight: 600;
        color: var(--color-text);
        line-height: 1.4;
        transition: all 0.2s ease;
      }

      .description {
        color: var(--color-text-secondary);
        font-size: 14px;
        line-height: 1.6;
        margin: 0 0 var(--spacing-md) 0;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        min-height: 44px;
      }

      /* 元数据区域 */
      .meta {
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
        margin-bottom: var(--spacing-md);
        flex-wrap: wrap;

        /* 趋势标签样式 */
        :deep(.el-tag) {
          border-radius: var(--radius-sm);
          font-weight: 500;
          padding: 2px 8px;
          height: 22px;
          line-height: 18px;
          font-size: 12px;
          border: none;
        }

        .time {
          color: var(--color-text-tertiary);
          font-size: 12px;
          margin-left: auto;
        }
      }

      /* 标签区域 */
      .tags {
        display: flex;
        flex-wrap: wrap;
        gap: var(--spacing-xs);

        :deep(.el-tag--small) {
          border-radius: var(--radius-sm);
          font-size: 12px;
          background: var(--color-bg-light);
          color: var(--color-text-secondary);
          border: 1px solid var(--color-border);
        }
      }
    }

    /* 卡片操作按钮区域 */
    .card-actions {
      display: flex;
      gap: var(--spacing-sm);
      padding: var(--spacing-md) var(--spacing-lg);
      border-top: 1px solid var(--color-border);
      background: linear-gradient(180deg, var(--color-bg) 0%, var(--color-bg-light) 100%);

      .action-btn {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        padding: 8px 16px;
        border: none;
        border-radius: var(--radius-md);
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);

        .el-icon {
          font-size: 16px;
        }

        &.detail-btn {
          background: linear-gradient(135deg, rgba(91, 143, 249, 0.1) 0%, rgba(91, 143, 249, 0.05) 100%);
          color: var(--color-primary);

          &:hover {
            background: linear-gradient(135deg, rgba(91, 143, 249, 0.2) 0%, rgba(91, 143, 249, 0.1) 100%);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(91, 143, 249, 0.2);
          }

          &:active {
            transform: translateY(0);
          }
        }

        &.edit-btn {
          background: linear-gradient(135deg, rgba(146, 84, 222, 0.1) 0%, rgba(146, 84, 222, 0.05) 100%);
          color: var(--color-secondary);

          &:hover {
            background: linear-gradient(135deg, rgba(146, 84, 222, 0.2) 0%, rgba(146, 84, 222, 0.1) 100%);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(146, 84, 222, 0.2);
          }

          &:active {
            transform: translateY(0);
          }
        }
      }
    }
  }

  /* 预览图片 */
  .preview-image {
    margin-top: var(--spacing-md);
    padding: var(--spacing-md);
    background: var(--color-bg-light);
    border-radius: var(--radius-md);
    display: inline-block;

    img {
      max-width: 300px;
      max-height: 200px;
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-card);
    }
  }

  /* 详情内容 */
  .detail-content {
    .detail-image {
      width: 100%;
      background: var(--color-bg-light);
      border-radius: var(--radius-lg);
      overflow: hidden;
      box-shadow: var(--shadow-card);

      img {
        width: 100%;
        display: block;
      }
    }

    h3 {
      margin: 0 0 var(--spacing-sm) 0;
      font-size: 28px;
      font-weight: 700;
      color: var(--color-text);
      line-height: 1.3;
      background: linear-gradient(135deg, #5B8FF9 0%, #7AA5FF 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    h3 + p {
      color: var(--color-text-secondary);
      font-size: 15px;
      line-height: 1.6;
      margin-bottom: var(--spacing-lg);
    }

    h4 {
      margin: 0 0 var(--spacing-md) 0;
      font-size: 18px;
      font-weight: 600;
      color: var(--color-text);
    }

    .kline-section {
      background: var(--color-bg-light);
      border-radius: var(--radius-lg);
      padding: var(--spacing-lg);
      margin-top: var(--spacing-lg);

      .kline-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--spacing-md);
      }
    }
  }

  /* 详情对话框头部 */
  .detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;

    .detail-title {
      font-size: 18px;
      font-weight: 600;
    }
  }

  /* 截取确认对话框 */
  .brush-confirm-content {
    .preview-section {
      margin-bottom: var(--spacing-lg);

      h4 {
        margin-bottom: var(--spacing-sm);
        font-size: 16px;
        font-weight: 600;
      }

      .preview-image {
        width: 100%;
        max-height: 300px;
        object-fit: contain;
        border-radius: var(--radius-md);
        border: 1px solid var(--color-border);
        background: var(--color-bg-light);
      }
    }

    .info-section {
      margin-top: var(--spacing-md);
    }
  }
}

/* Element Plus 组件局部样式调整 */
:deep(.el-dialog) {
  border-radius: var(--radius-xl);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);

  .el-dialog__header {
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--color-border);
  }

  .el-dialog__body {
    padding: var(--spacing-lg);
  }

  .el-dialog__footer {
    padding: var(--spacing-lg);
    border-top: 1px solid var(--color-border);
  }
}
</style>
