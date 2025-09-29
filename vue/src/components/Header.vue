<template>
  <el-header height="60px" class="header">
    <div class="brand" @click="$router.push('/')" >Welcome</div>
    <el-space>
      <!-- <el-button link @click="$router.push('/')">首页</el-button>
      <el-button link @click="$router.push('/upload')">上传</el-button> -->
      <template v-if="user">
        <span class="username">{{ user.username }}</span>
        <el-button link type="danger" @click="onLogout">退出登录</el-button>
      </template>
      <template v-else>
        <el-button link @click="$router.push('/login')">登录</el-button>
      </template>
    </el-space>
  </el-header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/appStore'

const router = useRouter()
const store = useAppStore()
const user = computed(() => store.user)

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
  padding: 0 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
.brand { font-weight: 600; cursor: pointer; }
.username { color: #606266; margin-right: 8px; }
</style>


