import axios from 'axios'
import store from '../store'
import { ElMessage } from 'element-plus'
import router from '../router'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 10000,
  withCredentials: true
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    const token = store.state.token
    if (token) {
      config.headers['Authorization'] = `Token ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => response,
  error => {
    console.error('响应错误:', error)
    
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // 未授权，清除token并跳转到登录页
          store.commit('CLEAR_AUTH')
          router.push('/login')
          ElMessage.error('登录已过期，请重新登录')
          break
        case 403:
          ElMessage.error('没有权限执行此操作')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误，请稍后重试')
          break
        default:
          ElMessage.error(error.response.data.message || '操作失败，请重试')
      }
    } else {
      ElMessage.error('网络错误，请检查您的网络连接')
    }
    
    return Promise.reject(error)
  }
)

// API端点
export const endpoints = {
  auth: {
    login: '/api/auth/login/',
    logout: '/api/auth/logout/',
    register: '/api/auth/register/'
  },
  users: {
    me: '/api/users/me/',
    list: '/api/users/',
    detail: id => `/api/users/${id}/`
  },
  surveys: {
    list: '/api/surveys/',
    detail: id => `/api/surveys/${id}/`,
    uploadMedia: id => `/api/surveys/${id}/upload_media/`
  },
  mediaItems: {
    list: '/api/media-items/',
    detail: id => `/api/media-items/${id}/`
  }
}

// API方法
export const authAPI = {
  login: credentials => api.post(endpoints.auth.login, credentials),
  logout: () => api.post(endpoints.auth.logout),
  register: data => api.post(endpoints.auth.register, data)
}

export const userAPI = {
  getCurrentUser: () => api.get(endpoints.users.me),
  getUsers: () => api.get(endpoints.users.list),
  getUser: id => api.get(endpoints.users.detail(id)),
  updateUser: (id, data) => api.put(endpoints.users.detail(id), data)
}

export const surveyAPI = {
  getSurveys: (params) => api.get(endpoints.surveys.list, { params }),
  getSurvey: id => api.get(endpoints.surveys.detail(id)),
  createSurvey: data => api.post(endpoints.surveys.list, data),
  updateSurvey: (id, data) => api.put(endpoints.surveys.detail(id), data),
  deleteSurvey: id => api.delete(endpoints.surveys.detail(id)),
  uploadMedia: (id, formData) => api.post(endpoints.surveys.uploadMedia(id), formData)
}

export const mediaAPI = {
  getMediaItems: (params) => api.get(endpoints.mediaItems.list, { params }),
  getMediaItem: id => api.get(endpoints.mediaItems.detail(id)),
  createMediaItem: data => api.post(endpoints.mediaItems.list, data),
  updateMediaItem: (id, data) => api.put(endpoints.mediaItems.detail(id), data),
  deleteMediaItem: id => api.delete(endpoints.mediaItems.detail(id))
}

export default api 