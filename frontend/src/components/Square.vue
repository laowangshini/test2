<template>
  <div class="square">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-input
          v-model="searchQuery"
          placeholder="搜索资料..."
          class="search-input"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="filter-row">
      <el-col :span="24">
        <el-select v-model="sortType" placeholder="排序方式" class="filter-item" @change="handleFilter">
          <el-option label="最新上传" value="newest" />
          <el-option label="最多收藏" value="likes" />
        </el-select>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="project-list">
      <el-col :span="8" v-for="project in filteredProjects" :key="project.id">
        <el-card class="project-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="project-title">{{ project.name }}</span>
              <el-tag size="small" type="success">已审核</el-tag>
            </div>
          </template>
          
          <div class="project-info">
            <div class="info-item">
              <div class="info-label">
                <el-icon><User /></el-icon>
                <span>调查人</span>
              </div>
              <span class="info-content">{{ project.investigator?.display_name }}</span>
            </div>
            <div class="info-item">
              <div class="info-label">
                <el-icon><Calendar /></el-icon>
                <span>调查时间</span>
              </div>
              <span class="info-content">{{ formatDate(project.start_date) }} 至 {{ formatDate(project.end_date) }}</span>
            </div>
            <div class="location-info">
              <span>地点</span>
              <div class="coordinate-container">
                <span class="info-content">{{ project.longitude }}°E，{{ project.latitude }}°N</span>
                <a-map-component
                  :latitude="`${project.latitude}°N`"
                  :longitude="`${project.longitude}°E`"
                  class="location-map"
                />
              </div>
            </div>
          </div>
          
          <div class="actions">
            <el-button type="primary" size="small" @click="viewFiles(project)">
              查看资料
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 查看文件对话框 -->
    <el-dialog v-model="dialogVisible" title="项目资料" width="80%" :fullscreen="isFullscreen">
      <template #header="{ close, titleId, titleClass }">
        <div class="dialog-header">
          <h4 :id="titleId" :class="titleClass">项目资料</h4>
          <div class="dialog-actions">
            <el-button @click="toggleFullscreen">
              <el-icon>
                <FullScreen v-if="!isFullscreen" />
                <Minus v-else />
              </el-icon>
              {{ isFullscreen ? '退出全屏' : '全屏' }}
            </el-button>
            <el-button @click="close">
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
        </div>
      </template>

      <div class="files-container">
        <!-- 左侧分类列表 -->
        <div class="files-list">
          <div class="category-item" 
               :class="{ active: selectedCategory === 'LITERATURE' }"
               @click="selectCategory('LITERATURE')">
            <el-icon><Document /></el-icon>
            <span>文献资料</span>
          </div>
          <div class="category-item" 
               :class="{ active: selectedCategory === 'INTERVIEW' }"
               @click="selectCategory('INTERVIEW')">
            <el-icon><Microphone /></el-icon>
            <span>访谈记录</span>
          </div>
          <div class="category-item" 
               :class="{ active: selectedCategory === 'FOLKLORE' }"
               @click="selectCategory('FOLKLORE')">
            <el-icon><Picture /></el-icon>
            <span>风土人情</span>
          </div>
        </div>

        <!-- 文件预览区域 -->
        <div class="file-preview" v-if="currentFile">
          <div class="preview-header">
            <h3>{{ currentFile.title }}</h3>
            <div class="preview-actions">
              <el-button @click="prevFile" :disabled="!hasPrevFile">
                <el-icon><ArrowLeft /></el-icon>
                上一个
              </el-button>
              <el-button type="primary" @click="downloadFile(currentFile)">
                <el-icon><Download /></el-icon>
                下载
              </el-button>
              <el-button @click="nextFile" :disabled="!hasNextFile">
                下一个
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </div>

          <div class="preview-content">
            <!-- 图片预览 -->
            <div v-if="currentFile?.media_type === 'IMAGE'" class="image-preview">
              <el-image 
                :src="currentFile.file_url" 
                :preview-src-list="[currentFile.file_url]"
                fit="contain"
                :initial-index="0"
                @load="handleImageLoad"
                @error="handleImageError"
              >
                <template #placeholder>
                  <div class="image-placeholder">
                    <el-icon><Loading /></el-icon>
                    <p>加载中...</p>
                  </div>
                </template>
                <template #error>
                  <div class="image-error">
                    <el-icon><Picture /></el-icon>
                    <p>图片加载失败</p>
                    <p class="error-url">URL: {{ currentFile.file_url }}</p>
                  </div>
                </template>
              </el-image>
            </div>

            <!-- 音频预览 -->
            <div v-else-if="currentFile.media_type === 'AUDIO'" class="audio-preview">
              <audio 
                controls 
                :src="currentFile.file_url"
                @error="handleAudioError"
                style="width: 100%"
              >
                <p>您的浏览器不支持音频播放</p>
              </audio>
            </div>

            <!-- PDF预览 -->
            <div v-else-if="currentFile.media_type === 'DOCUMENT'" class="pdf-preview">
              <object
                :data="currentFile.file_url"
                type="application/pdf"
                width="100%"
                height="600px"
              >
                <p>PDF预览不可用，请下载查看</p>
              </object>
            </div>

            <!-- 调试信息 -->
            <div class="debug-info" v-if="showDebugInfo">
              <p>当前文件信息：</p>
              <pre>{{ JSON.stringify(currentFile, null, 2) }}</pre>
            </div>
          </div>
        </div>

        <!-- 未选择分类时的提示 -->
        <div v-else class="no-file-selected">
          <el-empty description="请选择要查看的资料分类" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Search, 
  User, 
  Calendar, 
  Location, 
  Document, 
  Picture, 
  VideoPlay,
  Headset,
  Files,
  Loading,
  PictureFilled,
  Microphone,
  FullScreen,
  Minus,
  Close,
  Download,
  ArrowLeft,
  ArrowRight
} from '@element-plus/icons-vue'
import { surveyAPI } from '@/utils/api'
import AMapComponent from '@/components/AMapComponent.vue'

