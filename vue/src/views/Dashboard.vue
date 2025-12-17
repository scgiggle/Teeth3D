<template>
  <div class="dashboard">
    <!-- 标签页导航 -->
    <el-tabs v-model="activeTab" class="dashboard-tabs">
      <el-tab-pane label="首页" name="overview">
        <HomePage />
      </el-tab-pane>

      <el-tab-pane label="重建" name="new-project">
        <div class="reconstruction-container">
          <div class="container-header">
            <h3>重建信息</h3>
          </div>
          
          <div class="container-body">
            <!-- 左侧:表单和上传 -->
            <div class="left-section">
              <el-form :model="projectForm" label-width="100px" style="margin-bottom: 20px;">
                <el-form-item label="患者编号">
                  <el-autocomplete
                    v-model="state"
                    :fetch-suggestions="querySearch"
                    popper-class="my-autocomplete"
                    placeholder="选择或输入患者编号"
                    @select="handleSelect"
                  >
                    <template #suffix>
                      <el-icon class="el-input__icon" @click="handleIconClick">
                        <edit />
                      </el-icon>
                    </template>
                    <template #default="{ item }">
                      <div class="value">{{ item.value }}</div>
                      <span class="link">{{ item.link }}</span>
                    </template>
                  </el-autocomplete>
                </el-form-item>
                <el-form-item label="重建类型">
                  <el-select v-model="projectForm.reconstructionType" placeholder="选择重建类型" style="width: 100%;">
                    <el-option label="全口重建" value="全口重建" />
                  </el-select>
                </el-form-item>
              </el-form>

              <ImageUploader ref="uploaderRef" @select="onSelect" @append="onAppend" />
              <div v-if="previewUrls.length" style="margin-top: 16px;">
                <h4 style="margin: 0 0 12px 0; font-size: 14px;">预览</h4>
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
                <el-button type="primary" :disabled="!canSubmit" @click="onCreateProject">提交重建</el-button>
                <el-button style="margin-left: 8px;" @click="onReupload">重新上传</el-button>
              </div>

              <div class="history" v-if="store.submissions.length" style="margin-top: 24px;">
                <div class="history-header">
                  <h4 v-if="selectedRows.length === 0" style="margin: 0; font-size: 14px;">最近提交</h4>
                  <div v-else class="batch-actions">
                    <span class="selected-count">已选择 {{ selectedRows.length }} 项</span>
                    <el-button type="primary" size="small" @click="batchShare">
                      <el-icon><Share /></el-icon> 分享
                    </el-button>
                    <el-button type="success" size="small" @click="batchDownload">
                      <el-icon><Download /></el-icon> 下载
                    </el-button>
                    <el-button type="danger" size="small" @click="batchDelete">
                      <el-icon><Delete /></el-icon> 删除
                    </el-button>
                  </div>
                </div>
                <el-table 
                  ref="tableRef"
                  :data="store.submissions" 
                  size="small" 
                  style="width: 100%" 
                  @row-click="handleRowClick" 
                  @selection-change="handleSelectionChange"
                  :row-class-name="tableRowClassName"
                >
                  <el-table-column type="selection" width="45" />
                  <el-table-column type="index" :index="indexMethod" label="序号" width="60" />
                  <el-table-column prop="patient_number" label="患者编号" width="120" />
                  <el-table-column prop="reconstruction_type" label="重建类型" width="120" />
                  <el-table-column prop="created_at" label="提交时间" width="200" />
                  <el-table-column label="完成时间" width="200">
                    <template #default="{ row }">
                      <span v-if="row.status === '重建中'" style="color: #E6A23C;">重建中</span>
                      <span v-else-if="row.finish_time">{{ row.finish_time }}</span>
                      <span v-else>-</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="60">
                    <template #default="{ row, $index }">
                      <el-button type="danger" link @click.stop="deleteProject(row, $index)" size="small">删除</el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>

            <!-- 右侧:3D模型展示 -->
            <div class="right-section">
              <div class="model-header">
                <div class="model-title">
                  <h4 style="margin: 0; font-size: 14px;">3D 模型预览</h4>
                  <span v-if="selectedPatient" style="color: #606266; font-size: 13px; margin-left: 12px;">
                    当前患者: {{ selectedPatient }}
                  </span>
                </div>
                <div v-if="selectedPatient" style="display: flex; gap: 8px; align-items: center;">
                  <el-radio-group v-model="selectedMeshType" size="small" @change="loadModel">
                    <el-radio-button label="upper">上牙列</el-radio-button>
                    <el-radio-button label="lower">下牙列</el-radio-button>
                  </el-radio-group>
                  <el-button size="small" @click="resetView">重置视图</el-button>
                </div>
              </div>
              <div class="model-canvas" id="model-canvas">
                <p v-if="!selectedPatient" style="text-align: center; color: #999; padding-top: 200px;">请选择一个项目查看 3D 模型</p>
              </div>
              <ModelActions 
                v-if="selectedPatient" 
                :project-id="selectedProjectId" 
                :patient-name="selectedPatient"
                :mesh-type="selectedMeshType"
              />
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- <el-tab-pane label="牙齿分割" name="segment">
        <Segmentation />
      </el-tab-pane> -->

      <el-tab-pane label="重建进度" name="progress">
        <ProcessProgress />
      </el-tab-pane>

      <el-tab-pane label="重建结果" name="models">
        <ModelCheck />
      </el-tab-pane>
      <el-tab-pane label="数据上传" name="updata">
        <images />
      </el-tab-pane>
    </el-tabs>

  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../stores/appStore'
