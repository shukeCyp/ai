<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h2>系统仪表盘</h2>
      <p>实时监控系统运行状态</p>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>
    
    <template v-else>
      <!-- 统计卡片 -->
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card shadow="hover" class="data-card">
            <div class="data-card-content">
              <div class="data-card-icon blue">
                <i class="el-icon-user"></i>
              </div>
              <div class="data-card-info">
                <div class="data-card-title">用户总数</div>
                <div class="data-card-value">{{ dashboardData.users.total }}</div>
              </div>
            </div>
            <div class="data-card-footer">
              <span>今日新增: {{ dashboardData.users.today }}</span>
              <span style="margin-left: 10px;">昨日: {{ dashboardData.users.yesterday }}</span>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover" class="data-card">
            <div class="data-card-content">
              <div class="data-card-icon green">
                <i class="el-icon-video-camera"></i>
              </div>
              <div class="data-card-info">
                <div class="data-card-title">视频总数</div>
                <div class="data-card-value">{{ dashboardData.videos.total }}</div>
              </div>
            </div>
            <div class="data-card-footer">
              <span>今日生成: {{ dashboardData.videos.today }}</span>
              <span style="margin-left: 10px;">昨日: {{ dashboardData.videos.yesterday }}</span>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover" class="data-card">
            <div class="data-card-content">
              <div class="data-card-icon orange">
                <i class="el-icon-s-order"></i>
              </div>
              <div class="data-card-info">
                <div class="data-card-title">任务总数</div>
                <div class="data-card-value">{{ dashboardData.tasks.total }}</div>
              </div>
            </div>
            <div class="data-card-footer">
              <span>今日任务: {{ dashboardData.tasks.today }}</span>
              <span style="margin-left: 10px;">昨日: {{ dashboardData.tasks.yesterday }}</span>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover" class="data-card">
            <div class="data-card-content">
              <div class="data-card-icon purple">
                <i class="el-icon-key"></i>
              </div>
              <div class="data-card-info">
                <div class="data-card-title">账号总数</div>
                <div class="data-card-value">{{ dashboardData.accounts.total }}</div>
              </div>
            </div>
            <div class="data-card-footer">
              <span>今日产分: {{ dashboardData.accounts.today_points || 0 }}</span>
              <span style="margin-left: 10px;">昨日: {{ dashboardData.accounts.yesterday_points || 0 }}</span>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 状态卡片 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <!-- 线程池状态 -->
        <el-col :span="8">
          <el-card shadow="hover" class="status-panel">
            <div slot="header" class="clearfix">
              <span><i class="el-icon-cpu"></i> 线程池状态</span>
              <el-tag 
                :type="dashboardData.thread_pool.running ? 'success' : 'danger'"
                size="small" 
                style="float: right; margin-top: 3px;"
              >
                {{ dashboardData.thread_pool.running ? '运行中' : '已停止' }}
              </el-tag>
            </div>
            <div class="status-panel-content">
              <div class="status-metric">
                <div class="metric-value">{{ dashboardData.thread_pool.active_workers }}</div>
                <div class="metric-label">活跃线程</div>
              </div>
              <div class="status-metric">
                <div class="metric-value">{{ dashboardData.thread_pool.max_workers }}</div>
                <div class="metric-label">最大线程</div>
              </div>
              <div class="status-metric">
                <div class="metric-value">{{ dashboardData.thread_pool.queue_size }}</div>
                <div class="metric-label">队列大小</div>
              </div>
              <div class="status-progress">
                <div class="progress-label">
                  <span>线程使用率</span>
                  <span>{{ calculateThreadUsage }}%</span>
                </div>
                <el-progress 
                  :percentage="calculateThreadUsage" 
                  :status="threadPoolStatus"
                  :stroke-width="10"
                ></el-progress>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <!-- 账号池状态 -->
        <el-col :span="8">
          <el-card shadow="hover" class="status-panel">
            <div slot="header" class="clearfix">
              <span><i class="el-icon-s-platform"></i> 账号状态</span>
              <el-button 
                style="float: right; padding: 3px 0" 
                type="text"
                @click="cleanupStalledTasks"
              >
                清理卡住任务
              </el-button>
            </div>
            <div class="status-panel-content">
              <div class="status-metric">
                <div class="metric-value">{{ dashboardData.accounts.total_points || 0 }}</div>
                <div class="metric-label">总产分</div>
              </div>
              <div class="status-metric">
                <div class="metric-value">{{ dashboardData.accounts.total }}</div>
                <div class="metric-label">总账号数</div>
              </div>
              <div class="status-metric">
                <div class="metric-value">{{ dashboardData.accounts.active || 0 }}</div>
                <div class="metric-label">活跃账号</div>
              </div>
              <div class="status-metric">
                <div class="metric-value">{{ dashboardData.accounts.expired || 0 }}</div>
                <div class="metric-label">过期账号</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <!-- 任务状态 -->
        <el-col :span="8">
          <el-card shadow="hover" class="status-panel">
            <div slot="header" class="clearfix">
              <span><i class="el-icon-s-data"></i> 任务状态分布</span>
            </div>
            <div class="status-panel-content">
              <div class="status-metric">
                <div class="metric-value">{{ dashboardData.task_status.queued || 0 }}</div>
                <div class="metric-label">
                  <span class="status-dot queued-dot"></span>
                  排队中
                </div>
              </div>
              <div class="status-metric">
                <div class="metric-value">{{ dashboardData.task_status.processing || 0 }}</div>
                <div class="metric-label">
                  <span class="status-dot processing-dot"></span>
                  处理中
                </div>
              </div>
              <div class="status-metric">
                <div class="metric-value">{{ dashboardData.task_status.completed || 0 }}</div>
                <div class="metric-label">
                  <span class="status-dot completed-dot"></span>
                  已完成
                </div>
              </div>
              <div class="status-metric">
                <div class="metric-value">{{ dashboardData.task_status.failed || 0 }}</div>
                <div class="metric-label">
                  <span class="status-dot failed-dot"></span>
                  已失败
                </div>
              </div>
              <div class="status-metric" v-if="dashboardData.task_status.deleted">
                <div class="metric-value">{{ dashboardData.task_status.deleted }}</div>
                <div class="metric-label">
                  <span class="status-dot deleted-dot"></span>
                  已删除
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- Runway账号统计 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <el-card shadow="hover">
            <div slot="header" class="clearfix">
              <span>Runway账号使用情况</span>
            </div>
            <el-table
              v-loading="runwayLoading"
              :data="runwayAccounts"
              style="width: 100%"
              border
            >
              <el-table-column
                prop="id"
                label="ID"
                width="80"
                align="center"
              />
              <el-table-column
                prop="username"
                label="账号"
                min-width="150"
                align="center"
              />
              <el-table-column
                prop="total_videos"
                label="总生成数"
                width="100"
                align="center"
              />
              <el-table-column
                prop="today_videos"
                label="今日生成"
                width="100"
                align="center"
              />
              <el-table-column
                prop="yesterday_videos"
                label="昨日生成"
                width="100"
                align="center"
              />
              <el-table-column
                prop="plan_expires"
                label="到期时间"
                width="180"
                align="center"
              >
                <template slot-scope="scope">
                  <el-tag 
                    :type="isExpired(scope.row.plan_expires) ? 'danger' : 'success'"
                    size="medium"
                  >
                    {{ formatDate(scope.row.plan_expires) }}
                  </el-tag>
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
                    @click="viewAccountDetail(scope.row)"
                  >
                    详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </template>
  </div>
