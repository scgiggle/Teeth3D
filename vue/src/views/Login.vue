<template>
  <div class="center">
    <el-card class="box">
      <h2>{{ isRegisterMode ? '注册' : '登录' }}</h2>
      <el-form :model="form" label-width="80px" @submit.prevent>
        <el-form-item label="用户名">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" v-if="isRegisterMode">
          <el-input v-model="form.confirmPassword" show-password />
        </el-form-item>
        <el-form-item label="邮箱" v-if="isRegisterMode">
          <el-input v-model="form.email" type="email" />
        </el-form-item>
        <el-form-item label="验证码">
          <div class="captcha-container">
            <el-input v-model="form.captcha" placeholder="请输入验证码" style="width: 150px;" />
            <div class="captcha-image" @click="refreshCaptcha">
              <img v-if="captchaImage" :src="captchaImage" alt="验证码" />
              <div v-else class="captcha-loading">加载中...</div>
            </div>
          </div>
        </el-form-item>
        <el-form-item>
          <div class="button-group">
            <el-button type="primary" @click="onLogin" v-if="!isRegisterMode">登录</el-button>
            <el-button @click="toggleMode" v-if="isRegisterMode">返回登录</el-button>
            <el-button @click="toggleMode" v-if="!isRegisterMode">注册</el-button>
            <el-button type="primary" @click="onRegister" v-if="isRegisterMode">注册</el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/appStore'
import { ElMessage } from 'element-plus'
import { register, login, getCaptcha } from '../api'

const router = useRouter()
const store = useAppStore()
const isRegisterMode = ref(false)
const form = reactive({ 
  username: '', 
  password: '', 
  confirmPassword: '', 
  email: '', 
  captcha: '' 
})
const captchaImage = ref('')
const captchaId = ref('')
const captchaLoading = ref(false)

// 获取验证码
async function loadCaptcha() {
  try {
    captchaLoading.value = true
    const { data } = await getCaptcha()
    captchaImage.value = data.image
    captchaId.value = data.captcha_id
  } catch (error) {
    ElMessage.error('获取验证码失败')
    console.error('Captcha error:', error)
  } finally {
    captchaLoading.value = false
  }
}

// 刷新验证码
function refreshCaptcha() {
  loadCaptcha()
}

// 切换登录/注册模式
function toggleMode() {
  isRegisterMode.value = !isRegisterMode.value
  // 清空表单
  form.username = ''
  form.password = ''
  form.confirmPassword = ''
  form.email = ''
  form.captcha = ''
  refreshCaptcha()
}

async function onLogin() {
  if (!form.captcha.trim()) {
    ElMessage.error('请输入验证码')
    return
  }
  
  try {
    // 调用登录接口
    const { data } = await login({
      username: form.username,
      password: form.password,
      captcha: form.captcha,
      captcha_id: captchaId.value
    })
    
    // 存储token
    localStorage.setItem('access_token', data.access_token)
    
    ElMessage.success('登录成功')
    store.setUser({ username: form.username })
    const redirect = router.currentRoute.value.query.redirect || '/'
    router.push(redirect)
  } catch (error) {
    ElMessage.error('登录失败：' + (error.response?.data?.detail || '未知错误'))
    refreshCaptcha()
    form.captcha = ''
  }
}

async function onRegister() {
  if (!form.captcha.trim()) {
    ElMessage.error('请输入验证码')
    return
  }
  
  // 前端验证
  if (!form.username.trim()) {
    ElMessage.error('请输入用户名')
    return
  }
  if (!form.password.trim()) {
    ElMessage.error('请输入密码')
    return
  }
  if (form.password !== form.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }
  if (!form.email.trim()) {
    ElMessage.error('请输入邮箱')
    return
  }
  
  try {
    // 调用注册接口
    const { data } = await register({
      username: form.username,
      password: form.password,
      email: form.email,
      captcha: form.captcha,
      captcha_id: captchaId.value
    })
    
    ElMessage.success('注册成功，请登录')
    // 切换到登录模式
    isRegisterMode.value = false
    form.username = ''
    form.password = ''
    form.confirmPassword = ''
    form.email = ''
    form.captcha = ''
    refreshCaptcha()
  } catch (error) {
    ElMessage.error('注册失败：' + (error.response?.data?.detail || '未知错误'))
    refreshCaptcha()
    form.captcha = ''
  }
}

onMounted(() => {
  loadCaptcha()
})
</script>

<style scoped>
.center { 
  display: flex; 
  justify-content: center; 
  align-items: center; 
  min-height: calc(100vh - 150px); /*调整登录表单高度*/
  padding: 24px;
  background-image: url('../images/background.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}
.box { 
  width: 400px; 
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.captcha-container {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.captcha-image {
  cursor: pointer;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
  height: 50px;
  width: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
}

.captcha-image:hover {
  border-color: #409eff;
}

.captcha-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.captcha-loading {
  color: #909399;
  font-size: 12px;
}

.button-group {
  display: flex;
  justify-content: space-between;
  width: 100%;
}
</style>


