<template>
  <div
    class="min-h-screen w-full py-8 bg-gradient-to-br from-indigo-900 via-purple-800 to-blue-900 relative overflow-hidden"
  >
    <!-- 背景网格和粒子效果 -->
    <div class="absolute inset-0">
      <div class="h-full w-full bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxkZWZzPjxwYXR0ZXJuIGlkPSJncmlkIiB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHBhdHRlcm5Vbml0cz0idXNlclNwYWNlT25Vc2UiPjxwYXRoIGQ9Ik0gNDAgMCBMIDAgMCAwIDQwIiBmaWxsPSJub25lIiBzdHJva2U9IiNhYWEiIHN0cm9rZS13aWR0aD0iMC41Ii8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2dyaWQpIiBvcGFjaXR5PSIwLjA1Ii8+PC9zdmc+')]"></div>
    </div>
    
    <!-- 光晕效果 -->
    <div class="absolute top-0 left-1/4 w-1/2 h-1/2 bg-blue-500 rounded-full filter blur-[150px] opacity-20 animate-pulse-slow"></div>
    <div class="absolute bottom-0 right-1/4 w-1/2 h-1/2 bg-purple-500 rounded-full filter blur-[150px] opacity-20 animate-pulse-slow animation-delay-2000"></div>
    
    <!-- 浮动粒子 -->
    <div class="particles absolute inset-0 overflow-hidden pointer-events-none">
      <div v-for="n in 20" :key="n" 
           class="particle absolute rounded-full"
           :style="{
             width: `${Math.random() * 5 + 1}px`,
             height: `${Math.random() * 5 + 1}px`,
             background: `rgba(255, 255, 255, ${Math.random() * 0.5 + 0.2})`,
             left: `${Math.random() * 100}%`,
             top: `${Math.random() * 100}%`,
             animation: `float ${Math.random() * 10 + 10}s linear infinite, 
                         pulse ${Math.random() * 5 + 2}s ease-in-out infinite`
           }">
      </div>
    </div>

    <div class="mx-auto w-[1440px] min-h-[1024px] relative z-10">
      <!-- 顶部导航 -->
      <nav
        class="bg-white/90 backdrop-blur-md rounded-lg px-8 py-4 mb-8 flex items-center justify-between shadow-lg"
      >
        <div class="flex items-center gap-3">
          <button 
            @click="toggleDrawer"
            class="text-gray-600 hover:text-blue-600 transition-colors mr-2"
          >
            <i class="fas fa-bars text-xl"></i>
          </button>
          <img :src="logoUrl" alt="Logo" class="w-8 h-8" />
          <span class="text-xl font-medium text-gray-800">莲韵</span>
        </div>
        <div class="flex items-center gap-4">
          <span class="text-gray-600">欢迎，{{ username || '用户' }}</span>
        </div>
      </nav>
      
      <!-- 主要内容区域 - 使用 ImageVideoGenerator 组件 -->
      <ImageVideoGenerator />
    </div>

    <!-- 侧边抽屉背景 -->
    <div 
      class="fixed inset-0 bg-black/30 backdrop-blur-sm z-40 transition-opacity duration-300"
      :class="{ 'opacity-0 pointer-events-none': !drawerOpen, 'opacity-100': drawerOpen }"
      @click="drawerOpen = false"
    ></div>
    
    <!-- 侧边抽屉 -->
    <div 
      class="fixed top-0 bottom-0 left-0 w-64 bg-white/90 backdrop-blur-md shadow-lg z-50 transform transition-transform duration-300 ease-in-out"
      :class="{ '-translate-x-full': !drawerOpen, 'translate-x-0': drawerOpen }"
    >
      <div class="p-4 border-b border-gray-200/70">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-medium">功能菜单</h3>
          <button 
            @click="drawerOpen = false"
            class="text-gray-500 hover:text-gray-700"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
      
      <div class="p-4">
        <ul class="space-y-2">
          <li>
            <button 
              @click="drawerOpen = false"
              class="w-full text-left px-4 py-2 rounded-lg flex items-center bg-blue-100 text-blue-700"
            >
              <i class="fas fa-film mr-3"></i>
              图片转视频
            </button>
          </li>
        </ul>
      </div>
    </div>

    <!-- 通知弹窗 -->
    <div 
      v-if="showNotice" 
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 overflow-hidden">
        <!-- 弹窗标题 -->
        <div class="bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 text-white py-4 px-6 flex items-center justify-between">
          <div class="flex items-center">
            <i class="fas fa-bullhorn text-yellow-300 mr-2"></i>
            <h2 class="text-xl font-medium">欢迎光临莲韵视频</h2>
          </div>
          <button 
            @click="dismissNotice(false)" 
            class="text-white/80 hover:text-white focus:outline-none"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <!-- 弹窗内容 -->
        <div class="p-6">
          <div class="mb-6">
            <p class="font-medium mb-3 text-lg text-indigo-700">重要通知：</p>
            <ul class="list-disc pl-5 space-y-2 text-gray-700">
              <li>请遵守您所在地国家法律法规，禁止利用本站进行任何违法活动。</li>
              <li>虚拟商品原则上不接受任何退款要求！！！</li>
              <li>因技术持续更新迭代，功能性适用性存在差异，以本网站实现为准！确认购买即表示默认同意相关条款。</li>
              <li>本产品限制一机一号，换机无法登录</li>
              <li>请勿尝试抓取/破解本应用接口，如若尝试，一切后果自行承担</li>
            </ul>
          </div>
          
          <!-- 添加群聊二维码 -->
          <div class="mt-6 flex flex-col items-center">
            <p class="text-center text-indigo-700 font-medium mb-3">如有问题，请扫码进群交流</p>
            <div class="bg-gray-50 p-3 rounded-lg shadow-sm">
              <img :src="groupQrcode" alt="群聊二维码" class="w-40 h-40 object-contain" />
            </div>
          </div>
          
          <!-- 底部按钮 -->
          <div class="flex items-center justify-between mt-6">
            <label class="flex items-center text-gray-600 cursor-pointer">
              <input 
                type="checkbox" 
                v-model="doNotShowToday" 
                class="mr-2 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              今日不再提醒
            </label>
            <button 
              @click="dismissNotice(true)" 
              class="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              我已了解
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ImageVideoGenerator from "./ImageVideoGenerator.vue";
// 导入群聊二维码图片
import groupQrcode from "../assets/group_qrcode.png";

