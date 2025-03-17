<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>用户管理</span>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索用户名"
          style="width: 250px; float: right"
          clearable
          @clear="handleSearch"
          @keyup.enter.native="handleSearch"
        >
          <el-button slot="append" icon="el-icon-search" @click="handleSearch"></el-button>
        </el-input>
      </div>
      
      <el-table
        v-loading="loading"
        :data="userList"
        border
        style="width: 100%"
      >
        <el-table-column
          prop="id"
          label="ID"
          width="80"
          align="center"
        />
        <el-table-column
          prop="username"
          label="用户名"
          min-width="150"
          align="center"
        />
        <el-table-column
          prop="mac_address"
          label="MAC地址"
          min-width="150"
          align="center"
        >
          <template slot-scope="scope">
            {{ scope.row.mac_address || '未设置' }}
          </template>
        </el-table-column>
        <el-table-column
          prop="expired_at"
          label="到期时间"
          width="180"
          align="center"
        >
          <template slot-scope="scope">
            <el-tag v-if="scope.row.expired_at" :type="isExpired(scope.row.expired_at) ? 'danger' : 'success'">
              {{ formatDate(scope.row.expired_at) }}
            </el-tag>
            <span v-else>未设置</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="created_at"
          label="注册时间"
          width="180"
          align="center"
        >
          <template slot-scope="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          width="120"
          align="center"
        >
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="primary"
              @click="handleEdit(scope.row)"
            >
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          background
          layout="total, prev, pager, next"
          :total="total"
          :current-page.sync="listQuery.page"
          :page-size="listQuery.page_size"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script>
import { getUserList } from '../../../api/user.js';

export default {
  name: 'UserList',
  data() {
    return {
      loading: false,
      userList: [],
      total: 0,
      searchKeyword: '',
      listQuery: {
        page: 1,
        page_size: 10,
        keyword: ''
      }
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true
      
      try {
        // 设置搜索关键词
        if (this.searchKeyword) {
          this.listQuery.keyword = this.searchKeyword
        } else {
          delete this.listQuery.keyword
        }
        
        // 调用API获取用户列表
        const response = await getUserList(this.listQuery)
        this.userList = response.users
        this.total = response.total
      } catch (error) {
        console.error('获取用户列表失败:', error)
        this.$message.error('获取用户列表失败')
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      this.listQuery.page = 1
      this.fetchData()
    },
    handleCurrentChange(page) {
      this.listQuery.page = Number(page)
      this.fetchData()
    },
    handleEdit(row) {
      this.$router.push(`/users/detail/${row.id}`)
    },
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    },
    isExpired(dateString) {
      if (!dateString) return true
      const expiryDate = new Date(dateString)
      const now = new Date()
      return expiryDate < now
    }
  }
}
</script>

<style scoped>
.app-container {
  padding: 20px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.clearfix:after {
  content: "";
  display: table;
  clear: both;
}
</style> 