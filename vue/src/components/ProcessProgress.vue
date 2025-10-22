<template>
  <div class="homepage-container">
    <div class="panel recent-tasks">
      <div class="panel-header">
        <h3>重建进度</h3>
        <p class="progress-subtitle">跟踪所有正在进行的重建任务</p>
      </div>
      <div v-for="task in tasks" :key="task.id" class="task-card">
        <div class="task-head">
          <div class="task-title">
            <div class="task-name-row">
              <strong>{{ task.name }}</strong>
              <div v-if="task.status === 'processing'" class="loading-spinner">
                <svg class="spinning" width="16" height="16" viewBox="0 0 16 16">
                  <circle cx="8" cy="8" r="6" stroke="#409eff" stroke-width="2" fill="none" stroke-dasharray="37.7" stroke-dashoffset="37.7">
                    <animate attributeName="stroke-dasharray" dur="2s" values="0 37.7;18.85 18.85;0 37.7;0 37.7" repeatCount="indefinite"/>
                    <animate attributeName="stroke-dashoffset" dur="2s" values="0;-18.85;-37.7;-37.7" repeatCount="indefinite"/>
                  </circle>
                </svg>
              </div>
            </div>
            <div class="task-meta">{{ task.fileCount }} 个文件 · 开始时间: {{ formatTime(task.startTime) }}</div>
          </div>
          <div class="task-actions">
            <template v-if="task.status === 'completed'">
              <el-button size="mini" @click="viewTask(task)">查看</el-button>
              <el-button size="mini" @click="downloadTask(task)">下载</el-button>
              <el-button size="mini" type="danger" plain @click="deleteTask(task.id)">删除</el-button>
            </template>
            <template v-else-if="task.status === 'failed'">
              <el-button size="mini" type="danger" @click="retryTask(task)">重试</el-button>
              <el-button size="mini" type="danger" plain @click="deleteTask(task.id)">删除</el-button>
            </template>
            <template v-else>
              <el-button size="mini" type="info">处理中</el-button>
              <el-button size="mini" type="danger" plain @click="deleteTask(task.id)">删除</el-button>
            </template>
          </div>
        </div>

        <div class="task-stages">
          <div class="stages-bar-full">
            <div class="stage-full" v-for="(stage, i) in task.stages" :key="i"
              :class="{ 
                done: (task.status === 'completed' && stage.status === 'completed') || 
                      (task.status === 'processing' && stage.status === 'completed'),
                active: task.status === 'processing' && stage.status === 'processing',
                failed: task.status === 'failed' && stage.status === 'processing'
              }">
              <div class="stage-label">{{ stage.name }}</div>
            </div>
          </div>
          <el-progress 
            class="stages-progress" 
            :percentage="task.progress" 
            :status="getProgressStatus(task.status)"
          />
        </div>

        <div class="task-footer">
          <div v-if="task.status === 'failed'">
            <span style="color:#f56c6c">❌ 处理失败</span>
            <span style="color:#999; font-size:12px; margin-left:8px">{{ getFailureReason(task) }}</span>
          </div>
          <div v-else>预计剩余：{{ task.estimatedTime || (task.status === 'completed' ? '已完成' : '计算中...') }}</div>
          <div class="task-controls">
            <template v-if="task.status === 'processing'">
              <el-button size="mini" @click="togglePause(task)">{{ task.paused ? '恢复' : '暂停' }}</el-button>
            </template>
            <template v-else-if="task.status === 'completed'">
              <span style="color:#67c23a">✅ 已完成</span>
            </template>
            <template v-else-if="task.status === 'failed'">
              <el-button size="mini" type="text" @click="viewErrorDetails(task)" style="color:#f56c6c">查看详情</el-button>
            </template>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="tasks.length === 0" class="empty-state">
        <el-empty description="暂无重建任务">
          <el-button type="primary" @click="createNewTask">创建新任务</el-button>
        </el-empty>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Clock, 
  Check, 
  Close, 
  Loading,
  ArrowDown,
  Document,
  Download
} from '@element-plus/icons-vue'
import { 
  getTaskList, 
  getTaskProgress, 
  pauseTask as apiPauseTask,
  retryTask as apiRetryTask,
  deleteTask as apiDeleteTask,
  downloadTaskResult
} from '@/api'

