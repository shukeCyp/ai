<template>
  <div class="min-h-screen w-full flex items-center justify-center relative overflow-hidden">
    <!-- 背景图 -->
    <div class="absolute inset-0 w-full h-full">
      <div class="w-full h-full bg-gradient-to-br from-blue-900 via-purple-800 to-indigo-900"></div>
      <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-500/20 via-transparent to-transparent"></div>
      <div class="absolute inset-0">
        <div class="h-full w-full bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxkZWZzPjxwYXR0ZXJuIGlkPSJncmlkIiB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHBhdHRlcm5Vbml0cz0idXNlclNwYWNlT25Vc2UiPjxwYXRoIGQ9Ik0gNDAgMCBMIDAgMCAwIDQwIiBmaWxsPSJub25lIiBzdHJva2U9IiNhYWEiIHN0cm9rZS13aWR0aD0iMC41Ii8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2dyaWQpIiBvcGFjaXR5PSIwLjA1Ii8+PC9zdmc+')]"></div>
      </div>
      <div class="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-purple-500/10 animate-breath"></div>
      
      <!-- 添加浮动粒子效果 -->
      <div class="particles absolute inset-0 overflow-hidden">
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
    </div>

    <!-- 登录/注册卡片 -->
    <div class="w-[420px] backdrop-blur-md bg-white/90 p-8 rounded-2xl shadow-2xl animate-float">
      <!-- Logo -->
      <div class="text-center mb-8">
        <img :src="logoImageUrl" alt="Logo" class="w-16 h-16 mx-auto mb-4 rounded-xl" />
        <h1 class="text-2xl font-bold text-gray-800">{{ isLogin ? '欢迎回来' : '创建账号' }}</h1>
        <p class="text-gray-500 mt-2">{{ isLogin ? '莲韵视频 - 您的专属视频平台' : '加入莲韵视频' }}</p>
      </div>

      <!-- 切换登录/注册 -->
      <div class="flex justify-center mb-6">
        <div class="bg-gray-100 p-1 rounded-lg inline-flex">
          <button 
            @click="isLogin = true" 
            :class="[
              'px-4 py-2 rounded-lg transition-all',
              isLogin ? 'bg-white shadow-sm text-blue-600' : 'text-gray-500'
            ]"
          >
            登录
          </button>
          <button 
            @click="isLogin = false" 
            :class="[
              'px-4 py-2 rounded-lg transition-all',
              !isLogin ? 'bg-white shadow-sm text-blue-600' : 'text-gray-500'
            ]"
          >
            注册
          </button>
        </div>
      </div>

      <!-- 登录表单 -->
      <form v-if="isLogin" @submit.prevent="handleLogin" class="space-y-6">
        <!-- 用户名输入框 -->
        <div class="relative">
          <i class="fas fa-user absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>
          <input
            v-model="loginForm.username"
            type="text"
            class="w-full pl-10 pr-4 py-3 border-none bg-gray-50/50 rounded-lg focus:ring-2 focus:ring-blue-500 transition-all text-sm"
            :class="{'ring-2 ring-red-500': errors.loginUsername}"
            placeholder="请输入用户名"
          />
          <p v-if="errors.loginUsername" class="text-red-500 text-xs mt-1">{{ errors.loginUsername }}</p>
        </div>

        <!-- 密码输入框 -->
        <div class="relative">
          <i class="fas fa-lock absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>
          <input
            v-model="loginForm.password"
            :type="showPassword ? 'text' : 'password'"
            class="w-full pl-10 pr-12 py-3 border-none bg-gray-50/50 rounded-lg focus:ring-2 focus:ring-blue-500 transition-all text-sm"
            :class="{'ring-2 ring-red-500': errors.loginPassword}"
            placeholder="请输入密码"
          />
          <button 
            type="button"
            @click="togglePassword"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 !rounded-button"
          >
            <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
          </button>
          <p v-if="errors.loginPassword" class="text-red-500 text-xs mt-1">{{ errors.loginPassword }}</p>
        </div>

        <!-- 记住密码和忘记密码 -->
        <div class="flex items-center justify-between text-sm">
          <label class="flex items-center space-x-2 cursor-pointer">
            <input type="checkbox" v-model="loginForm.remember" class="rounded text-blue-500" />
            <span class="text-gray-600">记住密码</span>
          </label>
          <a href="#" class="text-blue-500 hover:text-blue-600">忘记密码？</a>
        </div>

        <!-- 登录按钮 -->
        <button 
          type="submit"
          class="w-full py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:opacity-90 transform hover:scale-[1.02] transition-all !rounded-button whitespace-nowrap"
        >
          登 录
        </button>

        <!-- 没有账号？注册 -->
        <div class="text-center mt-4">
          <p class="text-gray-600">
            没有账号？
            <button 
              type="button" 
              @click="isLogin = false" 
              class="text-blue-500 hover:text-blue-600 font-medium"
            >
              立即注册
            </button>
          </p>
        </div>

        <!-- 分割线 -->
        <div class="relative">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-200"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-white/90 text-gray-500">联系购买账号</span>
          </div>
        </div>

        <!-- 微信二维码 - 更新为使用本地图片 -->
        <div class="flex flex-col items-center space-y-4">
          <img :src="qrcodeImage" alt="微信二维码" class="w-32 h-32 rounded-lg shadow-md" />
          <p class="text-sm text-gray-600">扫描二维码联系客服购买账号</p>
        </div>
      </form>

      <!-- 注册表单 -->
      <form v-else @submit.prevent="handleRegister" class="space-y-6">
        <!-- 用户名输入框 -->
        <div class="relative">
          <i class="fas fa-user absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>
          <input
            v-model="registerForm.username"
            type="text"
            class="w-full pl-10 pr-4 py-3 border-none bg-gray-50/50 rounded-lg focus:ring-2 focus:ring-blue-500 transition-all text-sm"
            :class="{'ring-2 ring-red-500': errors.registerUsername}"
            placeholder="请输入用户名"
          />
          <p v-if="errors.registerUsername" class="text-red-500 text-xs mt-1">{{ errors.registerUsername }}</p>
        </div>

        <!-- 密码输入框 -->
        <div class="relative">
          <i class="fas fa-lock absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>
          <input
            v-model="registerForm.password"
            :type="showPassword ? 'text' : 'password'"
            class="w-full pl-10 pr-12 py-3 border-none bg-gray-50/50 rounded-lg focus:ring-2 focus:ring-blue-500 transition-all text-sm"
            :class="{'ring-2 ring-red-500': errors.registerPassword}"
            placeholder="请输入密码"
          />
          <button 
            type="button"
            @click="togglePassword"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 !rounded-button"
          >
            <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
          </button>
          <p v-if="errors.registerPassword" class="text-red-500 text-xs mt-1">{{ errors.registerPassword }}</p>
        </div>

        <!-- 卡密输入框 -->
        <div class="relative">
          <i class="fas fa-ticket-alt absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>
          <input
            v-model="registerForm.carmine"
            type="text"
            class="w-full pl-10 pr-4 py-3 border-none bg-gray-50/50 rounded-lg focus:ring-2 focus:ring-blue-500 transition-all text-sm"
            placeholder="请输入卡密"
          />
        </div>

        <!-- 注册按钮 -->
        <button 
          type="submit"
          class="w-full py-3 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg hover:opacity-90 transform hover:scale-[1.02] transition-all !rounded-button whitespace-nowrap"
        >
          注 册
        </button>

        <!-- 已有账号？登录 -->
        <div class="text-center mt-4">
          <p class="text-gray-600">
            已有账号？
            <button 
              type="button" 
              @click="isLogin = true" 
              class="text-blue-500 hover:text-blue-600 font-medium"
            >
              立即登录
            </button>
          </p>
        </div>

        <!-- 分割线 -->
        <div class="relative">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-200"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-white/90 text-gray-500">联系获取卡密</span>
          </div>
        </div>

        <!-- 微信二维码 -->
        <div class="flex flex-col items-center space-y-4">
          <img :src="qrcodeImage" alt="微信二维码" class="w-32 h-32 rounded-lg shadow-md" />
          <p class="text-sm text-gray-600">扫描二维码联系客服获取卡密</p>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { login, register, heartbeat } from '../api/user.js';
