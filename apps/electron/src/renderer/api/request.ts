import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

const service: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data

    // 先检查状态码
    if (res.status && res.status !== 200) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }

    // 处理 QuanDA 后端返回的数据格式
    // 后端返回格式：{ status: 200, res: {...} } 或 { status: 200, message: '...', res: null }
    // 我们需要返回 res 字段的内容，但要处理 null 的情况
    if (typeof res === 'object' && res !== null && 'res' in res) {
      // 如果 res �在，返回它（即使是 null）
      return res.res
    }

    // 如果没有 res 字段，直接返回整个响应
    return res
  },
  (error) => {
    console.error('响应错误:', error)
    const message = error.response?.data?.message || error.message || '网络错误'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default service