const searchQuery = ref('')
const selectedFileType = ref('')
const sortType = ref('newest')
const projects = ref([])
const currentProject = ref(null)
const dialogVisible = ref(false)
const isFullscreen = ref(false)
const selectedFile = ref(null)
const currentFiles = ref([])
const showDebugInfo = ref(false)
const selectedCategory = ref(null)
const currentFileIndex = ref(0)

// 添加基础URL配置
const API_BASE_URL = 'http://127.0.0.1:8000'

// 过滤后的项目列表
const filteredProjects = computed(() => {
  return projects.value.filter(project => {
    const matchesSearch = !searchQuery.value || 
      project.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      project.investigator?.display_name.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    const matchesType = !selectedFileType.value || project.media_items?.some(item => item.media_type === selectedFileType.value)
    
    return matchesSearch && matchesType
  })
})

// 获取项目列表
const fetchProjects = async () => {
  try {
    const params = {
      view_type: 'public',
      search: searchQuery.value,
      file_type: selectedFileType.value,
      sort: sortType.value
    }
    const response = await surveyAPI.getSurveys(params)
    projects.value = response.data.map(item => ({
      ...item,
      id: item.id,
      title: item.name,
      files: item.media_items.map(media => ({
        id: media.id,
        title: media.title,
        file_type: media.media_type.toLowerCase(),
        file_url: media.file_path,
        description: media.description
      })),
      author: item.investigator?.display_name,
      created_at: item.created_at,
      likes_count: 0,
      comments_count: 0,
      files_count: item.media_items?.length || 0,
      status: 'approved',
      is_liked: false
    }))
  } catch (error) {
    console.error('获取项目列表失败:', error)
    ElMessage.error('获取项目列表失败')
  }
}

// 处理图片URL
const getFullImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  // 确保url是相对于media目录的路径
  const cleanUrl = url.replace(/^\/media\//, '').replace(/^media\//, '')
  return `${API_BASE_URL}/media/${cleanUrl}`
}

// 选择文件
const selectFile = (file) => {
  selectedFile.value = file
  if (!selectedCategory.value) {
    selectedCategory.value = file.category
  }
}

// 下载文件
const downloadFile = (file) => {
  if (!file?.file_url) {
    ElMessage.error('文件URL无效')
    return
  }
  window.open(file.file_url, '_blank')
}

// 切换全屏
const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
}

// 查看文件
const viewFiles = async (project) => {
  currentProject.value = project
  dialogVisible.value = true
  await fetchProjectFiles(project.id)
}

// 收藏/取消收藏
const toggleLike = async (project) => {
  try {
    // 由于后端没有点赞功能，这里只做前端模拟
    project.is_liked = !project.is_liked
    project.likes_count += project.is_liked ? 1 : -1
    ElMessage.success(project.is_liked ? '点赞成功' : '已取消点赞')
  } catch (error) {
    ElMessage.error('操作失败')
    console.error('Failed to toggle like:', error)
  }
}

// 处理搜索
const handleSearch = () => {
  fetchProjects()
}

// 处理筛选
const handleFilter = () => {
  fetchProjects()
}

// 辅助函数
const formatDate = (date) => {
  return new Date(date).toLocaleDateString('zh-CN')
}

const countFilesByType = (files, type) => {
  return files.filter(file => file.file_type === type).length
}

const getFileTypeText = (type) => {
  const texts = {
    image: '图片',
    audio: '音频',
    document: '文献'
  }
  return texts[type] || type
}

