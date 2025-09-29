<template>
  <div class="dashboard">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>TeethDreamer
        三维重建系统</h1>
      <p>{{ currentTime }}</p>
    </div>

    <!-- 标签页导航 -->
    <el-tabs v-model="activeTab" class="dashboard-tabs">
      <el-tab-pane label="首页" name="overview">
        <div class="coming-soon">
          <el-empty description="概览功能待开发" />
        </div>
      </el-tab-pane>

      <el-tab-pane label="新建项目" name="new-project">
        <div class="upload-container">
          <h3>新建重建项目</h3>
          <el-form :model="projectForm" label-width="100px" style="margin-bottom: 16px;">
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="项目名称">
                  <el-input v-model="projectForm.projectName" placeholder="输入项目名称" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="重建类型">
                  <el-select v-model="projectForm.reconstructionType" placeholder="选择重建类型" style="width: 100%;">
                    <el-option label="全口重建" value="全口重建" />
                    <el-option label="单口重建" value="单口重建" />
                    <el-option label="局部重建" value="局部重建" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="项目描述">
              <el-input v-model="projectForm.description" type="textarea" rows="3" placeholder="描述重建需求和注意事项" />
            </el-form-item>
          </el-form>

          <ImageUploader ref="uploaderRef" @select="onSelect" @append="onAppend" />
          <div v-if="previewUrls.length" style="margin-top: 16px;">
            <h4>预览</h4>
            <div class="gallery">
              <div v-for="(item, idx) in items" :key="idx" class="tile">
                <img :src="item.url" alt="预览" class="thumb" />
                <div class="meta">
                  <span class="name" :title="item.file.name">{{ item.file.name }}</span>
                  <el-button type="danger" link @click="removeAt(idx)">删除</el-button>
                </div>
              </div>
            </div>
          </div>
          <div style="margin-top: 16px;">
            <el-button type="primary" :disabled="!canSubmit" @click="onCreateProject">提交分割</el-button>
            <el-button style="margin-left: 8px;" @click="onReupload">重新上传</el-button>
          </div>
          <div class="history" v-if="store.submissions.length" style="margin-top: 24px;">
            <h4>最近提交</h4>
            <el-table :data="store.submissions" size="small" style="width: 100%">
              <el-table-column prop="project_id" label="任务ID" width="160" />
              <el-table-column prop="project_name" label="项目名称" />
              <el-table-column prop="reconstruction_type" label="重建类型" width="140" />
              <el-table-column prop="status" label="项目状态" width="120" />
              <el-table-column prop="created_at" label="提交时间" width="220" />
            </el-table>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="处理进度" name="progress">
        <div class="coming-soon" v-if="!store.submissions.length">
          <el-empty description="暂无任务，请到“新建项目”提交图像" />
        </div>
        <div v-else>
          <el-table :data="store.submissions" style="width: 100%">
            <el-table-column prop="id" label="任务ID" width="260" />
            <el-table-column prop="filename" label="文件名" />
            <el-table-column prop="status" label="状态" width="120" />
            <el-table-column prop="createdAt" label="提交时间" width="200" />
            <el-table-column label="操作" width="160">
              <template #default="{ row }">
                <el-button type="primary" link @click="goSeg(row.id)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="模型查看" name="models">
        <div class="coming-soon">
          <el-empty description="模型查看功能待开发" />
        </div>
      </el-tab-pane>
    </el-tabs>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/appStore'
import ImageUploader from '../components/ImageUploader.vue'
import { uploadImage, createProject, uploadProjectImage, listProjects } from '../api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const store = useAppStore()
const activeTab = ref('overview')
// 初始化时从数据库拉取最近项目，替换本地缓存
async function loadRecentProjects() {
  try {
    const { data } = await listProjects({ limit: 20 })
    // 用后端数据覆盖本地 submissions
    store.submissions = (data.items || []).map(it => ({
      project_id: String(it.project_id),
      project_name: it.project_name,
      reconstruction_type: it.reconstruction_type,
      status: it.status,
      created_at: it.created_at,
    }))
    // 同步持久化
    localStorage.setItem('submissions', JSON.stringify(store.submissions))
  } catch (e) {
    // 回退到本地缓存
    store.loadSubmissions()
  }
}
loadRecentProjects()

// 当前时间
const currentTime = ref('')
let timeInterval = null

function updateTime() {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  
  currentTime.value = `${year}年${month}月${day}日 ${hours}:${minutes}:${seconds}`
}

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})

// 上传相关状态
const uploaderRef = ref(null)
const files = ref([])
const previewUrls = ref([])
const items = computed(() => files.value.map((file, idx) => ({ file, url: previewUrls.value[idx] })))
const projectForm = ref({ projectName: '', reconstructionType: '', description: '' })
const canSubmit = computed(() => !!projectForm.value.projectName && !!projectForm.value.reconstructionType && files.value.length > 0)

function fileKey(f) {
  return `${f.name}_${f.size}_${f.lastModified}`
}

