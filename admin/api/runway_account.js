import { request, getBaseURL } from './config.js';


/**
 * 添加Runway账号
 * @param {string} username - 用户名
 * @param {string} password - 密码
 * @returns {Promise} - 返回添加账号请求的Promise对象
 */
export function addRunwayAccount(username, password) {
  const url = `/admin/runway_account/account/add?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`;
  
  return request({
    url: url,
    method: 'POST',
    header: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
  });
}

/**
 * 获取Runway账号列表
 * @returns {Promise} - 返回获取账号列表的Promise对象
 */
export function getRunwayAccountList() {
  return request({
    url: `/admin/runway_account/account/list`,
    method: 'GET',
    header: {
      'Accept': 'application/json'
    }
  });
}

/**
 * 获取所有跑道账号
 * @returns {Promise} - 返回获取账号列表的Promise对象
 */
export function getAllAccounts() {
  return request({
    url: '/admin/runway/accounts',
    method: 'GET'
  });
}

/**
 * 添加跑道账号
 * @param {Object} accountData - 账号数据
 * @param {string} accountData.username - 用户名
 * @param {string} accountData.password - 密码
 * @param {string} accountData.nickname - 昵称
 * @param {string} accountData.remark - 备注
 * @returns {Promise} - 返回添加账号的Promise对象
 */
export function addAccount(accountData) {
  return request({
    url: '/admin/runway/account',
    method: 'POST',
    data: accountData
  });
}

/**
 * 更新跑道账号
 * @param {string} accountId - 账号ID
 * @param {Object} accountData - 更新的账号数据
 * @returns {Promise} - 返回更新账号的Promise对象
 */
export function updateAccount(accountId, accountData) {
  return request({
    url: `/admin/runway/account/${accountId}`,
    method: 'PUT',
    data: accountData
  });
}

/**
 * 删除跑道账号
 * @param {string} accountId - 要删除的账号ID
 * @returns {Promise} - 返回删除账号的Promise对象
 */
export function deleteAccount(accountId) {
  return request({
    url: `/admin/runway/account/${accountId}`,
    method: 'DELETE'
  });
}

/**
 * 获取账号详情
 * @param {string} accountId - 账号ID
 * @returns {Promise} - 返回账号详情的Promise对象
 */
export function getAccountDetail(accountId) {
  return request({
    url: `/admin/runway/account/${accountId}`,
    method: 'GET'
  });
}

/**
 * 修改账号状态
 * @param {string} accountId - 账号ID
 * @param {number} status - 状态值 (0: 禁用, 1: 启用)
 * @returns {Promise} - 返回修改状态的Promise对象
 */
export function changeAccountStatus(accountId, status) {
  return request({
    url: `/admin/runway/account/${accountId}/status`,
    method: 'PUT',
    data: { status }
  });
}

/**
 * 创建Runway账号Session
 * @param {number} runwayId - Runway账号ID
 * @returns {Promise} - 返回创建Session的Promise对象
 */
export function createRunwaySession(runwayId) {
  const url = `/admin/runway_account/session/create?runway_id=${runwayId}`;
  
  return request({
    url: url,
    method: 'POST',
    header: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
  });
}

/**
 * 获取Runway Session列表
 * @param {number} page - 页码
 * @param {number} pageSize - 每页数量
 * @param {number} [runwayId] - 可选的Runway账号ID，不传则获取所有
 * @returns {Promise} - 返回获取Session列表的Promise对象
 */
export function getRunwaySessionList(page = 1, pageSize = 10, runwayId = null) {
  let url = `/admin/runway_account/session/list?page=${page}&page_size=${pageSize}`;
  console.log(page)
  if (runwayId) {
    url += `&runway_id=${runwayId}`;
  }
  
  return request({
    url: url,
    method: 'GET',
    header: {
      'Accept': 'application/json'
    }
  });
}

/**
 * 删除Runway Session
 * @param {string} sessionId - Session ID
 * @returns {Promise} - 返回删除Session的Promise对象
 */
export function deleteRunwaySession(sessionId) {
  const url = `/admin/runway_account/session/delete?session_id=${sessionId}`;
  
  return request({
    url: url,
    method: 'DELETE',
    header: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
  });
}
