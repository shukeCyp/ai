<template>
  <div class="accounts-container">
    <div class="header-actions">
      <el-button type="primary" @click="showAddDialog">添加账号</el-button>
      <el-input
        v-model="searchKeyword"
        placeholder="搜索账号"
        style="width: 200px; margin-left: 10px"
        clearable
        @clear="handleSearch"
        @keyup.enter.native="handleSearch"
      >
        <el-button slot="append" icon="el-icon-search" @click="handleSearch"></el-button>
      </el-input>
    </div>

    <!-- 账号列表 -->
    <el-table
      v-loading="loading"
      :data="accountList"
      border
      style="width: 100%; margin-top: 20px"
    >
      <el-table-column prop="id" label="ID" width="80"></el-table-column>
      <el-table-column prop="username" label="用户名" width="150"></el-table-column>
      <el-table-column prop="password" label="密码" width="150"></el-table-column>
      <el-table-column prop="as_team_id" label="团队ID" width="150"></el-table-column>
      <el-table-column prop="plan_expires" label="计划到期时间" width="180">
        <template slot-scope="scope">
          {{ formatDate(scope.row.plan_expires) }}
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template slot-scope="scope">
          {{ formatDate(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="220">
        <template slot-scope="scope">
          <el-button
            size="mini"
            type="success"
            @click="handleCreateSession(scope.row)"
            :loading="scope.row.sessionLoading"
          >
            创建Session
          </el-button>
          <el-button
            size="mini"
            type="danger"
            @click="handleDelete(scope.row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        background
        layout="total, prev, pager, next, jumper"
        :current-page.sync="currentPage"
        :page-size="pageSize"
        :total="total"
        @current-change="handleCurrentChange"
      ></el-pagination>
    </div>

    <!-- 添加账号弹窗 -->
    <el-dialog title="添加账号" :visible.sync="dialogVisible" width="500px">
      <el-form :model="accountForm" :rules="accountRules" ref="accountForm" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="accountForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="accountForm.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleAddAccount">确 定</el-button>
      </div>
    </el-dialog>

    <!-- Session结果弹窗 -->
    <el-dialog title="Session创建成功" :visible.sync="sessionDialogVisible" width="500px">
      <div v-if="sessionResult" class="session-result">
        <p><strong>Session ID:</strong> {{ sessionResult.session_id }}</p>
        
        <!-- 复制按钮 -->
        <el-button 
          size="small" 
          type="primary" 
          @click="copySessionId"
          style="margin-top: 10px;"
        >
          复制Session ID
        </el-button>
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button @click="sessionDialogVisible = false">关闭</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { addRunwayAccount, getRunwayAccountList, createRunwaySession } from '../../../api/runway_account.js';

export default {
  name: 'RunwayAccounts',
  data() {
    return {
      loading: false,
      submitLoading: false,
      dialogVisible: false,
      sessionDialogVisible: false,
      searchKeyword: '',
      currentPage: 1,
      pageSize: 10,
      total: 0,
      accountList: [],
      accountForm: {
        username: '',
        password: ''
      },
      sessionResult: null,
      accountRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
        ]
      }
    };
  },
  created() {
    this.fetchAccounts();
  },
  methods: {
    // 获取账号列表
    fetchAccounts() {
      this.loading = true;
      getRunwayAccountList()
        .then(response => {
          if (response && response.accounts) {
            // 只添加sessionLoading属性，不再需要showPassword
            this.accountList = (response.accounts || []).map(account => ({
              ...account,
              sessionLoading: false
            }));
            this.total = response.total || 0;
          } else {
            this.accountList = [];
            this.total = 0;
          }
        })
        .catch(error => {
          console.error('获取账号列表失败:', error);
          this.$message.error('获取账号列表失败: ' + error.message);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    
    // 显示添加账号弹窗
    showAddDialog() {
      this.accountForm = {
        username: '',
        password: ''
      };
      this.dialogVisible = true;
      // 在下一个事件循环中重置表单验证
      this.$nextTick(() => {
        if (this.$refs.accountForm) {
          this.$refs.accountForm.resetFields();
        }
      });
    },
    
    // 添加账号
    handleAddAccount() {
      this.$refs.accountForm.validate(valid => {
        if (valid) {
          this.submitLoading = true;
          addRunwayAccount(this.accountForm.username, this.accountForm.password)
            .then(response => {
              this.$message.success('添加账号成功');
              this.dialogVisible = false;
              this.fetchAccounts(); // 重新加载账号列表
            })
            .catch(error => {
              console.error('添加账号失败:', error);
              this.$message.error('添加账号失败: ' + error.message);
            })
            .finally(() => {
              this.submitLoading = false;
            });
        } else {
          return false;
        }
      });
    },
    
    // 创建Session
    handleCreateSession(row) {
      // 设置当前行的loading状态
      this.$set(row, 'sessionLoading', true);
      
      createRunwaySession(row.id)
        .then(response => {
          this.sessionResult = response;
          this.sessionDialogVisible = true;
          this.$message.success('Session创建成功');
        })
        .catch(error => {
          console.error('创建Session失败:', error);
          this.$message.error('创建Session失败: ' + error.message);
        })
        .finally(() => {
          // 清除loading状态
          this.$set(row, 'sessionLoading', false);
        });
    },
    
    // 删除账号
    handleDelete(row) {
      this.$confirm('确认要删除该账号吗? 删除后无法恢复!', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 这里需要实现删除账号的API调用
        this.$message.success('删除成功');
        // 从列表中移除
        const index = this.accountList.findIndex(item => item.id === row.id);
        if (index !== -1) {
          this.accountList.splice(index, 1);
        }
      }).catch(() => {
        // 取消操作
      });
    },
    
    // 搜索
    handleSearch() {
      this.currentPage = 1;
      this.fetchAccounts();
    },
    
    // 页码变化
    handleCurrentChange(val) {
      this.currentPage = val;
      this.fetchAccounts();
    },
    
    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    },
    
    // 复制Session ID
    copySessionId() {
      if (this.sessionResult && this.sessionResult.session_id) {
        const el = document.createElement('textarea');
        el.value = this.sessionResult.session_id;
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
        this.$message.success('Session ID已复制到剪贴板');
      }
    }
  }
};
</script>

<style scoped>
.accounts-container {
  padding: 20px;
}

.header-actions {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.session-result {
  text-align: center;
}

.session-result p {
  font-size: 16px;
  margin-bottom: 15px;
}
</style> 