import ImageUploader from '../components/ImageUploader.vue'
import { uploadImage, createProject, uploadProjectImage, listProjects, deleteProject as deleteProjectAPI, listPatients, downloadProjectModels } from '../api'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import Segmentation from '../components/Segmentation.vue'
import HomePage from '../components/HomePage.vue' 
import ProcessProgress from '../components/ProcessProgress.vue'
import ModelCheck from '../components/ModelCheck.vue'
import ModelActions from '../components/ModelActions.vue'
import images from '../components/images.vue'
import { Edit, Share, Download, Delete } from '@element-plus/icons-vue'
import * as THREE from 'three'
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'

interface LinkItem {
  value: string
  link: string
}

const router = useRouter()
const store = useAppStore()
const route = useRoute()

// 从 URL 查询参数获取当前标签页，默认为 overview
const activeTab = ref(route.query.tab || 'overview')

// 表格序号（从 1 开始）
const indexMethod = (index) => index + 1

const projectStatusMap = ref<Record<string, string>>({})

// 初始化时从数据库拉取最近项目，替换本地缓存
async function loadRecentProjects(showNotification = false) {
  try {
    const { data } = await listProjects({ limit: 20 })
    // 用后端数据覆盖本地 submissions
    store.submissions = (data.items || []).map(it => ({
      project_id: String(it.project_id),
      project_name: it.project_name,
      patient_number: it.patient_number || it.project_name,
      reconstruction_type: it.reconstruction_type,
      status: it.status,
      created_at: it.created_at,
      finish_time: it.finish_time,
    }))
    // 同步持久化
    localStorage.setItem('submissions', JSON.stringify(store.submissions))

    ;(data.items || []).forEach(it => {
      const id = String(it.project_id)
      const prevStatus = projectStatusMap.value[id]
      if (
        showNotification &&
        prevStatus &&
        prevStatus !== '已完成' &&
        it.status === '已完成'
      ) {
        ElNotification({
          title: '重建完成',
          message: `患者 ${it.patient_number || it.project_name} 的牙齿重建已完成`,
          type: 'success',
          duration: 5000,
          position: 'top-right',
        })
      }
      projectStatusMap.value[id] = it.status
    })
  } catch (e) {
    // 回退到本地缓存
    store.loadSubmissions()
  }
}
loadRecentProjects()
// 当前时间
const currentTime = ref('')
let timeInterval = null
let refreshInterval: number | null = null

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

