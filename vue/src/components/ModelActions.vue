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
  
  // 展示对话框让用户自己复制
  ElMessageBox.alert(
    `<div style="position: relative; word-break: break-all; padding: 10px 40px 10px 10px; background: #f5f7fa; border-radius: 4px; font-family: monospace; font-size: 13px;">
      ${shareUrl}
      <button onclick="navigator.clipboard.writeText('${shareUrl}').then(() => { alert('链接已复制到剪贴板！'); })" style="position: absolute; top: 8px; right: 8px; width: 28px; height: 28px; padding: 0; background: white; border: 1px solid #dcdfe6; border-radius: 4px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.3s;" onmouseover="this.style.borderColor='#409eff'; this.style.color='#409eff';" onmouseout="this.style.borderColor='#dcdfe6'; this.style.color='#606266';" title="复制链接">
        <svg style="width: 14px; height: 14px; fill: currentColor;" viewBox="0 0 1024 1024"><path d="M768 832a64 64 0 0 1-64 64H192a64 64 0 0 1-64-64V320a64 64 0 0 1 64-64h512a64 64 0 0 1 64 64v512z m64-576v576a128 128 0 0 1-128 128H192a128 128 0 0 1-128-128V320a128 128 0 0 1 128-128h512a128 128 0 0 1 128 128z m64-64a64 64 0 0 1 64 64v512a32 32 0 0 1-64 0V256H384a32 32 0 0 1 0-64h512z"/></svg>
      </button>
    </div>`,
    '分享链接',
    {
      confirmButtonText: '关闭',
      dangerouslyUseHTMLString: true,
    }
  )
}
</script>

<style scoped>
.model-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  padding-top: 12px;
  flex-shrink: 0;
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
