import { get, post } from './config.js';

// 用户登录
export function login(data) {
  return post('/user/user/login', null, null, data);
}

// 用户注册
export function register(data) {
  return post('/user/user/register', data);
}

// 获取用户信息
export function getUserInfo() {
  return get('/user/user/info');
}

// 退出登录
export function logout() {
  return post('/user/user/logout');
}

// 心跳检测
export function heartbeat() {
  return get('/user/user/heartbeat');
}