// 只导入二维码图片，背景使用远程链接
import qrcodeImage from '../assets/qrcode.png';

export default {
  name: 'LoginPage',
  data() {
    return {
      // 移除背景图片
      logoImageUrl: 'https://ai-public.mastergo.com/ai/img_res/5058c6b6915071d2e8b7a53ee08ef13a.jpg',
      isLogin: true,
      showPassword: false,
      loginForm: {
        username: '',
        password: '',
        remember: false
      },
      registerForm: {
        username: '',
        password: '',
        carmine: ''
      },
      // 使用本地二维码图片
      qrcodeImage: qrcodeImage,
      // 添加错误信息字段
      errors: {
        loginUsername: '',
        loginPassword: '',
        registerUsername: '',
        registerPassword: ''
      }
    };
  },
  methods: {
    // 验证用户名和密码格式
    validateInput(value, type) {
      // 检查是否为空
      if (!value.trim()) {
        return `${type === 'username' ? '用户名' : '密码'}不能为空`;
      }
      
      // 检查长度是否至少为6位
      if (value.length < 6) {
        return `${type === 'username' ? '用户名' : '密码'}长度至少为6位`;
      }
      
      // 检查是否只包含字母和数字
      if (!/^[a-zA-Z0-9]+$/.test(value)) {
        return `${type === 'username' ? '用户名' : '密码'}只能包含英文字母和数字`;
      }
      
      // 检查是否纯数字
      if (/^\d+$/.test(value)) {
        return `${type === 'username' ? '用户名' : '密码'}不能是纯数字`;
      }
      
      return '';
    },
    
    async handleLogin() {
      // 验证用户名
      this.errors.loginUsername = this.validateInput(this.loginForm.username, 'username');
      // 验证密码
      this.errors.loginPassword = this.validateInput(this.loginForm.password, 'password');
      
      // 如果有错误，停止登录
      if (this.errors.loginUsername || this.errors.loginPassword) {
        return;
      }
      
      try {
        // 调用登录 API，使用 URL 参数
        const response = await login({
          username: this.loginForm.username,
          password: this.loginForm.password
        });
        
        if (response && response.token) {
          // 保存 token 和用户信息
          localStorage.setItem('token', response.token);
          localStorage.setItem('userId', response.user_id);
          localStorage.setItem('username', response.username);
          localStorage.setItem('expiresAt', response.expires_at);
          
          // 如果选择记住密码，保存用户名和密码
          if (this.loginForm.remember) {
            localStorage.setItem('savedUsername', this.loginForm.username);
            localStorage.setItem('savedPassword', this.loginForm.password);
          } else {
            localStorage.removeItem('savedUsername');
            localStorage.removeItem('savedPassword');
          }
          
          // 登录成功，跳转到主页
          window.location.href = '/home';
        } else {
          alert('登录失败，请检查用户名和密码');
        }
      } catch (error) {
        console.error('登录错误:', error);
        alert('登录失败: ' + (error.message || '未知错误'));
      }
    },
    
    async handleRegister() {
      // 验证用户名
      this.errors.registerUsername = this.validateInput(this.registerForm.username, 'username');
      // 验证密码
      this.errors.registerPassword = this.validateInput(this.registerForm.password, 'password');
      
      // 如果有错误，停止注册
      if (this.errors.registerUsername || this.errors.registerPassword) {
        return;
      }
      
      // 检查卡密是否为空
      if (!this.registerForm.carmine.trim()) {
        alert('请输入卡密');
        return;
      }
      
      try {
        // 调用注册 API
        const response = await register({
          username: this.registerForm.username,
          password: this.registerForm.password,
          carmine: this.registerForm.carmine
        });
        
        if (response && response.token) {
          // 注册成功，直接保存 token 和用户信息
          localStorage.setItem('token', response.token);
          localStorage.setItem('userId', response.user_id);
          localStorage.setItem('username', response.username);
          localStorage.setItem('expiresAt', response.expires_at);
          
          alert('注册成功');
          
          // 注册成功后直接跳转到主页
          window.location.href = '/home';
        } else {
          alert('注册失败: ' + (response.message || '未知错误'));
        }
      } catch (error) {
        console.error('注册错误:', error);
        alert('注册失败: ' + (error.message || '未知错误'));
      }
    },
    
    togglePassword() {
      this.showPassword = !this.showPassword;
    },
    
    // 检查登录状态
    async checkLoginStatus() {
      const token = localStorage.getItem('token');
      if (!token) {
        return; // 没有 token，停留在登录页
      }
      
      try {
        // 调用心跳接口检查 token 是否有效
        const response = await heartbeat();
        // 检查返回状态
        if (response && response.status === "ok") {
          // 心跳成功，用户已登录，跳转到主页
          window.location.href = '/home';
        } else {
          // 心跳返回异常状态
          console.error('心跳检测状态异常:', response);
          // 清除所有相关信息
          localStorage.removeItem('token');
          localStorage.removeItem('userId');
          localStorage.removeItem('username');
          localStorage.removeItem('expiresAt');
          // 停留在登录页
        }
      } catch (error) {
        console.error('心跳检测失败:', error);
        // 心跳失败，清除所有相关信息
        localStorage.removeItem('token');
        localStorage.removeItem('userId');
        localStorage.removeItem('username');
        localStorage.removeItem('expiresAt');
        // 停留在登录页
      }
    },
    
    // 实时验证登录用户名
    validateLoginUsername() {
      this.errors.loginUsername = this.validateInput(this.loginForm.username, 'username');
    },
    
    // 实时验证登录密码
    validateLoginPassword() {
      this.errors.loginPassword = this.validateInput(this.loginForm.password, 'password');
    },
    
    // 实时验证注册用户名
    validateRegisterUsername() {
      this.errors.registerUsername = this.validateInput(this.registerForm.username, 'username');
    },
    
    // 实时验证注册密码
    validateRegisterPassword() {
      this.errors.registerPassword = this.validateInput(this.registerForm.password, 'password');
    }
  },
  watch: {
    // 监听输入变化，实时验证
    'loginForm.username': function() {
      this.validateLoginUsername();
    },
    'loginForm.password': function() {
      this.validateLoginPassword();
    },
    'registerForm.username': function() {
      this.validateRegisterUsername();
    },
    'registerForm.password': function() {
      this.validateRegisterPassword();
    }
  },
  async created() {
    // 在组件创建时检查登录状态
    await this.checkLoginStatus();
  },
  mounted() {
    // 如果之前保存了用户名和密码，自动填充
    const savedUsername = localStorage.getItem('savedUsername');
    const savedPassword = localStorage.getItem('savedPassword');
    
    if (savedUsername && savedPassword) {
      this.loginForm.username = savedUsername;
      this.loginForm.password = savedPassword;
      this.loginForm.remember = true;
    }
  }
};
</script>

<style scoped>
@keyframes breath {
  0%, 100% {
    opacity: 0.8;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.02);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes glow {
  0%, 100% {
    box-shadow: 0 0 5px rgba(59, 130, 246, 0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.8);
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

.particle {
  position: absolute;
  pointer-events: none;
}

.animate-breath {
  animation: breath 8s ease-in-out infinite;
}

.animate-float {
  animation: float 6s ease-in-out infinite;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  animation: glow 3s ease-in-out infinite;
}

input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style>