// 监听标签页变化，更新 URL
watch(activeTab, (newTab) => {
  router.replace({ query: { ...route.query, tab: newTab } })
  
  // 当切换到重建页面时，确保 Three.js 场景已初始化
  if (newTab === 'new-project') {
    nextTick(() => {
      if (!scene || !renderer) {
        initThreeJS()
      }
    })
  }
})

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  
  // 只有在重建页面才初始化 Three.js
  if (activeTab.value === 'new-project') {
    nextTick(() => {
      initThreeJS()
    })
  }

  refreshInterval = window.setInterval(() => {
    loadRecentProjects(true)
  }, 30000)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
  disposeThreeJS()
})

// 3D模型相关状态
const selectedPatient = ref('')
const selectedProjectId = ref('')
const selectedMeshType = ref('upper')
let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let renderer: THREE.WebGLRenderer | null = null
let controls: OrbitControls | null = null
let currentModel: THREE.Group | null = null

// 初始化 Three.js 场景
function initThreeJS() {
  const container = document.getElementById('model-canvas')
  if (!container) return

  // 创建场景
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x1a1a1a)

  // 创建相机
  const width = container.clientWidth
  const height = container.clientHeight
  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000)
  camera.position.set(0, 50, 100)

  // 创建渲染器
  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(window.devicePixelRatio)
  container.innerHTML = ''
  container.appendChild(renderer.domElement)

  // 添加轨道控制器
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  
  // 启用所有交互功能
  controls.enableRotate = true    // 左键拖拽旋转
  controls.enableZoom = true      // 滚轮缩放
  controls.enablePan = true       // Shift + 左键平移
  
  // 设置鼠标按键 - 使用中键平移避免右键冲突
  controls.mouseButtons = {
    LEFT: THREE.MOUSE.ROTATE,     // 左键旋转
    MIDDLE: THREE.MOUSE.PAN,      // 中键平移
    RIGHT: null                    // 禁用右键，避免浏览器手势冲突
  }
  
  // Shift + 左键 = 平移
  controls.keys = {
    LEFT: 'ArrowLeft',
    UP: 'ArrowUp', 
    RIGHT: 'ArrowRight',
    DOWN: 'ArrowDown'
  }
  
  // 禁用画布上的右键菜单
  renderer.domElement.addEventListener('contextmenu', (e) => {
    e.preventDefault()
  })
  

  // 添加光源
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
  scene.add(ambientLight)

  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
  directionalLight.position.set(50, 50, 50)
  scene.add(directionalLight)

  const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.4)
  directionalLight2.position.set(-50, -50, -50)
  scene.add(directionalLight2)

  // 添加网格辅助线 - 暗色细网格
  // const gridHelper = new THREE.GridHelper(100, 20, 0x444444, 0x222222)
  // scene.add(gridHelper)

  // 启动动画循环
  animate()

  // 监听窗口大小变化
  window.addEventListener('resize', onWindowResize)
}

// 清理 Three.js 资源
function disposeThreeJS() {
  window.removeEventListener('resize', onWindowResize)
  
  if (currentModel && scene) {
    scene.remove(currentModel)
    currentModel.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        child.geometry.dispose()
        if (Array.isArray(child.material)) {
          child.material.forEach(m => m.dispose())
        } else {
          child.material.dispose()
        }
      }
    })
  }
  
  if (renderer) {
    renderer.dispose()
  }
  
  if (controls) {
    controls.dispose()
  }
}

// 重置视图到初始位置
function resetView() {
  if (!camera || !controls) return
  
  // 重置相机位置
  camera.position.set(0, 50, 100)
  camera.lookAt(0, 0, 0)
  
  // 重置控制器目标点
  controls.target.set(0, 0, 0)
  controls.update()
}

// 窗口大小调整
function onWindowResize() {
  const container = document.getElementById('model-canvas')
  if (!container || !camera || !renderer) return

  const width = container.clientWidth
  const height = container.clientHeight

  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
}

// 动画循环
function animate() {
  requestAnimationFrame(animate)
  
  if (controls) {
    controls.update()
  }
  
  if (scene && camera && renderer) {
    renderer.render(scene, camera)
  }
}

// 点击表格行加载3D模型
function handleRowClick(row) {
  // 检查项目状态
  if (row.status !== '已完成') {
    ElMessage.warning('重建未完成,请稍后再试')
    return
  }
  
  selectedProjectId.value = String(row.project_id)
  selectedPatient.value = row.patient_number || row.project_name
  loadModel()
}