</template>

<script>
import { getDashboardData, getRunwayDashboardData, cleanupStalledTasks } from '../../api/dashbroad.js';

export default {
  name: 'Dashboard',
  data() {
    return {
      loading: true,
      runwayLoading: true,
      dashboardData: {
        users: { total: 0, today: 0, yesterday: 0 },
        tasks: { total: 0, today: 0, yesterday: 0 },
        videos: { total: 0, today: 0, yesterday: 0 },
        accounts: { 
          total: 0, 
          today_points: 0, 
          yesterday_points: 0, 
          total_points: 0,
          active: 0,
          expired: 0,
          pool: { 
            available_instances: 0, 
            in_use_instances: 0, 
            total_instances: 0,
            unique_available: 0,
            unique_in_use: 0,
            unique_total: 0
          } 
        },
        task_status: { queued: 0, processing: 0, completed: 0, failed: 0, deleted: 0 },
        thread_pool: { queue_size: 0, active_workers: 0, max_workers: 0, running: false }
      },
      runwayAccounts: [],
    }
  },
  created() {
    this.loadData();
  },
  computed: {
    calculateThreadUsage() {
      const max = this.dashboardData.thread_pool.max_workers;
      if (!max) return 0;
      return Math.round((this.dashboardData.thread_pool.active_workers / max) * 100);
    },
    calculateAccountUsage() {
      const total = this.dashboardData.accounts.pool.total_instances;
      if (!total) return 0;
      return Math.round((this.dashboardData.accounts.pool.in_use_instances / total) * 100);
    },
    threadPoolStatus() {
      const usage = this.calculateThreadUsage;
      if (usage >= 90) return 'exception';
      if (usage >= 70) return 'warning';
      return 'success';
    },
    accountPoolStatus() {
      const usage = this.calculateAccountUsage;
      if (usage >= 90) return 'exception';
      if (usage >= 70) return 'warning';
      return 'success';
    }
  },
  methods: {
    async loadData() {
      this.loading = true;
      this.runwayLoading = true;
      
      try {
        // 获取仪表盘数据
        const dashboardResponse = await getDashboardData();
        this.dashboardData = dashboardResponse;
        
        // 获取Runway账号数据
        const runwayResponse = await getRunwayDashboardData();
        this.runwayAccounts = runwayResponse.accounts;
      } catch (error) {
        console.error('获取仪表盘数据失败:', error);
        this.$message.error('获取仪表盘数据失败');
      } finally {
        this.loading = false;
        this.runwayLoading = false;
      }
    },
    formatDate(dateString) {
      if (!dateString) return '未设置';
      const date = new Date(dateString);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    isExpired(dateString) {
      if (!dateString) return true;
      const date = new Date(dateString);
      return date < new Date();
    },
    viewAccountDetail(account) {
      this.$router.push(`/runway/account-detail/${account.id}`);
    },
    async cleanupStalledTasks() {
      try {
        const response = await cleanupStalledTasks();
        this.$message.success(response.message);
        // 刷新数据
        this.loadData();
      } catch (error) {
        console.error('清理卡住任务失败:', error);
        this.$message.error('清理卡住任务失败');
      }
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.dashboard-header {
  margin-bottom: 20px;
}

.dashboard-header h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.dashboard-header p {
  margin: 10px 0 0;
  color: #909399;
}

.loading-container {
  padding: 20px;
}

.data-card {
  height: 120px;
}

.data-card-content {
  display: flex;
  align-items: center;
}

.data-card-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
}

.data-card-icon i {
  font-size: 24px;
  color: #fff;
}

.blue {
  background-color: #409EFF;
}

.green {
  background-color: #67C23A;
}

.orange {
  background-color: #E6A23C;
}

.purple {
  background-color: #8e44ad;
}

.data-card-title {
  font-size: 14px;
  color: #909399;
}

.data-card-value {
  font-size: 24px;
  font-weight: bold;
  margin-top: 5px;
}

.data-card-footer {
  margin-top: 15px;
  font-size: 12px;
  color: #909399;
}

/* 新增样式 */
.status-panel {
  height: 100%;
}

.status-panel-content {
  display: flex;
  flex-wrap: wrap;
  padding: 10px 0;
}

.status-metric {
  width: 50%;
  text-align: center;
  margin-bottom: 15px;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.metric-label {
  font-size: 14px;
  color: #606266;
  margin-top: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-progress {
  width: 100%;
  padding: 0 10px;
  margin-top: 5px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 14px;
  color: #606266;
}

.status-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 5px;
}

.queued-dot {
  background-color: #E6A23C;
}

.processing-dot {
  background-color: #409EFF;
}

.completed-dot {
  background-color: #67C23A;
}

.failed-dot {
  background-color: #F56C6C;
}

.deleted-dot {
  background-color: #909399;
}

.clearfix:after {
  content: "";
  display: table;
  clear: both;
}
</style> 