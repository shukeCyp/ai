<!-- 代码已包含 CSS：使用 TailwindCSS , 安装 TailwindCSS 后方可看到布局样式效果 -->
<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
    <div class="max-w-7xl w-full bg-gray-50 rounded-xl overflow-hidden relative">
      <!-- 添加右上角关闭按钮 - 样式更明显 -->
      <button class="absolute top-3 right-3 z-10 w-10 h-10 flex items-center justify-center rounded-full bg-gray-200 hover:bg-gray-300 text-gray-700 hover:text-gray-900 shadow-lg transition-all duration-200" @click="$emit('close')">
        <i class="fas fa-times text-lg"></i>
      </button>
      <div class="bg-white shadow-lg p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-6">
          <h1 class="text-xl font-medium">视频编辑</h1>
        </div>
        <!-- 视频预览区域 -->
        <div class="grid grid-cols-2 gap-6 mb-6">
          <!-- 人像视频 -->
          <div class="bg-gray-900 rounded-lg aspect-video relative overflow-hidden">
            <video
              ref="humanVideo"
              :src="humanVideoUrl"
              class="absolute inset-0 w-full h-full object-contain"
              @loadedmetadata="onHumanVideoLoad"
              crossorigin="anonymous"
            ></video>
            <!-- 添加右上角下载按钮 -->
            <button 
              class="absolute top-3 right-3 z-10 w-10 h-10 flex items-center justify-center rounded-full bg-white/80 hover:bg-white text-gray-700 hover:text-gray-900 shadow-lg transition-all duration-200" 
              @click="downloadOriginalVideo('human')"
              title="下载原始视频"
            >
              <i class="fas fa-download text-lg"></i>
            </button>
            <!-- <div class="absolute inset-0 flex items-center justify-center">
              <i class="fas fa-user text-white text-4xl opacity-50"></i>
            </div> -->
            <!-- 添加播放控制按钮 -->
            <div 
              class="absolute inset-0 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity duration-300 bg-black/30"
              v-if="!isDragging"
            >
              <button 
                class="w-16 h-16 flex items-center justify-center bg-white/20 rounded-full hover:bg-white/40 transition-colors"
                @click="toggleHumanVideo"
              >
                <i :class="isHumanPlaying ? 'fas fa-pause' : 'fas fa-play'" class="text-white text-2xl"></i>
              </button>
            </div>
            <!-- 关键帧展示区域 -->
            <div class="absolute bottom-0 left-0 right-0 bg-black/70 p-2 overflow-x-auto human-keyframes select-none">
              <div class="flex relative">
                <img
                  v-for="(frame, index) in humanKeyframes"
                  :key="index"
                  :src="frame.url"
                  :style="{
                    width: `${keyframeWidth}px`,
                    height: `${keyframeHeight}px`,
                    objectFit: 'cover'
                  }"
                  class="pointer-events-none"
                />
                <!-- 视频裁剪蒙层 -->
                <div class="absolute inset-0 flex pointer-events-none">
                  <div
                    class="bg-black/60 flex-grow transition-all duration-200"
                    :style="{ width: startPercent + '%' }"
                  ></div>
                  <div
                    class="relative flex-shrink-0 transition-all duration-200"
                    :style="{ width: endPercent - startPercent + '%' }"
                  >
                    <div
                      class="absolute inset-y-0 -left-1 w-2 bg-white cursor-ew-resize pointer-events-auto"
                      @mousedown="startDragging('start')"
                    ></div>
                    <div
                      class="absolute inset-y-0 -right-1 w-2 bg-white cursor-ew-resize pointer-events-auto"
                      @mousedown="startDragging('end')"
                    ></div>
                  </div>
                  <div
                    class="bg-black/60 flex-grow transition-all duration-200"
                    :style="{ width: 100 - endPercent + '%' }"
                  ></div>
                </div>
              </div>
              <div class="flex items-center text-white mt-2">
                <span class="text-sm">{{ formatTime(startTime) }} - {{ formatTime(endTime) }}</span>
              </div>
            </div>
          </div>
          <!-- 商品视频 -->
          <div class="bg-gray-900 rounded-lg aspect-video relative overflow-hidden">
            <video
              ref="productVideo"
              :src="productVideoUrl"
              class="absolute inset-0 w-full h-full object-contain"
              @loadedmetadata="onProductVideoLoad"
              crossorigin="anonymous"
            ></video>
            <!-- 添加右上角下载按钮 -->
            <button 
              class="absolute top-3 right-3 z-10 w-10 h-10 flex items-center justify-center rounded-full bg-white/80 hover:bg-white text-gray-700 hover:text-gray-900 shadow-lg transition-all duration-200" 
              @click="downloadOriginalVideo('product')"
              title="下载原始视频"
            >
              <i class="fas fa-download text-lg"></i>
            </button>
            <!-- <div class="absolute inset-0 flex items-center justify-center">
              <i class="fas fa-shopping-bag text-white text-4xl opacity-50"></i>
            </div> -->
            <!-- 添加播放控制按钮 -->
            <div 
              class="absolute inset-0 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity duration-300 bg-black/30"
              v-if="!isDragging"
            >
              <button 
                class="w-16 h-16 flex items-center justify-center bg-white/20 rounded-full hover:bg-white/40 transition-colors"
                @click="toggleProductVideo"
              >
                <i :class="isProductPlaying ? 'fas fa-pause' : 'fas fa-play'" class="text-white text-2xl"></i>
              </button>
            </div>
            <!-- 关键帧展示区域 -->
            <div class="absolute bottom-0 left-0 right-0 bg-black/70 p-2 overflow-x-auto product-keyframes select-none">
              <div class="flex relative">
                <img
                  v-for="(frame, index) in productKeyframes"
                  :key="index"
                  :src="frame.url"
                  :style="{
                    width: `${keyframeWidth}px`,
                    height: `${keyframeHeight}px`,
                    objectFit: 'cover'
                  }"
                  class="pointer-events-none"
                />
                <!-- 视频裁剪蒙层 -->
                <div class="absolute inset-0 flex pointer-events-none">
                  <div
                    class="bg-black/60 flex-grow transition-all duration-200"
                    :style="{ width: productStartPercent + '%' }"
                  ></div>
                  <div
                    class="relative flex-shrink-0 transition-all duration-200"
                    :style="{
                      width: productEndPercent - productStartPercent + '%',
                    }"
                  >
                    <div
                      class="absolute inset-y-0 -left-1 w-2 bg-white cursor-ew-resize pointer-events-auto"
                      @mousedown="startDragging('productStart')"
                    ></div>
                    <div
                      class="absolute inset-y-0 -right-1 w-2 bg-white cursor-ew-resize pointer-events-auto"
                      @mousedown="startDragging('productEnd')"
                    ></div>
                  </div>
                  <div
                    class="bg-black/60 flex-grow transition-all duration-200"
                    :style="{ width: 100 - productEndPercent + '%' }"
                  ></div>
                </div>
              </div>
              <div class="flex items-center text-white mt-2">
                <span class="text-sm">{{ formatTime(productStartTime) }} - {{ formatTime(productEndTime) }}</span>
              </div>
            </div>
          </div>
        </div>
        <!-- 工具栏 -->
        <div class="flex items-center mb-6 border-b pb-4">
          <!-- 钩子输入框 - 带翻译按钮 -->
          <div class="flex-1 mr-4">
            <div class="flex items-center bg-gray-50 p-3 rounded-lg border border-gray-200 shadow-sm w-full">
              <span class="text-sm font-medium text-gray-700 mr-3">钩子：</span>
              <input
                type="text"
                v-model="hookText"
                placeholder="请输入视频钩子文本"
                class="flex-1 border-2 rounded-md px-4 py-2.5 text-base focus:border-green-500 focus:ring-2 focus:ring-green-500 focus:ring-opacity-50 outline-none transition-all duration-200"
              />
              <button 
                class="ml-2 px-3 py-2 bg-blue-50 text-blue-600 hover:bg-blue-100 rounded-md border border-blue-200 flex items-center transition-colors duration-200"
                @click="translateHook"
              >
                <i class="fas fa-language mr-1"></i>
                翻译
              </button>
            </div>
          </div>
          <button
            class="px-4 py-2 bg-green-500 text-white hover:bg-green-600 rounded !rounded-button whitespace-nowrap relative"
            @click="cutAndMergeVideos"
            :disabled="isGenerating"
          >
            <template v-if="!isGenerating">
              <i class="fas fa-video mr-2"></i>
              合成视频
            </template>
            <template v-else>
              <i class="fas fa-spinner fa-spin mr-2"></i>
              生成中...
            </template>
          </button>
        </div>
        
        <!-- 进度弹窗 -->
        <div v-if="isGenerating" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/50">
          <div class="bg-white rounded-lg p-6 w-[480px] shadow-xl">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-medium">{{ mergeStatus }}</h3>
              <button 
                class="text-gray-500 hover:text-gray-700"
                @click="cancelGeneration"
              >
                <i class="fas fa-times"></i>
              </button>
            </div>
            <div class="mb-4">
              <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  class="h-full bg-green-500 transition-all duration-300"
                  :style="{ width: mergeProgress + '%' }"
                ></div>
              </div>
              <div class="text-sm text-gray-600 mt-2 text-center">
                {{ Math.round(mergeProgress) }}%
              </div>
            </div>
          </div>
        </div>
       
        <!-- 预览区域 -->
        <div v-if="previewUrl" class="mt-6 border-t pt-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-medium">生成结果预览</h2>
            <div class="flex space-x-3 items-center">
              <!-- 增加文件名输入框的长度 -->
              <div class="relative">
                <input
                  type="text"
                  v-model="downloadFileName"
                  placeholder="输入保存文件名"
                  class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 w-80"
                />
                <span class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 text-sm">.mp4</span>
              </div>
              <button
                class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded flex items-center !rounded-button whitespace-nowrap"
                @click="handlePreview"
              >
                <i class="fas fa-eye mr-2"></i>
                预览视频
              </button>
              <button
                class="px-4 py-2 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded flex items-center !rounded-button whitespace-nowrap"
                @click="handleDownload"
              >
                <i class="fas fa-download mr-2"></i>
                下载视频
              </button>
            </div>
          </div>
          <div class="bg-gray-900 rounded-lg aspect-video relative overflow-hidden">
            <video
              ref="previewVideo"
              :src="previewUrl"
              class="w-full h-full object-contain"
              @timeupdate="onTimeUpdate"
              @loadedmetadata="onPreviewVideoLoad"
              @ended="onVideoEnded"
            ></video>
            <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/50 p-4">
              <div class="flex items-center text-white">
                <button
                  class="w-8 h-8 flex items-center justify-center hover:bg-white/20 rounded-full mr-2"
                  @click="togglePlay"
                >
                  <i :class="isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
                </button>
                <span class="text-sm">{{ formatTime(currentTime) }} / {{ formatTime(totalDuration) }}</span>
                <div class="flex-grow mx-4 relative">
                  <div class="h-1 bg-white/30 rounded overflow-hidden">
                    <div
                      class="h-full bg-white rounded"
                      :style="{ width: playProgress + '%' }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { FFmpeg } from '@ffmpeg/ffmpeg';