// 重试加载图片
const retryLoadImage = async () => {
  if (selectedFile.value) {
    try {
      const response = await fetch(selectedFile.value.file_url, { method: 'HEAD' })
      if (!response.ok) {
        ElMessage.error('文件不存在或无法访问')
        return
      }
      
      // 添加时间戳来避免缓存
      const timestamp = new Date().getTime()
      selectedFile.value = {
        ...selectedFile.value,
        file_url: `${selectedFile.value.file_url}${selectedFile.value.file_url.includes('?') ? '&' : '?'}t=${timestamp}`
      }
    } catch (error) {
      console.error('重试加载失败:', error)
      ElMessage.error('重试失败，请检查网络连接')
    }
  }
}

// 文件加载相关的处理函数
const handleImageLoad = () => {
  console.log('图片加载成功:', currentFile.value?.file_url)
}

const handleImageError = (error) => {
  console.error('图片加载失败:', error)
  console.log('图片URL:', currentFile.value?.file_url)
  ElMessage.error('图片加载失败，请检查网络连接或文件是否存在')
}

const handleAudioError = (error) => {
  console.error('音频加载失败:', error)
  console.log('音频URL:', currentFile.value?.file_url)
  ElMessage.error('音频加载失败，请检查网络连接或文件是否存在')
}

// 获取项目的文件列表
const fetchProjectFiles = async (projectId) => {
  try {
    console.log('Fetching files for project:', projectId)
    const response = await surveyAPI.getSurvey(projectId)
    console.log('Project response:', response.data)
    
    // 从 media_items 中获取文件列表
    const files = response.data.media_items || []
    console.log('Files from media_items:', files)
    
    currentFiles.value = files.map(file => {
      console.log('Processing file:', file)
      const category = getFileCategory(file.media_type)
      console.log(`File ${file.title} with media_type ${file.media_type} mapped to category ${category}`)
      return {
        ...file,
        category,
        file_url: getFullImageUrl(file.file_path)
      }
    })
    
    console.log('Processed files:', currentFiles.value)
    
    // 如果有文件但没有选择分类，自动选择第一个文件的分类
    if (currentFiles.value.length > 0 && !selectedCategory.value) {
      selectedCategory.value = currentFiles.value[0].category
      console.log('Auto selected category:', selectedCategory.value)
    }
  } catch (error) {
    console.error('获取文件列表失败:', error)
    ElMessage.error('获取文件列表失败')
  }
}

// 根据文件类型确定分类
const getFileCategory = (mediaType) => {
  if (!mediaType) {
    console.warn('Media type is undefined or null')
    return 'LITERATURE'
  }
  
  const type = mediaType.toUpperCase()
  console.log('Processing media type:', type)
  
  switch (type) {
    case 'DOCUMENT':
    case 'PDF':
      return 'LITERATURE'
    case 'AUDIO':
    case 'MP3':
      return 'INTERVIEW'
    case 'IMAGE':
    case 'PNG':
    case 'JPG':
    case 'JPEG':
      return 'FOLKLORE'
    default:
      console.warn(`Unknown media type: ${mediaType}, defaulting to LITERATURE`)
      return 'LITERATURE'
  }
}

// 当前分类的文件
const currentCategoryFiles = computed(() => {
  if (!selectedCategory.value) {
    console.log('No category selected')
    return []
  }
  
  const files = currentFiles.value.filter(file => {
    const matches = file.category === selectedCategory.value
    console.log(`File ${file.title}: category=${file.category}, selected=${selectedCategory.value}, matches=${matches}`)
    return matches
  })
  
  console.log('Filtered files for category:', selectedCategory.value, files)
  return files
})

// 当前显示的文件
const currentFile = computed(() => {
  if (!currentCategoryFiles.value.length) {
    console.log('No files in current category')
    return null
  }
  const file = currentCategoryFiles.value[currentFileIndex.value]
  console.log('Current file:', file)
  return file
})

// 选择分类
const selectCategory = (category) => {
  console.log('选择分类:', category)
  selectedCategory.value = category
  currentFileIndex.value = 0
  
  console.log('当前所有文件:', currentFiles.value)
  console.log('当前分类:', selectedCategory.value)
  console.log('当前分类文件列表:', currentCategoryFiles.value)
  if (currentFile.value) {
    console.log('当前显示的文件:', currentFile.value)
  }
}

// 文件导航相关方
const hasPrevFile = computed(() => {
  return currentFileIndex.value > 0
})

const hasNextFile = computed(() => {
  return currentFileIndex.value < currentCategoryFiles.value.length - 1
})

const prevFile = () => {
  if (hasPrevFile.value) {
    currentFileIndex.value--
  }
}

