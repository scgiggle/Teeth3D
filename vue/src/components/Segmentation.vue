<template>
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

</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { http } from '../api'
import { ElMessage } from 'element-plus'
import { ArrowLeftBold, CloseBold } from '@element-plus/icons-vue'

const dogSrc = new URL('../image/teeth.JPG', import.meta.url).href
const dogImg = ref(null)
const input_point = ref([])
const input_label = ref([])

const overlaySrc = ref('')
const activeTool = ref('hover')
const hideOverlay = ref(false)
const opacity = ref(1)
const currentImageIndex = ref(0)
const displayedImages = ref([
  new URL('../image/teeth.JPG', import.meta.url).href,
])
const hasImages = computed(() => (displayedImages.value && displayedImages.value.length > 0))
const displayIndexText = computed(() => hasImages.value ? `${currentImageIndex.value + 1}/${displayedImages.value.length}` : '0/0')

function formatOpacity(val) {
  return Math.round(val * 100) + '%'
}

async function onImgMouseDown(e) {
  const imgEl = dogImg.value || (e.currentTarget && e.currentTarget.querySelector('img'))
  if (!imgEl) return

  const rect = imgEl.getBoundingClientRect()
  const clickXDisplay = e.clientX - rect.left
  const clickYDisplay = e.clientY - rect.top

  const displayW = rect.width
  const displayH = rect.height
  const naturalW = imgEl.naturalWidth
  const naturalH = imgEl.naturalHeight

  if (!displayW || !displayH || !naturalW || !naturalH) return

  const scaleX = naturalW / displayW
  const scaleY = naturalH / displayH
  const x = Math.round(clickXDisplay * scaleX)
  const y = Math.round(clickYDisplay * scaleY)

  const label = e.button === 0 ? 1 : (e.button === 2 ? 0 : null)

  input_point.value.push([x, y])
  input_label.value.push(label)

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
    ElMessage.error('分割请求失败')
  }
}

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
  ElMessage.success('分割已提交（占位）')
}

function updateDisplayedSrc() {
  const src = displayedImages.value[currentImageIndex.value]
  if (src && dogImg.value) {
    dogImg.value.src = src
    overlaySrc.value = ''
  }
}

function onThumbClick(idx) {
  currentImageIndex.value = idx
  updateDisplayedSrc()
}

function onKeydown(e) {
  if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) return
  if (e.key === 'ArrowLeft') prevImage()
  else if (e.key === 'ArrowRight') nextImage()
  else if (e.key === 'r' || e.key === 'R') resetSegmentation()
}

function undo() {
  ElMessage.info('回退（占位）')
}

watch(opacity, (v) => {
  const el = document.querySelector('.dashboard')
  if (el) el.style.setProperty('--opacity', String(v))
}, { immediate: true })

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
  nextTick(() => updateDisplayedSrc())
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
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

.img-wrap { position: relative; display: inline-block }
.dog-img { max-width: 80%; border: 1px solid #eee; display: block; border-radius: 8px; }
.overlay-img { position: absolute; left: 0; top: 0; pointer-events: none; max-width: 80%; opacity: var(--opacity); border-radius: 8px; }

.thumb-row { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.thumb-item { cursor: pointer; }
.thumb-small { width: 72px; height: 48px; object-fit: cover; border-radius: 4px; }
.thumb-small.active { border: 2px solid #409eff }

.tool-accordion { background:#fff; border-radius:8px; padding:8px; border:1px solid #f0f0f0 }
.tool-item + .tool-item { margin-top:8px }
.tool-header { display:flex; gap:8px; align-items:center; padding:10px; cursor:pointer; background:#fff; color:#0f1724; border-radius:6px; border:1px solid #eef2f6 }
.tool-header .title { font-weight:700 }
.tool-header.active { background:#0f1724; color:#fff; border-color: transparent }
.tool-body { padding:8px; border-radius:6px; background:#fff }
.usage-line { color:#666; margin-bottom:6px; font-size:13px }

.opacity-row { display:flex; align-items:center; gap:8px }
.opacity-display { min-width:48px; text-align:center; font-size:13px; color:#444 }

.full-btn { width:100%; box-sizing: border-box; text-align:center; margin:8px 0; border-radius:6px; padding:12px 0 }

.media-box { display: inline-block; position: relative; text-align: left; }
.actions-row { display:flex; align-items:center; gap:8px }
.actions-left { display:flex; gap:8px }
.actions-right { margin-left: auto }
</style>
