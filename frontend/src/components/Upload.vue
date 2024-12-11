<template>
  <div class="upload-project">
    <!-- 步骤指示器 -->
    <el-steps :active="currentStep" finish-status="success" class="steps">
      <el-step title="项目信息"></el-step>
      <el-step title="资料上传"></el-step>
    </el-steps>

    <!-- 步骤1：项目基本信息 -->
    <div v-if="currentStep === 0" class="step-container">
      <h2>创建新项目</h2>
      <el-form :model="projectForm" label-width="120px" class="project-form">
        <el-form-item label="项目标题" required>
          <el-input v-model="projectForm.title" placeholder="例如：2024夏,林芝扎嘎乡"/>
        </el-form-item>
        <el-form-item label="纬度" required>
          <el-input-number v-model="projectForm.latitude" :precision="6"/>
        </el-form-item>
        <el-form-item label="经度" required>
          <el-input-number v-model="projectForm.longitude" :precision="6"/>
        </el-form-item>
        <el-form-item label="调查时间段" required>
          <el-date-picker
            v-model="projectForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="createProject">下一步</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 步骤2：资料上传 -->
    <div v-if="currentStep === 1" class="step-container">
      <div class="step-header">
        <h2>上传项目资料</h2>
        <div class="project-info">
          <span>当前项目：{{ projectForm.title }}</span>
        </div>
        <el-button @click="prevStep">返回上一步</el-button>
      </div>
      
      <div class="upload-grid">
        <!-- 风土人情和文物照片 -->
        <div class="upload-section">
          <div class="section-header">
            <el-icon><Picture /></el-icon>
            <h3>风土人情和文物照片</h3>
          </div>
          <el-upload
            :action="uploadUrl"
            :disabled="!projectForm.title"
            :headers="uploadHeaders"
            :data="{
              media_type: 'IMAGE',
              category: 'FOLKLORE'
            }"
            :http-request="customUpload"
            :before-upload="(file) => beforeUpload(file, 'IMAGE')"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            name="file"
            multiple
            list-type="picture-card"
            accept=".jpg,.jpeg,.png"
          >
            <template v-if="!projectForm.title">
              <el-icon><Warning /></el-icon>
              <div>请先创建项目</div>
            </template>
            <template v-else>
              <el-icon><Plus /></el-icon>
            </template>
          </el-upload>
          <div class="el-upload__tip">支持 jpg/png 格式图片</div>
        </div>

        <!-- 访谈记录 -->
        <div class="upload-section">
          <div class="section-header">
            <el-icon><Microphone /></el-icon>
            <h3>访谈记录</h3>
          </div>
          <el-upload
            :action="uploadUrl"
            :disabled="!projectForm.title"
            :headers="uploadHeaders"
            :data="{
              media_type: 'AUDIO',
              category: 'INTERVIEW'
            }"
            :http-request="customUpload"
            :before-upload="(file) => beforeUpload(file, 'AUDIO')"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            name="file"
            multiple
            accept=".mp3,.mp4"
          >
            <template v-if="!projectForm.title">
              <el-icon><Warning /></el-icon>
              <div>请先创建项目</div>
            </template>
            <template v-else>
              <el-button type="primary">
                <el-icon><Upload /></el-icon>
                <span>上传访谈</span>
              </el-button>
            </template>
          </el-upload>
          <div class="el-upload__tip">支持 mp3/mp4 格式文件</div>
        </div>

        <!-- 数字文献 -->
        <div class="upload-section">
          <div class="section-header">
            <el-icon><Document /></el-icon>
            <h3>数字文献</h3>
          </div>
          <el-upload
            :action="uploadUrl"
            :disabled="!projectForm.title"
            :headers="uploadHeaders"
            :data="{
              media_type: 'DOCUMENT',
              category: 'LITERATURE'
            }"
            :http-request="customUpload"
            :before-upload="(file) => beforeUpload(file, 'DOCUMENT')"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            name="file"
            multiple
            accept=".pdf"
          >
            <template v-if="!projectForm.title">
              <el-icon><Warning /></el-icon>
              <div>请��创建项目</div>
            </template>
            <template v-else>
              <el-button type="primary">
                <el-icon><Upload /></el-icon>
                <span>上传文献</span>
              </el-button>
            </template>
          </el-upload>
          <div class="el-upload__tip">支持 PDF 格式文件</div>
        </div>
      </div>

      <div class="step-footer">
        <el-button type="primary" @click="finishUpload">完成上传</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Picture, 
  Microphone, 
  Document, 
  Upload, 
  Plus, 
  Warning 
} from '@element-plus/icons-vue'
import axios from 'axios'
import { useStore } from 'vuex'

const store = useStore()
const currentStep = ref(0)

const projectForm = ref({
  title: '',
  latitude: null,
  longitude: null,
  dateRange: []
})

