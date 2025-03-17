<template>
  <!-- 主要内容区 -->
  <div class="bg-white rounded-lg p-8 mb-8">
    <div class="grid grid-cols-2 gap-8">
      <!-- 左侧上传区域 -->
      <div class="grid grid-cols-2 gap-4">
        <div
          class="border-2 border-dashed border-blue-200 rounded-lg p-4 flex flex-col items-center justify-center min-h-[200px]"
          :class="{ 
            'bg-gray-50': !personImage, 
            'border-blue-400': isDraggingPerson 
          }"
          @dragover.prevent="isDraggingPerson = true"
          @dragleave.prevent="isDraggingPerson = false"
          @drop.prevent="handlePersonDrop"
        >
          <input
            type="file"
            accept="image/*"
            class="hidden"
            ref="personInput"
            @change="handlePersonImageUpload"
          />
          <div v-if="!personImage" class="text-center">
            <i class="fas fa-user text-4xl text-blue-400 mb-4"></i>
            <p class="text-gray-600 mb-4">上传人像照片</p>
            <p class="text-gray-500 text-sm mb-4">支持拖拽上传</p>
            <button
              class="bg-blue-500 text-white px-6 py-2 !rounded-button whitespace-nowrap"
              @click="$refs.personInput.click()"
            >
              选择图片
            </button>
          </div>
          <div v-else class="relative w-full h-full">
            <button 
              class="absolute top-0 right-0 bg-red-500 text-white rounded-full w-8 h-8 flex items-center justify-center"
              @click="clearPersonImage"
            >
              <i class="fas fa-times"></i>
            </button>
            <div class="w-full h-full flex items-center justify-center">
              <img
                :src="personImage"
                alt="uploaded person"
                class="max-w-full max-h-[200px] object-contain"
              />
            </div>
          </div>
        </div>
        <!-- 人像提示词输入框 -->
        <div class="mt-3">
          <label class="block text-sm font-medium text-gray-700 mb-1">人像提示词</label>
          <input
            v-model="personPrompt"
            type="text"
            placeholder="请输入人像相关提示词"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div
          class="border-2 border-dashed border-blue-200 rounded-lg p-4 flex flex-col items-center justify-center min-h-[200px]"
          :class="{ 
            'bg-gray-50': !productImage, 
            'border-blue-400': isDraggingProduct 
          }"
          @dragover.prevent="isDraggingProduct = true"
          @dragleave.prevent="isDraggingProduct = false"
          @drop.prevent="handleProductDrop"
        >
          <input
            type="file"
            accept="image/*"
            class="hidden"
            ref="productInput"
            @change="handleProductImageUpload"
          />
          <div v-if="!productImage" class="text-center">
            <i class="fas fa-box text-4xl text-blue-400 mb-4"></i>
            <p class="text-gray-600 mb-4">上传商品照片</p>
            <p class="text-gray-500 text-sm mb-4">支持拖拽上传</p>
            <button
              class="bg-blue-500 text-white px-6 py-2 !rounded-button whitespace-nowrap"
              @click="$refs.productInput.click()"
            >
              选择图片
            </button>
          </div>
          <div v-else class="relative w-full h-full">
            <button 
              class="absolute top-0 right-0 bg-red-500 text-white rounded-full w-8 h-8 flex items-center justify-center"
              @click="clearProductImage"
            >
              <i class="fas fa-times"></i>
            </button>
            <div class="w-full h-full flex items-center justify-center">
              <img
                :src="productImage"
                alt="uploaded product"
                class="max-w-full max-h-[200px] object-contain"
              />
            </div>
          </div>
        </div>
        <!-- 商品提示词输入框 -->
        <div class="mt-3">
          <label class="block text-sm font-medium text-gray-700 mb-1">商品提示词</label>
          <input
            v-model="productPrompt"
            type="text"
            placeholder="请输入商品相关提示词"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>
      <!-- 右侧标签选择区域 -->
      <div>
        <h3 class="text-lg font-medium mb-4">场景标签</h3>
        <div class="space-y-6">
          <div v-if="loading" class="flex justify-center py-4">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
          <div v-else-if="categories.length === 0" class="text-center py-4 text-gray-500">
            暂无分类数据
          </div>
          <div v-else>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="category in categories"
                :key="category.name"
                :class="{
                  'bg-blue-500 text-white': selectedTags.includes(category.name_cn),
                  'bg-gray-100 text-gray-700': !selectedTags.includes(category.name_cn),
                }"
                class="px-4 py-1 rounded-full !rounded-button whitespace-nowrap"
                @click="toggleTag(category.name_cn)"
              >
                {{ category.name_cn }}
              </button>
            </div>
          </div>
        </div>
        <button
          class="w-full bg-blue-500 text-white py-3 mt-8 !rounded-button whitespace-nowrap"
          :disabled="!canGenerateVideo || isGenerating"
          :class="{ 'opacity-50 cursor-not-allowed': !canGenerateVideo || isGenerating }"
          @click="generateVideo"
        >
          <span v-if="isGenerating">
            <i class="fas fa-spinner fa-spin mr-2"></i>生成中...
          </span>
          <span v-else>生成视频</span>
        </button>
      </div>
    </div>
  </div>
  <!-- 历史记录区域 -->
  <div class="bg-white rounded-lg p-8">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-medium">生成记录</h2>
      <div class="flex gap-4 items-center">
        <button 
          @click="fetchVideoRecords(false)" 
          class="text-blue-500 hover:text-blue-700 mr-4"
          :disabled="isLoadingRecords"
        >
          <i class="fas fa-sync-alt" :class="{ 'animate-spin': isLoadingRecords }"></i>
        </button>
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :class="{
            'text-blue-500 border-blue-500': currentTab === tab.id,
          }"
          class="px-4 py-2 border-b-2 border-transparent !rounded-button whitespace-nowrap"
          @click="currentTab = tab.id"
        >
          {{ tab.name }}
        </button>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="isLoadingRecords" class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
    </div>
    
    <!-- 空状态 -->
    <div v-else-if="!records || records.length === 0" class="text-center py-12 text-gray-500">
      暂无生成记录
    </div>
    
    <!-- 记录列表 -->
    <div v-else class="grid grid-cols-4 gap-6">
      <div
        v-for="record in filteredRecords()"
        :key="record.id"
        class="bg-gray-50 rounded-lg p-4"
      >
        <div class="aspect-video mb-3 rounded-lg overflow-hidden">
          <!-- 根据状态显示不同内容 -->
          <div v-if="record.status === 0 || record.status === 1" 
               class="w-full h-full flex items-center justify-center bg-gray-100">
            <div class="text-center">
              <i class="fas fa-spinner fa-spin text-blue-500 text-2xl mb-2" v-if="record.status === 1"></i>
              <i class="fas fa-clock text-yellow-500 text-2xl mb-2" v-else></i>
              <p>{{ getStatusText(record) }}</p>
            </div>
          </div>
          <div v-else-if="record.status === 3" 
               class="w-full h-full flex items-center justify-center bg-gray-100">
            <div class="text-center">
              <i class="fas fa-exclamation-triangle text-red-500 text-2xl mb-2"></i>
              <p>生成失败</p>
            </div>
          </div>
          <img
            v-else
            :src="record.image"
            alt="record"
            class="w-full h-full object-cover"
          />
        </div>
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-600">{{ record.date }}</span>
            <span
              :class="{
                'bg-blue-100 text-blue-600': record.type === 'product',
                'bg-purple-100 text-purple-600': record.type === 'person',
                'bg-yellow-100 text-yellow-600': record.status === 0,
                'bg-blue-100 text-blue-600': record.status === 1,
                'bg-green-100 text-green-600': record.status === 2,
                'bg-red-100 text-red-600': record.status === 3,
              }"
              class="text-xs px-2 py-1 rounded-full"
            >
              {{ getStatusText(record) }}
            </span>
          </div>
          <div class="flex gap-2">
            <!-- 只有生成成功的视频才能编辑 -->
            <button
              v-if="record.status === 2"
              class="text-blue-500 !rounded-button whitespace-nowrap"
              @click="handleEdit(record)"
            >
              <i class="fas fa-edit"></i>
            </button>
            <!-- 只有已完成或失败的视频才能删除 -->
            <button 
              v-if="record.status === 2 || record.status === 3"
              class="text-red-500 !rounded-button whitespace-nowrap"
              @click="handleDelete(record)"
            >
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
        <div class="flex flex-wrap gap-1">
          <span
            v-for="tag in record.tags"
            :key="tag"
            class="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded-full"
          >
            {{ tag }}
          </span>
        </div>
      </div>
    </div>
    
    <!-- 分页控件 -->
    <div v-if="totalRecords > pageSize" class="flex justify-center mt-6">
      <button
        :disabled="currentPage === 1"
        :class="{ 'opacity-50 cursor-not-allowed': currentPage === 1 }"
        class="px-4 py-2 bg-gray-200 rounded-l-lg !rounded-button whitespace-nowrap"
        @click="changePage(currentPage - 1)"
      >
        上一页
      </button>
      <span class="px-4 py-2 bg-gray-100">{{ currentPage }} / {{ Math.ceil(totalRecords / pageSize) }}</span>
      <button
        :disabled="currentPage >= Math.ceil(totalRecords / pageSize)"
        :class="{ 'opacity-50 cursor-not-allowed': currentPage >= Math.ceil(totalRecords / pageSize) }"
        class="px-4 py-2 bg-gray-200 rounded-r-lg !rounded-button whitespace-nowrap"
        @click="changePage(currentPage + 1)"
      >
        下一页
      </button>
    </div>
  </div>

  <!-- 视频编辑弹窗 -->
  <VideoEditModal
    v-if="showEditModal"
    :record="currentEditRecord"
    @close="closeEditModal"
  />
