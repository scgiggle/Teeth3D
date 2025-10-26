<template>
  <div class="model-check-root">
    <div class="model-check-card">
      <el-row class="model-check-layout" :gutter="24" align="top">
        <el-col :span="14" class="viewer-column">
          <div class="viewer-header">
            <h3>3D模型查看</h3>
          </div>

          <div class="viewer-area" ref="viewerAreaRef">
            <div id="three-viewer" style="width:100%;height:100%"></div>
            <div class="viewer-toolbar">
              <el-tooltip v-if="isHide" content="显示框线" placement="bottom">
                <el-button circle size="small" @click="showLine">
                  <el-icon><View /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip v-else content="隐藏框线" placement="bottom">
                <el-button circle size="small" @click="hideLine">
                  <el-icon><Hide /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="重置视角" placement="bottom">
                <el-button circle size="small" @click="resetView">
                  <el-icon><RefreshLeft /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="全屏" placement="bottom">
                <el-button circle size="small" @click="toggleFullscreen">
                  <el-icon><FullScreen /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
          </div>

          
          <!-- 模型信息 -->
          <div class="viewer-meta">
            <div>模型大小：{{ modelMeta.size }}</div>
            <div>创建时间：{{ modelMeta.modified }}</div>
            <div>类型：{{ modelMeta.type }}</div>
          </div>
          
          <!-- 操作按钮：下载 & 分享 -->
          <div class="viewer-actions">
            <el-button plain :icon="Download" @click="downloadModel">下载模型</el-button>
            <el-button plain :icon="Share" @click="shareModel">分享链接</el-button>
          </div>
        </el-col>
        <el-col :span="10" class="history-column">
          <div class="project-history">
            <div class="panel-header">
              <h3>项目历史</h3>
              <el-input v-model="search" size="small" placeholder="搜索项目" clearable />
            </div>

            <div class="project-list">
              <div v-for="proj in filteredProjects" :key="proj.id" class="project-card">
                <img :src="proj.thumb" class="thumb" />
                <div class="meta">
                  <div class="title">{{ proj.name }}</div>
                  <div class="desc">{{ proj.duration }} · {{ proj.type }}</div>
                  <div class="size">模型大小: {{ proj.size }}</div>
                </div>
                <div class="actions actions-inline">
                  <el-button type="text" @click="viewProject(proj)" title="查看">
                    <el-icon><View /></el-icon>
                  </el-button>
                  <el-button type="text" @click="downloadProject(proj)" title="下载">
                    <el-icon><Download /></el-icon>
                  </el-button>
                  <el-button type="text" @click="deleteProject(proj)" title="删除" style="color:#f56c6c">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Hide, View, Download, Delete, RefreshLeft, FullScreen, Share } from '@element-plus/icons-vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js'
import { onMounted, onBeforeUnmount } from 'vue'


const search = ref('')
// 3D 视图容器与控制方法
const viewerAreaRef = ref(null)
const isHide = ref(false)
let cameraRef = null
let controlsRef = null
let rendererRef = null
let modelRootRef = null
let initialCamPosRef = null
let initialTargetRef = null

// 模型信息
const modelMeta = ref({ size: '-', modified: '-', type: '-' })
// 模型路径（与加载一致）
const MODEL_URL = '/model/adult_tooth_morphology.glb'

// 提供给模板的操作：重置与全屏
function resetView() {
  if (controlsRef && typeof controlsRef.reset === 'function') {
    controlsRef.reset()
    cameraRef && cameraRef.updateProjectionMatrix()
    return
  }
  if (cameraRef && controlsRef && initialCamPosRef && initialTargetRef) {
    cameraRef.position.copy(initialCamPosRef)
    controlsRef.target.copy(initialTargetRef)
    cameraRef.updateProjectionMatrix()
    controlsRef.update()
    return
  }
  // 如果初始位姿未记录，则重新fit
  if (cameraRef && modelRootRef) fitToObject(cameraRef, modelRootRef, 1.25, controlsRef)
}

