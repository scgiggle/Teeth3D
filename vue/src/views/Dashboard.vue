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

      <el-tab-pane label="牙齿分割" name="segment">
        <div class="segment-container">
          <div class="left-panel">
            <div class="controls">
              <div>
                <div class="tool-accordion">
                  <div class="tool-item">
                    <div :class="['tool-header', { active: activeTool === 'hover' }]" @click="activeTool = activeTool === 'hover' ? null : 'hover'">
                      <span class="icon">🖱️</span>
                      <span class="title">点击方式</span>
                    </div>
                    <div class="tool-body" v-show="activeTool === 'hover'">
                      <div class="usage-line">左键: 选中区域</div>
                      <div class="usage-line">右键: 删除区域</div>
                    </div>
                  </div>

                  <div class="tool-item">
                    <div :class="['tool-header', { active: activeTool === 'box' }]" @click="activeTool = activeTool === 'box' ? null : 'box'">
                      <span class="icon" style="margin-left:3px">▢</span>
                      <span class="title" style="margin-left:4px">框选方式</span>
                    </div>
                    <div class="tool-body" v-show="activeTool === 'box'">
                      <div class="usage-line">拖拽以框选区域</div>
                      <div class="usage-line"></div>
                    </div>
                  </div>
                  <el-divider/>
                  <div class="opacity-label">透明度设置</div>
                  <div class="opacity-row">
                    <el-slider v-model="opacity" :min="0" :max="1" :step="0.01" :format-tooltip="formatOpacity" />
                    <div class="opacity-display">{{ formatOpacity(opacity) }}</div>
                  </div>
                  <div class="tool-actions">
                    <el-button class="full-btn" @click="undo">
                      <el-icon><ArrowLeftBold /></el-icon>
                      回退
                    </el-button>
                    <el-button class="full-btn" @click="resetSegmentation">
                      <el-icon><CloseBold /></el-icon>
                      重置
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="right-panel">
              <div class="thumb-row" v-if="displayedImages.length">
                <div v-for="(t, i) in displayedImages" :key="i" class="thumb-item" @click="onThumbClick(i)">
                  <img :src="t" class="thumb-small" :class="{ active: i === currentImageIndex }" />
                </div>
              </div>
              <div class="img-wrap" ref="imgWrap" @mousedown="onImgMouseDown" @contextmenu.prevent>
                <div class="media-box">
                  <transition name="fade" mode="out-in">
                    <img key="main-{{ currentImageIndex }}" ref="dogImg" :src="displayedImages[currentImageIndex] || dogSrc" alt="dog" class="dog-img" />
                  </transition>
                  <transition name="fade">
                    <img v-if="overlaySrc && !hideOverlay" :src="overlaySrc" alt="overlay" class="overlay-img" />
                  </transition>

                  <div class="actions-row" style="margin-top: 15px">
                    <div class="actions-left">
                      <el-button :disabled="!hasImages" @click="prevImage">上一张</el-button>
                      <span>{{ displayIndexText }}</span>
                      <el-button :disabled="!hasImages" @click="nextImage">下一张</el-button>
                    </div>
                    <div class="actions-right">
                      <el-button>返回</el-button>
                      <el-button type="primary" :disabled="!hasImages" @click="submitSegmentation">完成分割</el-button>
                    </div>
                  </div>
                </div>
              </div>
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
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/appStore'
import ImageUploader from '../components/ImageUploader.vue'
import { http, uploadImage, createProject, uploadProjectImage, listProjects } from '../api'
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


const dogSrc = new URL('../image/teeth.JPG', import.meta.url).href
const dogImg = ref(null)
const lastClick = ref(null)
const input_point = ref([])
const input_label = ref([])

const overlaySrc = ref('')
const selectionMode = ref('click')
const boxEnabled = ref(false)
const activeTool = ref('hover')
const hideOverlay = ref(false)

function formatOpacity(val) {
  return Math.round(val * 100) + '%'
}

