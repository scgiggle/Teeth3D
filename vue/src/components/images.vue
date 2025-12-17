<template>
  <div class="app-container">
    <div class="main-content">
      <!-- 1. 头部区域 -->
      <header class="page-header">
        <div>
          <h1 class="page-title">图片智能处理</h1>
          <p class="page-subtitle">
            规则：自动裁剪 4:3 |
            <span class="highlight-text">自动识别 _0 / _1结尾的图片进行垂直镜像</span>
          </p>
        </div>
        <div v-if="files.length > 0" class="file-count-badge">
          已选择 <span class="count-number">{{ files.length }}</span> 张图片
        </div>
      </header>

      <!-- 2. 主体内容区 -->
      <main class="content-body">
        <!-- 左侧：图片处理区域 -->
        <div class="panel-left">
          <!-- 拖拽上传区 -->
          <div 
            v-if="files.length === 0" 
            class="upload-drop-zone"
            :class="{ 'is-dragging': isDragging }"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="handleDrop"
            @click="triggerFileInput"
          >
            <input 
              type="file" 
              ref="fileInputRef" 
              multiple 
              accept="image/*" 
              class="hidden-input" 
              @change="handleFileSelect"
            >
            <div class="upload-icon-circle">
              <svg xmlns="http://www.w3.org/2000/svg" class="icon-svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
            </div>
            <p class="upload-title">点击或拖拽图片到此处</p>
            <p class="upload-subtitle">支持 JPG, PNG, BMP (支持批量)</p>
          </div>

          <!-- 文件列表 -->
          <div v-else class="file-list-card">
            <!-- 列表项 (Grid Layout) -->
            <div class="list-body">
              <div 
                v-for="(file, index) in files" 
                :key="index"
                class="list-item"
                :class="{ 'is-done': file.status === 'done' }"
              >
                <!-- 顶部：缩略图 + 信息 -->
                <div class="card-main">
                  <div class="item-thumb-container" @click="openPreview(file)">
                    <img :src="file.processedUrl || file.originalUrl" class="item-thumb-img">
                    <div class="thumb-overlay">
                      <svg xmlns="http://www.w3.org/2000/svg" class="overlay-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                    </div>
                  </div>
                  
                  <div class="item-info">
                    <p class="info-name" :title="file.name">{{ file.name }}</p>
                    <p class="info-size">{{ formatSize(file.raw.size) }}</p>
                    <div class="item-status-row">
                      <span v-if="file.status === 'done'" class="status-pill status-success">已完成</span>
                      <span v-else-if="file.status === 'processing'" class="status-pill status-processing">处理中...</span>
                      <span v-else-if="file.status === 'pending'" class="status-text-pending">等待中</span>
                      <span v-else class="status-text-error">出错</span>
                    </div>
                  </div>

                  <button v-if="status !== 'processing'" @click="removeFile(index)" class="card-close-btn" title="移除">
                    <svg xmlns="http://www.w3.org/2000/svg" class="icon-xs" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <!-- 底部：规则 + 操作 -->
                <div class="card-footer">
                  <div class="item-rules">
                    <span class="badge badge-gray">裁剪4:3</span>
                    <span v-if="file.needsMirror" class="badge badge-indigo">镜像</span>
                  </div>
                  
                  <div class="card-actions">
                     <button v-if="file.status === 'done'" @click="openPreview(file)" class="btn-xs-primary">
                        查看结果
                     </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 底部操作栏 -->
          <footer class="page-footer" v-if="files.length > 0">
            <button 
              @click="clearAll" 
              class="btn-clear" 
              :disabled="status === 'processing'"
            >
              清空列表
            </button>

            <button 
              @click="processAllImages" 
              class="btn-primary"
              :disabled="status === 'processing'"
              :class="{
                'is-processing': status === 'processing',
                'is-finished': status === 'finished'
              }"
            >
              <span v-if="status === 'processing'" class="spinner"></span>
              <span v-else-if="status === 'finished'">下载全部处理结果</span>
              <span v-else>开始智能处理 ({{ files.length }})</span>
            </button>
          </footer>
        </div>

        <!-- 右侧：历史记录区域 (文件夹层级样式) -->
        <div class="panel-right" v-if="historyList.length > 0">
          <div class="history-section">
            <div class="section-header">
              <h3>最近处理记录</h3>
              <div class="section-actions">
                <button class="btn-text-sm btn-danger" @click="handleDeleteAllHistory" title="清空全部">
                  清空
                </button>
                <button class="btn-text-sm" @click="refreshHistory" :disabled="loadingHistory">
                  {{ loadingHistory ? '刷新中...' : '刷新' }}
                </button>
              </div>
            </div>
            
            <!-- 文件夹层级列表 -->
            <div class="tree-list">
              <div v-for="batch in historyList" :key="batch.batch_id" class="tree-folder">
                <!-- 文件夹头部 -->
                <div class="folder-header" @click="toggleBatch(batch.batch_id)">
                  <svg xmlns="http://www.w3.org/2000/svg" class="folder-icon" :class="{ 'is-open': expandedBatches.includes(batch.batch_id) }" viewBox="0 0 20 20" fill="currentColor">
                    <path v-if="expandedBatches.includes(batch.batch_id)" d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" />
                    <path v-else fill-rule="evenodd" d="M2 6a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1H8c-.55 0-1.11.22-1.52.63L4 12.13V8H2V6zm3.41 6l2.12-2.12a.5.5 0 01.36-.15H16v4.14a2 2 0 01-2 2H4a2 2 0 01-2-2v-.59l3.41-1.28z" clip-rule="evenodd" />
                  </svg>
                  <span class="folder-name">{{ batch.created_at.substring(5, 16) }}</span>
                  <span class="folder-count">({{ batch.count }}张)</span>
                  <button @click.stop="handleBatchDownload(batch)" class="folder-action" title="下载全部">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                  </button>
                  <button @click.stop="handleDeleteBatch(batch)" class="folder-action folder-action-delete" title="删除文件夹">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                    </svg>
                  </button>
                </div>
                
                <!-- 文件列表 (可折叠) -->
                <div class="folder-files" v-show="expandedBatches.includes(batch.batch_id)">
                  <div v-for="img in batch.images" :key="img.id" class="file-item">
                    <svg xmlns="http://www.w3.org/2000/svg" class="file-icon" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd" />
                    </svg>
                    <span class="file-name" :title="img.filename" @click="handleHistoryPreview(img)">{{ img.filename }}</span>
                    <span v-if="img.needs_mirror" class="badge badge-indigo">镜像</span>
                    <div class="file-actions">
                      <button @click="handleHistoryPreview(img)" class="file-action" title="查看">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                          <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                          <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
                        </svg>
                      </button>
                      <button @click="handleHistoryDownload(img)" class="file-action" title="下载">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg>
                      </button>
                      <button @click="handleHistoryDelete(img)" class="file-action file-action-delete" title="删除">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- 4. 预览模态框 -->
    <div v-if="previewVisible" class="modal-backdrop" @click.self="closePreview">
      <div class="modal-content">
        <!-- Header -->
        <div class="modal-header">
          <div>
            <h3 class="modal-title">{{ isEditing ? '手动裁剪模式' : '处理结果预览' }}</h3>
            <p v-if="isEditing" class="modal-subtitle highlight-orange">请拖动选框选择区域，比例已固定 4:3</p>
            <p v-else class="modal-subtitle text-gray">
              {{ currentFile?.name }} - {{ currentFile?.needsMirror ? '已垂直镜像' : '仅裁剪' }}
            </p>
          </div>
          <button @click="closePreview" class="btn-close-modal">
            <svg xmlns="http://www.w3.org/2000/svg" class="icon-sm" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Body -->
        <div class="modal-body">
          <img 
            v-if="!isEditing" 
            :src="currentFile?.processedUrl || currentFile?.originalUrl" 
            class="preview-img"
          >
          <div v-show="isEditing" class="cropper-wrapper">
            <img ref="cropperImgRef" :src="currentFile?.originalUrl" class="cropper-source">
          </div>
        </div>

        <!-- Footer -->
        <div class="modal-footer">
          <div class="footer-left">
            <span v-if="isEditing" class="text-sm-gray">裁剪后会自动应用镜像规则</span>
          </div>
          <div class="footer-right">
            <template v-if="!isEditing">
              <button @click="closePreview" class="btn-secondary">关闭</button>
              <button @click="startManualCrop" class="btn-primary-sm">
                <svg xmlns="http://www.w3.org/2000/svg" class="icon-xs" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
                手动重新裁剪
              </button>
            </template>
            <template v-else>
              <button @click="cancelManualCrop" class="btn-secondary">取消</button>
              <button @click="saveManualCrop" class="btn-success-sm">
                <svg xmlns="http://www.w3.org/2000/svg" class="icon-xs" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                确认并应用
              </button>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { processImageBatch, getImageHistory, downloadHistoryImage, deleteHistoryImage, getImageThumbnailUrl, downloadBatch, deleteBatch, deleteAllHistory } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