async function toggleFullscreen() {
  const el = viewerAreaRef.value
  if (!el) return
  if (document.fullscreenElement) {
    await document.exitFullscreen()
  } else {
    await el.requestFullscreen()
  }
}


function showLine() {
  const el = viewerAreaRef.value
  if (el) el.classList.remove('no-grid')
  isHide.value = false
}

function hideLine() {
  const el = viewerAreaRef.value
  if (el) el.classList.add('no-grid')
  isHide.value = true
}

// 获取模型元信息（大小/创建时间/类型）
async function fetchModelMeta(url) {
  try {
    const res = await fetch(url, { method: 'HEAD' })
    if (res.ok) {
      const len = res.headers.get('content-length')
      const lm = res.headers.get('last-modified')
      modelMeta.value.size = len ? formatBytes(Number(len)) : '-'
      modelMeta.value.modified = lm ? new Date(lm).toLocaleString() : '-'
    }
  } catch (_) { /* ignore */ }
  const ext = url.split('?')[0].split('#')[0].split('.').pop()?.toLowerCase()
  modelMeta.value.type = ext ? (ext === 'glb' ? 'GLB 模型' : `${ext.toUpperCase()} 模型`) : '-'
}

function formatBytes(bytes) {
  if (!Number.isFinite(bytes) || bytes <= 0) return '-'
  const units = ['B','KB','MB','GB','TB']
  const i = Math.min(Math.floor(Math.log(bytes)/Math.log(1024)), units.length-1)
  const v = bytes / Math.pow(1024, i)
  return `${v.toFixed(v>=100?0: v>=10?1:2)} ${units[i]}`
}

// 下载与分享
function downloadModel() {
  
}

async function shareModel() {
  
}

// 让相机完整框选对象
function fitToObject(cam, object, offset = 1.25, ctrls) {
  const box = new THREE.Box3().setFromObject(object)
  const size = box.getSize(new THREE.Vector3())
  const center = box.getCenter(new THREE.Vector3())
  ctrls && ctrls.target.copy(center)
  const maxSize = Math.max(size.x, size.y, size.z)
  const fitHeight = maxSize / (2 * Math.tan(THREE.MathUtils.degToRad(cam.fov / 2)))
  const fitWidth = fitHeight / cam.aspect
  const distance = offset * Math.max(fitHeight, fitWidth)
  const dir = new THREE.Vector3().subVectors(cam.position, center).normalize()
  cam.position.copy(dir.multiplyScalar(distance).add(center))
  cam.near = distance / 100
  cam.far = distance * 100
  cam.updateProjectionMatrix()
  ctrls && ctrls.update()
}

const teethThumb = new URL('../image/teeth.JPG', import.meta.url).href
const projects = ref([
  { id: 'p1', name: '患者张三 - 全口重建', files: 24, size: '15.2 MB', status: '已完成', thumb: teethThumb, duration: '45分钟', type: '全口重建', date: '2024-01-15' },
  { id: 'p2', name: '患者李四 - 单牙修复', files: 8, size: '3.8 MB', status: '已完成', thumb: teethThumb, duration: '12分钟', type: '单牙修复', date: '2024-01-14' },
  { id: 'p3', name: '患者王五 - 局部重建', files: 16, size: '9.0 MB', status: '处理中', thumb: teethThumb, duration: '8分钟', type: '局部重建', date: '2024-01-13' },
  { id: 'p4', name: '患者王五 - 局部重建', files: 16, size: '9.0 MB', status: '处理中', thumb: teethThumb, duration: '8分钟', type: '局部重建', date: '2024-01-13' },
])

const filteredProjects = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return projects.value
  return projects.value.filter(p => p.name.toLowerCase().includes(q))
})

