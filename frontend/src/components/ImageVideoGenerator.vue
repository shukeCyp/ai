<template>
  <div class="bg-white rounded-lg shadow-lg p-8">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-10">
      <!-- 左侧：上传和图片预览区域 (占2列) -->
      <div class="lg:col-span-2 space-y-8">
        <!-- 图片上传区域 -->
        <div 
          class="border-3 border-dashed border-gray-300 rounded-xl p-6 text-center hover:border-blue-500 transition-colors bg-gray-100 h-[500px] flex items-center justify-center"
          @dragover.prevent
          @drop.prevent="handleFileDrop"
        >
          <div v-if="!imagePreview" class="w-full">
            <i class="fas fa-cloud-upload-alt text-6xl text-gray-400 mb-6"></i>
            <p class="text-gray-600 mb-4 text-xl">点击或拖拽图片到此处上传</p>
            <p class="text-sm text-gray-500 mb-6">支持 JPG、PNG、WEBP 格式</p>
            <input 
              type="file" 
              ref="fileInput" 
              @change="handleFileChange" 
              accept="image/*" 
              class="hidden"
            />
            <button 
              @click="$refs.fileInput.click()" 
              class="px-8 py-4 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors shadow-lg text-lg"
            >
              <i class="fas fa-image mr-3"></i>
              选择图片
            </button>
          </div>
          
          <div v-else class="relative w-full h-full">
            <!-- 图片展示区域 -->
            <div class="h-full flex items-center justify-center">
              <img 
                :src="processedImagePreview || imagePreview" 
                alt="上传的图片" 
                class="max-h-full max-w-full object-contain" 
              />
              <i 
                @click="removeImage" 
                class="fas fa-trash-alt absolute bottom-4 right-4 p-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 shadow-lg cursor-pointer"
              ></i>
            </div>
              
            <div class="mt-6">
              <h3 class="text-xl font-semibold mb-4">图片设置</h3>
              
              <!-- 模式选择 -->
              <div class="flex justify-center space-x-4 mb-6">
                <button 
                  @click="setMode('crop')" 
                  class="px-4 py-3 rounded-lg flex items-center text-lg"
                  :class="mode === 'crop' ? 'bg-blue-500 text-white shadow-lg' : 'bg-gray-200 text-gray-700'"
                >
                  <i class="fas fa-crop-alt mr-2"></i>
                  裁剪模式
                </button>
                <button 
                  @click="setMode('fill')" 
                  class="px-4 py-3 rounded-lg flex items-center text-lg"
                  :class="mode === 'fill' ? 'bg-blue-500 text-white shadow-lg' : 'bg-gray-200 text-gray-700'"
                >
                  <i class="fas fa-expand mr-2"></i>
                  填充模式
                </button>
              </div>
              
              <!-- 分辨率选择 -->
              <div class="flex flex-wrap justify-center gap-4 mb-6">
                <button 
                  @click="setResolution('1280x768')" 
                  class="px-4 py-3 rounded-lg flex items-center text-lg"
                  :class="resolution === '1280x768' ? 'bg-blue-500 text-white shadow-lg' : 'bg-gray-200 text-gray-700'"
                >
                  <i class="fas fa-desktop mr-2"></i>
                  横版 (1280×768)
                </button>
                <button 
                  @click="setResolution('768x1280')" 
                  class="px-4 py-3 rounded-lg flex items-center text-lg"
                  :class="resolution === '768x1280' ? 'bg-blue-500 text-white shadow-lg' : 'bg-gray-200 text-gray-700'"
                >
                  <i class="fas fa-mobile-alt mr-2"></i>
                  竖版 (768×1280)
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右侧：设置和生成区域 (占1列) -->
      <div class="lg:col-span-1 space-y-8">
        <!-- 提示词输入 -->
        <div class="bg-gray-50 p-6 rounded-xl shadow-lg border border-gray-200">
          <label class="block text-lg font-medium text-gray-700 mb-3">提示词</label>
          <textarea 
            v-model="prompt" 
            rows="4" 
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-lg"
            placeholder="描述您想要生成的视频内容..."
          ></textarea>
          <p class="text-sm text-gray-500 mt-2">详细的提示词可以帮助生成更好的视频效果</p>
        </div>
        
        <!-- 参数设置区域 -->
        <div class="bg-gray-50 p-6 rounded-xl shadow-lg border border-gray-200">
          <h3 class="text-xl font-semibold mb-6 text-gray-700 flex items-center">
            <i class="fas fa-sliders-h text-blue-500 mr-3"></i>
            视频参数设置
          </h3>
          
          <!-- 视频时长选择 -->
          <div class="mb-6">
            <label class="block text-lg font-medium text-gray-700 mb-3">视频时长</label>
            <div class="flex space-x-4">
              <label class="flex items-center bg-white px-5 py-3 rounded-lg border border-gray-300 cursor-pointer flex-1 hover:bg-gray-50 transition-colors">
                <input type="radio" v-model="seconds" :value="5" class="mr-3" />
                <span class="text-lg">5秒</span>
              </label>
              <label class="flex items-center bg-white px-5 py-3 rounded-lg border border-gray-300 cursor-pointer flex-1 hover:bg-gray-50 transition-colors">
                <input type="radio" v-model="seconds" :value="10" class="mr-3" />
                <span class="text-lg">10秒</span>
              </label>
            </div>
          </div>
          
          <!-- 种子数设置 -->
          <div>
            <label class="block text-lg font-medium text-gray-700 mb-3">种子数</label>
            <div class="flex space-x-3">
              <input 
                type="number" 
                v-model="seed" 
                class="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-lg"
              />
              <i 
                @click="generateRandomSeed" 
                class="fas fa-random p-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors cursor-pointer flex items-center"
                title="生成随机种子"
              ></i>
            </div>
            <p class="text-sm text-gray-500 mt-2">种子数决定生成结果的随机性</p>
          </div>
        </div>
        
        <!-- 生成按钮 -->
        <div class="w-full">
          <button 
            @click="generateVideo" 
            class="w-full py-5 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl hover:from-blue-600 hover:to-indigo-700 transition-colors flex items-center justify-center shadow-xl text-xl"
            :disabled="isGenerating || !imageFile || !prompt"
            :class="{'opacity-70 cursor-not-allowed': isGenerating || !imageFile || !prompt}"
          >
            <i :class="isGenerating ? 'fas fa-spinner fa-spin mr-3' : 'fas fa-magic mr-3'"></i>
            {{ isGenerating ? '生成中...' : '生成视频' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 视频结果展示区域 -->
    <div v-if="videoResult" class="mt-10 bg-white rounded-lg shadow-lg p-6">
      <h2 class="text-2xl font-bold mb-6 text-center">生成的视频</h2>
      <div class="flex justify-center">
        <video 
          :src="videoResult.url" 
          controls 
          class="max-w-full rounded-lg shadow-lg h-[480px]"
        ></video>
      </div>
      <div class="mt-6 flex justify-center">
        <button 
          @click="downloadVideo(videoResult.url)" 
          class="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors shadow-lg text-lg"
        >
          <i class="fas fa-download mr-2"></i>
          下载视频
        </button>
      </div>
    </div>
  </div>
  
  <!-- 生成记录展示区域 - 独立的白色框 -->
  <div class="mt-10 bg-white rounded-lg shadow-lg p-8">
    <h2 class="text-2xl font-bold mb-6 text-center flex items-center justify-center">
      <i class="fas fa-history text-blue-500 mr-3"></i>
      生成记录
    </h2>
    <div v-if="videoList.length === 0" class="text-center text-gray-500 py-10">
      <i class="fas fa-film text-5xl mb-4 opacity-30"></i>
      <p class="text-xl">暂无视频记录</p>
    </div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="video in videoList" 
        :key="video.id" 
        class="bg-gray-50 rounded-lg overflow-hidden shadow-md border border-gray-200 cursor-pointer hover:shadow-lg transition-shadow"
        @click="openVideoModal(video)"
      >
        <div class="relative">
          <img v-if="video.status === 2" :src="video.image_url" alt="视频缩略图" class="w-full h-48 object-cover" />
          <div v-else class="w-full h-48 bg-gray-200 flex items-center justify-center">
            <i class="fas fa-film text-gray-400 text-4xl"></i>
          </div>
          <div class="absolute bottom-2 right-2 bg-black bg-opacity-70 text-white px-2 py-1 rounded text-sm">
            {{ video.seconds }}秒
          </div>
          <!-- 状态标签 -->
          <div class="absolute top-2 left-2 px-2 py-1 rounded text-sm" 
               :class="{
                 'bg-yellow-500 text-white': video.status === 0,
                 'bg-blue-500 text-white': video.status === 1,
                 'bg-green-500 text-white': video.status === 2,
                 'bg-red-500 text-white': video.status === 3
               }">
            {{ getStatusText(video.status) }}
          </div>
        </div>
        <div class="p-4">
          <p class="text-gray-700 font-medium mb-2 line-clamp-2">{{ video.prompt }}</p>
          <div class="flex justify-between items-center text-sm text-gray-500">
            <span>{{ formatDate(video.created_at) }}</span>
            <span>{{ video.resolution }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 视频详情弹窗 - 优化后 -->
  <div v-if="showVideoModal" class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-lg shadow-2xl max-w-3xl w-full mx-auto overflow-hidden">
      <div class="flex justify-between items-center p-5 bg-gray-50 border-b">
        <h3 class="text-xl font-bold text-gray-800">视频详情</h3>
        <button @click="closeVideoModal" class="text-gray-500 hover:text-gray-700 p-2 rounded-full hover:bg-gray-200 transition-colors">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div v-if="currentVideo" class="p-6">
        <div class="mb-6">
          <div class="bg-gray-100 p-4 rounded-lg mb-3">
            <p class="text-gray-800">{{ currentVideo.prompt }}</p>
          </div>
          <div class="flex justify-between text-sm text-gray-500">
            <span>{{ formatDate(currentVideo.created_at) }}</span>
            <span>{{ currentVideo.resolution }} | {{ currentVideo.seconds }}秒</span>
          </div>
        </div>
        
        <div class="relative rounded-lg overflow-hidden mb-6">
          <div v-if="currentVideo.status === 2" class="flex justify-center bg-black">
            <video 
              :src="currentVideo.video_url" 
              controls 
              class="max-w-full rounded-lg h-[480px]"
            ></video>
          </div>
          <div v-else class="bg-gray-200 flex items-center justify-center" style="height: 300px;">
            <div class="text-center">
              <i :class="currentVideo.status === 3 ? 'fas fa-exclamation-circle text-red-500 text-4xl mb-3' : 'fas fa-spinner fa-spin text-blue-500 text-4xl mb-3'"></i>
              <p class="text-gray-700">{{ getStatusText(currentVideo.status) }}</p>
            </div>
          </div>
        </div>
        
        <div class="flex justify-end">
          <button 
            v-if="currentVideo.status === 2"
            @click="downloadVideo(currentVideo.video_url)" 
            class="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors shadow-md flex items-center"
          >
            <i class="fas fa-download mr-2"></i>
            下载视频
          </button>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Toast 提示 - 移至顶部居中 -->
  <div v-if="showToast" class="fixed top-4 left-1/2 transform -translate-x-1/2 bg-white rounded-lg shadow-xl p-4 z-50 max-w-md">
    <div class="flex items-center">
      <div :class="toastIcon.class" class="mr-4 text-2xl">
        <i :class="toastIcon.icon"></i>
      </div>
      
      <div class="flex-1">
        <h3 class="font-bold text-lg">{{ toastMessage }}</h3>
      </div>
      
      <button @click="closeToast" class="ml-2 text-gray-500 hover:text-gray-700">
        <i class="fas fa-times"></i>
      </button>
    </div>
  </div>
</template>

<script>
import { createVideo, getVideoList } from '../api/ai_video.js';
import 'vue-cropper/dist/index.css';

export default {
  name: 'ImageVideoGenerator',
  components: {},
  data() {
    return {
      imageFile: null,
      imagePreview: null,
      originalImage: null, // 存储原始图片
      processedImagePreview: null, // 处理后的图片预览
      prompt: '',
      resolution: '1280x768',
      seconds: 10,
      seed: this.generateRandomSeedValue(),
      isGenerating: false,
      cropperWidth: 1280,
      cropperHeight: 768,
      mode: 'crop', // 默认为裁剪模式
      videoResult: null, // 添加视频结果数据
      videoList: [], // 存储视频列表
      refreshInterval: null, // 定时刷新间隔
      showVideoModal: false, // 控制视频弹窗显示
      currentVideo: null, // 当前播放的视频
      currentTaskId: null, // 当前任务ID
      showToast: false, // 控制Toast显示
      toastMessage: '', // Toast消息
      toastIcon: { icon: '', class: '' }, // Toast图标
      toastTimeout: null, // Toast定时器
    };
  },
  mounted() {
    this.fetchVideoList();
    // 设置定时刷新
    this.refreshInterval = setInterval(() => {
      this.silentRefreshVideoList();
    }, 30000); // 每30秒刷新一次
  },
  beforeUnmount() {
    // 组件销毁前清除定时器
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
    if (this.toastTimeout) {
      clearTimeout(this.toastTimeout);
    }
  },
  methods: {
    handleFileChange(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      this.imageFile = file;
      
      // 创建预览并保存原图
      const reader = new FileReader();
      reader.onload = (e) => {
        this.originalImage = e.target.result; // 保存原图
        this.imagePreview = e.target.result;
        // 初始化尺寸
        this.updateCropperSize();
        // 处理图片
        this.processImage();
      };
      reader.readAsDataURL(file);
    },
    
    handleFileDrop(event) {
      const file = event.dataTransfer.files[0];
      if (!file || !file.type.startsWith('image/')) return;
      
      this.imageFile = file;
      
      // 创建预览并保存原图
      const reader = new FileReader();
      reader.onload = (e) => {
        this.originalImage = e.target.result; // 保存原图
        this.imagePreview = e.target.result;
        // 初始化尺寸
        this.updateCropperSize();
        // 处理图片
        this.processImage();
      };
      reader.readAsDataURL(file);
    },
    
    removeImage() {
      this.imageFile = null;
      this.imagePreview = null;
      this.originalImage = null;
      this.processedImagePreview = null;
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = '';
      }
    },
    
    generateRandomSeed() {
      this.seed = this.generateRandomSeedValue();
    },
    
    generateRandomSeedValue() {
      return Math.floor(Math.random() * 1000000000);
    },
    
    async generateVideo() {
      if (!this.imageFile || !this.prompt) {
        this.showToastMessage('请上传图片并填写提示词', 'error');
        return;
      }
      
      try {
        this.isGenerating = true;
        
        // 准备表单数据
        const formData = new FormData();
        
        // 如果有处理后的图片，将其转换为文件并添加到表单
        if (this.processedImagePreview) {
          // 将 base64 图片转换为 Blob
          const response = await fetch(this.processedImagePreview);
          const blob = await response.blob();
          const processedFile = new File([blob], 'processed_' + this.imageFile.name, { type: 'image/jpeg' });
          formData.append('photo', processedFile);
        } else {
          // 使用原始图片
          formData.append('photo', this.imageFile);
        }
        
        // 添加其他参数
        formData.append('prompt', this.prompt);
        formData.append('resolution', this.resolution);
        formData.append('seconds', this.seconds);
        formData.append('seed', this.seed);
        
        // 调用 API 生成视频
        const result = await createVideo(formData);
        
        // 处理成功响应
        if (result && result.status === "success") {
          this.currentTaskId = result.task_id;
          this.showToastMessage('视频生成任务已创建！', 'success');
          // 刷新视频列表
          this.fetchVideoList();
          
          // 生成成功后清空图片和提示词
          this.removeImage();
          this.prompt = '';
        } else {
          throw new Error(result.message || '视频生成任务创建失败');
        }
      } catch (error) {
        console.error('视频生成失败:', error);
        this.showToastMessage('视频生成失败: ' + (error.message || '未知错误'), 'error');
      } finally {
        this.isGenerating = false;
      }
    },
    
    async fetchVideoList() {
      try {
        const response = await getVideoList();
        if (response && response.items) {
          this.videoList = response.items;
        }
      } catch (error) {
        console.error('获取视频列表失败:', error);
      }
    },
    
    // 静默刷新视频列表（不显示加载状态，不影响用户体验）
    async silentRefreshVideoList() {
      try {
        const response = await getVideoList();
        if (response && response.items) {
          // 检查数据是否有变化
          const currentIds = this.videoList.map(v => v.id).sort().join(',');
          const newIds = response.items.map(v => v.id).sort().join(',');
          
          if (currentIds !== newIds) {
            this.videoList = response.items;
          }
        }
      } catch (error) {
        console.error('静默刷新视频列表失败:', error);
        // 静默失败，不提示用户
      }
    },
    
    openVideoModal(video) {
      this.currentVideo = video;
      this.showVideoModal = true;
    },
    
    closeVideoModal() {
      this.showVideoModal = false;
      this.currentVideo = null;
    },
    
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    
    updateCropperSize() {
      // 根据分辨率设置尺寸
      const [width, height] = this.resolution.split('x').map(Number);
      this.cropperWidth = width;
      this.cropperHeight = height;
      
      // 更新图片处理
      if (this.originalImage) {
        this.processImage();
      }
    },
    
    setResolution(res) {
      this.resolution = res;
      this.updateCropperSize();
    },
    
    setMode(newMode) {
      this.mode = newMode;
      // 更新图片处理
      if (this.originalImage) {
        this.processImage();
      }
    },
    
    processImage() {
      if (!this.originalImage) return;
      
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // 设置目标尺寸
        const [targetWidth, targetHeight] = this.resolution.split('x').map(Number);
        canvas.width = targetWidth;
        canvas.height = targetHeight;
        
        // 根据模式处理图片
        if (this.mode === 'crop') {
          // 裁剪模式：裁剪中间区域
          const sourceWidth = img.width;
          const sourceHeight = img.height;
          
          // 计算裁剪区域
          let sx, sy, sWidth, sHeight;
          
          if (sourceWidth / sourceHeight > targetWidth / targetHeight) {
            // 原图更宽，裁剪两侧
            sHeight = sourceHeight;
            sWidth = sourceHeight * (targetWidth / targetHeight);
            sx = (sourceWidth - sWidth) / 2;
            sy = 0;
          } else {
            // 原图更高，裁剪上下
            sWidth = sourceWidth;
            sHeight = sourceWidth * (targetHeight / targetWidth);
            sx = 0;
            sy = (sourceHeight - sHeight) / 2;
          }
          
          // 绘制裁剪后的图像
          ctx.drawImage(img, sx, sy, sWidth, sHeight, 0, 0, targetWidth, targetHeight);
        } else {
          // 填充模式：保持原图比例，黑色填充
          ctx.fillStyle = '#000000';
          ctx.fillRect(0, 0, targetWidth, targetHeight);
          
          // 计算缩放后的尺寸
          let dWidth, dHeight;
          if (img.width / img.height > targetWidth / targetHeight) {
            // 原图更宽，适应宽度
            dWidth = targetWidth;
            dHeight = targetWidth * (img.height / img.width);
          } else {
            // 原图更高，适应高度
            dHeight = targetHeight;
            dWidth = targetHeight * (img.width / img.height);
          }
          
          // 计算居中位置
          const dx = (targetWidth - dWidth) / 2;
          const dy = (targetHeight - dHeight) / 2;
          
          // 绘制图像
          ctx.drawImage(img, 0, 0, img.width, img.height, dx, dy, dWidth, dHeight);
        }
        
        // 更新预览
        this.processedImagePreview = canvas.toDataURL('image/jpeg');
      };
      img.src = this.originalImage;
    },
    
    // 获取状态文本
    getStatusText(status) {
      switch (status) {
        case 0:
          return '排队中';
        case 1:
          return '生成中';
        case 2:
          return '已完成';
        case 3:
          return '生成失败';
        default:
          return '未知状态';
      }
    },
    
    // 显示Toast消息
    showToastMessage(message, type = 'info') {
      this.toastMessage = message;
      
      // 设置图标
      switch (type) {
        case 'success':
          this.toastIcon = { icon: 'fas fa-check-circle', class: 'text-green-500' };
          break;
        case 'error':
          this.toastIcon = { icon: 'fas fa-exclamation-circle', class: 'text-red-500' };
          break;
        case 'warning':
          this.toastIcon = { icon: 'fas fa-exclamation-triangle', class: 'text-yellow-500' };
          break;
        default:
          this.toastIcon = { icon: 'fas fa-info-circle', class: 'text-blue-500' };
      }
      
      this.showToast = true;
      
      // 3秒后自动关闭
      if (this.toastTimeout) {
        clearTimeout(this.toastTimeout);
      }
      
      this.toastTimeout = setTimeout(() => {
        this.closeToast();
      }, 3000);
    },
    
    // 关闭Toast
    closeToast() {
      this.showToast = false;
    },
    // 下载视频
    downloadVideo(url) {
      // 创建一个隐藏的a标签
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      
      // 使用当前时间作为文件名
      const now = new Date();
      const fileName = now.toISOString().replace(/[:.]/g, '-').replace('T', '_').split('Z')[0] + '.mp4';
      a.download = fileName;
      
      // 使用fetch获取视频内容并创建本地下载
      fetch(url)
        .then(response => response.blob())
        .then(blob => {
          // 创建blob URL
          const blobUrl = URL.createObjectURL(blob);
          a.href = blobUrl;
          document.body.appendChild(a);
          a.click();
          // 清理DOM和blob URL
          setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(blobUrl);
          }, 100);
        })
        .catch(error => {
          this.showToastMessage('下载视频失败: ' + error.message, 'error');
        });
    }
  }
}
</script>

<style scoped>
.aspect-video {
  aspect-ratio: 16/9;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>