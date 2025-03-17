<template>
  <div>
    <div class="bg-white rounded-lg p-8 mb-8">
      <h2 class="text-xl font-medium mb-6">视频去重处理</h2>
      
      <!-- 视频处理选项 -->
      <div class="mb-6">
        <div class="flex flex-wrap gap-3 mb-4">
          <button 
            v-for="option in videoProcessOptions" 
            :key="option.id"
            @click="toggleVideoProcessOption(option.id)"
            :class="[
              'px-4 py-2 rounded-full text-sm font-medium',
              selectedVideoOptions.includes(option.id)
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            ]"
          >
            <i :class="option.icon" class="mr-1"></i>
            {{ option.name }}
          </button>
        </div>
        
        <p class="text-sm text-gray-500 italic">
          选择上方的处理选项，可以有效避免平台判定为抄袭内容
        </p>
      </div>
      
      <!-- 视频上传区域 -->
      <div 
        class="border-2 border-dashed border-blue-200 rounded-lg p-8 flex flex-col items-center justify-center min-h-[300px]"
        :class="{ 
          'bg-gray-50': !videoFile, 
          'border-blue-400': isDraggingVideo 
        }"
        @dragover.prevent="isDraggingVideo = true"
        @dragleave.prevent="isDraggingVideo = false"
        @drop.prevent="handleVideoDrop"
      >
        <input
          type="file"
          accept="video/*"
          class="hidden"
          ref="videoInput"
          @change="handleVideoUpload"
        />
        
        <div v-if="!videoFile" class="text-center">
          <i class="fas fa-film text-5xl text-blue-400 mb-4"></i>
          <p class="text-gray-600 mb-4 text-lg">上传需要处理的视频</p>
          <p class="text-gray-500 text-sm mb-6">支持拖拽上传，最大支持100MB的视频文件</p>
          <button
            class="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors"
            @click="$refs.videoInput.click()"
          >
            <i class="fas fa-upload mr-2"></i>选择视频
          </button>
        </div>
        
        <div v-else class="w-full">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center">
              <i class="fas fa-file-video text-blue-500 text-2xl mr-3"></i>
              <div>
                <p class="font-medium">{{ videoFile.name }}</p>
                <p class="text-sm text-gray-500">{{ formatFileSize(videoFile.size) }}</p>
              </div>
            </div>
            <button 
              @click="clearVideoFile"
              class="text-red-500 hover:text-red-700"
            >
              <i class="fas fa-times"></i>
            </button>
          </div>
          
          <div class="mt-6">
            <button
              class="w-full bg-blue-500 text-white py-3 rounded-lg hover:bg-blue-600 transition-colors"
              :disabled="isProcessing || selectedVideoOptions.length === 0"
              :class="{ 'opacity-50 cursor-not-allowed': isProcessing || selectedVideoOptions.length === 0 }"
              @click="processVideo"
            >
              <span v-if="isProcessing">
                <i class="fas fa-spinner fa-spin mr-2"></i>处理中...
              </span>
              <span v-else>
                <i class="fas fa-magic mr-2"></i>开始处理
              </span>
            </button>
          </div>
        </div>
      </div>
      
      <!-- 处理说明 -->
      <div class="mt-8 bg-blue-50 p-4 rounded-lg">
        <h3 class="text-blue-700 font-medium mb-2 flex items-center">
          <i class="fas fa-info-circle mr-2"></i>
          视频去重说明
        </h3>
        <ul class="text-sm text-blue-700 space-y-1 pl-6 list-disc">
          <li>抽帧：随机删除部分视频帧，减少视频重复率</li>
          <li>滤镜：添加轻微滤镜效果，改变视频色调</li>
          <li>裁剪：轻微调整视频边缘，不影响主体内容</li>
          <li>水印：添加半透明水印，可有效防止被判定为抄袭</li>
          <li>音频调整：微调音频频率，避免音频指纹识别</li>
        </ul>
      </div>
    </div>
    
    <!-- 处理历史 -->
    <div class="bg-white rounded-lg p-8">
      <h2 class="text-xl font-medium mb-6">处理历史</h2>
      
      <!-- 示例历史记录 -->
      <div class="text-center py-12 text-gray-500">
        <i class="fas fa-history text-4xl mb-4 opacity-30"></i>
        <p>暂无处理记录</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "VideoUnique",
  data() {
    return {
      videoFile: null,
      isDraggingVideo: false,
      isProcessing: false,
      selectedVideoOptions: [],
      videoProcessOptions: [
        { id: 'frame-extract', name: '抽帧', icon: 'fas fa-film' },
        { id: 'filter', name: '滤镜', icon: 'fas fa-adjust' },
        { id: 'crop', name: '裁剪', icon: 'fas fa-crop' },
        { id: 'watermark', name: '水印', icon: 'fas fa-copyright' },
        { id: 'audio-adjust', name: '音频调整', icon: 'fas fa-volume-up' }
      ]
    };
  },
  methods: {
    toggleVideoProcessOption(optionId) {
      if (this.selectedVideoOptions.includes(optionId)) {
        this.selectedVideoOptions = this.selectedVideoOptions.filter(id => id !== optionId);
      } else {
        this.selectedVideoOptions.push(optionId);
      }
    },
    handleVideoDrop(event) {
      this.isDraggingVideo = false;
      const file = event.dataTransfer.files[0];
      if (file && file.type.startsWith('video/')) {
        this.videoFile = file;
      } else {
        alert('请上传视频文件');
      }
    },
    handleVideoUpload(event) {
      const file = event.target.files[0];
      if (file && file.type.startsWith('video/')) {
        this.videoFile = file;
      }
    },
    clearVideoFile() {
      this.videoFile = null;
      if (this.$refs.videoInput) this.$refs.videoInput.value = '';
    },
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    processVideo() {
      if (!this.videoFile) {
        alert('请先上传视频文件');
        return;
      }
      
      if (this.selectedVideoOptions.length === 0) {
        alert('请选择至少一种处理方式');
        return;
      }
      
      // 模拟处理过程
      this.isProcessing = true;
      setTimeout(() => {
        this.isProcessing = false;
        alert('视频处理完成！');
        // 这里可以添加实际的处理逻辑和结果展示
      }, 3000);
    }
  }
};
</script>

<style scoped>
/* 拖拽相关样式 */
.border-blue-400 {
  border-width: 2px;
  border-style: dashed;
  background-color: rgba(96, 165, 250, 0.1);
}
</style> 