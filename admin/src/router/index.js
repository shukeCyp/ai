import Vue from 'vue'
import VueRouter from 'vue-router'
import Login from '../views/Login.vue'
import Layout from '../layout/index.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录', hidden: true }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '仪表盘', icon: 'dashboard' }
      }
    ]
  },
  {
    path: '/runway',
    component: Layout,
    redirect: '/runway/accounts',
    name: 'Runway',
    meta: { title: 'Runway管理' },
    children: [
      {
        path: 'accounts',
        name: 'RunwayAccounts',
        component: () => import('../views/runway/Accounts.vue'),
        meta: { title: '账号管理', requiresAuth: true }
      },
      {
        path: 'account-detail/:id',
        name: 'AccountDetail',
        component: () => import('../views/runway/AccountDetail.vue'),
        meta: { title: '账号详情', activeMenu: '/runway/accounts' },
        hidden: true
      },
      {
        path: 'account-create',
        name: 'AccountCreate',
        component: () => import('../views/runway/AccountDetail.vue'),
        meta: { title: '创建账号', activeMenu: '/runway/accounts' },
        hidden: true
      },
      {
        path: 'sessions',
        name: 'RunwaySessions',
        component: () => import('../views/runway/Sessions.vue'),
        meta: { title: 'Session管理', requiresAuth: true }
      }
    ]
  },
  {
    path: '/users',
    component: Layout,
    redirect: '/users/list',
    name: 'Users',
    meta: { title: '用户管理' },
    children: [
      {
        path: 'list',
        name: 'UserList',
        component: () => import('../views/users/UserList.vue'),
        meta: { title: '用户列表', requiresAuth: true }
      },
      {
        path: 'detail/:id',
        component: () => import('@/views/users/UserDetail.vue'),
        name: 'UserDetail',
        meta: { title: '用户详情' },
        hidden: true
      }
    ]
  },
  {
    path: '/cards',
    component: Layout,
    redirect: '/cards/list',
    name: 'Cards',
    meta: { title: '卡密管理' },
    children: [
      {
        path: 'list',
        name: 'CardList',
        component: () => import('../views/cards/CardList.vue'),
        meta: { title: '卡密列表', requiresAuth: true }
      }
    ]
  },
  {
    path: '*',
    redirect: '/404',
    meta: { hidden: true }
  }
]

const router = new VueRouter({
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title || '管理系统'
  
  // 判断是否有token
  const hasToken = localStorage.getItem('token')
  
  if (hasToken) {
    if (to.path === '/login') {
      next({ path: '/' })
    } else {
      next()
    }
  } else {
    if (to.path === '/login') {
      next()
    } else {
      next(`/login?redirect=${to.path}`)
    }
  }
})

export default router 