// GLOBAL CONSTANTS
const TARGET_WIDTH = 2677
const TARGET_HEIGHT = 2008

// STATE
const files = ref([])
const isDragging = ref(false)
const status = ref('idle') // idle, processing, finished
const fileInputRef = ref(null)
const currentFile = ref(null)
const previewVisible = ref(false)
const isEditing = ref(false)
const cropperImgRef = ref(null)
let cropperInstance = null

// HISTORY STATE
const historyList = ref([])
const loadingHistory = ref(false)
const expandedBatches = ref([]) // 记录展开的批次ID

// LIFECYCLE
onMounted(() => {
  // Load Cropper.js CSS dynamically
  if (!document.getElementById('cropper-css')) {
    const link = document.createElement('link')
    link.id = 'cropper-css'
    link.rel = 'stylesheet'
    link.href = 'https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.css'
    document.head.appendChild(link)
  }
  
  // Load Scripts: Cropper, JSZip, FileSaver
  const loadScript = (src, checkVar) => {
    return new Promise((resolve) => {
      if (window[checkVar]) {
        resolve()
        return
      }
      const script = document.createElement('script')
      script.src = src
      script.onload = () => resolve()
      document.head.appendChild(script)
    })
  }

  Promise.all([
    loadScript('https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.js', 'Cropper'),
    loadScript('https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js', 'JSZip'),
    loadScript('https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.5/FileSaver.min.js', 'saveAs')
  ]).then(() => {
    Cropper = window.Cropper
  })

  refreshHistory()
})

