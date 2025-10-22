<template>
  <div class="container">
    <el-card>
      <h2>3D 模型查看</h2>
      <ThreeDModel :model-url="modelUrl" />
      <div style="margin-top: 12px;">
        <el-button @click="$router.push('/')">返回首页</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ThreeDModel from '../components/ModelCheck.vue'

const route = useRoute()
const modelUrl = computed(() => `/api/model/${route.params.modelId}`)
</script>

<style scoped>
.container { padding: 16px; }
</style>


