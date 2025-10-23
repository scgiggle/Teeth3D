<template>
  <div class="container">
    <el-card>
      <h2>处理进度111</h2>
      <ProcessProgress />
      <div style="margin-top: 12px;">
        <el-button @click="$router.push('/')">返回首页</el-button>
      </div>
    </el-card>
  </div>
</template>
<script setup>
import ProcessProgress from '@/components/ProcessProgress.vue';
</script>
<style scoped>

</style>