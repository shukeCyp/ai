import { get, post } from './config.js';

// 创建AI视频 - 使用原生fetch处理文件上传
export const createVideo = async (formData) => {
  try {
    return await post('/ai_video/create_video', formData, null, null, true);
  } catch (error) {
    console.error('API请求失败:', error);
    throw error;
  }
};

// 获取AI视频列表
export const getVideoList = async (page = 1, pageSize = 10) => {
  try {
    return await get(`/ai_video/list?page=${page}&page_size=${pageSize}`);
  } catch (error) {
    console.error('API请求失败:', error);
    throw error;
  }
};