// 响应式数据
const tasks = ref([])
const loading = ref(false)
const pollingTimer = ref(null)

// 模拟数据（后续替换为API调用）
const mockTasks = ref([
  {
    id: 1,
    name: '患者张三 - 全口重建',
    fileCount: 24,
    startTime: '2025-10-22T14:30:00',
    progress: 40,
    status: 'processing', // processing, completed, failed, paused
    estimatedTime: '25分钟',
    stages: [
      { name: '图像预处理', status: 'completed' },
      { name: '特征提取', status: 'completed' },
      { name: '三维重建', status: 'processing' },
      { name: '网格优化', status: 'pending' },
      { name: '纹理映射', status: 'pending' },
      { name: '后处理', status: 'pending' }
    ]
  },
  {
    id: 2,
    name: '患者李四 - 全口重建',
    fileCount: 8,
    startTime: '2025-10-22T13:45:00',
    progress: 100,
    status: 'completed',
    estimatedTime: null,
    stages: [
      { name: '图像预处理', status: 'completed' },
      { name: '特征提取', status: 'completed' },
      { name: '三维重建', status: 'completed' },
      { name: '网格优化', status: 'completed' },
      { name: '纹理映射', status: 'completed' },
      { name: '后处理', status: 'completed' }
    ]
  },
   {
    id: 3,
    name: '患者王五 - 全口重建',
    fileCount: 16,
    startTime: '2025-10-22T12:30:00',
    progress: 35,
    status: 'failed',
    estimatedTime: null,
    stages: [
      { name: '图像预处理', status: 'completed' },
      { name: '特征提取', status: 'completed' },
      { name: '三维重建', status: 'processing' }, // 失败在这个阶段
      { name: '网格优化', status: 'pending' },
      { name: '纹理映射', status: 'pending' },
      { name: '后处理', status: 'pending' }
    ]
  }
])

// 计算属性
const processingTasks = computed(() => tasks.value.filter(t => t.status === 'processing'))
const completedTasks = computed(() => tasks.value.filter(t => t.status === 'completed'))
const failedTasks = computed(() => tasks.value.filter(t => t.status === 'failed'))
// 方法
const formatTime = (timeStr) => {
  return new Date(timeStr).toLocaleString('zh-CN')
}

const getStatusColor = (status) => {
  const colors = {
    'processing': '#409EFF',
    'completed': '#67C23A', 
    'failed': '#F56C6C',
    'paused': '#E6A23C'
  }
  return colors[status] || '#909399'
}

const getStatusIcon = (status) => {
  const icons = {
    'processing': Loading,
    'completed': Check,
    'failed': Close,
    'paused': Clock
  }
  return icons[status] || Clock
}

const getProgressStatus = (status) => {
  return status === 'completed' ? 'success' : 
         status === 'failed' ? 'exception' : null
}

const getCurrentStage = (task) => {
  const current = task.stages.find(s => s.status === 'processing')
  return current ? current.name : '准备中'
}

// 首页风格的任务操作方法
function viewTask(t) {
  ElMessage.info(`查看任务: ${t.name}`)
}

function downloadTask(t) {
  ElMessage.success(`开始下载: ${t.name}`)
}

function togglePause(t) {
  t.paused = !t.paused
  ElMessage.info(t.paused ? '任务已暂停' : '任务已恢复')
}

function retryTask(task) {
  ElMessage.info(`正在重试任务: ${task.name}`)
  // 重置任务状态
  task.status = 'processing'
  task.progress = 0
  task.estimatedTime = '预计30分钟'
  task.stages.forEach(stage => {
    stage.status = 'pending'
  })
  task.stages[0].status = 'processing'
}

