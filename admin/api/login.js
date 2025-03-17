import { request, getBaseURL } from './config.js';

/**
 * 用户登录
 * @param {string} username - 用户名
 * @param {string} password - 密码
 * @returns {Promise} - 返回登录请求的Promise对象
 */
export function login(username, password) {
  // 使用 URLSearchParams 构建查询参数
  const url = `/admin/user/login?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`;
  
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
 * 直接获取登录URL (用于特殊情况)
 * @param {string} username - 用户名
 * @param {string} password - 密码
 * @returns {string} - 完整的登录URL
 */
export function getLoginUrl(username, password) {
  const baseURL = getBaseURL();
  return `${baseURL}/admin/user/login?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`;
}

/**
 * 登出
 * @returns {Promise} - 返回登出请求的Promise对象
 */
export function logout() {
  return request({
    url: '/admin/user/logout',
    method: 'POST'
  });
}