</template>

<script>
import VideoEditModal from "./VideoEditModal.vue";
import { getCategories } from "../api/category.js";
import { 
  generateVideo as apiGenerateVideo, 
  getUserVideos,
  deleteUserVideo 
} from "../api/video_generation.js";

export default {
  name: "AIVideo",
  components: {
    VideoEditModal,
  },
  data() {
    return {
      personImage: "",
      productImage: "",
      personPrompt: "",
      productPrompt: "",
      selectedTags: [],
      currentTab: "all",
      showEditModal: false,
      currentEditRecord: null,
      loading: true,
      categories: [],
      tabs: [
        { id: "all", name: "全部记录" },
        { id: "pending", name: "待处理" },
        { id: "completed", name: "已完成" },
        { id: "failed", name: "失败" }
      ],
      records: [],
      isGenerating: false,
      isLoadingRecords: false,
      currentPage: 1,
      pageSize: 10,
      totalRecords: 0,
      refreshInterval: null,
      // 添加拖拽状态
      isDraggingPerson: false,
      isDraggingProduct: false,
    };
  },
  computed: {
    canGenerateVideo() {
      // 检查是否可以生成视频
      return (
        (this.personImage || this.productImage) && 
        this.selectedTags.length > 0
      );
    }
  },
  methods: {
    toggleTag(tag) {
      if (this.selectedTags.includes(tag)) {
        this.selectedTags = this.selectedTags.filter((t) => t !== tag);
      } else {
        // 清空之前选中的标签，实现单选功能
        this.selectedTags = [tag];
      }
    },
    handleEdit(record) {
      this.currentEditRecord = record;
      this.showEditModal = true;
    },
    closeEditModal() {
      this.showEditModal = false;
      this.currentEditRecord = null;
    },
    handlePersonDrop(event) {
      this.isDraggingPerson = false;
      const file = event.dataTransfer.files[0];
      if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.personImage = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    },
    handleProductDrop(event) {
      this.isDraggingProduct = false;
      const file = event.dataTransfer.files[0];
      if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.productImage = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    },
    handlePersonImageUpload(event) {
      this.isDraggingPerson = false;
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.personImage = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    },
    handleProductImageUpload(event) {
      this.isDraggingProduct = false;
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.productImage = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    },
    clearProductImage() {
      this.productImage = "";
      this.isDraggingProduct = false;
      if (this.$refs.productInput) this.$refs.productInput.value = "";
    },
    clearPersonImage() {
      this.personImage = "";
      this.isDraggingPerson = false;
      if (this.$refs.personInput) this.$refs.personInput.value = "";
    },
    async fetchCategories() {
      try {
        this.loading = true;
        const response = await getCategories();
        if (response && response.categories) {
          this.categories = response.categories;
        }
      } catch (error) {
        console.error('获取分类失败:', error);
      } finally {
        this.loading = false;
      }
    },
    async fetchVideoRecords(silent = false) {
      try {
        // 只有在非静默模式下才显示加载状态
        if (!silent) {
          this.isLoadingRecords = true;
        }
        
        const response = await getUserVideos(this.currentPage, this.pageSize);
        console.log('获取到的视频记录:', response);
        
        if (response && response.videos && Array.isArray(response.videos)) {
          // 处理新获取的数据
          const newRecords = response.videos.map(video => {
            return {
              id: video.task_id || 0,
              type: video.person_video_url ? "person" : "product",
              image: video.product_image_url || video.person_image_url || 'https://via.placeholder.com/300x200?text=No+Image',
              date: video.created_at ? new Date(video.created_at).toLocaleString() : '未知时间',
              tags: video.product_categories ? 
                    (typeof video.product_categories === 'string' ? 
                      video.product_categories.split(',') : 
                      Array.isArray(video.product_categories) ? 
                        video.product_categories : []) : 
                    [],
              status: typeof video.status === 'number' ? video.status : 0,
              personVideoUrl: video.person_video_url || '',
              productVideoUrl: video.product_video_url || '',
              personImageUrl: video.person_image_url || '',
              productImageUrl: video.product_image_url || ''
            };
          });
          
          // 检查数据是否有变化
          const hasChanges = this.checkForChanges(this.records, newRecords);
          
          // 只有在数据有变化或非静默模式下才更新记录
          if (hasChanges || !silent) {
            console.log('数据有变化，更新记录');
            this.records = newRecords;
            this.totalRecords = response.total || 0;
          } else {
            console.log('数据无变化，保持当前状态');
          }
        } else if (!silent) {
          // 只有在非静默模式下才清空记录
          console.warn('响应中没有有效的 videos 数组:', response);
          this.records = [];
          this.totalRecords = 0;
        }
      } catch (error) {
        console.error('获取视频记录失败:', error);
        // 只有在非静默模式下才清空记录
        if (!silent) {
          this.records = [];
          this.totalRecords = 0;
        }
      } finally {
        // 只有在非静默模式下才更新加载状态
        if (!silent) {
          this.isLoadingRecords = false;
        }
      }
    },
    // 检查两组记录是否有变化
    checkForChanges(oldRecords, newRecords) {
      // 如果记录数量不同，肯定有变化
      if (oldRecords.length !== newRecords.length) {
        return true;
      }
      
      // 创建一个映射，用于快速查找旧记录
      const oldRecordsMap = new Map();
      oldRecords.forEach(record => {
        oldRecordsMap.set(record.id, record);
      });
      
      // 检查每条新记录是否与旧记录有差异
      for (const newRecord of newRecords) {
        const oldRecord = oldRecordsMap.get(newRecord.id);
        
        // 如果找不到对应的旧记录，说明有变化
        if (!oldRecord) {
          return true;
        }
        
        // 检查关键字段是否有变化
        if (
          oldRecord.status !== newRecord.status ||
          oldRecord.personVideoUrl !== newRecord.personVideoUrl ||
          oldRecord.productVideoUrl !== newRecord.productVideoUrl
        ) {
          return true;
        }
      }
      
      // 如果所有记录都没有变化，返回 false
      return false;
    },
    async generateVideo() {
      if (!this.canGenerateVideo) {
        this.$toast.warning('请上传至少一张图片并选择标签');
        return;
      }
      
      try {
        // 创建 FormData 对象
        const formData = new FormData();
        
        // 添加提示词 - 确保即使为空也发送字符串
        formData.append('person_prompt', this.personPrompt || '默认人像提示词');
        formData.append('product_prompt', this.productPrompt || '默认商品提示词');
        
        // 添加分类标签 - 使用英文名
        if (this.selectedTags.length > 0) {
          // 将选中的中文标签转换为英文标签
          const selectedEnglishTags = this.selectedTags.map(chineseName => {
            // 查找对应的分类对象
            const category = this.categories.find(cat => cat.name_cn === chineseName);
            // 如果找到了，返回英文名，否则返回中文名
            return category ? category.name : chineseName;
          });
          
          // 添加到表单
          selectedEnglishTags.forEach(tag => {
            formData.append('person_categories', tag);
            formData.append('product_categories', tag);
          });
        } else {
          // 如果没有选择标签，添加一个默认标签
          formData.append('person_categories', 'default');
          formData.append('product_categories', 'default');
        }
        
        // 添加图片文件
        if (this.personImage) {
          // 将 base64 图片转换为 Blob
          const personBlob = this.dataURLtoBlob(this.personImage);
          formData.append('person_photo', personBlob, 'person.jpg');
        }
        
        if (this.productImage) {
          // 将 base64 图片转换为 Blob
          const productBlob = this.dataURLtoBlob(this.productImage);
          formData.append('product_photo', productBlob, 'product.jpg');
        }
        
        // 显示加载状态
        this.isGenerating = true;
        
        // 调用生成视频 API
        const response = await apiGenerateVideo(formData);
        
        if (response && response.status === 'processing') {
          this.$toast.success(`视频生成请求已提交，任务ID: ${response.task_id}`);
          
          // 清空表单
          this.resetForm();
          
          // 刷新历史记录
          await this.fetchVideoRecords();
        } else {
          this.$toast.error('视频生成请求失败: ' + (response.message || '未知错误'));
        }
      } catch (error) {
        console.error('生成视频错误:', error);
        // 显示更详细的错误信息
        let errorMessage = '未知错误';
        if (error.message) {
          try {
            // 尝试解析错误消息中的 JSON
            const errorJson = JSON.parse(error.message);
            if (Array.isArray(errorJson)) {
              errorMessage = errorJson.map(err => `${err.loc.join('.')}：${err.msg}`).join('\n');
            } else {
              errorMessage = error.message;
            }
          } catch (e) {
            errorMessage = error.message;
          }
        }
        this.$toast.error('生成视频失败: ' + errorMessage);
      } finally {
        this.isGenerating = false;
      }
    },
    
    // 将 dataURL 转换为 Blob
    dataURLtoBlob(dataURL) {
      const arr = dataURL.split(',');
      const mime = arr[0].match(/:(.*?);/)[1];
      const bstr = atob(arr[1]);
      let n = bstr.length;
      const u8arr = new Uint8Array(n);
      
      while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
      }
      
      return new Blob([u8arr], { type: mime });
    },
    
    // 重置表单
    resetForm() {
      this.personImage = '';
      this.productImage = '';
      this.personPrompt = '';
      this.productPrompt = '';
      this.selectedTags = [];
      if (this.$refs.personInput) this.$refs.personInput.value = '';
      if (this.$refs.productInput) this.$refs.productInput.value = '';
    },
    getStatusText(record) {
      if (record.status === 0) return '排队中';
      if (record.status === 1) {
        // 如果状态是生成中，根据人像链接是否为空来显示不同的提示
        if (record.personVideoUrl) {
          return '产品生成中';
        } else {
          return '人像生成中';
        }
      }
      if (record.status === 2) return '已完成';
      if (record.status === 3) return '生成失败';
      return record.type === "product" ? "商品" : "人像";
    },
    async changePage(page) {
      if (page < 1 || page > Math.ceil(this.totalRecords / this.pageSize)) return;
      this.currentPage = page;
      await this.fetchVideoRecords();
    },
    filteredRecords() {
      if (this.currentTab === 'all') return this.records;
      if (this.currentTab === 'pending') return this.records.filter(r => r.status === 0 || r.status === 1);
      if (this.currentTab === 'completed') return this.records.filter(r => r.status === 2);
      if (this.currentTab === 'failed') return this.records.filter(r => r.status === 3);
      return this.records;
    },
    async handleDelete(record) {
      if (!confirm('确定要删除这个视频记录吗？')) {
        return;
      }
      
      try {
        const response = await deleteUserVideo(record.id);
        
        if (response && response.success) {
          // 删除成功，刷新列表
          this.$toast.success('删除成功');
          await this.fetchVideoRecords();
        } else {
          this.$toast.error('删除失败: ' + (response.message || '未知错误'));
        }
      } catch (error) {
        console.error('删除视频记录失败:', error);
        this.$toast.error('删除失败: ' + (error.message || '未知错误'));
      }
    },
  },
  mounted() {
    // 在组件挂载后获取分类数据和视频记录
    this.fetchCategories();
    this.fetchVideoRecords(false); // 初始加载，非静默模式
    
    // 设置定时刷新，使用静默模式
    this.refreshInterval = setInterval(() => {
      this.fetchVideoRecords(true); // 定时刷新，静默模式
    }, 30000); // 每30秒刷新一次
  },
  beforeUnmount() {
    // 组件卸载前清除定时器
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  }
};
</script>

<style scoped>
/* 添加拖拽相关样式 */
.border-blue-400 {
  border-width: 2px;
  border-style: dashed;
  background-color: rgba(96, 165, 250, 0.1);
}
</style>