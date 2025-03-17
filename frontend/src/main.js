import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'
import toast from './plugins/toast'

// 导入组件
import LoginPage from './components/LoginPage.vue'
import HomePage from './components/HomePage.vue'
// 移除不需要的组件导入
// import AIVideo from './components/AIVideo.vue'
// import ImageVideoGenerator from './components/ImageVideoGenerator.vue'

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
      meta: { requiresAuth: false }
    },
    {
      path: '/home',
      name: 'home',
      component: HomePage,
      meta: { requiresAuth: true }
    },
    // 移除不需要的路由
    // {
    //   path: '/ai-video',
    //   name: 'ai-video',
    //   component: AIVideo,
    //   meta: { requiresAuth: true }
    // },
    // {
    //   path: '/image-video',
    //   name: 'image-video',
    //   component: ImageVideoGenerator,
    //   meta: { requiresAuth: true }
    // }
  ]
})

// 添加全局路由守卫
router.beforeEach((to, from, next) => {
  // 检查路由是否需要认证
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false);
  
  // 如果路由不需要认证，直接放行
  if (!requiresAuth) {
    next();
    return;
  }
  
  // 检查是否有 token
  const token = localStorage.getItem('token');
  // const token = 'asdfadsfgsadfg'
  if (!token) {
    // 如果没有 token，重定向到登录页
    next({ name: 'login' });
  } else {
    // 有 token，放行
    next();
  }
})

// 创建 Vue 应用实例
const app = createApp(App)

// 使用路由
app.use(router)
app.use(toast)

// 挂载应用
app.mount('#app')
