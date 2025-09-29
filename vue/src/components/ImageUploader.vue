<template>
  <el-upload
    ref="uploadRef"
    drag
    :auto-upload="false"
    multiple
    :on-change="onFileChange"
    accept=".png,.jpg,.jpeg"
    :show-file-list="false"
  >
    <el-icon><UploadFilled /></el-icon>
    <div class="el-upload__text">拖拽文件到此，或<em>点击上传</em></div>
    <template #tip>
      <div class="el-upload__tip">仅支持 JPG/PNG，大小建议小于 10MB</div>
    </template>
  </el-upload>
</template>

<script setup>
import { UploadFilled } from '@element-plus/icons-vue'
import { ref } from 'vue'
const emit = defineEmits(['select', 'append'])
const uploadRef = ref(null)

function onFileChange(file, fileList) {
  // 逐个追加当前变更的文件
  if (file && file.raw) {
    emit('append', file.raw)
  } else {
    const raws = fileList.map(f => f.raw).filter(Boolean)
    emit('select', raws)
  }
}

function clear() {
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
  emit('select', [])
}

function open() {
  // 触发隐藏的 input 点击
  const root = uploadRef.value?.$el
  const input = root?.querySelector('input[type="file"]')
  if (input) input.click()
}

defineExpose({ clear, open })
</script>


