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
        <el-form-item label="地点选择" required>
          <div class="location-section">
            <div class="location-input">
              <el-input
                v-model="searchKeyword"
                placeholder="输入地点名称搜索"
                :prefix-icon="Search"
                @input="handleSearchInput"
                class="search-input"
                clearable
              >
                <template #append>
                  <el-button @click="handleSearch" :loading="searching">搜索</el-button>
                </template>
              </el-input>
              
              <!-- 修改搜索结果显示 -->
              <div v-if="searchResults.length > 0" class="search-results">
                <div
                  v-for="(item, index) in searchResults"
                  :key="index"
                  class="search-result-item"
                  @click="selectLocation(item)"
                >
                  <span>{{ item.name }}</span>
                  <span class="address" v-if="item.district || item.address">
                    {{ item.district }}{{ item.address }}
                  </span>
                </div>
              </div>
            </div>

            <!-- 地图容器 -->
            <div ref="mapContainer" class="map-container"></div>

            <!-- 经纬度显示 -->
            <div class="coordinates-display">
              <el-input
                v-model="projectForm.latitude"
                placeholder="纬度"
                class="coordinate-input"
              >
                <template #prepend>纬度</template>
                <template #append>°N</template>
              </el-input>
              <el-input
                v-model="projectForm.longitude"
                placeholder="经度"
                class="coordinate-input"
              >
                <template #prepend>经度</template>
                <template #append>°E</template>
              </el-input>
            </div>
          </div>
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
              <div>请先创建项目</div>
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
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Picture, 
  Microphone, 
  Document, 
  Upload, 
  Plus, 
  Warning, 
  Search 
} from '@element-plus/icons-vue'
import axios from 'axios'
import { useStore } from 'vuex'

const store = useStore()
const currentStep = ref(0)
const mapContainer = ref(null)
const map = ref(null)
const marker = ref(null)
const searchKeyword = ref('')
const searchResults = ref([])
const searching = ref(false)
const autoComplete = ref(null)
const placeSearch = ref(null)
const mapLoaded = ref(false)

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

