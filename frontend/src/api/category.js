import { get, post } from './config.js';

// 获取分类列表
export function getCategories() {
  return get('/prompt/categories');
}