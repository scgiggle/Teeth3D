<template>
  <div class="container">
    <el-card>
      <h2>分割结果</h2>
      <el-row :gutter="16">
        <el-col :span="16">
          <SegmentationOverlay :image-url="imageUrl" :mask-opacity="opacity" />
        </el-col>
        <el-col :span="8">
          <div>
            <div>叠加透明度：{{ opacity.toFixed(2) }}</div>
            <el-slider v-model="opacity" :min="0" :max="1" :step="0.01" />
            <el-button type="primary" @click="onConfirm">确认并重建3D模型</el-button>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SegmentationOverlay from '../components/SegmentationOverlay.vue'
import { requestReconstruction } from '../api'

const route = useRoute()
const router = useRouter()
const imageId = computed(() => route.params.imageId)
const imageUrl = computed(() => `/api/segmentation/${imageId.value}/image`)
const opacity = ref(0.5)

async function onConfirm() {
  const { data } = await requestReconstruction(imageId.value)
  router.push(`/model/${data.modelId}`)
}
</script>

<style scoped>
.container { padding: 16px; }
</style>


