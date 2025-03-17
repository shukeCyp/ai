import { request, getBaseURL } from './config.js';

/**
 * 获取用户列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码，从1开始
 * @param {number} params.page_size - 每页数量
 * @param {string} [params.keyword] - 搜索关键词
 * @returns {Promise} 返回用户列表数据
 */
export const getUserList = (params) => {
  return request({
    url: '/admin/users',
    method: 'GET',
    params
  });
};

/**
 * 获取用户详细信息
 * @param {number} userId - 用户ID
 * @returns {Promise} 返回用户详细信息
 */
export const getUserDetail = (userId) => {
  return request({
    url: `/admin/user/${userId}`,
    method: 'GET'
  });
};