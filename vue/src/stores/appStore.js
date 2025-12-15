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
      const username = localStorage.getItem('username')
      if (token && username) {
        this.user = { token, username }
      }
    },
    setUser(user) {
      this.user = user
      if (user) {
        // 保存到 localStorage
        if (user.token) localStorage.setItem('access_token', user.token)
        if (user.username) localStorage.setItem('username', user.username)
      } else {
        // 清除 localStorage
        localStorage.removeItem('access_token')
        localStorage.removeItem('username')
      }
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