function viewProject(p) { ElMessage.info(`查看项目: ${p.name}`) }
function downloadProject(p) { ElMessage.success(`下载: ${p.name}`) }
function deleteProject(p) { ElMessage.warning(`删除: ${p.name}`) }
function toggleQuality() { ElMessage.info('切换质量（示例）') }


onMounted(() => {
  const container = document.getElementById('three-viewer')
  const width = container.clientWidth
  const height = container.clientHeight

  const scene = new THREE.Scene()
  const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000)
  camera.position.set(-50, 100, -80)

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  // 提升观感：色彩空间、色调映射、曝光、阴影
  renderer.outputColorSpace = THREE.SRGBColorSpace
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.1
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap
  container.appendChild(renderer.domElement)

  // 暴露引用供按钮使用
  cameraRef = camera
  rendererRef = renderer

  // 基于房间环境的环境贴图，增强材质质感
  const pmrem = new THREE.PMREMGenerator(renderer)
  const envScene = new RoomEnvironment(renderer)
  const envMap = pmrem.fromScene(envScene, 0.04).texture
  scene.environment = envMap
  scene.background = null

  // 三点布光 + 半球光
  const hemi = new THREE.HemisphereLight(0xffffff, 0x404040, 0.35)
  scene.add(hemi)

  const keyLight = new THREE.DirectionalLight(0xffffff, 1.1)
  keyLight.position.set(60, 80, 60)
  keyLight.castShadow = true
  keyLight.shadow.mapSize.set(1024, 1024)
  scene.add(keyLight)

  const fillLight = new THREE.DirectionalLight(0xffffff, 0.5)
  fillLight.position.set(-60, 30, 40)
  scene.add(fillLight)

  const rimLight = new THREE.DirectionalLight(0xffffff, 0.6)
  rimLight.position.set(0, 60, -60)
  scene.add(rimLight)

  // 轨道控制器：左键旋转、滚轮缩放、右键平移（可关闭平移）
  const controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.enablePan = false
  controls.rotateSpeed = 0.9
  controls.zoomSpeed = 0.8
  controls.minDistance = 10
  controls.maxDistance = 500
  controlsRef = controls

  // 拉取模型元信息
  fetchModelMeta(MODEL_URL)

  const loader = new GLTFLoader()
  loader.load(MODEL_URL, (gltf) => {
    const root = gltf.scene
    modelRootRef = root

    // 阴影与环境贴图强度
    root.traverse((obj) => {
      if (obj.isMesh) {
        obj.castShadow = true
        obj.receiveShadow = true
        if (obj.material && 'envMapIntensity' in obj.material) {
          obj.material.envMapIntensity = 1.1
        }
      }
    })

    scene.add(root)

  // 自适应相机到模型
  fitCameraToObject(camera, root, 1.25, controls)
  // 记录初始视角用于重置
  initialCamPosRef = camera.position.clone()
  initialTargetRef = controls.target.clone()
  // 也记录到 OrbitControls 的内部 state，使用 reset()
  controls.saveState()

    animate()
  })

  function animate() {
    requestAnimationFrame(animate)
    controls.update()
    renderer.render(scene, camera)
  }

  // 根据对象包围盒调整相机位置与控件目标，使模型完整显示
  function fitCameraToObject(cam, object, offset = 1.25, ctrls) {
    const box = new THREE.Box3().setFromObject(object)
    const size = box.getSize(new THREE.Vector3())
    const center = box.getCenter(new THREE.Vector3())

    // 重置控件目标到模型中心
    if (ctrls) {
      ctrls.target.copy(center)
    }

    const maxSize = Math.max(size.x, size.y, size.z)
    const fitHeightDistance = maxSize / (2 * Math.tan(THREE.MathUtils.degToRad(cam.fov / 2)))
    const fitWidthDistance = fitHeightDistance / cam.aspect
    const distance = offset * Math.max(fitHeightDistance, fitWidthDistance)

    const direction = new THREE.Vector3()
      .subVectors(cam.position, center)
      .normalize()

    cam.position.copy(direction.multiplyScalar(distance).add(center))
    cam.near = distance / 100
    cam.far = distance * 100
    cam.updateProjectionMatrix()
    ctrls && ctrls.update()
  }

  // 自适应窗口尺寸变化
  function onResize() {
    const w = container.clientWidth
    const h = container.clientHeight
    camera.aspect = w / h
    camera.updateProjectionMatrix()
    renderer.setSize(w, h)
  }
  window.addEventListener('resize', onResize)
  const onFullscreenChange = () => onResize()
  document.addEventListener('fullscreenchange', onFullscreenChange)

  // 资源释放
  onBeforeUnmount(() => {
    renderer.dispose()
    controls.dispose()
    window.removeEventListener('resize', onResize)
    document.removeEventListener('fullscreenchange', onFullscreenChange)
    container.innerHTML = ''
    pmrem.dispose()
  })
})
</script>

