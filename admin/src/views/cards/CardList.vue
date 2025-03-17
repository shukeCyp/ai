<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>卡密管理</span>
        <div style="float: right; display: flex;">
          <el-button type="primary" size="small" @click="showGenerateDialog" style="margin-right: 10px;">
            批量生成
          </el-button>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索卡密"
            style="width: 200px;"
            clearable
            @clear="handleSearch"
            @keyup.enter.native="handleSearch"
          >
            <el-button slot="append" icon="el-icon-search" @click="handleSearch"></el-button>
          </el-input>
        </div>
      </div>
      
      <!-- 筛选条件 -->
      <div class="filter-container">
        <el-select v-model="listQuery.type" placeholder="卡密类型" clearable @change="handleFilter">
          <el-option
            v-for="(value, key) in cardTypes"
            :key="key"
            :label="value.name"
            :value="key"
          />
        </el-select>
        
        <el-select v-model="listQuery.status" placeholder="卡密状态" clearable @change="handleFilter" style="margin-left: 10px;">
          <el-option label="全部" value="all" />
          <el-option label="未使用" value="unused" />
          <el-option label="已使用" value="used" />
          <el-option label="已过期" value="expired" />
        </el-select>
      </div>
      
      <el-table
        v-loading="loading"
        :data="cardList"
        border
        style="width: 100%; margin-top: 15px;"
      >
        <el-table-column
          prop="id"
          label="ID"
          width="80"
          align="center"
        />
        <el-table-column
          prop="code"
          label="卡密"
          width="220"
          align="center"
        />
        <el-table-column
          prop="type"
          label="类型"
          width="120"
          align="center"
        >
          <template slot-scope="scope">
            <el-tag :type="getCardTypeTag(scope.row.type)">
              {{ getCardTypeName(scope.row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="days"
          label="时长"
          width="120"
          align="center"
        >
          <template slot-scope="scope">
            {{ formatDays(scope.row.days) }}
          </template>
        </el-table-column>
        <el-table-column
          prop="status"
          label="状态"
          width="100"
          align="center"
        >
          <template slot-scope="scope">
            <el-tag :type="scope.row.status === 0 ? 'success' : scope.row.status === 1 ? 'danger' : 'info'">
              {{ scope.row.status === 0 ? '未使用' : scope.row.status === 1 ? '已使用' : '已过期' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="used_by"
          label="使用者"
          width="120"
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
          prop="used_at"
          label="使用时间"
          width="180"
          align="center"
        >
          <template slot-scope="scope">
            {{ formatDate(scope.row.used_at) }}
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
              @click="copyCardCode(scope.row.code)"
              title="复制"
            />
            <el-button
              size="mini"
              type="danger"
              icon="el-icon-delete"
              @click="handleDelete(scope.row)"
              title="删除"
              :disabled="scope.row.status === 1"
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
    
    <!-- 批量生成卡密弹窗 -->
    <el-dialog title="批量生成卡密" :visible.sync="generateDialogVisible" width="400px">
      <el-form :model="generateForm" :rules="generateRules" ref="generateForm" label-width="100px">
        <el-form-item label="卡密类型" prop="type">
          <el-select v-model="generateForm.type" placeholder="请选择卡密类型" style="width: 100%">
            <el-option v-for="(item, key) in cardTypes" :key="key" :label="item.name" :value="key" />
          </el-select>
        </el-form-item>
        <el-form-item label="生成数量" prop="count">
          <el-input-number v-model="generateForm.count" :min="1" :max="100" style="width: 100%" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="generateDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="handleGenerateSubmit" :loading="generateLoading">确 定</el-button>
      </div>
    </el-dialog>
    
    <!-- 生成卡密结果弹窗 -->
    <el-dialog title="生成卡密结果" :visible.sync="resultDialogVisible" width="500px">
      <div class="card-result-container">
        <div v-for="(code, index) in generatedCodes" :key="index" class="card-code-item">
          {{ code }}
        </div>
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button @click="resultDialogVisible = false">关 闭</el-button>
        <el-button type="primary" @click="copyAllCodes">
          <i class="el-icon-document-copy"></i> 复制全部
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getCardList, generateCards, deleteCard } from '../../../api/carmine'

export default {
  name: 'CardList',
  data() {
    return {
      loading: false,
      generateLoading: false,
      cardList: [],
      total: 0,
      searchKeyword: '',
      listQuery: {
        page: 1,
        page_size: 10,
        type: '',
        status: 'all'
      },
      generateDialogVisible: false,
      resultDialogVisible: false,
      generatedCodes: [],
      generateForm: {
        type: 'month',
        count: 10
      },
      generateRules: {
        type: [{ required: true, message: '请选择卡密类型', trigger: 'change' }],
        count: [{ required: true, message: '请输入生成数量', trigger: 'blur' }]
      },
      // 卡密类型
      cardTypes: {
        "day": {"name": "天卡", "days": 1},
        "week": {"name": "周卡", "days": 7},
        "month": {"name": "月卡", "days": 30},
        "year": {"name": "年卡", "days": 365},
        "forever": {"name": "永久卡", "days": 36500}
      },
      // 模拟数据
      mockCards: [
        {
          id: 1,
          code: 'CARD-ABC1-DEF2-GHI3',
          type: 'month',
          days: 30,
          status: 0,
          used_by: null,
          created_at: '2023-05-20 12:30:45',
          used_at: null
        },
        {
          id: 2,
          code: 'CARD-JKL4-MNO5-PQR6',
          type: 'year',
          days: 365,
          status: 1,
          used_by: 'user123',
          created_at: '2023-05-15 09:20:30',
          used_at: '2023-05-16 14:25:10'
        },
        {
          id: 3,
          code: 'CARD-STU7-VWX8-YZ90',
          type: 'forever',
          days: 36500,
          status: 0,
          used_by: null,
          created_at: '2023-05-10 16:45:20',
          used_at: null
        }
      ]
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    // 获取卡密列表数据
    fetchData() {
      this.loading = true
      
      // 创建一个新的查询对象，避免修改原始对象
      const query = { ...this.listQuery }
      
      // 如果状态是"全部"，则不传递status参数
      if (query.status === 'all') {
        delete query.status
      }
      
      // 如果有搜索关键词，添加到查询参数中
      if (this.searchKeyword && this.searchKeyword.trim() !== '') {
        query.search = this.searchKeyword.trim()
      }
      
      console.log('发送查询参数:', query) // 调试日志
      
      // 使用真实API请求
      getCardList(query)
        .then(response => {
          console.log('API返回数据:', response) // 调试日志
          
          // 处理API返回的特定数据结构
          if (response && Array.isArray(response.carmines)) {
            // 将API返回的数据映射到组件需要的格式
            this.cardList = response.carmines.map(item => ({
              id: item.id,
              code: item.carmine,
              type: this.getTypeFromName(item.type_name),
              days: item.duration,
              status: item.user_id ? 1 : 0, // 如果有user_id则表示已使用
              used_by: item.user_id,
              created_at: item.created_at,
              used_at: item.activated_at
            }))
            this.total = response.total
          } else {
            // 兜底方案
            this.cardList = []
            this.total = 0
            console.error('未知的API返回格式:', response)
          }
        })
        .catch(error => {
          console.error('获取卡密列表失败:', error)
          this.$message.error('获取卡密列表失败: ' + (error.message || '未知错误'))
          // 出错时使用空数据
          this.cardList = []
          this.total = 0
        })
        .finally(() => {
          this.loading = false
        })
    },
    
    // 处理搜索按钮点击
    handleSearch() {
      this.listQuery.page = 1 // 重置页码
      this.fetchData() // 重新获取数据
    },
    
    // 处理筛选条件变化
    handleFilter() {
      this.listQuery.page = 1 // 重置页码
      this.fetchData() // 重新获取数据
    },
    
    showGenerateDialog() {
      this.generateDialogVisible = true
      this.$nextTick(() => {
        this.$refs.generateForm && this.$refs.generateForm.resetFields()
      })
    },
    handleGenerateSubmit() {
      this.$refs.generateForm.validate(valid => {
        if (valid) {
          this.generateLoading = true
          
          // 使用修改后的API调用
          generateCards({
            type: this.generateForm.type,
            count: this.generateForm.count
          })
            .then(response => {
              this.$message.success(`成功生成 ${this.generateForm.count} 张卡密`)
              this.generateDialogVisible = false
              
              // 显示生成的卡密列表
              if (response && Array.isArray(response.carmines)) {
                this.generatedCodes = response.carmines
                this.resultDialogVisible = true
              }
              
              this.fetchData()
            })
            .catch(error => {
              console.error('生成卡密失败:', error)
              this.$message.error('生成卡密失败: ' + (error.message || '未知错误'))
            })
            .finally(() => {
              this.generateLoading = false
            })
        }
      })
    },
    // 复制所有生成的卡密
    copyAllCodes() {
      const text = this.generatedCodes.join('\n')
      const textarea = document.createElement('textarea')
      textarea.value = text
      textarea.setAttribute('readonly', '')
      textarea.style.position = 'absolute'
      textarea.style.left = '-9999px'
      document.body.appendChild(textarea)
      
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
      
      this.$message({
        message: '已复制全部卡密到剪贴板',
        type: 'success',
        duration: 1500
      })
    },
    handleCurrentChange(page) {
      this.listQuery.page = Number(page)
      this.fetchData()
    },
    copyCardCode(code) {
      // 创建一个临时的textarea元素
      const textarea = document.createElement('textarea')
      textarea.value = code
      textarea.setAttribute('readonly', '')
      textarea.style.position = 'absolute'
      textarea.style.left = '-9999px'
      document.body.appendChild(textarea)
      
      // 选择并复制文本
      textarea.select()
      document.execCommand('copy')
      
      // 移除临时元素
      document.body.removeChild(textarea)
      
      // 显示成功提示
      this.$message({
        message: '卡密已复制到剪贴板',
        type: 'success',
        duration: 1500
      })
    },
    handleDelete(row) {
      this.$confirm(`确认删除卡密 ${row.code}?`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 调用删除API
        deleteCard(row.id)
          .then(response => {
            this.$message.success('删除成功!')
            this.fetchData() // 重新加载数据
          })
          .catch(error => {
            console.error('删除卡密失败:', error)
            this.$message.error('删除卡密失败: ' + (error.message || '未知错误'))
          })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
      })
    },
    formatDate(dateString) {
      if (!dateString) return '-'
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
    getCardTypeName(type) {
      return this.cardTypes[type]?.name || type
    },
    getCardTypeTag(type) {
      const typeMap = {
        'day': 'info',
        'week': 'warning',
        'month': 'success',
        'year': 'primary',
        'forever': 'danger'
      }
      return typeMap[type] || ''
    },
    formatDays(days) {
      if (days >= 36500) {
        return '永久'
      } else if (days >= 365) {
        return `${Math.floor(days / 365)} 年`
      } else if (days >= 30) {
        return `${Math.floor(days / 30)} 个月`
      } else if (days >= 7) {
        return `${Math.floor(days / 7)} 周`
      } else {
        return `${days} 天`
      }
    },
    // 根据类型名称获取类型代码
    getTypeFromName(typeName) {
      // 反向查找类型
      for (const [key, value] of Object.entries(this.cardTypes)) {
        if (value.name === typeName) {
          return key
        }
      }
      
      // 默认处理
      switch (typeName) {
        case '天卡': return 'day'
        case '周卡': return 'week'
        case '月卡': return 'month'
        case '年卡': return 'year'
        case '永久卡': return 'forever'
        default: return 'unknown'
      }
    }
  }
}
</script>

<style scoped>
.app-container {
  padding: 20px;
}

.filter-container {
  margin-bottom: 15px;
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

.card-result-container {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 10px;
  background-color: #f9f9f9;
}

.card-code-item {
  padding: 8px;
  margin-bottom: 5px;
  background-color: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 3px;
  font-family: monospace;
  font-size: 14px;
}
</style> 