// 表格多选相关
const tableRef = ref(null)
const selectedRows = ref([])

function handleSelectionChange(selection) {
  selectedRows.value = selection
}

// 批量分享
function batchShare() {
  if (selectedRows.value.length === 0) return
  
  // 生成所有选中项目的分享链接
  const shareLinks = selectedRows.value.map(row => {
    const patientName = row.patient_number || row.project_name
    const shareUrl = `${window.location.origin}${window.location.pathname}?tab=new-project&projectId=${row.project_id}`
    return `${patientName}: ${shareUrl}`
  }).join('\n\n')
  
  // 合并所有链接用于复制
  const allUrls = selectedRows.value.map(row => 
    `${window.location.origin}${window.location.pathname}?tab=new-project&projectId=${row.project_id}`
  ).join('\n')
  
  // 展示对话框让用户自己复制
  ElMessageBox.alert(
    `<div style="position: relative; word-break: break-all; padding: 10px 40px 10px 10px; background: #f5f7fa; border-radius: 4px; font-family: monospace; font-size: 13px; max-height: 300px; overflow-y: auto; white-space: pre-wrap;">
${shareLinks}
      <button onclick="navigator.clipboard.writeText(\`${allUrls}\`).then(() => { alert('所有链接已复制到剪贴板！'); })" style="position: absolute; top: 8px; right: 8px; width: 28px; height: 28px; padding: 0; background: white; border: 1px solid #dcdfe6; border-radius: 4px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.3s;" onmouseover="this.style.borderColor='#409eff'; this.style.color='#409eff';" onmouseout="this.style.borderColor='#dcdfe6'; this.style.color='#606266';" title="复制所有链接">
        <svg style="width: 14px; height: 14px; fill: currentColor;" viewBox="0 0 1024 1024"><path d="M768 832a64 64 0 0 1-64 64H192a64 64 0 0 1-64-64V320a64 64 0 0 1 64-64h512a64 64 0 0 1 64 64v512z m64-576v576a128 128 0 0 1-128 128H192a128 128 0 0 1-128-128V320a128 128 0 0 1 128-128h512a128 128 0 0 1 128 128z m64-64a64 64 0 0 1 64 64v512a32 32 0 0 1-64 0V256H384a32 32 0 0 1 0-64h512z"/></svg>
      </button>
    </div>`,
    `批量分享链接 (${selectedRows.value.length} 个项目)`,
    {
      confirmButtonText: '关闭',
      dangerouslyUseHTMLString: true,
    }
  )
}

