import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    user: null,
    uploadedImages: [],
    segmentationResults: {},
    models: {},
    submissions: [],
  }),
  actions: {
    // 初始化用户状态（从 localStorage 恢复）
    initUser() {
      const token = localStorage.getItem('access_token')
      if (token) {
        // 这里可以设置一个简单的用户对象，或者调用 API 获取用户信息
        this.user = { token }
      }
    },
    setUser(user) {
      this.user = user
    },
    addUploadedImage(image) {
      this.uploadedImages.push(image)
    },
    setSegmentationResult(imageId, result) {
      this.segmentationResults[imageId] = result
    },
    setModel(modelId, model) {
      this.models[modelId] = model
    },
    loadSubmissions() {
      try {
        const raw = localStorage.getItem('submissions')
        this.submissions = raw ? JSON.parse(raw) : []
      } catch {
        this.submissions = []
      }
    },
    addSubmission(submission) {
      if (!this.submissions) this.submissions = []
      this.submissions.unshift(submission)
      try {
        localStorage.setItem('submissions', JSON.stringify(this.submissions.slice(0, 50)))
      } catch {}
    },
  },
})


