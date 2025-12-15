<template>
  <div class="center">
    <div class="login-box">
      <div class="login-header">
        <h1>{{ isRegisterMode ? '注册' : '登录' }}</h1>
        <p>{{ isRegisterMode ? '创建账号以继续' : '请登录以继续' }}</p>
      </div>
      
      <div class="login-form">
        <div class="input-group">
          <input 
            type="text" 
            v-model="form.username" 
            placeholder="用户名"
            class="login-input"
          />
        </div>
        
        <div class="input-group">
          <input 
            :type="showPassword ? 'text' : 'password'" 
            v-model="form.password" 
            placeholder="密码"
            class="login-input"
          />
        </div>
        
        <div class="input-group" v-if="isRegisterMode">
          <input 
            :type="showPassword ? 'text' : 'password'" 
            v-model="form.confirmPassword" 
            placeholder="确认密码"
            class="login-input"
          />
        </div>
        
        <div class="input-group" v-if="isRegisterMode">
          <input 
            type="email" 
            v-model="form.email" 
            placeholder="邮箱"
            class="login-input"
          />
        </div>
        
        <div class="captcha-row">
          <input 
            type="text" 
            v-model="form.captcha" 
            placeholder="验证码"
            class="login-input captcha-input"
          />
          <div class="captcha-image" @click="refreshCaptcha">
            <img v-if="captchaImage" :src="captchaImage" alt="验证码" />
            <div v-else class="captcha-loading">加载中...</div>
          </div>
        </div>
        
        <button 
          class="login-btn" 
          @click="isRegisterMode ? onRegister() : onLogin()"
        >
          {{ isRegisterMode ? '注册' : '登录' }}
        </button>
      </div>
      
      <div class="register-link">
        <span v-if="!isRegisterMode">没有账号？<a @click="toggleMode">立即注册</a></span>
        <span v-else>已有账号？<a @click="toggleMode">返回登录</a></span>
      </div>
    </div>
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
const showPassword = ref(false)
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
    
    ElMessage.success('登录成功')
    // 存储用户信息（包含 token 和 username）
    store.setUser({ 
      username: form.username,
      token: data.access_token 
    })
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
  min-height: calc(100vh - 76px);
  margin: 0 8px 8px 8px;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}
.center::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: url('../images/background.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.login-box {
  width: 380px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  padding: 40px 36px;
  position: relative;
  z-index: 1;
}

.login-header {
  margin-bottom: 32px;
}

.login-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 8px 0;
}

.login-header p {
  font-size: 14px;
  color: #8c8c8c;
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-group {
  position: relative;
}

.login-input {
  width: 100%;
  height: 50px;
  padding: 0 16px;
  border: 1.5px solid #e8e8e8;
  border-radius: 10px;
  font-size: 15px;
  color: #333;
  background: #fafafa;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.login-input:focus {
  outline: none;
  border-color: #4a6cf7;
  background: white;
  box-shadow: 0 0 0 3px rgba(74, 108, 247, 0.1);
}

.login-input::placeholder {
  color: #b8b8b8;
}

.captcha-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.captcha-input {
  flex: 1;
}

.captcha-image {
  cursor: pointer;
  border: 1.5px solid #e8e8e8;
  border-radius: 10px;
  overflow: hidden;
  height: 50px;
  width: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fafafa;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.captcha-image:hover {
  border-color: #4a6cf7;
}

.captcha-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.captcha-loading {
  color: #b8b8b8;
  font-size: 12px;
}

.login-btn {
  width: 100%;
  height: 50px;
  margin-top: 8px;
  background: linear-gradient(135deg, #4a6cf7, #6366f1);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.login-btn:hover {
  background: linear-gradient(135deg, #3b5bdb, #5558e3);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(74, 108, 247, 0.4);
}

.login-btn:active {
  transform: translateY(0);
}

.register-link {
  text-align: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
  color: #8c8c8c;
  font-size: 14px;
}

.register-link a {
  color: #4a6cf7;
  cursor: pointer;
  font-weight: 600;
  margin-left: 4px;
}

.register-link a:hover {
  text-decoration: underline;
}
</style>