// 加载高德地图脚本
const loadAMapScript = () => {
  return new Promise((resolve, reject) => {
    if (window.AMap) {
      resolve(window.AMap)
      return
    }

    const script = document.createElement('script')
    script.type = 'text/javascript'
    script.async = true
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${process.env.VUE_APP_AMAP_KEY}&plugin=AMap.PlaceSearch,AMap.AutoComplete,AMap.Geocoder,AMap.ToolBar,AMap.Scale&callback=initAMap`

    // 添加全局回调函数
    window.initAMap = () => {
      resolve(window.AMap)
      delete window.initAMap
    }
    
    script.onerror = () => {
      reject(new Error('高德地图脚本加载失败'))
      delete window.initAMap
    }

    document.head.appendChild(script)
  })
}

// 初始化搜索服务
const initSearchServices = () => {
  try {
    if (!window.AMap) return

    // 初始化搜索服务
    placeSearch.value = new window.AMap.PlaceSearch({
      pageSize: 10,
      pageIndex: 1,
      extensions: 'all',
      autoFitView: false,
      citylimit: false
    })

    // 初始化自动完成服务
    autoComplete.value = new window.AMap.AutoComplete({
      city: '全国',
      citylimit: false,
      datatype: 'all',
      outPutDirAuto: true  // 输出城市区域
    })

    // 添加自动完成事件监听
    autoComplete.value.on('select', onAutoCompleteSelect)
  } catch (error) {
    console.error('搜索服务初始化失败:', error)
  }
}

// 添加自动完成选择事件处理
const onAutoCompleteSelect = (e) => {
  if (e.poi && e.poi.location) {
    const lnglat = new window.AMap.LngLat(e.poi.location.lng, e.poi.location.lat)
    updateMarkerAndCoordinates(lnglat)
    map.value.setZoomAndCenter(13, lnglat)
  }
}

// 初始化地图
const initMap = async () => {
  try {
    if (!mapContainer.value) return
    
    await loadAMapScript()
    
    // 设置地图配置项
    const mapOptions = {
      zoom: 4,
      center: [116.397428, 39.90923],
      resizeEnable: true,
      viewMode: '2D',
      features: ['bg', 'road', 'point'],
      mapStyle: 'amap://styles/normal',
      preloadMode: false,
      WebGLParams: {
        preserveDrawingBuffer: true,
        willReadFrequently: true  // 添加此配置
      }
    }

    map.value = new window.AMap.Map(mapContainer.value, mapOptions)

    // 等待地图加载完成
    await new Promise((resolve) => {
      map.value.on('complete', resolve)
    })

    // 初始化插件
    await new Promise((resolve) => {
      window.AMap.plugin([
        'AMap.PlaceSearch',
        'AMap.AutoComplete',
        'AMap.ToolBar',
        'AMap.Scale',
        'AMap.Geocoder'
      ], () => {
        initSearchServices()
        resolve()
      })
    })

    // 添加地图控件
    map.value.addControl(new window.AMap.ToolBar({
      position: 'RB'
    }))
    map.value.addControl(new window.AMap.Scale())

    // 添加地图点击事件
    map.value.on('click', handleMapClick)

    mapLoaded.value = true
  } catch (error) {
    console.error('地图初始化失败:', error)
    ElMessage.error('地图加载失败')
  }
}

// 更新标记和坐标
const updateMarkerAndCoordinates = (lnglat) => {
  if (!map.value || !window.AMap) return

  // 移除旧标记
  if (marker.value) {
    marker.value.setMap(null)
  }

  // 添加新标记
  marker.value = new window.AMap.Marker({
    position: lnglat,
    map: map.value
  })

  // 更新坐标显示
  projectForm.value.latitude = lnglat.getLat().toFixed(6)
  projectForm.value.longitude = lnglat.getLng().toFixed(6)

  // 将地图中心移动到选中位置
  map.value.setCenter(lnglat)
}

// 处理搜索输入
const handleSearchInput = (value) => {
  if (!value || !value.trim() || !autoComplete.value || !mapLoaded.value) {
    searchResults.value = []
    return
  }

  console.log('搜索关键词:', value)  // 添加调试日志

  autoComplete.value.search(value, (status, result) => {
    console.log('搜索状态:', status)  // 添加调试日志
    console.log('搜索结果:', result)  // 添加调试日志

    if (status === 'complete' && result.tips) {
      searchResults.value = result.tips
    } else {
      searchResults.value = []
    }
  })
}

// 处理搜索按钮点击
const handleSearch = async () => {
  if (!searchKeyword.value?.trim() || !placeSearch.value || !mapLoaded.value) {
    return
  }

  searching.value = true
  try {
    placeSearch.value.search(searchKeyword.value, (status, result) => {
      searching.value = false
      if (status === 'complete' && result.poiList?.pois?.length > 0) {
        const firstPoi = result.poiList.pois[0]
        const lnglat = new window.AMap.LngLat(firstPoi.location.lng, firstPoi.location.lat)
        updateMarkerAndCoordinates(lnglat)
        searchKeyword.value = firstPoi.name
        map.value.setZoomAndCenter(13, lnglat)
      } else {
        ElMessage.warning('未找到相关地点')
      }
    })
  } catch (error) {
    searching.value = false
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败')
  }
}

// 选择搜索结果
const selectLocation = (item) => {
  if (!item || !placeSearch.value || !mapLoaded.value) return
  
  placeSearch.value.search(item.name, (status, result) => {
    if (status === 'complete' && result.poiList?.pois?.length > 0) {
      const poi = result.poiList.pois[0]
      const lnglat = new window.AMap.LngLat(poi.location.lng, poi.location.lat)
      updateMarkerAndCoordinates(lnglat)
      searchKeyword.value = poi.name
      map.value.setZoomAndCenter(13, lnglat)
    }
  })
  
  searchResults.value = []
}

// 处理地图点击
const handleMapClick = (e) => {
  if (!mapLoaded.value) return
  const lnglat = e.lnglat
  updateMarkerAndCoordinates(lnglat)
}

// 组件挂载时初始化地图
onMounted(() => {
  initMap()
})

// 在组件卸载时清理地图实例
onUnmounted(() => {
  if (map.value) {
    map.value.destroy()
  }
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

.location-section {
  margin: 20px 0;
}

.location-input {
  margin-bottom: 15px;
  position: relative;
}

.search-input {
  width: 100%;
}

.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.search-result-item {
  padding: 12px;
  cursor: pointer;
  border-bottom: 1px solid #ebeef5;
}

.search-result-item:hover {
  background-color: #f5f7fa;
}

.search-result-item .address {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.map-container {
  width: 100%;
  height: 400px;
  margin-bottom: 15px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}

.coordinates-display {
  display: flex;
  gap: 15px;
}

.coordinate-input {
  flex: 1;
}
</style>
 