async function onImgMouseDown(e) {
  const imgEl = dogImg.value || (e.currentTarget && e.currentTarget.querySelector('img'))
  if (!imgEl) return

  // get bounding rect of displayed image
  const rect = imgEl.getBoundingClientRect()
  const clickXDisplay = e.clientX - rect.left
  const clickYDisplay = e.clientY - rect.top

  // displayed size
  const displayW = rect.width
  const displayH = rect.height
  // natural/original size in pixels
  const naturalW = imgEl.naturalWidth
  const naturalH = imgEl.naturalHeight

  // guard
  if (!displayW || !displayH || !naturalW || !naturalH) return

  // map display coords -> natural image pixel coords
  const scaleX = naturalW / displayW
  const scaleY = naturalH / displayH
  const x = Math.round(clickXDisplay * scaleX)
  const y = Math.round(clickYDisplay * scaleY)

  const label = e.button === 0 ? 1 : (e.button === 2 ? 0 : null)
  lastClick.value = { x, y, label }

  // accumulate points and labels (you may change to send only current point if desired)
  input_point.value.push([x, y])
  input_label.value.push(label)

  // draw the original (natural-size) image into a canvas to preserve pixel size
  const canvas = document.createElement('canvas')
  canvas.width = naturalW
  canvas.height = naturalH
  const ctx = canvas.getContext('2d')
  ctx.drawImage(imgEl, 0, 0, canvas.width, canvas.height)

  try {
    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'))
    const form = new FormData()
    form.append('file', blob, 'capture.png')
    form.append('point_coords', JSON.stringify(input_point.value))
    form.append('point_labels', JSON.stringify(input_label.value))

    const { data } = await http.post('/segmentation/predict', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    if (data && data.image_base64) {
      overlaySrc.value = data.image_base64
    }
  } catch (err) {
    console.error('predict error', err)
  }
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

// 牙齿分割相关
const opacity = ref(1)
const currentImageIndex = ref(0)
// displayedImages 可替换为从后端加载的 image urls，当前为占位
const displayedImages = ref([
  new URL('../image/teeth.JPG', import.meta.url).href,
  // 添加更多占位或从项目中加载
])
const images = displayedImages // 兼容旧代码
const jumpIndex = ref(1)

const hasImages = computed(() => (displayedImages.value && displayedImages.value.length > 0))
const displayIndexText = computed(() => hasImages.value ? `${currentImageIndex.value + 1}/${displayedImages.value.length}` : '0/0')

function resetSegmentation() {
  overlaySrc.value = ''
}

function prevImage() {
  if (!hasImages.value) return
  currentImageIndex.value = (currentImageIndex.value - 1 + displayedImages.value.length) % displayedImages.value.length
  updateDisplayedSrc()
}

function nextImage() {
  if (!hasImages.value) return
  currentImageIndex.value = (currentImageIndex.value + 1) % displayedImages.value.length
  updateDisplayedSrc()
}

function submitSegmentation() {
  // TODO: 集成后端提交逻辑；当前为占位行为
  ElMessage.success('分割已提交（占位）')
}

function updateDisplayedSrc() {
  // 更新主图与 overlay 的 src
  const src = displayedImages.value[currentImageIndex.value]
  if (src && dogImg.value) {
    dogImg.value.src = src
    // 清掉 overlay（保持用户选择的行为），如需保留 overlay 则注释下一行
    overlaySrc.value = ''
  }
}

function jumpTo(val) {
  if (!hasImages.value) return
  const idx = Math.max(0, Math.min(displayedImages.value.length - 1, (val || jumpIndex.value) - 1))
  currentImageIndex.value = idx
  updateDisplayedSrc()
}

function toggleAutoplay() {
}

function onThumbClick(idx) {
  currentImageIndex.value = idx
  updateDisplayedSrc()
}

// 监听 opacity 并注入 CSS 变量，驱动 overlay-img 的透明度
watch(opacity, (v) => {
  const el = document.querySelector('.dashboard')
  if (el) el.style.setProperty('--opacity', String(v))
}, { immediate: true })

// 键盘快捷键: 左/右 翻页, R 重置, Space 播放/暂停
function onKeydown(e) {
  if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) return
  if (e.key === 'ArrowLeft') prevImage()
  else if (e.key === 'ArrowRight') nextImage()
  else if (e.key === 'r' || e.key === 'R') resetSegmentation()
}

function undo() {
  // 占位：回退上一步（界面级占位，未实现实际回退逻辑）
  ElMessage.info('回退（占位）')
}

onMounted(() => {
  // 已有时间更新逻辑，追加键盘与 autoplay 管理
  window.addEventListener('keydown', onKeydown)
  // 初始化图片
  nextTick(() => updateDisplayedSrc())
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
})
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

.segment-simple { padding: 16px; }
.img-wrap { position: relative; display: inline-block }
.dog-img { max-width: 80%; border: 1px solid #eee; display: block; border-radius: 8px; }
.overlay-img { position: absolute; left: 0; top: 0; pointer-events: none; max-width: 80%; opacity: var(--opacity); border-radius: 8px; }
.thumb-row { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.thumb-item { cursor: pointer; }
.thumb-small { width: 72px; height: 48px; object-fit: cover; border-radius: 4px; }
:root, .dashboard { --opacity: 1; }

/* 过渡与动画 */
.fade-enter-active, .fade-leave-active { transition: opacity 300ms ease; }
.fade-enter-from, .fade-leave-to { opacity: 0 }
.thumb-small { transition: box-shadow 180ms ease; }
.thumb-small.active { border: 2px solid #409eff }
.thumb-row { overflow-x: auto; padding-bottom: 6px }
.img-wrap { display:flex; align-items:center; justify-content:center; min-height:240px }
.dog-img { transition: box-shadow 220ms ease }
.overlay-img { transition: opacity 220ms ease }
.click-info { margin-top: 12px; background: #fff; padding: 8px; border-radius: 6px }

.controls {
  margin-top: 16px;
}

.visibility-control { background:#fff; padding:8px; border-radius:8px; border:1px solid #f0f0f0; margin-bottom:8px }
.vis-row { display:flex; align-items:center; gap:8px; margin-bottom:8px }
.opacity-label { font-size:13px; color:#666; margin-bottom:6px }
.opacity-row { display:flex; align-items:center; gap:8px }
.opacity-display { min-width:48px; text-align:center; font-size:13px; color:#444 }

.selection-panel {
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  border: 1px solid #f0f0f0;
}
.selection-header { font-weight:600; margin-bottom:6px }
.selection-usage { margin-top:6px; color:#666 }
.usage-title { font-weight:600; font-size:13px }
.usage-sub { font-size:12px; color:#999 }

.vertical-panel {
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  border: 1px solid #f0f0f0;
}
.panel-header { background:#0f1724; color:#fff; padding:8px 10px; border-radius:6px; display:flex; gap:8px; align-items:center }
.panel-header .title { font-weight:700 }
.panel-usage { padding:8px 2px; color:#666; font-size:13px }
.panel-option { padding:6px 2px }
.panel-control { padding:8px 2px }
.control-label { font-size:12px; color:#666; margin-bottom:6px }

.tool-accordion { background:#fff; border-radius:8px; padding:8px; border:1px solid #f0f0f0 }
.tool-item + .tool-item { margin-top:8px }
.tool-header { display:flex; gap:8px; align-items:center; padding:10px; cursor:pointer; background:#fff; color:#0f1724; border-radius:6px; border:1px solid #eef2f6 }
.tool-header .title { font-weight:700 }
.tool-header.active { background:#0f1724; color:#fff; border-color: transparent }
.tool-body { padding:8px; border-radius:6px; background:#fff }
.tool-body .usage-line { color:#666; margin-bottom:6px; font-size:13px }
.tool-body[style] { transition: all 180ms ease }

.tool-actions { margin-top:10px; padding: 0 }
.full-btn { width:100%; box-sizing: border-box; text-align:center; margin:8px 0; border-radius:6px; padding:12px 0 }

.navigation {
  margin-top: 16px;
}

.actions-row { display:flex; align-items:center; gap:8px }
.actions-left { display:flex; gap:8px }
.actions-right { margin-left: auto }

@media (max-width: 720px) {
  .actions-row { flex-wrap:wrap }
  .actions-right { margin-left: 0; width:100% }
}

.segment-container {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.right-panel {
  flex: 2;
  margin-left: 120px;
}

.left-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.img-wrap {
  position: relative;
  display: block;
}

.dog-img {
  max-width: 100%;
  width: auto;
  border: 1px solid #eee;
  display: block;
  border-radius: 8px;
}

.overlay-img {
  position: absolute;
  left: 0;
  top: 0;
  pointer-events: none;
  max-width: 100%;
  opacity: var(--opacity);
  border-radius: 8px;
}

.media-box {
  display: inline-block;
  position: relative;
  text-align: left;
}

.media-box .actions-row { width: 100%; box-sizing: border-box; padding: 8px 4px 0 0 }
.media-box .actions-right { margin-left: auto }
</style>


