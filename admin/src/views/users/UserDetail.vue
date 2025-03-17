<template>
  <div class="app-container">
    <div class="page-header">
      <el-button icon="el-icon-back" @click="goBack">返回</el-button>
      <h2>用户详情</h2>
    </div>
    
    <el-card v-loading="loading" class="box-card">
      <template v-if="!loading && userDetail">
        <el-descriptions title="基本信息" :column="2" border>
          <el-descriptions-item label="用户ID">{{ userDetail.id }}</el-descriptions-item>
          <el-descriptions-item label="用户名">{{ userDetail.username }}</el-descriptions-item>
          <el-descriptions-item label="MAC地址">{{ userDetail.mac_address || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="注册时间">{{ formatDate(userDetail.created_at) }}</el-descriptions-item>
        </el-descriptions>
        
        <el-divider></el-divider>
        
        <el-descriptions title="卡密信息" :column="2" border>
          <template v-if="userDetail.carmine">
            <el-descriptions-item label="卡密">{{ userDetail.carmine.code }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="userDetail.carmine.status === 1 ? 'success' : 'danger'">
                {{ userDetail.carmine.status === 1 ? '有效' : '无效' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="到期时间">{{ formatDate(userDetail.carmine.expired_at) }}</el-descriptions-item>
            <el-descriptions-item label="激活时间">{{ formatDate(userDetail.carmine.created_at) }}</el-descriptions-item>
          </template>
          <template v-else>
            <el-descriptions-item :span="2">
              <el-empty description="未绑定卡密"></el-empty>
            </el-descriptions-item>
          </template>
        </el-descriptions>
      </template>
    </el-card>
  </div>
</template>

<script>
import { getUserDetail } from '../../../api/user.js';

export default {
  name: 'UserDetail',
  data() {
    return {
      loading: true,
      userDetail: null
    }
  },
  created() {
    this.fetchUserDetail()
  },
  methods: {
    async fetchUserDetail() {
      this.loading = true
      try {
        const userId = this.$route.params.id
        const response = await getUserDetail(userId)
        this.userDetail = response
      } catch (error) {
        console.error('获取用户详情失败:', error)
        this.$message.error('获取用户详情失败')
      } finally {
        this.loading = false
      }
    },
    goBack() {
      this.$router.push('/users')
    },
    formatDate(dateString) {
      if (!dateString) return '未设置'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.app-container {
  padding: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 0 15px;
}

.box-card {
  margin-bottom: 20px;
}

.el-divider {
  margin: 24px 0;
}
</style> 