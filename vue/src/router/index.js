import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import UploadImage from '../views/UploadImage.vue'
import ModelViewer from '../views/ModelViewer.vue'
import SegmentationResult from '../views/SegmentationResult.vue'
import { useAppStore } from '../stores/appStore'

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

router.beforeEach((to) => {
  const token = localStorage.getItem('access_token')
  if (to.path !== '/login' && !token) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
})

export default router