import { toBlobURL, fetchFile } from '@ffmpeg/util';

export default {
  name: "VideoEditModal",
  props: {
    record: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      // humanVideoUrl: "https://dnznrvs05pmza.cloudfront.net/153d6dd9-8067-4b8d-81b3-a7717f9683a5.mp4?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiYWU0MmI0Y2FmM2I0ZGI3YSIsImJ1Y2tldCI6InJ1bndheS10YXNrLWFydGlmYWN0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTc0MTQ3ODQwMH0.EMrsOyfob6ksy076q_FtL5mMzyq86M7OIBCgiDpZ_A8",
      // productVideoUrl: "https://dnznrvs05pmza.cloudfront.net/b4d64fca-1837-43ff-a4a8-fdb2854f808e.mp4?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiNjE2MWQyMTRjMzBkOGI5NSIsImJ1Y2tldCI6InJ1bndheS10YXNrLWFydGlmYWN0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTc0MTQ3ODQwMH0.5UtAPP8_z4M87srXFgQL8jOfMz8rMNGLG4KfNcKNmL0",
      humanVideoUrl: "/videos/3.mp4",
      productVideoUrl: "/videos/4.mp4",
      startPercent: 0,
      endPercent: 30,
      productStartPercent: 10,
      productEndPercent: 50,
      isDragging: false,
      dragTarget: null,
      startTime: 0,
      endTime: 0,
      productStartTime: 0,
      productEndTime: 0,
      isGenerating: false,
      mergeProgress: 0,
      mergeStatus: '',
      previewUrl: "",
      isPlaying: false,
      isHumanPlaying: false,
      isProductPlaying: false,
      isMuted: false,
      currentTime: 0,
      totalDuration: 0,
      playProgress: 0,
      startTimeInput: "",
      endTimeInput: "",
      ffmpeg: null,
      humanKeyframes: [],
      productKeyframes: [],
      keyframeContainerWidth: 0,
      keyframeWidth: 80,
      keyframeHeight: 45,
      hookText: "",
      downloadFileName: "",
    };
  },
  async mounted() {
    await this.initFFmpeg();
    // 添加点击事件监听器，处理点击蒙层或视频外区域时暂停视频
    document.addEventListener('click', this.handleOutsideClick);
    // 初始化视频数据
    this.initVideoData();
  },
  
  beforeUnmount() {
    // 组件销毁前移除事件监听器
    document.removeEventListener('click', this.handleOutsideClick);
  },
  watch: {
    record: {
      handler: 'initVideoData',
      immediate: true
    }
  },
  methods: {
    initVideoData() {
      if (this.record) {
        // 从record中获取视频URL
        if (this.record.personVideoUrl) {
          this.humanVideoUrl = this.record.personVideoUrl;
        }
        if (this.record.productVideoUrl) {
          this.productVideoUrl = this.record.productVideoUrl;
        }
        
        // 设置默认下载文件名
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').substring(0, 19);
        this.downloadFileName = `视频_${this.record.id || ''}_${timestamp}`;
      }
    },
    isInSelectedRange(index, type) {
      const frameCount = 14;
      const video = type === 'human' ? this.$refs.humanVideo : this.$refs.productVideo;
      const duration = video.duration;
      const frameTime = (index / (frameCount - 1)) * duration;
      
      if (type === 'human') {
        const startTime = duration * (this.startPercent / 100);
        const endTime = duration * (this.endPercent / 100);
        return frameTime >= startTime && frameTime <= endTime;
      } else if (type === 'product') {
        const startTime = duration * (this.productStartPercent / 100);
        const endTime = duration * (this.productEndPercent / 100);
        return frameTime >= startTime && frameTime <= endTime;
      }
      
      return false;
    },
    async initFFmpeg() {
      if (this.ffmpeg?.loaded) {
        console.log('FFmpeg已经加载，跳过初始化');
        return;
      }

      try {
        console.log('开始创建FFmpeg实例...');
        this.ffmpeg = new FFmpeg();
        console.log('FFmpeg实例创建成功，开始加载...');

        try {
          console.log('正在加载本地FFmpeg核心文件...');
          console.log('开始加载FFmpeg WASM模块...');
          await this.ffmpeg.load();
          console.log('FFmpeg WASM模块加载成功');
          
          console.log('FFmpeg加载完成，检查加载状态...');
          console.log('FFmpeg WASM模块加载状态:', this.ffmpeg?.loaded);
          
          if (!this.ffmpeg?.loaded) {
            throw new Error('FFmpeg WASM模块加载失败');
          }
          console.log('FFmpeg初始化完成，可以使用');
        } catch (error) {
          console.error('FFmpeg加载过程出错:', error);
          throw error;
        }
      } catch (error) {
        console.error('FFmpeg初始化失败:', error);
        alert('视频处理组件初始化失败，请刷新页面重试');
      }
    },
    async onHumanVideoLoad() {
      const video = this.$refs.humanVideo;
      this.totalDuration = Math.floor(video.duration);
      
      // 设置人像视频默认裁剪时间为0-3秒
      this.startTime = 0;
      this.endTime = Math.min(3, this.totalDuration);
      
      // 根据时间计算百分比
      this.startPercent = (this.startTime / this.totalDuration) * 100;
      this.endPercent = (this.endTime / this.totalDuration) * 100;
      
      await this.extractKeyframes('human');
    },
    async onProductVideoLoad() {
      const video = this.$refs.productVideo;
      this.productDuration = Math.floor(video.duration);
      
      // 设置商品视频默认裁剪时间为1-5秒
      this.productStartTime = 1;
      this.productEndTime = Math.min(5, this.productDuration);
      
      // 根据时间计算百分比
      this.productStartPercent = (this.productStartTime / this.productDuration) * 100;
      this.productEndPercent = (this.productEndTime / this.productDuration) * 100;
      
      await this.extractKeyframes('product');
    },
    async extractKeyframes(type) {
      try {
        const videoUrl = type === 'human' ? this.humanVideoUrl : this.productVideoUrl;
        const video = type === 'human' ? this.$refs.humanVideo : this.$refs.productVideo;
        const duration = video.duration;
        const keyframes = await this.extractFramesFromVideo(videoUrl);
        
        // 更新关键帧数组
        if (type === 'human') {
          this.humanKeyframes = keyframes.map((base64, index) => ({
            url: base64,
            timestamp: (index / 13) * duration,
            selected: false
          }));
        } else {
          this.productKeyframes = keyframes.map((base64, index) => ({
            url: base64,
            timestamp: (index / 13) * duration,
            selected: false
          }));
        }

        // 计算容器宽度
        const container = document.querySelector(type === 'human' ? '.human-keyframes' : '.product-keyframes');
        if (container) {
          this.keyframeContainerWidth = container.offsetWidth;
        }
      } catch (error) {
        console.error('提取关键帧失败:', error);
      }
    },
    onPreviewVideoLoad() {
      const video = this.$refs.previewVideo;
      if (video) {
        video.currentTime = 0;
        this.totalDuration = Math.floor(video.duration);
      }
    },
    onTimeUpdate() {
      const video = this.$refs.previewVideo;
      this.currentTime = Math.floor(video.currentTime);
      this.playProgress = (video.currentTime / video.duration) * 100;
    },
    
    onVideoEnded() {
      this.isPlaying = false;
      if (this.$refs.previewVideo) {
        this.$refs.previewVideo.currentTime = 0;
      }
    },
    async cutVideos() {
      try {
        console.log('开始剪切视频...');
        
        // 将人像视频写入FFmpeg虚拟文件系统
        console.log('正在写入人像视频...');
        const humanResponse = await fetch(this.humanVideoUrl);
        const humanData = await humanResponse.arrayBuffer();
        await this.ffmpeg.writeFile('human.mp4', new Uint8Array(humanData));
        
        // 将商品视频写入FFmpeg虚拟文件系统
        console.log('正在写入商品视频...');
        const productResponse = await fetch(this.productVideoUrl);
        const productData = await productResponse.arrayBuffer();
        await this.ffmpeg.writeFile('product.mp4', new Uint8Array(productData));
        
        // 裁切人像视频
        console.log('正在裁切人像视频...');
        console.log('裁切参数:', {
          startTime: this.startTime,
          endTime: this.endTime,
          duration: this.endTime - this.startTime,
          startTimeFormatted: this.formatTime(this.startTime),
          endTimeFormatted: this.formatTime(this.endTime),
          totalDuration: this.totalDuration,
          totalDurationFormatted: this.formatTime(this.totalDuration)
        });
        await this.ffmpeg.exec([
          '-i', 'human.mp4',
          '-ss', this.startTime.toString(),
          '-t', (this.endTime - this.startTime).toString(),
          '-c:v', 'libx264',
          '-c:a', 'aac',
          '-strict', 'experimental',
          'human_cut.mp4'
        ]);
        
        // 验证人像视频剪切结果
        const humanCutCheck = await this.checkFileExists('human_cut.mp4');
        if (!humanCutCheck.exists || humanCutCheck.size < 1000) {
          console.error('人像视频剪切失败，文件大小异常:', humanCutCheck.size, '字节');
          throw new Error('人像视频剪切失败，请尝试调整剪切时间范围');
        }
        console.log('人像视频剪切成功，文件大小:', humanCutCheck.size, '字节');
        
        // 裁切商品视频
        console.log('正在裁切商品视频...');
        console.log('商品视频裁切参数:', {
          startTime: this.productStartTime,
          endTime: this.productEndTime,
          duration: this.productEndTime - this.productStartTime,
          startTimeFormatted: this.formatTime(this.productStartTime),
          endTimeFormatted: this.formatTime(this.productEndTime),
          totalDuration: this.productDuration,
          totalDurationFormatted: this.formatTime(this.productDuration)
        });
        await this.ffmpeg.exec([
          '-i', 'product.mp4',
          '-ss', this.productStartTime.toString(),
          '-t', (this.productEndTime - this.productStartTime).toString(),
          '-c:v', 'libx264',
          '-c:a', 'aac',
          '-strict', 'experimental',
          'product_cut.mp4'
        ]);
        
        // 验证商品视频剪切结果
        const productCutCheck = await this.checkFileExists('product_cut.mp4');
        if (!productCutCheck.exists || productCutCheck.size < 1000) {
          console.error('商品视频剪切失败，文件大小异常:', productCutCheck.size, '字节');
          throw new Error('商品视频剪切失败，请尝试调整剪切时间范围');
        }
        console.log('商品视频剪切成功，文件大小:', productCutCheck.size, '字节');
        
        // 合并视频
        await this.mergeVideos();
      } catch (error) {
        console.error('视频剪切失败:', error);
        alert('视频剪切失败，请重试');
      }
    },
    async checkFileExists(filename) {
      try {
        console.log(`正在检查文件 ${filename}...`);
        const fileData = await this.ffmpeg.readFile(filename);
        const fileSize = fileData.length;
        console.log(`文件 ${filename} 检查: 大小 ${fileSize} 字节`);
        
        if (fileSize <= 0) {
          return { exists: false, size: 0, error: new Error('文件大小为0') };
        }
        
        return { exists: true, size: fileSize, data: fileData };
      } catch (readError) {
        console.error(`读取文件 ${filename} 失败:`, readError);
        return { exists: false, size: 0, error: readError };
      }
    },
    async cutAndMergeVideos() {
      let mergeTimeout = null;
      let outputBlob = null;
      try {
        this.isGenerating = true;
        this.mergeStatus = '正在准备视频处理...'
        this.mergeProgress = 0;
        console.log('开始剪切并合并视频...');

        // 检查FFmpeg是否已加载
        if (!this.ffmpeg?.loaded) {
          throw new Error('FFmpeg尚未加载，请稍后再试');
        }

        // 将人像视频写入FFmpeg虚拟文件系统
        this.mergeStatus = '正在加载人像视频...';
        this.mergeProgress = 5;
        console.log('正在写入人像视频...');
        const humanResponse = await fetch(this.humanVideoUrl);
        const humanData = await humanResponse.arrayBuffer();
        await this.ffmpeg.writeFile('human.mp4', new Uint8Array(humanData));
        
        // 将商品视频写入FFmpeg虚拟文件系统
        this.mergeStatus = '正在加载商品视频...';
        this.mergeProgress = 15;
        console.log('正在写入商品视频...');
        const productResponse = await fetch(this.productVideoUrl);
        const productData = await productResponse.arrayBuffer();
        await this.ffmpeg.writeFile('product.mp4', new Uint8Array(productData));
        
        // 裁切人像视频
        this.mergeStatus = '正在剪切人像视频...';
        this.mergeProgress = 25;
        console.log('正在裁切人像视频...');
        console.log('裁切参数:', {
          startTime: this.startTime,
          endTime: this.endTime,
          duration: this.endTime - this.startTime,
          startTimeFormatted: this.formatTime(this.startTime),
          endTimeFormatted: this.formatTime(this.endTime),
          totalDuration: this.totalDuration,
          totalDurationFormatted: this.formatTime(this.totalDuration)
        });
        await this.ffmpeg.exec([
          '-i', 'human.mp4',
          '-ss', this.startTime.toString(),
          '-t', (this.endTime - this.startTime).toString(),
          '-c:v', 'libx264',
          '-c:a', 'aac',
          '-strict', 'experimental',
          'human_cut.mp4'
        ]);
        
        // 验证人像视频剪切结果
        const humanCutCheck = await this.checkFileExists('human_cut.mp4');
        if (!humanCutCheck.exists || humanCutCheck.size < 1000) {
          console.error('人像视频剪切失败，文件大小异常:', humanCutCheck.size, '字节');
          throw new Error('人像视频剪切失败，请尝试调整剪切时间范围');
        }
        console.log('人像视频剪切成功，文件大小:', humanCutCheck.size, '字节');
        
        // 裁切商品视频
        this.mergeStatus = '正在剪切商品视频...';
        this.mergeProgress = 40;
        console.log('正在裁切商品视频...');
        console.log('商品视频裁切参数:', {
          startTime: this.productStartTime,
          endTime: this.productEndTime,
          duration: this.productEndTime - this.productStartTime,
          startTimeFormatted: this.formatTime(this.productStartTime),
          endTimeFormatted: this.formatTime(this.productEndTime),
          totalDuration: this.productDuration,
          totalDurationFormatted: this.formatTime(this.productDuration)
        });
        await this.ffmpeg.exec([
          '-i', 'product.mp4',
          '-ss', this.productStartTime.toString(),
          '-t', (this.productEndTime - this.productStartTime).toString(),
          '-c:v', 'libx264',
          '-c:a', 'aac',
          '-strict', 'experimental',
          'product_cut.mp4'
        ]);
        
        // 验证商品视频剪切结果
        const productCutCheck = await this.checkFileExists('product_cut.mp4');
        if (!productCutCheck.exists || productCutCheck.size < 1000) {
          console.error('商品视频剪切失败，文件大小异常:', productCutCheck.size, '字节');
          throw new Error('商品视频剪切失败，请尝试调整剪切时间范围');
        }
        console.log('商品视频剪切成功，文件大小:', productCutCheck.size, '字节');
        
        // 开始合并视频
        this.mergeStatus = '正在合并视频...';
        this.mergeProgress = 60;
        console.log('开始合并视频...');

        mergeTimeout = setTimeout(() => {
          console.error('视频合并操作超时');
          this.isGenerating = false;
        }, 180000);

        // 尝试三种不同的合并方法，按复杂度递增
        const mergeMethods = [
          // 方法2: 使用concat demuxer（带编码器设置）
          async () => {
            console.log('尝试方法2: 使用concat demuxer...');
            const concatContent = "file 'human_cut.mp4'\nfile 'product_cut.mp4'";
            await this.ffmpeg.writeFile('concat_list.txt', concatContent);
            await this.ffmpeg.exec([
              '-f', 'concat',
              '-safe', '0',
              '-i', 'concat_list.txt',
              '-c:v', 'libx264',
              '-preset', 'ultrafast',
              '-c:a', 'aac',
              '-strict', 'experimental',
              '-pix_fmt', 'yuv420p',
              '-movflags', '+faststart',
              '-y',
              'merged.mp4'
            ]);
            return 'concat demuxer with encoding';
          },
          
          // 方法3: 使用filter_complex
          async () => {
            console.log('尝试方法3: 使用filter_complex...');
            await this.ffmpeg.exec([
              '-i', 'human_cut.mp4',
              '-i', 'product_cut.mp4',
              '-filter_complex', '[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[outv][outa]',
              '-map', '[outv]',
              '-map', '[outa]',
              '-c:v', 'libx264',
              '-preset', 'ultrafast',
              '-c:a', 'aac',
              '-strict', 'experimental',
              '-pix_fmt', 'yuv420p',
              '-movflags', '+faststart',
              '-y',
              'merged.mp4'
            ]);
            return 'filter_complex';
          }
        ];

        let mergeSuccess = false;
        let successMethod = '';
        let lastError = null;

        for (let i = 0; i < mergeMethods.length; i++) {
          try {
            this.mergeStatus = `正在合并视频...`;
            this.mergeProgress = 60 + (i * 10);
            console.log(`执行合并方法 ${i+1}/${mergeMethods.length}...`);
            successMethod = await mergeMethods[i]();
            console.log(`方法 ${i+1} (${successMethod}) 执行成功`);

            // 检查输出文件
            try {
              this.mergeStatus = '正在处理输出文件...';
              this.mergeProgress = 85;
              console.log('开始检查输出文件...');
              
              const mergedCheck = await this.checkFileExists('merged.mp4');
              if (!mergedCheck.exists || mergedCheck.size < 1000) {
                console.warn(`方法 ${i+1} 生成的文件无效或过小: ${mergedCheck.size} 字节`);
                continue;
              }
              
              // 如果有钩子文本，添加到视频上
              if (this.hookText && this.hookText.trim() !== '') {
                this.mergeStatus = '正在添加文本...';
                this.mergeProgress = 90;
                await this.addTextToVideo('merged.mp4', 'output.mp4', this.hookText);
              } else {
                // 如果没有钩子文本，直接复制合并后的视频
                await this.ffmpeg.exec([
                  '-i', 'merged.mp4',
                  '-c', 'copy',
                  '-y',
                  'output.mp4'
                ]);
              }
              
              // 检查最终输出文件
              const outputCheck = await this.checkFileExists('output.mp4');
              if (!outputCheck.exists || outputCheck.size < 1000) {
                throw new Error(`最终输出文件无效或过小: ${outputCheck.size} 字节`);
              }
              
              // 直接从FFmpeg读取输出文件
              try {
                const outputData = await this.ffmpeg.readFile('output.mp4');
                const fileSize = outputData.length;
                
                if (fileSize <= 0) {
                  console.warn(`方法 ${i+1} 生成的文件无效或过小: ${fileSize} 字节`);
                  // 添加延迟，给FFmpeg更多时间完成写入
                  await new Promise(resolve => setTimeout(resolve, 1000));
                  continue;
                }
                
                console.log(`输出文件验证成功: ${fileSize} 字节`);
                
                // 创建ArrayBuffer并转换为Blob
                const buffer = outputData.buffer.slice(0);
                outputBlob = new Blob([buffer], { type: 'video/mp4' });
                console.log('成功创建输出Blob对象，大小:', outputBlob.size, '字节');
                
                mergeSuccess = true;
                break;
              } catch (blobError) {
                console.error('处理输出文件失败:', blobError);
                this.mergeStatus = `处理输出文件失败: ${blobError.message}`;
                // 继续尝试下一个方法，而不是立即失败
                console.log('将尝试下一个合并方法...');
              }
            } catch (fileError) {
              console.error(`检查输出文件时出错:`, fileError);
              this.mergeStatus = `检查文件错误: ${fileError.message}`;
              // 继续尝试下一个方法，而不是立即失败
              console.log('将尝试下一个合并方法...');
            }

          } catch (error) {
            console.error(`方法 ${i+1} 执行失败:`, error);
            lastError = error;
          }
        }

        if (mergeTimeout) {
          clearTimeout(mergeTimeout);
          mergeTimeout = null;
        }

        if (!mergeSuccess) {
          throw new Error(`所有合并方法都失败，最后错误: ${lastError?.message || '未知错误'}`);
        }

        this.mergeStatus = '视频处理完成';
        this.mergeProgress = 100;
        console.log(`视频合并成功，使用方法: ${successMethod}`);

        // 创建预览URL
        if (this.previewUrl) {
          URL.revokeObjectURL(this.previewUrl);
        }
        
        if (outputBlob) {
          try {
            this.previewUrl = URL.createObjectURL(outputBlob);
            console.log('预览URL已更新:', this.previewUrl);
            
            // 等待进度条动画完成后再关闭弹窗并滚动到预览区域
            setTimeout(() => {
              this.isGenerating = false;
              // 使用 nextTick 确保预览区域已渲染
              this.$nextTick(() => {
                const previewSection = document.querySelector('.mt-6.border-t');
                if (previewSection) {
                  previewSection.scrollIntoView({ behavior: 'smooth' });
                }
                // 重置预览视频的时间
                const video = this.$refs.previewVideo;
                if (video) {
                  video.currentTime = 0;
                }
              });
            }, 500);
            
          } catch (urlError) {
            console.error('创建预览URL失败:', urlError);
            throw new Error(`创建预览URL失败: ${urlError.message}`);
          }
        } else {
          console.error('无法创建预览URL: outputBlob为空');
          throw new Error('视频合并成功但无法创建预览，请重试');
        }

        this.isGenerating = false;
        // alert('视频合成完成');

      } catch (error) {
        console.error('视频处理过程出错:', error);
        alert(error.message || '视频处理失败，请重试');
        if (mergeTimeout) {
          clearTimeout(mergeTimeout);
        }
        this.isGenerating = false;
      }
    },
    cancelGeneration() {
      // 取消生成操作
      this.isGenerating = false;
      // 如果有其他需要清理的资源，在这里处理
      alert('已取消视频生成');
    },
    handlePreview() {
      const video = this.$refs.previewVideo;
      if (video) {
        video.currentTime = 0;
        video.play();
      }
    },
    handleDownload() {
      if (!this.previewUrl) {
        alert('请先生成视频');
        return;
      }
      
      // 确保文件名不为空
      const fileName = this.downloadFileName.trim() || `视频_${new Date().getTime()}`;
      
      // 创建下载链接
      const a = document.createElement('a');
      a.href = this.previewUrl;
      a.download = `${fileName}.mp4`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    },
    togglePlay() {
      const video = this.$refs.previewVideo;
      if (video) {
        if (video.paused) {
          video.play();
          this.isPlaying = true;
        } else {
          video.pause();
          this.isPlaying = false;
        }
      }
    },
    toggleMute() {
      const video = this.$refs.previewVideo;
      if (video) {
        video.muted = !video.muted;
        this.isMuted = video.muted;
      }
    },
    seekVideo(e) {
      const video = this.$refs.previewVideo;
      if (video) {
        const rect = e.target.getBoundingClientRect();
        const offsetX = e.clientX - rect.left;
        const percent = offsetX / rect.width;
        const targetTime = video.duration * percent;
        
        // 限制拖动范围在选定区域内
        if (targetTime >= this.startTime && targetTime <= this.endTime) {
          video.currentTime = targetTime;
        } else if (targetTime < this.startTime) {
          video.currentTime = this.startTime;
        } else if (targetTime > this.endTime) {
          video.currentTime = this.endTime;
        }
      }
    },
    startDragging(target) {
      // 如果正在播放视频，先暂停
      if (this.isHumanPlaying) {
        this.toggleHumanVideo();
      }
      if (this.isProductPlaying) {
        this.toggleProductVideo();
      }
      
      this.isDragging = true;
      this.dragTarget = target;
      document.addEventListener('mousemove', this.onDrag);
      document.addEventListener('mouseup', this.stopDragging);
      
      // 添加拖拽状态类
      const container = target.startsWith('product') 
        ? this.$refs.productVideo.parentElement
        : this.$refs.humanVideo.parentElement;
      container.classList.add('dragging');
    },
    
    stopDragging() {
      if (!this.isDragging) return;
      
      this.isDragging = false;
      document.removeEventListener('mousemove', this.onDrag);
      document.removeEventListener('mouseup', this.stopDragging);
      
      // 移除拖拽状态类
      const container = this.dragTarget.startsWith('product')
        ? this.$refs.productVideo.parentElement
        : this.$refs.humanVideo.parentElement;
      container.classList.remove('dragging');
      this.dragTarget = null;
    },
    
    updateVideoFrame(video, time) {
      if (video.readyState >= 2) {
        video.currentTime = time;
      }
    },
    
    onDrag(e) {
      if (!this.isDragging) return;
      
      const container = this.dragTarget.startsWith('product') 
        ? this.$refs.productVideo.parentElement
        : this.$refs.humanVideo.parentElement;
      const rect = container.getBoundingClientRect();
      const x = Math.max(rect.left, Math.min(e.clientX, rect.right));
      const percent = ((x - rect.left) / rect.width) * 100;
      
      requestAnimationFrame(() => {
        if (this.dragTarget === 'start') {
          const newStartPercent = Math.min(percent, this.endPercent - 1);
          if (newStartPercent !== this.startPercent) {
            this.startPercent = newStartPercent;
            this.startTime = Math.floor(this.totalDuration * (this.startPercent / 100));
            this.updateVideoFrame(this.$refs.humanVideo, this.startTime);
          }
        } else if (this.dragTarget === 'end') {
          const newEndPercent = Math.max(percent, this.startPercent + 1);
          if (newEndPercent !== this.endPercent) {
            this.endPercent = newEndPercent;
            this.endTime = Math.floor(this.totalDuration * (this.endPercent / 100));
            this.updateVideoFrame(this.$refs.humanVideo, this.endTime);
          }
        } else if (this.dragTarget === 'productStart') {
          const newProductStartPercent = Math.min(percent, this.productEndPercent - 1);
          if (newProductStartPercent !== this.productStartPercent) {
            this.productStartPercent = newProductStartPercent;
            const productDuration = this.$refs.productVideo.duration;
            this.productStartTime = Math.floor(productDuration * (this.productStartPercent / 100));
            this.updateVideoFrame(this.$refs.productVideo, this.productStartTime);
          }
        } else if (this.dragTarget === 'productEnd') {
          const newProductEndPercent = Math.max(percent, this.productStartPercent + 1);
          if (newProductEndPercent !== this.productEndPercent) {
            this.productEndPercent = newProductEndPercent;
            const productDuration = this.$refs.productVideo.duration;
            this.productEndTime = Math.floor(productDuration * (this.productEndPercent / 100));
          }
        }
      });
    },
    
    updateVideoFrame(videoElement, time) {
      if (videoElement && videoElement.readyState >= 2) {
        videoElement.currentTime = time;
      }
    },

     onDrag(e) {
      if (!this.isDragging) return;

      const container = this.dragTarget.startsWith('product')
        ? this.$refs.productVideo.parentElement
        : this.$refs.humanVideo.parentElement;
      const rect = container.getBoundingClientRect();
      const x = Math.max(rect.left, Math.min(e.clientX, rect.right));
      const percent = ((x - rect.left) / rect.width) * 100;

      requestAnimationFrame(() => {
        if (this.dragTarget === 'start') {
          const newStartPercent = Math.min(percent, this.endPercent - 1);
          if (newStartPercent !== this.startPercent) {
            this.startPercent = newStartPercent;
            this.startTime = Math.floor(this.totalDuration * (this.startPercent / 100));
            this.updateVideoFrame(this.$refs.humanVideo, this.startTime);
          }
        } else if (this.dragTarget === 'end') {
          const newEndPercent = Math.max(percent, this.startPercent + 1);
          if (newEndPercent !== this.endPercent) {
            this.endPercent = newEndPercent;
            this.endTime = Math.floor(this.totalDuration * (this.endPercent / 100));
          }
        } else if (this.dragTarget === 'productStart') {
          const newProductStartPercent = Math.min(percent, this.productEndPercent - 1);
          if (newProductStartPercent !== this.productStartPercent) {
            this.productStartPercent = newProductStartPercent;
            const productDuration = this.$refs.productVideo.duration;
            this.productStartTime = Math.floor(productDuration * (this.productStartPercent / 100));
            this.updateVideoFrame(this.$refs.productVideo, this.productStartTime);
          }
        } else if (this.dragTarget === 'productEnd') {
          const newProductEndPercent = Math.max(percent, this.productStartPercent + 1);
          if (newProductEndPercent !== this.productEndPercent) {
            this.productEndPercent = newProductEndPercent;
            const productDuration = this.$refs.productVideo.duration;
            this.productEndTime = Math.floor(productDuration * (this.productEndPercent / 100));
          }
        }
      });
    },

    stopDragging() {
      this.isDragging = false;
      document.removeEventListener('mousemove', this.onDrag);
      document.removeEventListener('mouseup', this.stopDragging);
    },

    // 处理点击蒙层或视频外区域时暂停视频
    handleOutsideClick(event) {
      // 如果正在拖拽，不处理点击事件
      if (this.isDragging) return;
      
      // 检查是否点击了人像视频的蒙层区域
      if (this.isHumanPlaying) {
        const humanVideo = this.$refs.humanVideo;
        const humanContainer = humanVideo.parentElement;
        if (humanContainer.contains(event.target)) {
          // 获取点击位置相对于容器的百分比
          const rect = humanContainer.getBoundingClientRect();
          const x = event.clientX - rect.left;
          const percent = (x / rect.width) * 100;
          
          // 如果点击了蒙层区域，暂停视频
          if (percent <= this.startPercent || percent >= this.endPercent) {
            this.isHumanPlaying = false;
            humanVideo.pause();
          }
        }
      }
      
      // 检查是否点击了商品视频的蒙层区域
      if (this.isProductPlaying) {
        const productVideo = this.$refs.productVideo;
        const productContainer = productVideo.parentElement;
        if (productContainer.contains(event.target)) {
          // 获取点击位置相对于容器的百分比
          const rect = productContainer.getBoundingClientRect();
          const x = event.clientX - rect.left;
          const percent = (x / rect.width) * 100;
          
          // 如果点击了蒙层区域，暂停视频
          if (percent <= this.productStartPercent || percent >= this.productEndPercent) {
            this.isProductPlaying = false;
            productVideo.pause();
          }
        }
      }
      
      // 检查是否点击了预览视频外部区域
      if (this.isPlaying && this.$refs.previewVideo) {
        const previewVideo = this.$refs.previewVideo;
        const previewContainer = previewVideo.parentElement;
        if (!previewContainer.contains(event.target) && !event.target.closest('.flex.items-center.text-white')) {
          this.isPlaying = false;
          previewVideo.pause();
        }
      }
    },
    toggleHumanVideo() {
      const video = this.$refs.humanVideo;
      if (video) {
        if (video.paused) {
          // 如果视频当前不在选定区域内，先将其设置到开始位置
          if (video.currentTime < this.startTime || video.currentTime > this.endTime) {
            video.currentTime = this.startTime;
          }
          video.play();
          this.isHumanPlaying = true;
          
          // 添加监听器，当视频播放到结束区域时暂停
          const checkTime = () => {
            if (video.currentTime >= this.endTime) {
              video.pause();
              this.isHumanPlaying = false;
              video.removeEventListener('timeupdate', checkTime);
            }
          };
          video.addEventListener('timeupdate', checkTime);
        } else {
          video.pause();
          this.isHumanPlaying = false;
        }
      }
    },
    toggleProductVideo() {
      const video = this.$refs.productVideo;
      if (video) {
        if (video.paused) {
          // 如果视频当前不在选定区域内，先将其设置到开始位置
          if (video.currentTime < this.productStartTime || video.currentTime > this.productEndTime) {
            video.currentTime = this.productStartTime;
          }
          video.play();
          this.isProductPlaying = true;
          
          // 添加监听器，当视频播放到结束区域时暂停
          const checkTime = () => {
            if (video.currentTime >= this.productEndTime) {
              video.pause();
              this.isProductPlaying = false;
              video.removeEventListener('timeupdate', checkTime);
            }
          };
          video.addEventListener('timeupdate', checkTime);
        } else {
          video.pause();
          this.isProductPlaying = false;
        }
      }
    },
    updateVideoTime(time, type) {
      const video = type === 'human' ? this.$refs.humanVideo : this.$refs.productVideo;
      if (video) {
        video.currentTime = time;
      }
    },
    formatTime(seconds) {
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = Math.floor(seconds % 60);
      return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
    },
    async extractFramesFromVideo(videoUrl) {
      return new Promise(async (resolve, reject) => {
        try {
          // 创建临时video元素
          const video = document.createElement('video');
          video.src = videoUrl;
          video.crossOrigin = 'anonymous';

          // 创建canvas元素
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');

          // 等待视频加载完成
          await new Promise((resolve, reject) => {
            video.onloadedmetadata = () => resolve();
            video.onerror = () => reject(new Error('视频加载失败'));
          });

          // 设置canvas尺寸
          canvas.width = this.keyframeWidth;
          canvas.height = this.keyframeHeight;

          // 提取14个关键帧
          const frames = [];
          const frameCount = 14;
          const interval = video.duration / (frameCount - 1);

          for (let i = 0; i < frameCount; i++) {
            video.currentTime = i * interval;
            await new Promise(resolve => {
              video.onseeked = () => {
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                frames.push(canvas.toDataURL('image/jpeg', 0.7));
                resolve();
              };
            });
          }

          resolve(frames);
        } catch (error) {
          console.error('提取视频帧失败:', error);
          reject(error);
        }
      });
    },
    async translateHook() {
      if (!this.hookText) {
        alert('请先输入需要翻译的文本');
        return;
      }
      
      const originalText = this.hookText;
      this.hookText = '翻译中...';
      
      try {
        // 使用MyMemory翻译API
        const fromLang = this.isChineseText(originalText) ? 'zh-CN' : 'en';
        const toLang = this.isChineseText(originalText) ? 'en' : 'zh-CN';
        const url = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(originalText)}&langpair=${fromLang}|${toLang}`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
          throw new Error('翻译请求失败');
        }
        
        const data = await response.json();
        
        if (data.responseData && data.responseData.translatedText) {
          this.hookText = data.responseData.translatedText;
        } else {
          throw new Error('未获取到翻译结果');
        }
      } catch (error) {
        console.error('翻译出错:', error);
        
        // 如果API调用失败，回退到模拟翻译
        if (this.isChineseText(originalText)) {
          this.hookText = this.mockTranslateToEnglish(originalText);
        } else {
          this.hookText = this.mockTranslateToChinese(originalText);
        }
        
        // 显示错误提示
        alert('翻译服务暂时不可用，已使用本地翻译');
      }
    },
    isChineseText(text) {
      // 简单判断文本是否包含中文字符
      return /[\u4e00-\u9fa5]/.test(text);
    },
    
    mockTranslateToEnglish(text) {
      // 模拟中译英（实际应用中应替换为真实的翻译API）
      const mockTranslations = {
        '这个产品很好用': 'This product works great',
        '推荐购买': 'Recommended purchase',
        '性价比很高': 'Great value for money',
        '质量不错': 'Good quality',
        '快来购买': 'Come and buy now'
      };
      
      return mockTranslations[text] || 'Translated text (English)';
    },
    
    mockTranslateToChinese(text) {
      // 模拟英译中（实际应用中应替换为真实的翻译API）
      const mockTranslations = {
        'This product works great': '这个产品很好用',
        'Recommended purchase': '推荐购买',
        'Great value for money': '性价比很高',
        'Good quality': '质量不错',
        'Come and buy now': '快来购买'
      };
      
      return mockTranslations[text] || '翻译后的文本 (中文)';
    },
    // 修改 addTextToVideo 方法，使用更简单的方法
    async addTextToVideo(inputFile, outputFile, text) {
      console.log('开始添加文本到视频:', text);
      
      try {
        // 尝试使用overlay方法添加文本
        console.log('尝试使用overlay方法添加文本...');
        
        // 创建一个带有文本的图像
        const width = 640;
        const height = 240;
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        
        // 清除背景（透明）
        ctx.clearRect(0, 0, width, height);
        
        // 设置字体大小
        let fontSize = text.length <= 10 ? 72 : 64; // 短文本使用更大字体
        ctx.font = `bold ${fontSize}px Arial, sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        // 添加文本，调整左右间距
        const maxTextWidth = width - 100;
        
        // 处理文本换行
        const words = text.split(' ');
        let lines = [];
        let currentLine = '';
        
        // 如果是中文，按字符长度分割
        if (this.isChineseText(text)) {
          // 中文每5-8个字符左右换行
          const charsPerLine = Math.floor(maxTextWidth / (fontSize * 0.6));
          
          for (let i = 0; i < text.length; i += charsPerLine) {
            lines.push(text.substring(i, Math.min(i + charsPerLine, text.length)));
          }
        } else {
          // 英文按单词分割并计算宽度
          for (let i = 0; i < words.length; i++) {
            const testLine = currentLine + words[i] + ' ';
            const metrics = ctx.measureText(testLine);
            const testWidth = metrics.width;
            
            if (testWidth > maxTextWidth && i > 0) {
              lines.push(currentLine);
              currentLine = words[i] + ' ';
            } else {
              currentLine = testLine;
            }
          }
          lines.push(currentLine);
        }
        
        // 如果文本太长，自动调整字体大小
        while ((lines.length > 3 || ctx.measureText(lines[0]).width > maxTextWidth) && fontSize > 40) {
          fontSize -= 4;
          ctx.font = `bold ${fontSize}px Arial, sans-serif`;
          
          // 重新计算换行
          lines = [];
          currentLine = '';
          
          if (this.isChineseText(text)) {
            const charsPerLine = Math.floor(maxTextWidth / (fontSize * 0.6));
            for (let i = 0; i < text.length; i += charsPerLine) {
              lines.push(text.substring(i, Math.min(i + charsPerLine, text.length)));
            }
          } else {
            for (let i = 0; i < words.length; i++) {
              const testLine = currentLine + words[i] + ' ';
              const metrics = ctx.measureText(testLine);
              const testWidth = metrics.width;
              
              if (testWidth > maxTextWidth && i > 0) {
                lines.push(currentLine);
                currentLine = words[i] + ' ';
              } else {
                currentLine = testLine;
              }
            }
            lines.push(currentLine);
          }
        }
        
        // 计算文本区域大小
        const lineHeight = fontSize * 1.2;
        const totalTextHeight = lineHeight * lines.length;
        
        // 确保所有文本都能显示，计算每行文本的最大宽度
        const textWidths = lines.map(line => ctx.measureText(line).width);
        const maxWidth = Math.max(...textWidths);
        
        // 计算背景矩形的尺寸和位置
        const padding = 30; // 增加内边距
        
        // 确保背景有最小尺寸
        const minBgWidth = Math.max(maxWidth + padding * 2, 300); // 最小宽度300px
        const minBgHeight = Math.max(totalTextHeight + padding * 2, fontSize * 2.5); // 最小高度为字体大小的2.5倍
        
        const bgWidth = minBgWidth;
        const bgHeight = minBgHeight;
        const bgX = (width - bgWidth) / 2;
        const bgY = (height - bgHeight) / 2;
        
        // 绘制圆角白色背景
        const radius = Math.min(30, bgHeight / 4); // 圆角半径，但不超过高度的1/4
        ctx.fillStyle = 'white';
        
        // 绘制圆角矩形
        ctx.beginPath();
        ctx.moveTo(bgX + radius, bgY);
        ctx.lineTo(bgX + bgWidth - radius, bgY);
        ctx.quadraticCurveTo(bgX + bgWidth, bgY, bgX + bgWidth, bgY + radius);
        ctx.lineTo(bgX + bgWidth, bgY + bgHeight - radius);
        ctx.quadraticCurveTo(bgX + bgWidth, bgY + bgHeight, bgX + bgWidth - radius, bgY + bgHeight);
        ctx.lineTo(bgX + radius, bgY + bgHeight);
        ctx.quadraticCurveTo(bgX, bgY + bgHeight, bgX, bgY + bgHeight - radius);
        ctx.lineTo(bgX, bgY + radius);
        ctx.quadraticCurveTo(bgX, bgY, bgX + radius, bgY);
        ctx.closePath();
        
        // 添加轻微阴影效果
        ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
        ctx.shadowBlur = 15;
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 5;
        ctx.fill();
        
        // 重置阴影，避免影响文字
        ctx.shadowColor = 'transparent';
        ctx.shadowBlur = 0;
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 0;
        
        // 绘制黑色文本
        ctx.fillStyle = 'black';
        
        // 调整文本垂直居中位置
        const startY = bgY + (bgHeight / 2) - ((lines.length - 1) * lineHeight / 2);
        
        for (let i = 0; i < lines.length; i++) {
          ctx.fillText(lines[i], width / 2, startY + i * lineHeight);
        }
        
        // 将canvas转换为图像数据
        const dataUrl = canvas.toDataURL('image/png');
        const binaryString = atob(dataUrl.split(',')[1]);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        
        // 将图像写入FFmpeg
        await this.ffmpeg.writeFile('text_overlay.png', bytes);
        
        // 使用overlay滤镜添加图像 - 调整位置到顶部居中
        await this.ffmpeg.exec([
          '-i', inputFile,
          '-i', 'text_overlay.png',
          '-filter_complex', '[0:v][1:v]overlay=(W-w)/2:50:enable=\'between(t,0,999)\'',
          '-c:v', 'libx264',
          '-preset', 'ultrafast',
          '-c:a', 'copy',
          '-y',
          outputFile
        ]);
        
        const overlayCheck = await this.checkFileExists(outputFile);
        if (overlayCheck.exists && overlayCheck.size > 1000) {
          console.log('Overlay方法添加文本成功');
          return true;
        }
        
        // 如果overlay方法失败，尝试其他方法...
        // ... 现有的备用方法代码 ...
        
      } catch (error) {
        console.error('添加文本到视频失败:', error);
        
        // 如果所有方法都失败，直接复制原视频
        console.log('所有添加文本方法都失败，直接复制原视频...');
        await this.ffmpeg.exec([
          '-i', inputFile,
          '-c', 'copy',
          '-y',
          outputFile
        ]);
        
        return false;
      }
    },
    downloadOriginalVideo(type) {
      try {
        const videoUrl = type === 'human' ? this.humanVideoUrl : this.productVideoUrl;
        const fileName = type === 'human' ? '人像视频_' : '商品视频_';
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').substring(0, 19);
        
        // 使用fetch获取视频文件
        fetch(videoUrl)
          .then(response => response.blob())
          .then(blob => {
            // 创建blob URL
            const blobUrl = URL.createObjectURL(blob);
            
            // 创建下载链接
            const a = document.createElement('a');
            a.href = blobUrl;
            a.download = `${fileName}${timestamp}.mp4`;
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            
            // 清理
            setTimeout(() => {
              document.body.removeChild(a);
              URL.revokeObjectURL(blobUrl);
            }, 100);
          })
          .catch(error => {
            console.error('下载视频失败:', error);
            alert('下载视频失败，请重试');
          });
      } catch (error) {
        console.error('下载视频出错:', error);
        alert('下载视频出错，请重试');
      }
    },
  },
};
</script>
<style scoped>
.aspect-video {
  aspect-ratio: 16/9;
}
.human-keyframes img,
.product-keyframes img {
  transition: opacity 0.2s ease;
}

.dragging .human-keyframes img,
.dragging .product-keyframes img {
  transition: none;
}
</style>
