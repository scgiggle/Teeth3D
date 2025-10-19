<template>
  <div class="homepage-container">
    <div class="home-page">
      <el-row :gutter="20" class="top-stats">
        <el-col :span="6" v-for="(s, idx) in stats" :key="idx">
          <el-card class="stat-card">
            <div class="stat-badge" :style="{ background: '#fff' }">
              <div class="stat-icon">{{ s.icon }}</div>
              <div class="stat-subtitle">{{ s.subtitle }}</div>
            </div>
            <div class="stat-title">{{ s.title }}</div>
            <div class="stat-value">{{ s.value }}</div>
            <div class="stat-sub" :class="{ positive: s.positive, negative: !s.positive }">
              {{ s.change }}
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="content-row">
        <el-col :span="14">
          <div class="panel recent-tasks">
            <div class="panel-header">
              <h3>最近任务</h3>
            </div>

            <div v-for="task in recentTasks" :key="task.id" class="task-card">
              <div class="task-head">
                <div class="task-title">
                  <strong>{{ task.name }}</strong>
                  <div class="task-meta">{{ task.files }} 个文件 · 开始时间: {{ task.startAt }}</div>
                </div>
                <div class="task-actions">
                  <template v-if="task.progress >= 100">
                    <el-button size="mini" @click="viewTask(task)">查看</el-button>
                    <el-button size="mini" @click="downloadTask(task)">下载</el-button>
                  </template>
                </div>
              </div>

              <div class="task-stages">
                <div class="stages-bar-full">
                  <div class="stage-full" v-for="(ph, i) in PHASES" :key="i"
                    :class="{ 
                      done: task.progress >= 100 || i < taskStageIndex(task.progress),
                      active: task.progress < 100 && i === taskStageIndex(task.progress)
                    }">
                    <div class="stage-label">{{ ph }}</div>
                  </div>
                </div>
                <el-progress class="stages-progress" :percentage="task.progress" :status="task.progress === 100 ? 'success' : 'active'" />
              </div>

              <div class="task-tags">
                <el-tag v-for="(t, j) in task.tags" :key="j" type="success" size="small">{{ t }}</el-tag>
              </div>

              <div class="task-footer">
                <div>预计剩余：{{ task.eta }}</div>
                <div class="task-controls">
                  <template v-if="task.progress < 100">
                    <el-button size="mini" @click="togglePause(task)">{{ task.paused ? '恢复' : '暂停' }}</el-button>
                  </template>
                  <template v-else>
                    <span style="color:#999">已完成</span>
                  </template>
                </div>
              </div>
            </div>
          </div>
        </el-col>

        <el-col :span="10">
          <div class="panel project-history">
            <div class="panel-header">
              <h3>项目历史</h3>
              <el-input v-model="search" size="small" placeholder="搜索项目" clearable @clear="search = ''" >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
              </el-input>
            </div>

            <div v-for="proj in filteredProjects" :key="proj.id" class="proj-item">
              <el-card class="proj-card" shadow="never">
                <div class="proj-row">
                  <img :src="proj.thumb" class="proj-thumb" />
                  <div class="proj-body">
                    <div class="proj-title-row">
                      <div class="proj-title">{{ proj.name }}</div>
                      <el-tag size="mini" :type="proj.status === '已完成' ? 'success' : proj.status === '处理中' ? 'warning' : 'danger'">
                        {{ proj.status }}
                      </el-tag>
                    </div>

                    <div class="proj-meta-row">
                      <span class="proj-meta">{{ proj.files }} 文件</span>
                      <span class="proj-meta">· {{ proj.duration || '—' }}</span>
                      <span class="proj-meta">· {{ proj.type || '全口重建' }}</span>
                      <span class="proj-date">{{ proj.date || '' }}</span>
                    </div>

                    <div class="proj-bottom-row">
                      <div class="proj-size">模型大小: {{ proj.size }}</div>
                      <div class="proj-actions-inline">
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
              </el-card>
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
import { View, Download, Delete, Search } from '@element-plus/icons-vue'


const search = ref('')

const stats = ref([
  { title: '总重建数', value: '1,234', change: '+12%', positive: true, icon: '📈', subtitle: '同比', iconBg: '#e6f7ff' },
  { title: '处理中任务', value: '8', change: '实时', positive: true, icon: '⚙️', subtitle: '当前', iconBg: '#fff7e6' },
  { title: '成功率', value: '98.5%', change: '+0.5%', positive: true, icon: '✅', subtitle: '稳定', iconBg: '#f0fff4' },
  { title: '活跃用户', value: '156', change: '+8%', positive: true, icon: '👥', subtitle: '本周', iconBg: '#fff0f6' },
])

const recentTasks = ref([
  {
    id: 1,
    name: '患者张三 - 全口重建',
    files: 24,
    startAt: '14:30',
    progress: 65,
    eta: '15分钟',
    paused: false
  },
  {
    id: 2,
    name: '患者李四 - 单牙修复',
    files: 8,
    startAt: '13:45',
    progress: 100,
    eta: '已完成',
    paused: false
  }
])

// 全局阶段列表（6 个阶段）
const PHASES = ['图像预处理', '特征提取', '三维重建', '网格优化', '纹理映射', '后处理']

function taskStageIndex(progress) {
  const per = 100 / PHASES.length
  const idx = Math.floor(progress / per)
  return Math.min(PHASES.length - 1, Math.max(0, idx))
}

