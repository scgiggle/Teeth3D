import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import UploadImage from '../views/UploadImage.vue'
import ModelViewer from '../views/ModelViewer.vue'
import SegmentationResult from '../views/SegmentationResult.vue'
import { useAppStore } from '../stores/appStore'
import { getCurrentUser } from '../api'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: Login },
    { path: '/', name: 'dashboard', component: Dashboard },
    { path: '/upload', name: 'upload', component: UploadImage },
    { path: '/segmentation/:imageId', name: 'segmentation', component: SegmentationResult, props: true },
    { path: '/model/:modelId', name: 'model', component: ModelViewer, props: true },
    
  ],
})

router.beforeEach(async (to) => {
  const token = localStorage.getItem('access_token')
  
  // 如果访问登录页，直接放行
  if (to.path === '/login') {
    return true
  }
  
  // 如果没有 token，重定向到登录页
  if (!token) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  
  // 验证 token 是否有效
  try {
    await getCurrentUser()
    return true
  } catch (error) {
    // token 无效，清除并重定向到登录页
    localStorage.removeItem('access_token')
    return { path: '/login', query: { redirect: to.fullPath } }
  }
})

export default router


