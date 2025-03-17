import { request, getBaseURL } from './config.js';

/**
 * 获取卡密列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.type - 卡密类型(可选)
 * @param {string} params.status - 卡密状态(可选): unused, used, expired
 * @returns {Promise} - 返回获取卡密列表的Promise对象
 */
export function getCardList(params) {
  console.log('发送请求:', params) // 调试日志
  
  // 构建URL查询参数
  let url = '/admin/carmine/list';
  if (params) {
    const queryParams = [];
    for (const key in params) {
      if (params[key] !== undefined && params[key] !== null) {
        queryParams.push(`${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`);
      }
    }
    if (queryParams.length > 0) {
      url += '?' + queryParams.join('&');
    }
  }
  
  return request({
    url: url,
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    method: 'GET'
  })
}

/**
 * 批量生成卡密
 * @param {Object} data - 生成参数
 * @param {string} data.type - 卡密类型
 * @param {number} data.count - 生成数量
 * @returns {Promise} - 返回生成卡密的Promise对象
 */
export function generateCards(data) {
  return request({
    url: `/admin/carmine/generate?type=${data.type}&count=${data.count}`,
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
  });
}

/**
 * 删除卡密
 * @param {number} id - 卡密ID
 * @returns {Promise} - 返回删除卡密的Promise对象
 */
export function deleteCard(id) {
  return request({
    url: `/admin/carmine/${id}`,
    method: 'DELETE'
  })
} 