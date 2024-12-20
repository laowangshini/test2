<template>
  <div>
    <div class="coordinate-text">{{ latitude }}，{{ longitude }}</div>
    <div ref="mapDiv" class="map-container"></div>
  </div>
</template>

<script>
import { Loader } from '@googlemaps/js-api-loader';

export default {
  name: 'GoogleMap',
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
      marker: null
    }
  },
  mounted() {
    this.initMap();
  },
  methods: {
    async initMap() {
      try {
        const loader = new Loader({
          apiKey: "YOUR_GOOGLE_MAPS_API_KEY", // 替换为你的 API Key
          version: "weekly"
        });

        const google = await loader.load();
        
        // 解析经纬度
        const lat = this.parseCoordinate(this.latitude);
        const lng = this.parseCoordinate(this.longitude);
        
        const position = { lat, lng };
        
        this.map = new google.maps.Map(this.$refs.mapDiv, {
          center: position,
          zoom: 8,
        });

        this.marker = new google.maps.Marker({
          position: position,
          map: this.map,
          title: `${this.latitude}，${this.longitude}`
        });
      } catch (error) {
        console.error("Google Maps 加载失败:", error);
      }
    },
    parseCoordinate(coord) {
      // 处理类似 "34°E" 或 "2°N" 的格式
      const num = parseFloat(coord);
      const direction = coord.slice(-1);
      return direction === 'S' || direction === 'W' ? -num : num;
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
</style> 