onUnmounted(() => {
  clearAll()
  if (cropperInstance) cropperInstance.destroy()
})

// FILE ACTIONS
const triggerFileInput = () => fileInputRef.value?.click()

const handleFileSelect = (e) => {
  addFiles(e.target.files)
  e.target.value = ''
}

const handleDrop = (e) => {
  isDragging.value = false
  addFiles(e.dataTransfer.files)
}

const addFiles = (fileList) => {
  if (status.value === 'finished') {
    status.value = 'idle'
  }
  
  Array.from(fileList).forEach(file => {
    if (files.value.some(f => f.name === file.name)) return
    
    const nameNoExt = file.name.substring(0, file.name.lastIndexOf('.'))
    const needsMirror = nameNoExt.endsWith('_0') || nameNoExt.endsWith('_1')
    const originalUrl = URL.createObjectURL(file)
    
    files.value.push({
      raw: file,
      name: file.name,
      originalUrl,
      processedUrl: null,
      processedBlob: null,
      needsMirror,
      status: 'pending', // pending, processing, done, error
      dbId: null // will be set after processing
    })
  })
}

const removeFile = (index) => {
  const f = files.value[index]
  if (f.originalUrl) URL.revokeObjectURL(f.originalUrl)
  if (f.processedUrl) URL.revokeObjectURL(f.processedUrl)
  files.value.splice(index, 1)
  if (files.value.length === 0) status.value = 'idle'
}