<style scoped>
.model-check-root {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  
}
.model-check-card {
  width: 100%;
  background: #fff;
  border-radius: 6px;
  padding: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
  margin-bottom: 12px;
  margin-left: 50px;
}
.model-check-layout { display:flex; gap:24px; align-items:flex-start; }

.viewer-column { flex: 1 1 0; min-width:0; }
.viewer-header { display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:12px }
.viewer-header h3 { margin: 0; }
.viewer-area {
  height:420px;
  border-radius:8px;
  /* 最底层网格背景 */
  background-color:#f7f9fc;
  background-image:
    /* 细网格，每20px */
    linear-gradient(#e0e6ee 1px, transparent 1px),
    linear-gradient(90deg, #e0e6ee 1px, transparent 1px),
    /* 粗网格，每100px */
    linear-gradient(#c9d2e0 1px, transparent 1px),
    linear-gradient(90deg, #c9d2e0 1px, transparent 1px);
  background-size: 20px 20px, 20px 20px, 100px 100px, 100px 100px;
  display:flex; align-items:center; justify-content:center;
  border:1px dashed #eee;
  position:relative; overflow:hidden
}
.viewer-area.no-grid {
  /* 隐藏网格线背景 */
  background-image: none !important;
}
.viewer-toolbar { position:absolute; right:10px; top:10px; display:flex; gap:8px; z-index:3 }
.viewer-placeholder { color:#c8cbd0 }
.viewer-meta { display:flex; justify-content:space-between; margin-top:12px; color:#666; font-size: 13px; }

/* 让两个按钮与显示区域同宽，并各占一半 */
.viewer-actions { display:flex;  margin-top: 32px }
.viewer-actions .el-button {
  flex:1 1 0;
  height:40px;
  justify-content:center;
  color:#1f2937; /* 更深的文字 */
  font-weight:600;
}
.viewer-actions .el-button:hover { color:#111827; background-color:#f9fafb }

.history-column { width:420px; flex:0 0 420px }
.project-history .panel-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: nowrap;
}
.project-history .panel-header h3 {
  margin: 0;
  white-space: nowrap;
  flex: 0 0 auto;
}
.project-history .panel-header .el-input {
  flex: 1 1 auto;
  min-width: 0;
}
.project-list { display:flex; flex-direction:column; gap:14px }
.project-card { display:flex; gap:12px; align-items:center; padding:12px; border-radius:8px; background:#fff; border:1px solid #edf2f7 }
.project-card .thumb { width:96px; height:96px; object-fit:cover; border-radius:6px }
.project-card .meta { flex:1; min-width:0 }
.project-card .title { font-weight:600; margin-bottom:6px }
.project-card .desc, .project-card .size { color:#8a8f98; font-size:13px }
.project-card .actions { display:flex; flex-direction:row; gap:8px; align-items:center; }
.actions-inline .el-button { padding:4px; }
.actions-inline .el-icon { font-size:16px; }
</style>