// 批量下载
async function batchDownload() {
  if (selectedRows.value.length === 0) return
  const completedRows = selectedRows.value.filter(r => r.status === '已完成')
  if (completedRows.length === 0) {
    ElMessage.warning('选中的项目均未完成，无法下载')
    return
  }
  
  ElMessage.info(`正在准备下载 ${completedRows.length} 个项目的模型...`)
  
  // 逐个下载每个项目的模型
  for (const row of completedRows) {
    try {
      const response = await downloadProjectModels(row.project_id)
      
      // 获取文件名
      const patientName = row.patient_number || row.project_name
      const filename = `${patientName}_牙齿模型.zip`
      
      // 创建 Blob 并下载
      const blob = new Blob([response.data], { type: 'application/zip' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error(`下载项目 ${row.project_id} 失败:`, error)
    }
  }
  
  ElMessage.success(`已完成 ${completedRows.length} 个项目的模型下载`)
}

// 批量删除
async function batchDelete() {
  if (selectedRows.value.length === 0) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRows.value.length} 个项目吗？此操作不可撤销。`,
      '确认批量删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    // 逐个删除
    for (const row of selectedRows.value) {
      await deleteProjectAPI(row.project_id)
      const index = store.submissions.findIndex(s => s.project_id === row.project_id)
      if (index > -1) {
        store.submissions.splice(index, 1)
      }
    }
    
    // 同步持久化
    localStorage.setItem('submissions', JSON.stringify(store.submissions))
    
    // 清空选择
    selectedRows.value = []
    tableRef.value?.clearSelection()
    
    ElMessage.success('批量删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.response?.data?.detail || '未知错误'))
    }
  }
}

// 表格行样式
function tableRowClassName({ row }) {
  if (String(row.project_id) === selectedProjectId.value) {
    return 'selected-row'
  }
  return ''
}

// 加载3D模型
function loadModel() {
  if (!scene) return
  
  // 移除旧模型
  if (currentModel) {
    scene.remove(currentModel)
    currentModel.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        child.geometry.dispose()
        if (Array.isArray(child.material)) {
          child.material.forEach(m => m.dispose())
        } else {
          child.material.dispose()
        }
      }
    })
  }

  // 目前阶段：无论选择哪个患者，都从固定路径加载模型
  const meshType = selectedMeshType.value === 'upper' ? 'Upper' : 'Lower'
  const modelPath = `/3Dmersh/Pred_${meshType}_Mesh_Tag=TEE_01.obj`
  
  console.log(`加载模型: ${selectedPatient.value} - ${selectedMeshType.value === 'upper' ? '上牙列' : '下牙列'}`)
  console.log(`模型路径: ${modelPath}`)
  
  // 使用 OBJLoader 加载模型
  const loader = new OBJLoader()
  loader.load(
    modelPath,
    (object) => {
      // 设置材质
      object.traverse((child) => {
        if (child instanceof THREE.Mesh) {
          child.material = new THREE.MeshPhongMaterial({
            color: 0xf5e6d3,
            shininess: 30,
            specular: 0x444444
          })
        }
      })

      // 计算模型中心并调整位置
      const box = new THREE.Box3().setFromObject(object)
      const center = box.getCenter(new THREE.Vector3())
      object.position.sub(center)

      // 调整模型大小以适应视野
      const size = box.getSize(new THREE.Vector3())
      const maxDim = Math.max(size.x, size.y, size.z)
      const scale = 50 / maxDim
      object.scale.multiplyScalar(scale)

      currentModel = object
      scene!.add(object)

      console.log('模型加载成功')
    },
    (xhr) => {
      console.log((xhr.loaded / xhr.total * 100) + '% 已加载')
    },
    (error) => {
      console.error('模型加载失败:', error)
      ElMessage.error('模型加载失败，请检查文件路径')
    }
  )
}

// 上传相关状态
const uploaderRef = ref(null)
const files = ref([])
const previewUrls = ref([])
const items = computed(() => files.value.map((file, idx) => ({ file, url: previewUrls.value[idx] })))
// 患者编号
const state = ref('')
const projectForm = ref({ projectName: '', reconstructionType: '', description: '' })
const canSubmit = computed(() => !!state.value && !!projectForm.value.reconstructionType && files.value.length > 0)

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
  clearProjectForm()
  uploaderRef.value?.open()
}

function clearProjectForm() {
  // 清除项目表单
  projectForm.value = { projectName: '', reconstructionType: '', description: '' }
  state.value = ''
  // 清除文件列表
  files.value = []
  // 释放并清除预览URL
  previewUrls.value.forEach(u => URL.revokeObjectURL(u))
  previewUrls.value = []
  // 清除上传组件状态
  uploaderRef.value?.clear()
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
  // 校验图片数量是否为 5 张
  if (files.value.length !== 5) {
    ElMessage.warning(`图片数量不符合要求：必须上传 5 张图片才能提交（当前已上传 ${files.value.length} 张）`)
    return
  }
  try {
    const { data: p } = await createProject({
      project_name: state.value,
      reconstruction_type: projectForm.value.reconstructionType,
      description: '',
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
      project_name: p.project_name,
      patient_number: p.patient_number || state.value,
      reconstruction_type: projectForm.value.reconstructionType,
      status: p.status,
      created_at: p.created_at,
      finish_time: null,
    })
    await ElMessageBox.alert('重建项目已提交，请耐心等待，大约十分钟后可查看。', '提示', {
      confirmButtonText: '我知道了',
    })
    
    // 清除表单和文件状态
    clearProjectForm()
    
    // activeTab.value = 'segment'
  } catch (e) {
    ElMessage.error('提交失败：' + (e.response?.data?.detail || '未知错误'))
  }
}

// 删除项目
async function deleteProject(row, index) {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目"${row.project_name}"吗？此操作不可撤销。`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    // 调用后端删除接口
    await deleteProjectAPI(row.project_id)
    
    // 从本地状态中移除
    store.submissions.splice(index, 1)
    
    // 同步持久化
    localStorage.setItem('submissions', JSON.stringify(store.submissions))
    
    ElMessage.success('项目删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.response?.data?.detail || '未知错误'))
    }
  }
}