const nextFile = () => {
  if (hasNextFile.value) {
    currentFileIndex.value++
  }
}

// 在组件挂载时获取项目列表
onMounted(() => {
  fetchProjects()
})
</script>

<style lang="scss" scoped>
.square {
  padding: 20px;

  .search-input {
    margin-bottom: 20px;
  }

  .filter-row {
    margin-bottom: 20px;
    
    .filter-item {
      margin-right: 16px;
      width: 160px;
    }
  }

  .project-list {
    margin-bottom: 20px;
    
    .project-card {
      margin-bottom: 20px;
      
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        
        .project-title {
          font-weight: bold;
          flex: 1;
          margin-right: 12px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }
      
      .project-info {
        .info-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
          
          strong {
            font-weight: bold;
          }
        }
      }
      
      .actions {
        display: flex;
        justify-content: space-between;
        margin-top: 16px;
      }
    }
  }

  .files-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
  }

  .file-item {
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 15px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .file-type {
    font-weight: bold;
    color: #666;
  }

  .file-title {
    font-size: 16px;
  }

  .file-actions {
    display: flex;
    justify-content: flex-end;
  }
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;

  h4 {
    margin: 0;
    font-size: 18px;
  }

  .dialog-actions {
    display: flex;
    gap: 10px;
  }
}

.files-container {
  display: flex;
  gap: 20px;
  height: 100%;
}

.files-list {
  width: 200px;
  flex-shrink: 0;
  padding: 16px;
  border-right: 1px solid #eee;
}

.file-preview {
  flex: 1;
  padding: 16px;
  overflow: auto;
}

.category-item {
  display: flex;
  align-items: center;
  padding: 16px;
  margin-bottom: 8px;
  border-radius: 8px;
  background-color: #f5f7fa;
  cursor: pointer;
  transition: all 0.3s;
}

.category-item:hover {
  background-color: #ecf5ff;
  color: #409eff;
}

.category-item.active {
  background-color: #409eff;
  color: white;
}

.category-item .el-icon {
  font-size: 24px;
  margin-right: 12px;
}

.category-item span {
  font-size: 16px;
}

.preview-actions {
  display: flex;
  gap: 8px;
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;

  .el-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }

  p {
    margin: 0;
  }
}

.project-card {
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.project-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.project-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.project-info {
  padding: 10px 0;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  color: #666;
  line-height: 1.4;
}

.info-label {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
  font-size: 13px;
}

.info-label .el-icon {
  font-size: 14px;
}

.info-content {
  color: #606266;
  font-size: 13px;
  text-align: right;
  flex: 1;
  margin-left: 8px;
}

.stats {
  margin-top: 16px;
  display: flex;
  justify-content: space-around;
  color: #909399;
  border-top: 1px solid #f0f0f0;
  padding-top: 12px;
}

.stats span {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
}

.stats .el-icon {
  font-size: 16px;
}

.actions {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

.category-section {
  margin-bottom: 24px;
}

.category-section h3 {
  color: #333;
  font-size: 16px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.preview-actions {
  display: flex;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  margin-bottom: 4px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.file-item:hover {
  background-color: #f5f7fa;
}

.file-item.active {
  background-color: #ecf5ff;
  color: #409eff;
}

.file-item .el-icon {
  margin-right: 8px;
  font-size: 16px;
}

.file-info {
  flex: 1;
}

.file-title {
  font-size: 14px;
  line-height: 1.4;
}

.category-item {
  display: flex;
  align-items: center;
  padding: 16px;
  margin-bottom: 8px;
  border-radius: 8px;
  background-color: #f5f7fa;
  cursor: pointer;
  transition: all 0.3s;
}

.category-item:hover {
  background-color: #ecf5ff;
  color: #409eff;
}

.category-item .el-icon {
  font-size: 24px;
  margin-right: 12px;
}

.category-item span {
  font-size: 16px;
}

.category-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.category-header h3 {
  margin: 0 0 0 8px;
  font-size: 16px;
  color: #333;
}

.preview-actions {
  display: flex;
  gap: 8px;
}

.debug-info {
  margin-top: 20px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
  font-family: monospace;
}

.error-url {
  font-family: monospace;
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.image-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.image-placeholder, .image-error {
  text-align: center;
  padding: 20px;
}

.image-placeholder .el-icon, .image-error .el-icon {
  font-size: 48px;
  color: #909399;
  margin-bottom: 10px;
}

.audio-preview {
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.pdf-preview {
  background-color: #f8f9fa;
  border-radius: 4px;
  overflow: hidden;
}

.location-info {
  display: flex;
  align-items: flex-start;
  margin-bottom: 10px;
}

.coordinate-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.location-map {
  margin-top: 10px;
  width: 100%;
  max-width: 600px;
}
</style> 