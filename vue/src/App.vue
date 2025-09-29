<template>
  <el-config-provider>
    <Header />
    <router-view />
  </el-config-provider>
  
</template>

<script setup>
import Header from './components/Header.vue'
</script>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
}
</style>