//患者编号输入或选择
const links = ref<LinkItem[]>([])

// 从后端加载患者列表
async function loadPatients() {
  try {
    const { data } = await listPatients()
    links.value = (data.items || []).map(patient => {
      const genderText = patient.gender === 'male' ? '男' : patient.gender === 'female' ? '女' : '其他'
      return {
        value: patient.patient_id,
        link: `${patient.name || '未知'}  ${genderText}  ${patient.age || '未知'}岁`
      }
    })
  } catch (e) {
    console.error('加载患者列表失败:', e)
    // 如果加载失败，使用默认数据
    links.value = loadAll()
  }
}

const querySearch = (queryString: string, cb) => {
  const results = queryString
    ? links.value.filter(createFilter(queryString))
    : links.value
  // call callback function to return suggestion objects
  cb(results)
}
const createFilter = (queryString: string) => {
  return (restaurant: LinkItem) => {
    return (
      restaurant.value.toLowerCase().indexOf(queryString.toLowerCase()) === 0
    )
  }
}
const loadAll = () => {
  return [
    { value: 'P10000', link: '张三    男    12岁' },
    { value: 'P10001', link: '李四  女  16岁' },
    { value: 'P10002', link: '王五  男  20岁' },
    { value: 'P10003', link: '赵六  女  24岁' },
    { value: 'P10004', link: '孙七  男  30岁' },
    { value: 'P10005', link: '周八  女  10岁' },
    { value: 'P10006', link: '吴九  男  7岁' },
    { value: 'P10007', link: '郑十  女  14岁' },

  ]
}
    
const handleSelect = (item: Record<string, any>) => {
  console.log(item)
}

const handleIconClick = (ev: Event) => {
  console.log(ev)
}

onMounted(() => {
  loadPatients()
})

</script>

<style scoped>
:root { --opacity: 1; }

.dashboard {
  padding: 16px;
  background: linear-gradient(135deg, #4a90e2, #667eea);
  min-height: calc(100vh - 76px);
  margin: 0 8px 8px 8px;
  border-radius: 12px;
}

.dashboard-tabs {
  background: white;
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  min-height: calc(100vh - 120px);
}

:deep(.el-tabs__header) {
  margin-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.el-tabs__nav-wrap::after) {
  display: none;
}

:deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 500;
  color: #8c8c8c;
  padding: 0 20px;
  height: 42px;
  line-height: 42px;
}

:deep(.el-tabs__item:hover) {
  color: #4a90e2;
}

:deep(.el-tabs__item.is-active) {
  color: #4a90e2;
  font-weight: 600;
}

:deep(.el-tabs__active-bar) {
  background: #4a90e2;
  height: 3px;
  border-radius: 2px;
}

/* 重建页面统一容器 */
.reconstruction-container {
  height: calc(100vh - 220px);
  display: flex;
  flex-direction: column;
}

.container-header {
  margin-bottom: 24px;
}

.container-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #262626;
}

.container-body {
  flex: 1;
  display: flex;
  gap: 24px;
  overflow: hidden;
}

.left-section {
  flex: 0 0 48%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.history {
  flex: 1;
  overflow-y: auto;
  margin-top: 20px;
}

.history-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  min-height: 32px;
}

.history h4 {
  color: #262626;
  font-weight: 600;
  font-size: 14px;
  margin: 0 0 12px 0;
}

.batch-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.selected-count {
  color: #4a90e2;
  font-size: 14px;
  font-weight: 500;
  margin-right: 8px;
}

.right-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.model-title {
  display: flex;
  align-items: center;
}

