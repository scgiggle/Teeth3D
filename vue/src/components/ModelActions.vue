<template>
  <div class="model-actions">
    <button class="action-btn" @click="handleDownload">
      <el-icon><Download /></el-icon>
      下载模型
    </button>
    <button class="action-btn" @click="handleShare">
      <el-icon><Share /></el-icon>
      分享链接
    </button>
  </div>
</template>

<script setup lang="ts">
import { Download, Share } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface Props {
  projectId: string
  patientName: string
  meshType: 'upper' | 'lower'
}

const props = defineProps<Props>()

// 下载模型功能
function handleDownload() {
  const meshType = props.meshType === 'upper' ? 'Upper' : 'Lower'
  const modelPath = `/3Dmersh/Pred_${meshType}_Mesh_Tag=TEE_01.obj`
  const fileName = `${props.patientName}_${props.meshType === 'upper' ? '上牙列' : '下牙列'}.obj`
  
  // 创建一个隐藏的a标签来触发下载
  const link = document.createElement('a')
  link.href = modelPath
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  ElMessage.success('模型下载已开始')
}

// 分享链接功能
function handleShare() {
  const meshType = props.meshType
  // 生成分享链接（包含项目ID 和模型类型）
  const shareUrl = `${window.location.origin}${window.location.pathname}?tab=new-project&projectId=${props.projectId}&meshType=${meshType}`
  
  // 复制到剪贴板
  navigator.clipboard.writeText(shareUrl).then(() => {
    ElMessage.success('分享链接已复制到剪贴板')
  }).catch(() => {
    // 如果剪贴板 API 不可用，展示对话框
    ElMessageBox.alert(shareUrl, '分享链接', {
      confirmButtonText: '关闭',
    })
  })
}
</script>

<style scoped>
.model-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.action-btn {
  flex: 1;
  height: 40px;
  font-size: 14px;
  border: 1px solid #e0e0e0;
  background: white;
  color: #606266;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn:hover {
  background: #f5f7fa;
  border-color: #409eff;
  color: #409eff;
}

.action-btn .el-icon {
  font-size: 16px;
}
</style>
