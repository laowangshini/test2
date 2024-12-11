<template>
  <div class="my-projects">
    <h2>我的项目</h2>
    
    <el-table :data="projects" style="width: 100%">
      <el-table-column prop="name" label="项目名称" />
      <el-table-column prop="start_date" label="开始日期" />
      <el-table-column prop="end_date" label="结束日期" />
      <el-table-column label="位置">
        <template #default="{ row }">
          <span>{{ row.latitude }}, {{ row.longitude }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280">
        <template #default="{ row }">
          <el-button @click="handleEdit(row)" type="primary" size="small">编辑</el-button>
          <el-button @click="handleViewFiles(row)" type="info" size="small">查看文件</el-button>
          <el-button @click="handleDelete(row)" type="danger" size="small">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 编辑项目对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑项目" width="80%" :fullscreen="true">
      <div class="edit-container">
        <!-- 左侧基本信息 -->
        <div class="basic-info">
          <h3>基本信息</h3>
          <el-form :model="editForm" label-width="120px">
            <el-form-item label="项目名称" required>
              <el-input v-model="editForm.name" />
            </el-form-item>
            <el-form-item label="纬度" required>
              <el-input-number v-model="editForm.latitude" :precision="6" />
            </el-form-item>
            <el-form-item label="经度" required>
              <el-input-number v-model="editForm.longitude" :precision="6" />
            </el-form-item>
            <el-form-item label="调查时间段" required>
              <el-date-picker
                v-model="editForm.dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
              />
            </el-form-item>
          </el-form>
        </div>

        <!-- 右侧文件管理 -->
        <div class="file-management">
          <h3>资料管理</h3>
          
          <!-- 文件分类标签页 -->
          <el-tabs v-model="activeTab">
            <el-tab-pane label="风土人情" name="FOLKLORE">
              <div class="upload-section">
                <el-upload
                  :action="uploadUrl"
                  :headers="uploadHeaders"
                  :data="{
                    media_type: 'IMAGE',
                    category: 'FOLKLORE',
                    survey_name: editForm.name
                  }"
                  :http-request="customUpload"
                  :before-upload="(file) => beforeUpload(file, 'IMAGE')"
                  :on-success="handleUploadSuccess"
                  :on-error="handleUploadError"
                  multiple
                  list-type="picture-card"
                  accept=".jpg,.jpeg,.png"
                >
                  <el-icon><Plus /></el-icon>
                </el-upload>
              </div>
              <div class="file-list">
                <div v-for="file in getFilesByCategory('FOLKLORE')" :key="file.id" class="file-item">
                  <img v-if="file.media_type === 'IMAGE'" :src="file.file_path" class="file-thumbnail">
                  <div class="file-info">
                    <span class="file-name">{{ file.title }}</span>
                    <el-button type="danger" size="small" @click="handleDeleteFile(file)">删除</el-button>
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="访谈记录" name="INTERVIEW">
              <div class="upload-section">
                <el-upload
                  :action="uploadUrl"
                  :headers="uploadHeaders"
                  :data="{
                    media_type: 'AUDIO',
                    category: 'INTERVIEW',
                    survey_name: editForm.name
                  }"
                  :http-request="customUpload"
                  :before-upload="(file) => beforeUpload(file, 'AUDIO')"
                  :on-success="handleUploadSuccess"
                  :on-error="handleUploadError"
                  multiple
                  accept=".mp3,.mp4"
                >
                  <el-button type="primary">
                    <el-icon><Upload /></el-icon>
                    <span>上传访谈</span>
                  </el-button>
                </el-upload>
              </div>
              <div class="file-list">
                <div v-for="file in getFilesByCategory('INTERVIEW')" :key="file.id" class="file-item">
                  <el-icon><Headset /></el-icon>
                  <div class="file-info">
                    <span class="file-name">{{ file.title }}</span>
                    <el-button type="danger" size="small" @click="handleDeleteFile(file)">删除</el-button>
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="文献资料" name="LITERATURE">
              <div class="upload-section">
                <el-upload
                  :action="uploadUrl"
                  :headers="uploadHeaders"
                  :data="{
                    media_type: 'DOCUMENT',
                    category: 'LITERATURE',
                    survey_name: editForm.name
                  }"
                  :http-request="customUpload"
                  :before-upload="(file) => beforeUpload(file, 'DOCUMENT')"
                  :on-success="handleUploadSuccess"
                  :on-error="handleUploadError"
                  multiple
                  accept=".pdf"
                >
                  <el-button type="primary">
                    <el-icon><Upload /></el-icon>
                    <span>上传文献</span>
                  </el-button>
                </el-upload>
              </div>
              <div class="file-list">
                <div v-for="file in getFilesByCategory('LITERATURE')" :key="file.id" class="file-item">
                  <el-icon><Document /></el-icon>
                  <div class="file-info">
                    <span class="file-name">{{ file.title }}</span>
                    <el-button type="danger" size="small" @click="handleDeleteFile(file)">删除</el-button>
                  </div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveEdit">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 查看文件对话框 -->
    <el-dialog v-model="filesDialogVisible" title="项目文件" width="80%" :fullscreen="true">
      <Square v-if="filesDialogVisible" :project="currentProject" />
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog v-model="deleteDialogVisible" title="确认删除" width="30%">
      <p>确定要删除项目"{{ deleteProject?.name }}"吗？此操作不可恢复。</p>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="confirmDelete">确定删除</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useStore } from 'vuex'
