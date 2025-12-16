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
          <!-- 列表头 -->
          <div class="list-header">
            <div class="col-thumb">缩略图</div>
            <div class="col-name">文件名</div>
            <div class="col-rules">自动规则</div>
            <div class="col-status">状态</div>
            <div class="col-actions">操作</div>
          </div>

          <!-- 列表项 -->
          <div class="list-body">
            <div 
              v-for="(file, index) in files" 
              :key="index"
              class="list-item"
              :class="{ 'is-done': file.status === 'done' }"
            >
              <!-- 缩略图 -->
              <div class="item-thumb-container" @click="openPreview(file)">
                <img :src="file.processedUrl || file.originalUrl" class="item-thumb-img">
                <div class="thumb-overlay">
                  <svg xmlns="http://www.w3.org/2000/svg" class="overlay-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
              </div>

              <!-- 文件名 -->
              <div class="item-info">
                <p class="info-name">{{ file.name }}</p>
                <p class="info-size">{{ formatSize(file.raw.size) }}</p>
              </div>

              <!-- 规则 -->
              <div class="item-rules">
                <span class="badge badge-gray">裁剪 4:3</span>
                <span v-if="file.needsMirror" class="badge badge-indigo">↕ 垂直镜像</span>
              </div>

              <!-- 状态 -->
              <div class="item-status">
                <span v-if="file.status === 'done'" class="status-pill status-success">已完成</span>
                <span v-else-if="file.status === 'processing'" class="status-pill status-processing">处理中...</span>
                <span v-else-if="file.status === 'pending'" class="status-text-pending">等待中</span>
                <span v-else class="status-text-error">出错</span>
              </div>

              <!-- 操作 -->
              <div class="item-actions">
                <button v-if="file.status === 'done'" @click="openPreview(file)" class="action-btn" title="查看/调整">
                  <svg xmlns="http://www.w3.org/2000/svg" class="action-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                  </svg>
                </button>
                <button v-if="status !== 'processing'" @click="removeFile(index)" class="action-btn btn-delete" title="移除">
                  <svg xmlns="http://www.w3.org/2000/svg" class="action-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>

      <!-- 3. 底部操作栏 -->
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
import { processImageBatch } from '../api'
import { ElMessage } from 'element-plus'

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
      status: 'pending' // pending, processing, done, error
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

  // Process concurrency control
  const CONCURRENCY = 3
  const queue = [...pendingFiles]
  let activeCount = 0
  let completedCount = 0
  const total = pendingFiles.length

  const processNext = async () => {
    if (queue.length === 0 && activeCount === 0) {
      status.value = 'finished'
      ElMessage.success('全部处理完成！')
      return
    }

    if (queue.length > 0) {
      const file = queue.shift()
      activeCount++
      processOneImage(file).finally(() => {
        activeCount--
        completedCount++
        processNext()
      })
      
      if (activeCount < CONCURRENCY) {
        processNext()
      }
    }
  }

  // Start initial batch
  processNext()
}

const processOneImage = async (file) => {
  file.status = 'processing'
  try {
    const formData = new FormData()
    formData.append('file', file.raw)
    
    // Pass manual crop params if needed later, currently backend handles auto-crop
    
    const response = await processImage(formData)
    
    // response.data is Blob
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

// PREVIEW UI ACTIONS
const openPreview = (file) => {
// if (file.status !== 'done') return // Allow preview for all statuses
  currentFile.value = file
  previewVisible.value = true
  isEditing.value = false
}

const closePreview = () => {
  previewVisible.value = false
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

.main-content {
  max-width: 72rem; /* max-w-6xl */
  margin: 0 auto;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-shrink: 0;
}

.page-title {
  font-size: 1.5rem; /* text-2xl */
  font-weight: 700;
  color: #1e293b; /* text-slate-800 */
  margin: 0;
  letter-spacing: -0.025em;
}

.page-subtitle {
  font-size: 0.875rem; /* text-sm */
  color: #64748b; /* text-slate-500 */
  margin-top: 0.25rem;
}

.highlight-text {
  color: #4f46e5; /* text-indigo-600 */
  font-weight: 500;
}

.file-count-badge {
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.5rem 1rem;
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  border: 1px solid #e2e8f0;
}

.count-number {
  color: #2563eb; /* text-blue-600 */
}

/* Content Body */
.content-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  gap: 1.5rem;
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

.list-header {
  padding: 0.75rem 1.5rem;
  border-bottom: 1px solid #f1f5f9;
  background-color: #f8fafc;
  display: flex;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  flex-shrink: 0; /* Prevent header from shrinking */
}

.col-thumb { width: 5rem; }
.col-name { flex: 1; }
.col-rules { width: 8rem; }
.col-status { width: 6rem; text-align: center; }
.col-actions { width: 6rem; text-align: right; }

.list-body {
  flex: 1;
  overflow-y: auto; /* Enable vertical scrolling */
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.list-item {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  border-radius: 0.5rem;
  border: 1px solid transparent;
  transition: background-color 0.2s;
}

.list-item:hover {
  background-color: #f8fafc;
}

.list-item.is-done:hover {
  background-color: #f0fdf4; /* hover:bg-green-50 */
  border-color: #dcfce7; /* hover:border-green-100 */
}

/* Item Content */
.item-thumb-container {
  width: 5rem;
  height: 4rem;
  background-color: #f1f5f9;
  border-radius: 0.25rem;
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
  padding: 0 1rem;
  overflow: hidden;
}
.info-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #334155;
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

.item-rules {
  width: 8rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 6px;
  border-radius: 0.25rem;
  font-size: 0.625rem; /* 10px */
  font-weight: 500;
  width: fit-content;
}
.badge-gray { background-color: #f3f4f6; color: #4b5563; }
.badge-indigo { background-color: #e0e7ff; color: #4338ca; }

.item-status { width: 6rem; text-align: center; }
.status-pill {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
}
.status-success { color: #16a34a; background-color: #dcfce7; }
.status-processing { color: #3b82f6; animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
.status-text-pending { color: #94a3b8; font-size: 0.75rem; }
.status-text-error { color: #ef4444; font-size: 0.75rem; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: .5; }
}

.item-actions { width: 6rem; display: flex; justify-content: flex-end; gap: 0.5rem; }
.action-btn {
  padding: 0.5rem;
  color: #94a3b8;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
}
.action-btn:hover { color: #2563eb; }
.btn-delete:hover { color: #ef4444; }
.action-icon { width: 1.25rem; height: 1.25rem; }

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