export default {
  name: "HomePage",
  components: {
    ImageVideoGenerator
  },
  data() {
    return {
      logoUrl:
        "https://ai-public.mastergo.com/ai/img_res/5058c6b6915071d2e8b7a53ee08ef13a.jpg",
      username: localStorage.getItem('username') || '用户',
      showNotice: true,
      doNotShowToday: false,
      // 抽屉相关
      drawerOpen: false,
      // 群聊二维码
      groupQrcode: groupQrcode
    };
  },
  methods: {
    // 关闭提示
    dismissNotice(confirmed) {
      this.showNotice = false;
      
      if (confirmed && this.doNotShowToday) {
        // 如果选择了"今日不再提醒"，则保存当前日期
        const today = new Date().toISOString().split('T')[0]; // 格式：YYYY-MM-DD
        localStorage.setItem('noticeDissmissedDate', today);
      } else if (confirmed) {
        // 如果只是点击了"我已了解"但没选"今日不再提醒"，不保存日期
        localStorage.removeItem('noticeDissmissedDate');
      }
    },
    // 抽屉相关方法
    toggleDrawer() {
      this.drawerOpen = !this.drawerOpen;
    }
  },
  mounted() {
    // 检查是否今天已经关闭过提示
    const today = new Date().toISOString().split('T')[0];
    const dismissedDate = localStorage.getItem('noticeDissmissedDate');
    
    if (dismissedDate === today) {
      this.showNotice = false;
    }
  }
};
</script>

<style scoped>
.min-h-screen {
  min-height: 100vh;
}

@keyframes pulse-slow {
  0%, 100% {
    opacity: 0.2;
  }
  50% {
    opacity: 0.3;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.2;
  }
  50% {
    opacity: 0.8;
  }
}

.animate-pulse-slow {
  animation: pulse-slow 8s ease-in-out infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.particle {
  position: absolute;
  pointer-events: none;
}
</style>