function onSelect(selected) {
  // 去重：同一批次选择中若有重复文件，仅保留一份
  const byKey = new Map()
  selected.forEach(f => { byKey.set(fileKey(f), f) })
  files.value = Array.from(byKey.values())
  // 生成所有文件的预览
  previewUrls.value = files.value.map(f => URL.createObjectURL(f))
}

function onAppend(file) {
  const key = fileKey(file)
  const existsIndex = files.value.findIndex(f => fileKey(f) === key)
  if (existsIndex !== -1) {
    // 如果已存在同一文件，先移除旧的预览，替换为最新选择
    const oldUrl = previewUrls.value[existsIndex]
    if (oldUrl) URL.revokeObjectURL(oldUrl)
    files.value.splice(existsIndex, 1, file)
    previewUrls.value.splice(existsIndex, 1, URL.createObjectURL(file))
  } else {
    files.value.push(file)
    previewUrls.value.push(URL.createObjectURL(file))
  }
}

function removeAt(index) {
  const [removed] = files.value.splice(index, 1)
  const [url] = previewUrls.value.splice(index, 1)
  if (url) URL.revokeObjectURL(url)
}

function onReupload() {
  files.value = []
  previewUrls.value.forEach(u => URL.revokeObjectURL(u))
  previewUrls.value = []
  uploaderRef.value?.clear()
  uploaderRef.value?.open()
}

async function onUpload() {
  if (!files.value.length) return
  // 这里仍按单文件接口示例，取第一张上传
  const first = files.value[0]
  const fd = new FormData()
  fd.append('file', first)
  const { data } = await uploadImage(fd)
  const imageId = data.image_id || data.imageId
  store.addUploadedImage({ id: imageId, name: first.name })
  store.addSubmission({ id: imageId, filename: first.name, status: 'queued', createdAt: new Date().toISOString() })
  activeTab.value = 'progress'
}

function goSeg(id) {
  router.push(`/segmentation/${id}`)
}

// 新建项目并上传首张图片（接口占位，后端接入 MySQL 表 project_data 与 project_images）
async function onCreateProject() {
  if (!canSubmit.value) return
  try {
    const { data: p } = await createProject({
      project_name: projectForm.value.projectName,
      reconstruction_type: projectForm.value.reconstructionType,
      description: projectForm.value.description,
    })
    const projectId = p.project_id
    // 循环上传所有选择的文件
    for (const f of files.value) {
      const fd = new FormData()
      fd.append('file', f)
      await uploadProjectImage(projectId, fd)
    }
    // 前端沿用“任务”列表，字段对齐 project_data
    store.addSubmission({
      project_id: String(projectId),
      project_name: projectForm.value.projectName,
      reconstruction_type: projectForm.value.reconstructionType,
      status: p.status ||'重建中',
      created_at: p.created_at,
    })
    ElMessage.success('提交成功，请前往“处理进度”查看')
    activeTab.value = 'progress'
  } catch (e) {
    ElMessage.error('提交失败：' + (e.response?.data?.detail || '未知错误'))
  }
}
</script>

<style scoped>
.dashboard {
  padding: 24px;
  background-color: #f5f5f5;
  min-height: calc(100vh - 60px);
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #303133;
}

.page-header p {
  color: #606266;
  margin: 0;
}

.dashboard-tabs {
  margin-bottom: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 8px;
}

.stat-content {
  text-align: center;
  padding: 16px;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.stat-desc {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-trend {
  font-size: 12px;
  font-weight: 600;
}

.stat-trend.positive {
  color: #67c23a;
}

.stat-status {
  font-size: 12px;
  color: #409eff;
  font-weight: 600;
}

.section {
  margin-bottom: 32px;
}

.section h3 {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #303133;
}

.section p {
  color: #606266;
  margin: 0 0 16px 0;
}

.task-card {
  margin-bottom: 16px;
  border-radius: 8px;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.task-info h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  color: #303133;
}

.task-info p {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.task-progress {
  margin-top: 16px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
}

.progress-steps {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.search-bar {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 8px;
}

.project-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.project-card {
  border-radius: 8px;
}

.project-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.project-thumbnail {
  width: 80px;
  height: 60px;
  border-radius: 6px;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.thumbnail-placeholder {
  font-size: 24px;
}

.project-info {
  flex: 1;
}

.project-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #303133;
}

.project-info p {
  margin: 4px 0;
  font-size: 14px;
  color: #606266;
}

.model-size {
  color: #909399 !important;
  font-size: 12px !important;
}

.project-actions {
  display: flex;
  gap: 8px;
}

.coming-soon {
  padding: 40px 0;
  text-align: center;
}

.upload-container {
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.upload-container h3 {
  margin: 0 0 20px 0;
  color: #303133;
}

.gallery {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.tile {
  width: 200px;
}

.thumb {
  width: 200px;
  height: 130px;
  object-fit: cover;
  border: 1px solid #eee;
}

.meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
}

.name {
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>


