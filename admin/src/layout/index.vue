<template>
  <div class="app-wrapper">
    <div class="sidebar-container">
      <div class="logo-container">
        <h1 class="logo-title">管理系统</h1>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
      >
        <el-menu-item index="/dashboard">
          <i class="el-icon-s-home"></i>
          <template #title>仪表盘</template>
        </el-menu-item>
        
        <el-submenu index="/runway">
          <template #title>
            <i class="el-icon-s-platform"></i>
            <span>Runway管理</span>
          </template>
          <el-menu-item index="/runway/accounts">
            <i class="el-icon-user"></i>
            <span>账号管理</span>
          </el-menu-item>
          <el-menu-item index="/runway/sessions">
            <i class="el-icon-time"></i>
            <span>Session管理</span>
          </el-menu-item>
        </el-submenu>
        
        <el-menu-item index="/users">
          <i class="el-icon-user"></i>
          <template #title>用户管理</template>
        </el-menu-item>
        <el-menu-item index="/settings">
          <i class="el-icon-setting"></i>
          <template #title>系统设置</template>
        </el-menu-item>
        
        <el-submenu index="/cards">
          <template #title>
            <i class="el-icon-s-ticket"></i>
            <span>卡密管理</span>
          </template>
          <el-menu-item index="/cards/list">
            <i class="el-icon-tickets"></i>
            <span>卡密列表</span>
          </el-menu-item>
        </el-submenu>
      </el-menu>
    </div>
    
    <div class="main-container">
      <div class="navbar">
        <div class="right-menu">
          <el-dropdown trigger="click">
            <span class="el-dropdown-link">
              管理员<i class="el-icon-arrow-down el-icon--right"></i>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人信息</el-dropdown-item>
                <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
      
      <div class="app-main">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LayoutContainer',
  computed: {
    activeMenu() {
      const { meta, path } = this.$route
      if (meta.activeMenu) {
        return meta.activeMenu
      }
      return path
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('token')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.app-wrapper {
  display: flex;
  width: 100%;
  height: 100%;
}

.sidebar-container {
  width: 210px;
  height: 100%;
  background: #304156;
  transition: width 0.28s;
  overflow-y: auto;
}

.logo-container {
  height: 60px;
  line-height: 60px;
  text-align: center;
}

.logo-title {
  margin: 0;
  color: #fff;
  font-size: 18px;
}

.sidebar-menu {
  border-right: none;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.navbar {
  height: 50px;
  overflow: hidden;
  position: relative;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 20px;
}

.right-menu {
  margin-right: 20px;
}

.el-dropdown-link {
  cursor: pointer;
  color: #409EFF;
}

.app-main {
  flex: 1;
  overflow: auto;
  padding: 20px;
  background-color: #f0f2f5;
}
</style> 