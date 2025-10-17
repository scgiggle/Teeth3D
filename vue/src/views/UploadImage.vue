<template>
  <div class="container">
    <el-card>
      <h2>上传牙齿图像</h2>
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
        <el-button type="primary" :disabled="!files.length" @click="onUpload">提交分割</el-button>
        <el-button style="margin-left: 8px;" @click="onReupload">重新上传</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import ImageUploader from '../components/ImageUploader.vue'
import { uploadImage } from '../api'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/appStore'

const router = useRouter()
const store = useAppStore()
const uploaderRef = ref(null)
const files = ref([])
const previewUrls = ref([])
const items = computed(() => files.value.map((file, idx) => ({ file, url: previewUrls.value[idx] })))
function fileKey(f) {
  return `${f.name}_${f.size}_${f.lastModified}`
}

function onSelect(selected) {
  // 清除旧状态
  clearPreviewUrls()
  // 去重：同一批次选择中若有重复文件，仅保留一份
  const byKey = new Map()
  selected.forEach(f => { byKey.set(fileKey(f), f) })
  files.value = Array.from(byKey.values())
  // 生成所有文件的预览
  previewUrls.value = files.value.map(f => URL.createObjectURL(f))
}

function clearPreviewUrls() {
  previewUrls.value.forEach(u => URL.revokeObjectURL(u))
  previewUrls.value = []
}

function clearPageState() {
  files.value = []
  clearPreviewUrls()
  uploaderRef.value?.clear()
}

async function onUpload() {
  if (!files.value.length) return
  
  const first = files.value[0]
  const fd = new FormData()
  fd.append('file', first)
  
  try {
    const { data } = await uploadImage(fd)
    const imageId = data.image_id || data.imageId
    
    store.addUploadedImage({ id: imageId, name: first.name })
    store.addSubmission({
      id: imageId,
      filename: first.name,
      status: 'queued',
      createdAt: new Date().toISOString(),
    })
    
    ElMessage.success('提交成功，请前往"处理进度"查看')
    clearPageState()
  } catch (e) {
    ElMessage.error('提交失败，请重试')
  }
}

function removeAt(index) {
  files.value.splice(index, 1)
  const [url] = previewUrls.value.splice(index, 1)
  if (url) URL.revokeObjectURL(url)
}

function onReupload() {
  clearPageState()
  uploaderRef.value?.open()
}

function onAppend(file) {
  const key = fileKey(file)
  const existsIndex = files.value.findIndex(f => fileKey(f) === key)
  
  if (existsIndex !== -1) {
    // 替换已存在的文件
    const oldUrl = previewUrls.value[existsIndex]
    if (oldUrl) URL.revokeObjectURL(oldUrl)
    files.value[existsIndex] = file
    previewUrls.value[existsIndex] = URL.createObjectURL(file)
  } else {
    // 添加新文件
    files.value.push(file)
    previewUrls.value.push(URL.createObjectURL(file))
  }
}
</script>

<style scoped>
.container { padding: 16px; }
.gallery { display: flex; flex-wrap: wrap; gap: 12px; }
.tile { width: 200px; }
.thumb { width: 200px; height: 130px; object-fit: cover; border: 1px solid #eee; }
.meta { display: flex; justify-content: space-between; align-items: center; margin-top: 4px; }
.name { max-width: 140px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>


