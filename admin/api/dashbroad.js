import { request, getBaseURL } from './config.js';

/**
 * 获取仪表盘数据
 * @returns {Promise} 返回仪表盘数据
 */
export const getDashboardData = () => {
  return request({
    url: '/admin/dashbroad/dashboard',
    method: 'GET'
  });
};

/**
 * 获取Runway账号仪表盘数据
 * @returns {Promise} 返回Runway账号仪表盘数据
 */
export const getRunwayDashboardData = () => {
  return request({
    url: '/admin/dashbroad/runway_dashboard',
    method: 'GET'
  });
};

/**
 * 获取指定Runway账号的详细统计数据
 * @param {number} accountId - Runway账号ID
 * @returns {Promise} 返回账号详细统计数据
 */
export const getRunwayAccountStats = (accountId) => {
  return request({
    url: `/admin/dashbroad/runway_account_stats/${accountId}`,
    method: 'GET'
  });
};

/**
 * 清理卡住的任务
 * @returns {Promise} 返回清理结果
 */
export const cleanupStalledTasks = () => {
  return request({
    url: '/admin/dashbroad/cleanup_stalled_tasks',
    method: 'POST'
  });
};