.model-title h4 {
  color: #262626;
  font-weight: 600;
  font-size: 14px;
  margin: 0;
}

.gallery { display:flex; flex-wrap:wrap; gap:12px; margin-top: 12px; }
.tile { width:120px }
.thumb { width:120px; height:80px; object-fit:cover; border:1px solid #e8e8e8; border-radius: 6px; }

.model-canvas {
  flex: 1;
  background: #1a1a2e;
  border-radius: 8px;
  min-height: 350px;
  position: relative;
  overflow: hidden;
}

/* 表格样式 */
:deep(.el-table) {
  --el-table-border-color: #f0f0f0;
  --el-table-header-bg-color: #fafafa;
  font-size: 13px;
}

:deep(.el-table th.el-table__cell) {
  background: #fafafa;
  color: #8c8c8c;
  font-weight: 500;
  font-size: 13px;
  padding: 10px 0;
}

:deep(.el-table td.el-table__cell) {
  padding: 12px 0;
  color: #595959;
}

:deep(.selected-row) {
  background-color: #e6f4ff !important;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover > td) {
  background-color: #fafafa !important;
}

/* 表单样式 */
:deep(.el-form-item__label) {
  color: #595959;
  font-weight: 500;
  font-size: 14px;
}

:deep(.el-input__wrapper),
:deep(.el-select__wrapper) {
  border-radius: 6px;
  box-shadow: 0 0 0 1px #d9d9d9 inset;
}

:deep(.el-input__wrapper:hover),
:deep(.el-select__wrapper:hover) {
  box-shadow: 0 0 0 1px #4a90e2 inset;
}

:deep(.el-input__wrapper.is-focus),
:deep(.el-select__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #4a90e2 inset;
}

/* 按钮样式 */
:deep(.el-button--primary) {
  background: #4a90e2;
  border-color: #4a90e2;
  border-radius: 6px;
  font-weight: 500;
}

:deep(.el-button--primary:hover) {
  background: #3a7bc8;
  border-color: #3a7bc8;
}

:deep(.el-button--default) {
  border-radius: 6px;
  border-color: #d9d9d9;
  color: #595959;
}

:deep(.el-button--default:hover) {
  color: #4a90e2;
  border-color: #4a90e2;
  background: white;
}

.meta { display:flex; justify-content:space-between; align-items:center; margin-top:4px }
.name { max-width:100px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color: #8c8c8c; font-size: 12px; }

/* Controls and panels */
.controls { margin-top:16px }
.tool-accordion { background:#fff; border-radius:8px; padding:8px; border:1px solid #f0f0f0 }
.tool-header { display:flex; gap:8px; align-items:center; padding:10px; cursor:pointer; background:#fff; color:#0f1724; border-radius:6px; border:1px solid #eef2f6 }
.tool-header .title { font-weight:700 }
.tool-header.active { background:#0f1724; color:#fff }
.tool-body { padding:8px }
.opacity-row { display:flex; align-items:center; gap:8px }
.opacity-display { min-width:48px; text-align:center; font-size:13px; color:#444 }
.full-btn { width:100%; box-sizing:border-box; text-align:center; margin:8px 0; border-radius:6px; padding:12px 0 }

.actions-row { display:flex; align-items:center; gap:8px }
.actions-left { display:flex; gap:8px }
.actions-right { margin-left:auto }

/* Transitions */
.fade-enter-active, .fade-leave-active { transition: opacity 300ms ease }
.fade-enter-from, .fade-leave-to { opacity: 0 }

@media (max-width: 720px) {
  .actions-row { flex-wrap:wrap }
  .actions-right { margin-left:0; width:100% }
}

.my-autocomplete li {
  line-height: 1.2;
  padding: 12px 7px;
  margin-bottom: 4px;
}
.my-autocomplete li .value {
  text-overflow: ellipsis;
  overflow: hidden;
  line-height: 1.2;
}
.my-autocomplete li .link {
  font-size: 12px;
  color: #b4b4b4;
  display: block;
  line-height: 1.2;
  margin-top: 0;
  margin-bottom: 10px;
}
.my-autocomplete li .highlighted .link {
  color: #ddd;
}
</style>




