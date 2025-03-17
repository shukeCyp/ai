<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>Session 管理</span>
        <el-input
          v-model="listQuery.runway_id"
          placeholder="按账号ID筛选"
          style="width: 200px; float: right"
          clearable
          @clear="fetchData"
          @keyup.enter.native="fetchData"
        >
          <el-button slot="append" icon="el-icon-search" @click="fetchData"></el-button>
        </el-input>
      </div>
      
      <el-table
        v-loading="loading"
        :data="sessionList"
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
          prop="runway_id"
          label="账号ID"
          width="120"
          align="center"
        />
        <el-table-column
          prop="session_id"
          label="Session ID"
          min-width="280"
          align="center"
        />
        <el-table-column
          prop="created_at"
          label="创建时间"
          width="180"
          align="center"
        >
          <template slot-scope="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          width="150"
          align="center"
        >
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="primary"
              icon="el-icon-document-copy"
              @click="copySessionId(scope.row.session_id)"
              title="复制"
            />
            <el-button
              size="mini"
              type="danger"
              icon="el-icon-delete"
              @click="handleDelete(scope.row)"
              title="删除"
            />
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
import { getRunwaySessionList, deleteRunwaySession } from '../../../api/runway_account.js';

export default {
  name: 'SessionManagement',
  data() {
    return {
      loading: false,
      sessionList: [],
      total: 0,
      listQuery: {
        page: 1,
        page_size: 10,
        runway_id: ''
      }
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      this.loading = true
      
      // 使用参数方式传递
      getRunwaySessionList(
        Number(this.listQuery.page), 
        Number(this.listQuery.page_size), 
        this.listQuery.runway_id || null
      )
        .then(response => {
          this.sessionList = response.sessions || []
          this.total = response.total || 0
        })
        .catch(error => {
          console.error('获取Session列表失败:', error)
          this.$message.error('获取Session列表失败: ' + error.message)
        })
        .finally(() => {
          this.loading = false
        })
    },
    handleCurrentChange(page) {
      this.listQuery.page = Number(page)
      this.fetchData()
    },
    copySessionId(sessionId) {
      // 复制到剪贴板
      navigator.clipboard.writeText(sessionId).then(() => {
        this.$message({
          message: 'Session ID 已复制到剪贴板',
          type: 'success'
        })
      }).catch(() => {
        // 备用复制方法
        const el = document.createElement('textarea')
        el.value = sessionId
        document.body.appendChild(el)
        el.select()
        document.execCommand('copy')
        document.body.removeChild(el)
        this.$message({
          message: 'Session ID 已复制到剪贴板',
          type: 'success'
        })
      })
    },
    handleDelete(row) {
      this.$confirm('确认删除该 Session?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        deleteRunwaySession(row.id)
          .then(() => {
            this.$message({
              type: 'success',
              message: '删除成功!'
            })
            this.fetchData() // 重新加载数据
          })
          .catch(error => {
            console.error('删除Session失败:', error)
            this.$message.error('删除Session失败: ' + error.message)
          })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
      })
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