function getFailureReason(task) {
  const reasons = [
    '图像质量不佳，无法识别关键特征',
    '网络连接中断，处理被终止',
    '内存不足，处理过程异常结束',
    '模型参数错误，重建失败'
  ]
  return reasons[task.id % reasons.length]
}

function viewErrorDetails(task) {
  ElMessageBox.alert(
    `任务: ${task.name}\n失败原因: ${getFailureReason(task)}\n\n建议:\n1. 检查图像质量是否清晰\n2. 确认网络连接稳定\n3. 重新上传图像并重试`,
    '错误详情',
    {
      confirmButtonText: '知道了',
      type: 'error'
    }
  )
}

const deleteTask = async (taskId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个任务吗？此操作不可恢复。', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 调用删除API
    tasks.value = tasks.value.filter(t => t.id !== taskId)
    ElMessage.success('任务已删除')
  } catch {
    // 用户取消
  }
}

const duplicateTask = (taskId) => {
  ElMessage.info('复制任务功能开发中')
}

const createNewTask = () => {
  // 跳转到创建任务页面
  ElMessage.info('跳转到创建任务页面')
}

// 加载任务列表
const loadTasks = async () => {
  loading.value = true
  try {
    // 临时使用模拟数据
    tasks.value = mockTasks.value
    // 实际API调用：
    // const { data } = await getTaskList()
    // tasks.value = data.tasks
  } catch (error) {
    ElMessage.error('加载任务列表失败')
  } finally {
    loading.value = false
  }
}

// 轮询更新进度
const startPolling = () => {
  pollingTimer.value = setInterval(async () => {
    if (processingTasks.value.length === 0) return
    
    try {
      // 更新正在处理的任务进度
      for (const task of processingTasks.value) {
        // const { data } = await getTaskProgress(task.id)
        // Object.assign(task, data)
      }
    } catch (error) {
      console.error('更新进度失败:', error)
    }
  }, 5000) // 每5秒更新一次
}

const stopPolling = () => {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value)
    pollingTimer.value = null
  }
}

// 生命周期
onMounted(() => {
  loadTasks()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.homepage-container {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.panel {
  background: #fff;
  border-radius: 6px;
  padding: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
  margin-bottom: 12px;
  width: 100%;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 12px;
  flex-wrap: nowrap;
}

.panel-header h3 {
  margin: 0;
  white-space: nowrap;
  flex: 0 0 auto;
}

.progress-subtitle {
  color: #606266;
  margin: 0;
  font-size: 14px;
}

.recent-tasks .task-card {
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 12px;
  background: #fff;
  border: 1px solid #e8eef4;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
  display: block;
}

.task-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.task-title {
  max-width: 70%;
}

.task-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-spinner {
  display: flex;
  align-items: center;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.task-meta {
  color: #999;
  font-size: 12px;
  margin-top: 4px;
}

.task-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  color: #666;
  font-size: 13px;
}

.task-stages {
  margin: 8px 0 12px 0;
}

.stages-bar-full {
  display: flex;
  gap: 0;
  margin-bottom: 8px;
}

.stage-full {
  flex: 1;
  text-align: center;
  color: #999;
  font-size: 13px;
  padding: 8px 6px;
  transition: all 0.15s ease;
  border: 1px solid #eee;
  border-radius: 6px;
  background: #f7f7f7;
  box-sizing: border-box;
}

.stage-full.done {
  color: #2f855a;
  border-color: #d1f0dc;
  background: #f0fff4;
}

.stage-full.active {
  color: #1f6fbf;
  border-color: #bfe0ff;
  background: #f2f9ff;
}

.stage-full.failed {
  color: #f56c6c;
  border-color: #fbc4c4;
  background: #fef0f0;
}

.stages-progress {
  width: 100%;
}

.stages-progress :deep(.el-progress-bar__inner) {
  background-image: none !important;
  background: #7fc97f !important;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}
</style>