const teethThumb = new URL('../image/teeth.JPG', import.meta.url).href
const projects = ref([
  { id: 'p1', name: '患者张三 - 全口重建', files: 24, size: '15.2 MB', status: '已完成', thumb: teethThumb, duration: '45分钟', type: '全口重建', date: '2024-01-15' },
  { id: 'p2', name: '患者李四 - 单牙修复', files: 8, size: '3.8 MB', status: '已完成', thumb: teethThumb, duration: '12分钟', type: '单牙修复', date: '2024-01-14' },
  { id: 'p3', name: '患者王五 - 局部重建', files: 16, size: '9.0 MB', status: '处理中', thumb: teethThumb, duration: '8分钟', type: '局部重建', date: '2024-01-13' },
])

const filteredProjects = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return projects.value
  return projects.value.filter(p => p.name.toLowerCase().includes(q))
})

function refreshTasks() {
  ElMessage.info('刷新任务（示例）')
}

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

function viewProject(p) {
  ElMessage.info(`查看项目: ${p.name}`)
}

function downloadProject(p) {
  ElMessage.success(`下载: ${p.name}`)
}

function deleteProject(p) {
  ElMessage.warning(`删除: ${p.name}`)
  // projects.value = projects.value.filter(x => x.id !== p.id)
}
</script>

<style scoped>
.homepage-container {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  /* 更浅的阴影 */
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.home-page { width: 100%; }
.top-stats { margin-bottom: 18px; }
.stat-card { padding: 18px; text-align: left; }
.stat-card { padding: 18px; text-align: left; position:relative; }
.stat-badge { position:absolute; right:12px; top:12px; background:#fff; padding:6px 8px; border-radius:8px; display:flex; align-items:center; gap:8px; }
.stat-icon { width:28px; height:28px; display:flex; align-items:center; justify-content:center; font-size:14px; }
.stat-subtitle { color:#999; font-size:12px; }
.stat-title { color: #666; font-size: 13px; }
.stat-value { font-size: 22px; font-weight: 700; margin-top: 6px; }
.stat-sub { margin-top: 8px; font-size: 12px; }
.stat-sub.positive { color: #67c23a; }
.stat-sub.negative { color: #f56c6c; }

.panel { background: #fff; border-radius: 6px; padding: 12px; /* 更浅的面板阴影 */ box-shadow: 0 1px 3px rgba(0,0,0,0.03); margin-bottom: 12px; }
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 12px;
  flex-wrap: nowrap; /* 禁止换行，保持标题与控件在一行 */
}

/* 标题不换行，防止占用过多空间 */
.panel-header h3 {
  margin: 0;
  white-space: nowrap;
  flex: 0 0 auto;
}

/* 允许输入在可用空间内收缩（关键：min-width:0）防止因溢出导致换行 */
.panel-header .el-input {
  flex: 1 1 auto;
  min-width: 0;
}

/* 让项目历史的搜索框色调更灰、更低对比（合并，禁止渐变） */
.panel-header :deep(.el-input__inner) {
  background: #fafafa;
  border-color: #e6e6e6;
  color: #666;
  background-image: none !important; /* 禁止渐变 */
}
.panel-header :deep(.el-input__inner)::placeholder {
  color: #999;
}

/* 禁止输入框的任何渐变 */
.panel-header :deep(.el-input__inner) {
  background-image: none !important;
}
.recent-tasks .task-card {
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 12px;
  background: #fff;
  border: 1px solid #e8eef4;         /* 细线边框 */
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
  display: block;
}
.task-head { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px; }
.task-title { max-width: 70%; }
.task-meta { color:#999; font-size:12px; margin-top:4px; }
.task-tags { margin-top:8px; }
.task-footer { display:flex; justify-content:space-between; align-items:center; margin-top:8px; color:#666; font-size:13px; }

.task-stages { margin: 8px 0 12px 0; }
.stages-bar-full { display:flex; gap:0; margin-bottom:8px; }
.stage-full { 
  flex: 1; 
  text-align: center; 
  color: #999;               /* 未完成阶段使用灰色文字 */
  font-size: 13px; 
  padding: 8px 6px; 
  transition: all 0.15s ease; 
  border: 1px solid #eee;    /* 更浅的边框 */
  border-radius: 6px; 
  background: #f7f7f7;      /* 未完成阶段灰色背景 */
  box-sizing: border-box;
}
.stage-full.done { color:#2f855a; border-color: #d1f0dc; background: #f0fff4; }
.stage-full.active { color:#1f6fbf; border-color: #bfe0ff; background: #f2f9ff;}
.stages-progress { width:100%; }

/* 移除进度条填充的渐变，使用单色填充（覆盖 Element Plus 的默认样式） */
.stages-progress :deep(.el-progress-bar__inner) {
  background-image: none !important;
  /* 使用与 done 状态相近的绿色单色填充（可按需修改） */
  background: #7fc97f !important;
}

.proj-item { margin-bottom: 10px; }
.proj-card {
  padding: 8px;
  display: block;
  background: #fff;
  border-radius: 6px;
  box-shadow: none;
}
.proj-row { display:flex; gap:16px; align-items:center; }
.proj-thumb { width:96px; height:96px; object-fit:cover; border-radius:6px; }

.proj-body { flex:1; min-width:0; display:flex; flex-direction:column; gap:8px; }

.proj-title-row {
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:8px;
}
.proj-title { font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }

.proj-meta-row { display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
.proj-date { margin-left:auto; font-size:12px; }

.proj-meta-row, .proj-meta, .proj-date, .proj-size {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
  font-size: 12px;
  line-height: 1.4;
  color: #666;
}

.proj-bottom-row {
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
}

.proj-size { color:#666; font-size:13px; }

.proj-actions-inline { display:flex; gap:8px; align-items:center; }

/* 按钮图标更紧凑 */
.proj-actions-inline .el-button { padding:4px; }
.proj-actions-inline .el-icon { font-size:16px; }
</style>