const clearAll = () => {
  files.value.forEach(f => {
    if (f.originalUrl) URL.revokeObjectURL(f.originalUrl)
    if (f.processedUrl) URL.revokeObjectURL(f.processedUrl)
  })
  files.value = []
  status.value = 'idle'
}

// BACKEND API PROCESSING
import { processImage } from '../api'

const processAllImages = async () => {
  if (status.value === 'finished') {
    downloadAll()
    return
  }
  
  status.value = 'processing'
  
  const pendingFiles = files.value.filter(f => f.status !== 'done')
  if (pendingFiles.length === 0) {
    status.value = 'finished'
    return
  }

  // 生成一个共享的 batch_id（前8位UUID）
  const batchId = crypto.randomUUID().substring(0, 8)
  
  // 并发控制：最多同时处理 3 张图片
  const CONCURRENCY = 3
  const queue = [...pendingFiles]
  let activeCount = 0
  let completedCount = 0
  const total = pendingFiles.length

  const processNext = async () => {
    if (queue.length === 0 && activeCount === 0) {
      status.value = 'finished'
      ElMessage.success('全部处理完成！')
      refreshHistory()
      return
    }

    if (queue.length > 0 && activeCount < CONCURRENCY) {
      const file = queue.shift()
      activeCount++
      processOneImage(file, batchId).finally(() => {
        activeCount--
        completedCount++
        processNext()
      })
      
      if (activeCount < CONCURRENCY && queue.length > 0) {
        processNext()
      }
    }
  }

  // 启动初始批次
  for (let i = 0; i < Math.min(CONCURRENCY, pendingFiles.length); i++) {
    processNext()
  }
}

const processOneImage = async (file, batchId = null) => {
  file.status = 'processing'
  try {
    const formData = new FormData()
    formData.append('file', file.raw)
    if (batchId) {
      formData.append('batch_id', batchId)
    }
    
    const response = await processImage(formData)
    
    const blob = new Blob([response.data], { type: 'image/jpeg' })
    file.processedBlob = blob
    file.processedUrl = URL.createObjectURL(blob)
    file.status = 'done'
  } catch (error) {
    console.error(`Error processing ${file.name}:`, error)
    file.status = 'error'
  }
}

const downloadAll = () => {
  if (!window.JSZip || !window.saveAs) {
    ElMessage.error('下载组件未加载，请刷新页面重试')
    return
  }
  
  const zip = new window.JSZip()
  let count = 0
  
  files.value.forEach(f => {
    if (f.status === 'done' && f.processedBlob) {
      zip.file(f.name, f.processedBlob)
      count++
    }
  })
  
  if (count === 0) {
    ElMessage.warning('没有可下载的已处理图片')
    return
  }
  
  zip.generateAsync({ type: 'blob' }).then(content => {
    window.saveAs(content, 'processed_images.zip')
  })
}

// HISTORY ACTIONS
async function refreshHistory() {
  loadingHistory.value = true
  try {
    const { data } = await getImageHistory()
    historyList.value = data
    // 默认展开第一个批次
    if (data.length > 0) {
      expandedBatches.value = [data[0].batch_id]
    }
  } catch (e) {
    console.error('Fetch history failed', e)
  } finally {
    loadingHistory.value = false
  }
}

async function handleHistoryPreview(item) {
  try {
    const { data } = await downloadHistoryImage(item.id, 'processed')
    const blob = new Blob([data], { type: 'image/jpeg' })
    const url = URL.createObjectURL(blob)
    
    currentFile.value = {
      name: item.filename,
      processedUrl: url,
      processedBlob: blob,
      needsMirror: item.needs_mirror, // rough check
      isHistory: true
    }
    previewVisible.value = true
    isEditing.value = false
  } catch (e) {
    ElMessage.error('加载预览失败')
  }
}

async function handleHistoryDownload(item) {
  try {
    const { data } = await downloadHistoryImage(item.id, 'processed')
    const blob = new Blob([data], { type: 'image/jpeg' })
    window.saveAs(blob, item.filename)
  } catch (e) {
    ElMessage.error('下载失败')
  }
}