// 计算上传URL
const uploadUrl = computed(() => {
  return `/api/upload_media/`
})

// 上传请求头
const uploadHeaders = computed(() => ({
  'Authorization': `Token ${store.state.token}`
}))

// 创建项目
const createProject = async () => {
  if (!projectForm.value.title || !projectForm.value.latitude || 
      !projectForm.value.longitude || !projectForm.value.dateRange) {
    ElMessage.error('请填写所有必填项')
    return
  }

  try {
    const projectData = {
      name: projectForm.value.title,
      latitude: projectForm.value.latitude,
      longitude: projectForm.value.longitude,
      start_date: projectForm.value.dateRange[0].toISOString().split('T')[0],
      end_date: projectForm.value.dateRange[1].toISOString().split('T')[0]
    }
    
    const response = await axios({
      method: 'post',
      url: '/api/surveys/',
      data: projectData,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${store.state.token}`
      }
    })
    
    console.log('项目创建成功:', response.data)
    currentStep.value = 1
    ElMessage.success('项目创建成功，请上传资料')
  } catch (error) {
    console.error('项目创建失败:', error)
    ElMessage.error('创建项目失败')
  }
}

// 自定义上传方法
const customUpload = async (options) => {
  const { file, data } = options
  
  if (!projectForm.value.title) {
    ElMessage.error('请先创建项目')
    return
  }
  
  const formData = new FormData()
  formData.append('file_path', file)
  formData.append('title', file.name)
  formData.append('survey_name', projectForm.value.title)  // 使用项目名称关联
  formData.append('media_type', data.media_type)
  formData.append('category', data.category)
  formData.append('description', `Uploaded ${file.name}`)
  
  try {
    const response = await axios({
      method: 'post',
      url: '/api/media-items/',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Token ${store.state.token}`
      }
    })

    if (response.status === 200 || response.status === 201) {
      console.log('上传成功:', response.data)
      ElMessage.success('文件上传成功')
      options.onSuccess(response.data)
    } else {
      console.error('上传失败:', response.data)
      ElMessage.error('文件上传失败')
      options.onError(new Error('上传失败'))
    }
  } catch (error) {
    console.error('上传错误:', error.response?.data || error)
    ElMessage.error('文件上传失败')
    options.onError(error)
  }
}

// 文件上传前的处理
const beforeUpload = (file, mediaType) => {
  if (!projectForm.value.title) {
    ElMessage.error('请先创建项目')
    return false
  }

  if (!file.name) {
    ElMessage.error('文件必须有名称')
    return false
  }
  
  // 检查文件类型
  const allowedTypes = {
    'IMAGE': ['.jpg', '.jpeg', '.png'],
    'AUDIO': ['.mp3', '.mp4'],
    'DOCUMENT': ['.pdf']
  }
  
  const fileExt = '.' + file.name.split('.').pop().toLowerCase()
  if (!allowedTypes[mediaType].includes(fileExt)) {
    ElMessage.error(`不支持的文件类型，请上传${allowedTypes[mediaType].join('/')}格式文件`)
    return false
  }
  
  return true
}

// 上传成功处理
const handleUploadSuccess = (response, file) => {
  console.log('文件上传成功:', response)
}

// 上传失败处理
const handleUploadError = (error, file) => {
  console.error('文件上传失败:', error)
  const errorMessage = error.response?.data?.detail || error.message || '未知错误'
  ElMessage.error(`${file.name} 上传失败: ${errorMessage}`)
}

// 返回上一步
const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 完成上传
const finishUpload = () => {
  ElMessage.success('项目上传完成')
  currentStep.value = 0
  projectForm.value = {
    title: '',
    latitude: null,
    longitude: null,
    dateRange: []
  }
}

// 监听步骤变化
watch(currentStep, (newStep, oldStep) => {
  console.log('步骤变化:', oldStep, '->', newStep)
})
</script>

<style scoped>
.upload-project {
  padding: 20px;
}

.steps {
  margin-bottom: 40px;
}

.step-container {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
}

.project-form {
  max-width: 600px;
  margin: 0 auto;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.project-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 16px 0;
  color: #666;
}

.project-info span {
  font-size: 14px;
}

.upload-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.upload-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.section-header .el-icon {
  margin-right: 8px;
  font-size: 24px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.el-upload {
  position: relative;
}

.el-upload.is-disabled {
  cursor: not-allowed;
}

.el-upload.is-disabled .el-upload-dragger {
  background-color: #f5f7fa;
  border-color: #e4e7ed;
}

.el-upload__tip {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.step-footer {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

:deep(.el-upload--picture-card) {
  width: 148px;
  height: 148px;
  line-height: 148px;
}

h2 {
  margin-top: 0;
  margin-bottom: 24px;
  color: #333;
  font-size: 24px;
}
</style>
 