import { surveyAPI, mediaAPI } from '../utils/api'
import Square from './Square.vue'
import {
  Plus,
  Upload,
  Document,
  Headset
} from '@element-plus/icons-vue'

const store = useStore()
const projects = ref([])
const editDialogVisible = ref(false)
const filesDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const editForm = ref({})
const currentProject = ref(null)
const deleteProject = ref(null)
const activeTab = ref('FOLKLORE')

// 上传相关
const uploadUrl = computed(() => '/api/media-items/')
const uploadHeaders = computed(() => ({
  'Authorization': `Token ${store.state.token}`
}))

// 自定义上传方法
const customUpload = async (options) => {
  const { file, data } = options
  
  const formData = new FormData()
  formData.append('file_path', file)
  formData.append('title', file.name)
  formData.append('survey_name', editForm.value.name)
  formData.append('media_type', data.media_type)
  formData.append('category', data.category)
  formData.append('description', `Uploaded ${file.name}`)
  
  try {
    const response = await mediaAPI.createMediaItem(formData)
    options.onSuccess(response.data)
  } catch (error) {
    console.error('上传失败:', error)
    options.onError(error)
  }
}

// 获取我的项目列表
const fetchProjects = async () => {
  try {
    const response = await surveyAPI.getSurveys({ view_type: 'my' })
    projects.value = response.data
  } catch (error) {
    console.error('获取项目列表失败:', error)
    ElMessage.error('获取项目列表失败')
  }
}

// 编辑项目
const handleEdit = async (project) => {
  try {
    const response = await surveyAPI.getSurvey(project.id)
    editForm.value = {
      ...response.data,
      dateRange: [new Date(response.data.start_date), new Date(response.data.end_date)]
    }
    editDialogVisible.value = true
  } catch (error) {
    console.error('获取项目详情失败:', error)
    ElMessage.error('获取项目详情失败')
  }
}

// 查看文件
const handleViewFiles = (project) => {
  currentProject.value = project
  filesDialogVisible.value = true
}

// 删除项目
const handleDelete = (project) => {
  deleteProject.value = project
  deleteDialogVisible.value = true
}

// 确认删除
const confirmDelete = async () => {
  try {
    await surveyAPI.deleteSurvey(deleteProject.value.id)
    ElMessage.success('项目删除成功')
    deleteDialogVisible.value = false
    fetchProjects()
  } catch (error) {
    console.error('删除项目失败:', error)
    ElMessage.error('删除项目失败')
  }
}

// 保存编辑
const handleSaveEdit = async () => {
  try {
    const data = {
      ...editForm.value,
      start_date: editForm.value.dateRange[0].toISOString().split('T')[0],
      end_date: editForm.value.dateRange[1].toISOString().split('T')[0]
    }
    delete data.dateRange
    delete data.media_items

    await surveyAPI.updateSurvey(editForm.value.id, data)
    ElMessage.success('项目更新成功')
    editDialogVisible.value = false
    fetchProjects()
  } catch (error) {
    console.error('更新项目失败:', error)
    ElMessage.error('更新项目失败')
  }
}

// 文件上传前的处理
const beforeUpload = (file, mediaType) => {
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
const handleUploadSuccess = (response) => {
  console.log('文件上传成功:', response)
  ElMessage.success('文件上传成功')
  handleEdit(editForm.value)  // 重新加载项目详情以获取最新文件列表
}

// 上传失败处理
const handleUploadError = (error) => {
  console.error('文件上传失败:', error)
  ElMessage.error('文件上传失败')
}

// 删除文件
const handleDeleteFile = async (file) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文件"${file.title}"吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await mediaAPI.deleteMediaItem(file.id)
    ElMessage.success('文件删除成功')
    handleEdit(editForm.value)  // 重新加载项目详情以更新文件列表
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除文件失败:', error)
      ElMessage.error('删除文件失败')
    }
  }
}

// 按分类获取文件
const getFilesByCategory = (category) => {
  return editForm.value.media_items?.filter(file => {
    const fileCategory = getFileCategory(file.media_type)
    return fileCategory === category
  }) || []
}

// 获取文件分类
const getFileCategory = (mediaType) => {
  if (!mediaType) return 'LITERATURE'
  
  const type = mediaType.toUpperCase()
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
      return 'LITERATURE'
  }
}

// 在组件挂载时获取项目列表
onMounted(() => {
  fetchProjects()
})
</script>

<style scoped>
.my-projects {
  padding: 20px;
}

.edit-container {
  display: flex;
  gap: 24px;
  height: calc(100vh - 200px);
  overflow: hidden;
}

.basic-info {
  flex: 0 0 400px;
  overflow-y: auto;
  padding-right: 16px;
}

.file-management {
  flex: 1;
  overflow-y: auto;
  padding-right: 16px;
}

h3 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 18px;
  color: #333;
}

.upload-section {
  margin-bottom: 20px;
}

.file-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.file-item {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-thumbnail {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
}

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-name {
  font-size: 14px;
  color: #333;
}

.el-icon {
  font-size: 24px;
  color: #909399;
}

:deep(.el-dialog__body) {
  padding: 0;
}

:deep(.el-tabs__content) {
  padding: 20px;
}
</style>