async function handleHistoryDelete(item) {
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', { type: 'warning' })
    await deleteHistoryImage(item.id)
    ElMessage.success('删除成功')
    refreshHistory()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

// BATCH ACTIONS
function toggleBatch(batchId) {
  const index = expandedBatches.value.indexOf(batchId)
  if (index > -1) {
    expandedBatches.value.splice(index, 1)
  } else {
    expandedBatches.value.push(batchId)
  }
}

function getThumbnailUrl(imageId) {
  return getImageThumbnailUrl(imageId)
}

function handleThumbError(e) {
  // 缩略图加载失败时显示占位图
  e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 80 80"%3E%3Crect fill="%23f1f5f9" width="80" height="80"/%3E%3Ctext x="50%25" y="50%25" fill="%2394a3b8" font-size="12" text-anchor="middle" dy=".3em"%3E无图%3C/text%3E%3C/svg%3E'
}

async function handleBatchDownload(batch) {
  // 使用直接链接下载，让浏览器显示原生下载进度
  const token = localStorage.getItem('access_token')
  const downloadUrl = `http://localhost:8000/api/images/batch/${batch.batch_id}/download?token=${token}`
  
  // 创建隐藏的 a 标签触发浏览器原生下载
  const link = document.createElement('a')
  link.href = downloadUrl
  link.download = `batch_${batch.batch_id}.zip`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  ElMessage.info('下载已开始，请查看浏览器下载进度')
}

async function handleDeleteBatch(batch) {
  try {
    await ElMessageBox.confirm(`确定要删除这个文件夹吗？（包含 ${batch.count} 张图片）`, '删除确认', { type: 'warning' })
    await deleteBatch(batch.batch_id)
    ElMessage.success('删除成功')
    refreshHistory()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

async function handleDeleteAllHistory() {
  try {
    await ElMessageBox.confirm('确定要清空所有历史记录吗？此操作不可撤销！', '清空确认', { type: 'warning', confirmButtonText: '确定清空', cancelButtonText: '取消' })
    await deleteAllHistory()
    ElMessage.success('已清空所有历史记录')
    historyList.value = []
    expandedBatches.value = []
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('清空失败')
  }
}

// PREVIEW UI ACTIONS
const openPreview = (file) => {
  currentFile.value = file
  previewVisible.value = true
  isEditing.value = false
}

const closePreview = () => {
  previewVisible.value = false
  // Clean up if it was a history item blob
  if (currentFile.value?.isHistory && currentFile.value.processedUrl) {
    URL.revokeObjectURL(currentFile.value.processedUrl)
  }
  if (cropperInstance) {
    cropperInstance.destroy()
    cropperInstance = null
  }
}

const startManualCrop = async () => {
  isEditing.value = true
  await nextTick()
  if (cropperInstance) cropperInstance.destroy()
  
  cropperInstance = new Cropper(cropperImgRef.value, {
    aspectRatio: 4 / 3,
    viewMode: 1,
    dragMode: 'move',
    autoCropArea: 0.8,
    guides: true,
  })
}

const cancelManualCrop = () => {
  isEditing.value = false
  if (cropperInstance) {
    cropperInstance.destroy()
    cropperInstance = null
  }
}

const saveManualCrop = () => {
  if (!cropperInstance) return
  const croppedCanvas = cropperInstance.getCroppedCanvas({
    width: TARGET_WIDTH,
    height: TARGET_HEIGHT,
    imageSmoothingEnabled: true,
    imageSmoothingQuality: 'high',
  })
  
  if (currentFile.value.needsMirror) {
    const finalCanvas = document.createElement('canvas')
    finalCanvas.width = TARGET_WIDTH
    finalCanvas.height = TARGET_HEIGHT
    const ctx = finalCanvas.getContext('2d')
    ctx.scale(1, -1)
    ctx.translate(0, -TARGET_HEIGHT)
    ctx.drawImage(croppedCanvas, 0, 0)
    finalCanvas.toBlob(blob => updateFileResult(blob), 'image/jpeg', 0.95)
  } else {
    croppedCanvas.toBlob(blob => updateFileResult(blob), 'image/jpeg', 0.95)
  }
}

const updateFileResult = (newBlob) => {
  if (currentFile.value.processedUrl) URL.revokeObjectURL(currentFile.value.processedUrl)
  currentFile.value.processedBlob = newBlob
  currentFile.value.processedUrl = URL.createObjectURL(newBlob)
  cancelManualCrop()
}

const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}
</script>

<style scoped>
/* Reset & Base */
.app-container {
  height: calc(100vh - 160px); /* Fixed height subtracts approximate header/tabs height */
  min-height: 500px;
  background-color: #f8fafc;
  padding: 1.5rem;
  color: #334155;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Ensure no scroll on this container */
}

/* Content Body */
.content-body {
  flex: 1;
  display: flex;
  flex-direction: row; /* Changed to row */
  min-height: 0;
  gap: 1.5rem;
}

.main-content {
  /* Removed max-width to fill page */
  margin: 0 auto;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* Panels */
.panel-left {
  flex: 1; /* Grow to fill space */
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

.panel-right {
  width: 350px; /* Initial fixed width */
  min-width: 300px;
  max-width: 500px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  /* Resizing could be added via future enhancements */
}

/* History Section Adjusted */
.history-section {
  background-color: white;
  border-radius: 1rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  border: 1px solid #e2e8f0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%; /* Fill the panel height */
  /* margin-top: 1rem; Removed as it's now in a flex row */
}

/* Upload Drop Zone */
.upload-drop-zone {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2px dashed #cbd5e1; /* border-slate-300 */
  background-color: white;
  border-radius: 1rem; /* rounded-2xl */
  cursor: pointer;
  transition: all 0.3s;
}

.upload-drop-zone:hover {
  border-color: #60a5fa; /* hover:border-blue-400 */
}

.upload-drop-zone.is-dragging {
  border-color: #3b82f6; /* border-blue-500 */
  background-color: #eff6ff; /* bg-blue-50 */
}

.hidden-input {
  display: none;
}

.upload-icon-circle {
  width: 4rem;
  height: 4rem;
  background-color: #dbeafe; /* bg-blue-100 */
  color: #2563eb; /* text-blue-600 */
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.icon-svg {
  width: 2rem;
  height: 2rem;
}

.upload-title {
  font-size: 1.125rem; /* text-lg */
  font-weight: 500;
  color: #334155;
  margin: 0;
}

.upload-subtitle {
  font-size: 0.875rem; /* text-sm */
  color: #94a3b8; /* text-slate-400 */
  margin-top: 0.5rem;
}

/* File List */
.file-list-card {
  flex: 1;
  min-height: 0; /* Crucial for nested flex scrolling */
  display: flex;
  flex-direction: column;
  background-color: white;
  border-radius: 1rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  border: 1px solid #e2e8f0;
  overflow: hidden;
  height: 100%; /* Ensure it takes full height */
}


.list-body {
  flex: 1;
  overflow-y: auto; /* Enable vertical scrolling */
  padding: 1rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-auto-rows: max-content;
  gap: 1rem;
}

.list-item {
  display: flex;
  flex-direction: column;
  background-color: white;
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
  transition: all 0.2s;
  overflow: hidden;
}

.list-item:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
  transform: translateY(-1px);
}

.list-item.is-done {
  border-left: 4px solid #16a34a;
}

/* Card Main Area */
.card-main {
  display: flex;
  padding: 0.75rem;
  gap: 0.75rem;
  position: relative;
}

.item-thumb-container {
  width: 4.5rem;
  height: 4.5rem;
  background-color: #f1f5f9;
  border-radius: 0.5rem;
  overflow: hidden;
  flex-shrink: 0;
  position: relative;
  cursor: pointer;
}

.item-thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-overlay {
  position: absolute;
  inset: 0;
  background-color: rgba(0,0,0,0);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.item-thumb-container:hover .thumb-overlay {
  background-color: rgba(0,0,0,0.2);
}
.overlay-icon {
  width: 1.5rem;
  height: 1.5rem;
  color: white;
  opacity: 0;
}
.item-thumb-container:hover .overlay-icon {
  opacity: 1;
}

.item-info {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.25rem;
}

.info-name {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin: 0;
}
.info-size {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0;
}

.item-status-row {
  display: flex;
  align-items: center;
}

/* Card Close Button */
.card-close-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  padding: 0.25rem;
  color: #cbd5e1;
  background: none;
  border: none;
  cursor: pointer;
  border-radius: 9999px;
  line-height: 0;
}
.card-close-btn:hover {
  color: #ef4444;
  background-color: #fef2f2;
}

/* Card Footer */
.card-footer {
  padding: 0.5rem 0.75rem;
  background-color: #f8fafc;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-rules {
  display: flex;
  gap: 0.5rem;
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 6px;
  border-radius: 0.25rem;
  font-size: 0.625rem;
  font-weight: 500;
}
.badge-gray { background-color: #f3f4f6; color: #4b5563; border: 1px solid #e5e7eb; }
.badge-indigo { background-color: #e0e7ff; color: #4338ca; border: 1px solid #c7d2fe; }

/* Status Styles */
.status-pill {
  font-size: 0.625rem;
  font-weight: 700;
  padding: 0.125rem 0.375rem;
  border-radius: 9999px;
  text-transform: uppercase;
}
.status-success { color: #16a34a; background-color: #dcfce7; }
.status-processing { color: #3b82f6; background-color: #dbeafe; }
.status-text-pending { color: #94a3b8; font-size: 0.75rem; }
.status-text-error { color: #ef4444; font-size: 0.75rem; }

/* Action Buttons */
.btn-xs-primary {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  border-radius: 0.375rem;
  background-color: white;
  color: #2563eb;
  border: 1px solid #bfdbfe;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}
.btn-xs-primary:hover {
  background-color: #2563eb;
  color: white;
}



.section-header {
  padding: 0.75rem 1.5rem;
  border-bottom: 1px solid #f1f5f9;
  background-color: #f8fafc;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h3 {
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.btn-text-sm {
  background: none;
  border: none;
  color: #2563eb;
  font-size: 0.75rem;
  cursor: pointer;
}
.btn-text-sm:hover { text-decoration: underline; }
.btn-text-sm:disabled { color: #94a3b8; cursor: not-allowed; }
.btn-text-sm.btn-danger { color: #dc2626; }
.btn-text-sm.btn-danger:hover { color: #b91c1c; }

.section-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

/* Tree List (Folder Hierarchy) */
.tree-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.tree-folder {
  margin-bottom: 0.25rem;
}

.folder-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  border-radius: 0.375rem;
  transition: background-color 0.15s;
}

.folder-header:hover {
  background-color: #f1f5f9;
}

.folder-icon {
  width: 1.125rem;
  height: 1.125rem;
  color: #f59e0b;
  flex-shrink: 0;
}

.folder-icon.is-open {
  color: #d97706;
}

.folder-name {
  font-size: 0.8125rem;
  font-weight: 500;
  color: #334155;
}

.folder-count {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-left: auto;
}

.folder-action {
  padding: 0.25rem;
  background: none;
  border: none;
  cursor: pointer;
  color: #64748b;
  border-radius: 0.25rem;
  opacity: 0;
  transition: opacity 0.15s, background-color 0.15s;
}

.folder-action svg {
  width: 1rem;
  height: 1rem;
}

.folder-header:hover .folder-action {
  opacity: 1;
}

.folder-action:hover {
  background-color: #e2e8f0;
  color: #2563eb;
}

.folder-action-delete:hover {
  background-color: #fee2e2;
  color: #dc2626;
}

/* Folder Files */
.folder-files {
  padding-left: 1.5rem;
  border-left: 1px solid #e2e8f0;
  margin-left: 0.5rem;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.5rem;
  border-radius: 0.25rem;
  transition: background-color 0.15s;
}

.file-item:hover {
  background-color: #f8fafc;
}

.file-icon {
  width: 1rem;
  height: 1rem;
  color: #3b82f6;
  flex-shrink: 0;
}

.file-name {
  flex: 1;
  font-size: 0.75rem;
  color: #475569;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
}

.file-name:hover {
  color: #2563eb;
}

.file-actions {
  display: flex;
  gap: 0.125rem;
  opacity: 0;
  transition: opacity 0.15s;
}

.file-item:hover .file-actions {
  opacity: 1;
}

.file-action {
  padding: 0.25rem;
  background: none;
  border: none;
  cursor: pointer;
  color: #64748b;
  border-radius: 0.25rem;
  transition: background-color 0.15s, color 0.15s;
}

.file-action svg {
  width: 0.875rem;
  height: 0.875rem;
}

.file-action:hover {
  background-color: #e2e8f0;
  color: #2563eb;
}

.file-action-delete:hover {
  background-color: #fee2e2;
  color: #dc2626;
}

.h-info {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.5rem;
}

.h-name {
  flex: 1;
  color: #334155;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.h-time {
  font-size: 0.75rem;
  color: #94a3b8;
  flex-shrink: 0;
}

.h-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.h-tags {
  display: flex;
}

.h-actions {
  display: flex;
  gap: 0.25rem;
}

/* Footer */
.page-footer {
  margin-top: 1rem;
  border-top: 1px solid #e2e8f0;
  padding-top: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.btn-clear {
  font-size: 0.875rem;
  color: #64748b;
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 500;
  padding: 0 1rem;
}
.btn-clear:hover { color: #dc2626; }

.btn-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 2rem;
  border-radius: 0.75rem;
  font-weight: 700;
  color: white;
  background-color: #2563eb;
  border: none;
  cursor: pointer;
  box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
  transition: all 0.2s;
}
.btn-primary:hover { background-color: #1d4ed8; }
.btn-primary:active { transform: scale(0.95); }

.btn-primary.is-processing { background-color: #cbd5e1; cursor: not-allowed; }
.btn-primary.is-finished { background-color: #16a34a; }
.btn-primary.is-finished:hover { background-color: #15803d; }

.spinner {
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid white;
  border-bottom-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 50;
  background-color: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.modal-content {
  background-color: white;
  border-radius: 1rem;
  overflow: hidden;
  max-width: 56rem;
  width: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  max-height: 90vh;
}

.modal-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #f3f4f6;
  background-color: #f9fafb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-title { margin: 0; font-size: 1.125rem; font-weight: 700; color: #1f2937; }
.modal-subtitle { margin: 0.25rem 0 0 0; font-size: 0.75rem; }
.highlight-orange { color: #ea580c; }
.text-gray { color: #6b7280; }

.btn-close-modal {
  color: #9ca3af;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 9999px;
}
.btn-close-modal:hover { background-color: #e5e7eb; color: #4b5563; }

.modal-body {
  flex: 1;
  background-color: #111827;
  overflow: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  position: relative;
  min-height: 400px;
}
.preview-img { max-height: 100%; max-width: 100%; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
.cropper-wrapper { width: 100%; height: 100%; }
.cropper-source { max-width: 100%; display: block; }

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #f3f4f6;
  background-color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.text-sm-gray { font-size: 0.875rem; color: #6b7280; }

.footer-right { display: flex; gap: 0.75rem; }

.action-btn {
  padding: 0.5rem;
  color: #94a3b8;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
}
.action-btn:hover { color: #2563eb; }
.btn-delete:hover { color: #ef4444; }
.action-icon { width: 1.25rem; height: 1.25rem; }

.btn-secondary {
  padding: 0.5rem 1rem;
  color: #4b5563;
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 500;
  border-radius: 0.5rem;
}
.btn-secondary:hover { background-color: #f3f4f6; }

.btn-primary-sm, .btn-success-sm {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
}
.btn-primary-sm { background-color: #2563eb; }
.btn-primary-sm:hover { background-color: #1d4ed8; }
.btn-success-sm { background-color: #16a34a; }
.btn-success-sm:hover { background-color: #15803d; }

.icon-xs { width: 1rem; height: 1rem; }
.icon-sm { width: 1.5rem; height: 1.5rem; }
</style>