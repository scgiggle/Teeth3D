import axios from 'axios'

export const http = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 30000,
})

// 请求拦截器：添加认证token
http.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：处理认证错误
http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 认证相关接口
export const login = (data) => http.post('/auth/login', data)
export const register = (data) => http.post('/auth/register', data)
export const getCurrentUser = () => http.get('/auth/me')

// 验证码相关接口
export const getCaptcha = () => http.get('/captcha')
export const verifyCaptcha = (data) => http.post('/captcha/verify', data)

// 图像分割相关接口
export const uploadImage = (formData) => http.post('/segmentation/upload', formData)
export const getSegmentation = (imageId) => http.get(`/segmentation/${imageId}`)
export const requestReconstruction = (imageId) => http.post(`/segmentation/${imageId}/reconstruct`)

// 3D模型相关接口
export const getModel = (modelId) => http.get(`/model/${modelId}`)

// 项目相关接口（根据 project_data / project_images 表预留）
export const createProject = (data) => http.post('/project', data)
export const uploadProjectImage = (projectId, formData) => http.post(`/project/${projectId}/images`, formData)
export const listProjects = (params) => http.get('/project', { params })
export const deleteProject = (projectId) => http.delete(`/project/${projectId}`)

// 进度查询接口
export const getProcessProgress = (taskId) => http.get(`/process/${taskId}/progress`)



