<template>
  <el-header height="60px" class="header">
    <div class="brand" @click="$router.push('/')">
      <div class="brand-logo">
        <img src="../image/System_icons.png" alt="logo" />
      </div>
      <div class="brand-text">
        <h1>口腔数字孪生平台</h1>
        <p>{{ currentTime }}</p>
      </div>
    </div>
    <el-space>
      <!-- <el-button link @click="$router.push('/')">首页</el-button>
      <el-button link @click="$router.push('/upload')">上传</el-button> -->
      <template v-if="user">
        <span class="username">{{ user.username }}</span>
        <el-button link type="danger" @click="onLogout">退出登录</el-button>
      </template>
      <template v-else-if="!isLoginPage">
        <el-button link @click="$router.push('/login')">登录</el-button>
      </template>
    </el-space>
  </el-header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/appStore'

const router = useRouter()
const store = useAppStore()
const user = computed(() => store.user)
const isLoginPage = computed(() => router.currentRoute.value.path === '/login')

// 当前时间
const currentTime = ref('')
let timer = null

function updateTime() {
  const now = new Date()
  const y = now.getFullYear()
  const m = now.getMonth() + 1
  const d = now.getDate()
  const h = now.getHours().toString().padStart(2, '0')
  const min = now.getMinutes().toString().padStart(2, '0')
  const s = now.getSeconds().toString().padStart(2, '0')
  currentTime.value = `${y}年${m}月${d}日 ${h}:${min}:${s}`
}

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

function onLogout() {
  store.setUser(null)
  router.push('/login')
}
</script>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px 0 0;
  margin: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  background: linear-gradient(135deg, #4a90e2, #667eea);
  border-radius: 12px;
}
.brand { 
  display: flex;
  align-items: center;
  gap: 14px;
  font-weight: 600; 
  cursor: pointer; 
  color: white;
  padding: 0 0 0 10px;
}
.brand-logo {
  display: flex;
  align-items: center;
  justify-content: center;
}
.brand-logo img {
  height: 46px;
  width: auto;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}
.brand-text h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  letter-spacing: 1px;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}
.brand-text p {
  margin: 4px 0 0 0;
  font-size: 12px;
  opacity: 0.85;
}
.username { 
  color: white; 
  margin-right: 6px;
  margin-bottom: 6px;
  font-weight: 500;
  display: flex;
  align-items: center;
}
</style>


