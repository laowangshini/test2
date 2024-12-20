<template>
  <div>
    <div class="coordinate-text">{{ latitude }}，{{ longitude }}</div>
    <div v-if="mapError" class="error-message">
      {{ mapError }}
      <div class="coordinate-fallback">
        经度: {{ lng }}
        纬度: {{ lat }}
      </div>
    </div>
    <div v-else ref="mapContainer" class="map-container"></div>
  </div>
</template>

<script>
export default {
  name: 'AMapComponent',
  props: {
    latitude: {
      type: String,
      required: true
    },
    longitude: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      map: null,
      marker: null,
      mapError: null,
      lat: 0,
      lng: 0
    }
  },
  mounted() {
    this.initMap();
  },
  methods: {
    async initMap() {
      try {
        // 解析经纬度
        this.lat = this.parseCoordinate(this.latitude);
        this.lng = this.parseCoordinate(this.longitude);
        
        // 使用开发环境特定配置加载地图
        await this.loadAMap();
        
        // 创建地图实例
        this.map = new AMap.Map(this.$refs.mapContainer, {
          zoom: 8,
          center: [this.lng, this.lat],
          viewMode: '2D'
        });

        // 添加标记
        this.marker = new AMap.Marker({
          position: [this.lng, this.lat],
          title: `${this.latitude}，${this.longitude}`
        });
        
        this.marker.setMap(this.map);

        // 添加工具条和比例尺
        this.map.plugin(['AMap.ToolBar', 'AMap.Scale'], () => {
          // 在插件加载完成后添加控件
          this.map.addControl(new AMap.ToolBar({
            position: 'RB'
          }));
          this.map.addControl(new AMap.Scale());
        });

      } catch (error) {
        console.error("高德地图加载失败:", error);
        this.mapError = "地图加载失败，显示坐标信息";
      }
    },
    loadAMap() {
      return new Promise((resolve, reject) => {
        if (window.AMap) {
          resolve(window.AMap);
          return;
        }

        // 检查是否为本地开发环境
        const isLocalhost = window.location.hostname === 'localhost' || 
                          window.location.hostname === '127.0.0.1';

        if (!isLocalhost) {
          reject(new Error('非本地开发环境'));
          return;
        }

        const script = document.createElement('script');
        script.type = 'text/javascript';
        script.async = true;
        
        // 使用 HTTP 协议加载，并添加插件参数
        const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
        script.src = `${protocol}//webapi.amap.com/maps?v=2.0&key=${process.env.VUE_APP_AMAP_KEY}&plugin=AMap.ToolBar,AMap.Scale`;
        
        script.onerror = () => {
          reject(new Error('地图脚本加载失败'));
        };
        
        script.onload = () => {
          if (window.AMap) {
            resolve(window.AMap);
          } else {
            reject(new Error('AMap 对象未找到'));
          }
        };

        document.head.appendChild(script);
      });
    },
    parseCoordinate(coord) {
      try {
        const num = parseFloat(coord);
        const direction = coord.slice(-1);
        return direction === 'S' || direction === 'W' ? -num : num;
      } catch (error) {
        console.error('坐标解析错误:', error);
        return 0;
      }
    }
  }
}
</script>

<style scoped>
.map-container {
  width: 100%;
  height: 300px;
  margin-top: 10px;
  border-radius: 4px;
}

.coordinate-text {
  margin-bottom: 8px;
  color: #666;
}

.error-message {
  color: #f56c6c;
  padding: 20px;
  background: #fef0f0;
  border-radius: 4px;
  margin-top: 10px;
}

.coordinate-fallback {
  margin-top: 10px;
  color: #666;
  font-size: 14px;
}
</style> 